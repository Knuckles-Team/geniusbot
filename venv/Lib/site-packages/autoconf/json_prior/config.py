import inspect
import json
import logging
from collections import Sized
from glob import glob
from typing import List, Type, Tuple

from autoconf.exc import PriorException
from autoconf.named import family

logger = logging.getLogger(__name__)

default_prior = {
    "type": "Uniform",
    "lower_limit": 0.0,
    "upper_limit": 1.0,
    "width_modifier": {"type": "Absolute", "value": 0.2},
    "gaussian_limits": {"lower": 0.0, "upper": 1.0}
}


def make_config_for_class(cls):
    path = path_for_class(cls)
    arg_spec = inspect.getfullargspec(cls)
    arguments = arg_spec.args[1:]
    defaults = list(reversed(arg_spec.defaults or list()))

    config = dict()
    for i, argument in enumerate(reversed(arguments)):
        if i < len(defaults):
            default = defaults[i]
            if isinstance(
                    default,
                    Sized
            ):
                for j in range(len(default)):
                    config[f"{argument}_{j}"] = default_prior
                continue
        config[argument] = default_prior

    return path, config


def path_for_class(cls) -> List[str]:
    """
    A list describing the import path for a given class.

    Parameters
    ----------
    cls
        A class with some module path

    Returns
    -------
    A list of modules terminating in the name of a class
    """
    return f"{cls.__module__}.{cls.__name__}".split(".")


class JSONPriorConfig:
    def __init__(self, config_dict: dict, directory=None):
        """
        Parses configuration describing priors associated with classes.

        The path pointing to a class is the same as the path to import it.

        Paths can be strings with '.' as a delimiter.
        {"module.class": config}

        Else they can be a series of dictionary keys.
        {"module": {"class": config}}

        Or any combination thereof.

        Parameters
        ----------
        config_dict
            A dictionary describing the prior configuration for constructor arguments
            of different classes.
        """
        self.obj = config_dict
        self.directory = directory
        self._path_value_map = None

    @property
    def paths(self):
        return list(self.path_value_map.keys())

    @property
    def path_value_map(self) -> dict:
        """
        A dictionary matching every possible path to the configuration it points to.
        """
        if self._path_value_map is None:

            def get_path_values(obj):
                path_values = dict()
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        path_values[key] = value
                        for path, path_value in get_path_values(value).items():
                            path_values[f"{key}.{path}"] = path_value

                return path_values

            self._path_value_map = get_path_values(self.obj)
        return self._path_value_map

    @property
    def path_value_tuples(self) -> List[Tuple[str, object]]:
        """
        Tuple pairs matching every possible path to the configuration it points to.
        These are ordered by key length with the longest key first.
        """
        return sorted(
            list(self.path_value_map.items()),
            key=lambda item: len(item[0]),
            reverse=True,
        )

    @classmethod
    def from_directory(cls, directory: str) -> "JSONPriorConfig":
        """
        Load JSONPriorConfiguration from a file.

        Parameters
        ----------
        directory
            The path to a file.

        Returns
        -------
        A configuration instance.
        """
        config_dict = dict()
        for file in glob(f"{directory}/*.json"):
            with open(file) as f:
                config_dict[file.split("/")[-1].split(".")[0]] = json.load(f)

        return JSONPriorConfig(config_dict, directory=directory)

    def save(self):
        for key in self.obj.keys():
            with open(f"{self.directory}/{key}.json", "w+") as f:
                json.dump(self.obj[key], f, indent=4)

    def __str__(self):
        return json.dumps(self.obj)

    def __getitem__(self, item):
        return JSONPriorConfig(self.obj[".".join(item)], directory=self.directory)

    def __contains__(self, item):
        return ".".join(item) in self.obj

    def for_class_and_suffix_path(self, cls: Type, suffix_path: List[str], should_retry=True):
        """
        Get configuration for a prior.

        If it is just basic configuration then the suffix path is just the
        name of the prior in a list. Width configuration also adds an
        additional "width_modifier" item.

        If configuration is not found for the class then configurations for
        parents of the class are searched.

        Parameters
        ----------
        should_retry
        cls
            The class with which the prior is associated.
        suffix_path
            The path to the prior.

        Returns
        -------
        A configuration dictionary
        """
        for c in family(cls):
            try:
                return self(path_for_class(c) + suffix_path)
            except PriorException:
                pass

        if not should_retry:
            raise PriorException(f"No config found for {cls} and {suffix_path}")

        self._path_value_map = None

        path, value = make_config_for_class(cls)

        self.obj[".".join(path)] = value

        self.rearrange()
        self.save()

        return self.for_class_and_suffix_path(
            cls,
            suffix_path,
            should_retry=False
        )

    def rearrange(self):
        """
        Rearrange the configuration trying to create a more embedded
        dictionary structure rather than a big collection of paths
        mapped to values.
        """

        class PathDict:
            def __init__(self, value=None):
                self.value = value
                self.__dict = dict()

            def __getitem__(self, item):
                if item not in self.__dict:
                    self.__dict[item] = PathDict()
                return self.__dict[item]

            def __setitem__(self, key, value):
                self.__dict[key] = value

            def collapsed(self, key=None):
                if len(self.__dict) == 1:
                    new_key = list(self.__dict.keys())[0]
                    new_dict = self.__dict[new_key]
                    if key is not None:
                        new_key = f"{key}.{new_key}"
                    return new_dict.collapsed(new_key)
                if len(self.__dict) == 0:
                    if key is not None:
                        return {key: self.value}
                    return self.value
                if len(self.__dict) > 1:
                    dicts = {k: value.collapsed() for k, value in self.__dict.items()}
                    if key is not None:
                        return {key: dicts}
                    return dicts

            @property
            def dict(self):
                return {key: value.dict for key, value in self.__dict.items()}

            def add_path(self, path, value):
                current = self
                for item in path:
                    current = current[item]
                current.value = value

        path_dict = PathDict()
        for path_key in self.paths:
            path_list = path_key.split(".")
            path_dict.add_path(path_list, self(path_list))
        self.obj = path_dict.collapsed()

    def __call__(self, config_path: List[str]):
        """
        Get the config at the end of the config_path.

        The configuration dictionary is traversed until config is found
        at the end, else an exception is thrown.

        Parameters
        ----------
        config_path
            The import path of a package, module, class or class and constructor
            argument name.

        Returns
        -------
        A configuration dictionary or value

        Raises
        ------
        PriorException
            If no configuration is found.
        """
        key = ".".join(config_path)
        for path, value in self.path_value_tuples:
            if key.endswith(path):
                return value
        raise PriorException(
            f"No configuration was found for the path {config_path}"
            + ("" if self.directory is None else f" ({self.directory})")
        )
