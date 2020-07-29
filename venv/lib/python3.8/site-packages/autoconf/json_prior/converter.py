import json
import logging
import os
from configparser import ConfigParser
from functools import wraps
from glob import glob

logger = logging.getLogger(__name__)


def string_infinity(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result == float("inf"):
            return "inf"
        if result == float("-inf"):
            return "-inf"
        return result

    return wrapper


def default_empty(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            return dict()

    return wrapper


class Object:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


class Width:
    def __init__(self, prior):
        self.prior = prior

    @property
    def dict(self):
        return {"type": self.type_string, "value": float(self.prior.width_array[1])}

    @property
    def type_string(self):
        width_character = self.prior.width_array[0]
        if width_character == "r":
            return "Relative"
        if width_character == "a":
            return "Absolute"
        raise AssertionError(f"Width character {width_character} not recognised")


class Prior(Object):
    def __init__(self, cls, name):
        super().__init__(name)
        self.cls = cls

    @property
    def width(self):
        return Width(self)

    @property
    def default_string(self):
        return self.cls.default_section[self.name]

    @property
    def default_array(self):
        return self.default_string.split(",")

    @property
    def width_string(self):
        return self.cls.width_section[self.name]

    @property
    def width_array(self):
        return self.width_string.split(",")

    @property
    def limit_string(self):
        return self.cls.limit_section[self.name]

    @property
    def limit_array(self):
        return self.limit_string.split(",")

    @property
    def type_character(self):
        return self.default_array[0]

    @property
    def type_string(self):
        if self.type_character == "d":
            return "Deferred"
        if self.type_character in ("c", "n"):
            return "Constant"
        if self.type_character == "l":
            return "LogUniform"
        if self.type_character == "g":
            return "Gaussian"
        if self.type_character == "u":
            return "Uniform"

    @property
    @string_infinity
    def lower_limit(self):
        if self.type_character == "g":
            try:
                return float(self.limit_array[0])
            except KeyError:
                return float("-inf")
        try:
            return float(self.default_array[1])
        except IndexError:
            pass

    @property
    @string_infinity
    def upper_limit(self):
        if self.type_character == "g":
            try:
                return float(self.limit_array[1])
            except KeyError:
                return float("inf")
        return float(self.default_array[2])

    @property
    @string_infinity
    def gaussian_limit_lower(self):
        return float(self.limit_array[0])

    @property
    @string_infinity
    def gaussian_limit_higher(self):
        return float(self.limit_array[1])

    @property
    @default_empty
    def dict(self):
        prior_dict = {"type": self.type_string}
        if self.type_character == "d":
            return prior_dict
        if self.type_character == "n":
            return {**prior_dict, "value": None}
        if self.type_character == "c":
            return {**prior_dict, "value": float(self.default_array[1])}
        prior_dict = {
            **prior_dict,
            "lower_limit": self.lower_limit,
            "upper_limit": self.upper_limit,
        }
        try:
            prior_dict["width_modifier"] = self.width.dict
        except KeyError:
            pass
        if self.type_character in ("u", "l"):
            try:
                prior_dict["gaussian_limits"] = {
                    "lower": self.gaussian_limit_lower,
                    "upper": self.gaussian_limit_higher,
                }
            except KeyError:
                pass
            return prior_dict
        if self.type_character == "g":
            return {
                **prior_dict,
                "mean": float(self.default_array[1]),
                "sigma": float(self.default_array[2]),
            }
        raise AssertionError(f"Unrecognised prior type {self.type_character}")


class Class(Object):
    def __init__(self, module, name):
        super().__init__(name)
        self.module = module

    @property
    def priors(self):
        return [Prior(self, name) for name in self.default_section]

    @property
    def default_section(self):
        return self.module.default[self.name]

    @property
    def limit_section(self):
        return self.module.limit[self.name]

    @property
    def width_section(self):
        return self.module.width[self.name]

    @property
    @default_empty
    def dict(self):
        return {prior.name: prior.dict for prior in self.priors}


class Module(Object):
    def __init__(self, converter, name):
        super().__init__(name)
        self.converter = converter
        self.default = ConfigParser()
        self.default.read(f"{self.converter.default_directory}/{self.name}.ini")
        self.limit = ConfigParser()
        self.limit.read(f"{self.converter.limit_directory}/{self.name}.ini")
        self.default = ConfigParser()
        self.default.read(f"{self.converter.default_directory}/{self.name}.ini")
        self.width = ConfigParser()
        self.width.read(f"{self.converter.width_directory}/{self.name}.ini")

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return super().__eq__(other)

    @property
    def classes(self):
        return [Class(self, section) for section in self.default.sections()]

    @property
    @default_empty
    def dict(self):
        return {cls.name: cls.dict for cls in self.classes}


class Converter:
    def __init__(self, directory):
        self.directory = directory

    @property
    def default_directory(self):
        return f"{self.directory}/default"

    @property
    def limit_directory(self):
        return f"{self.directory}/limit"

    @property
    def width_directory(self):
        return f"{self.directory}/width"

    @property
    def modules(self):
        paths = glob(f"{self.directory}/default/*.ini")
        return [Module(self, path.replace(".ini", "").split("/")[-1]) for path in paths]

    @property
    @default_empty
    def dict(self):
        return {f"{module.name}": module.dict for module in self.modules}


def convert(in_directory, out_directory):
    converter = Converter(in_directory)
    os.makedirs(out_directory, exist_ok=True)
    for module in converter.modules:
        with open(f"{out_directory}/{module.name}.json", "w+") as f:
            json.dump(module.dict, f, indent=4)


if __name__ == "__main__":
    from sys import argv

    convert(argv[1], argv[1])
