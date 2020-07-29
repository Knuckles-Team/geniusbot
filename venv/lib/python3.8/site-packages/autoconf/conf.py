import os

from autoconf.json_prior.config import JSONPriorConfig
from autoconf.json_prior.converter import convert
from autoconf.named import NamedConfig, LabelConfig


def get_matplotlib_backend():
    return instance.visualize_general.get("general", "backend", str)


class NonLinear:
    def __init__(self, directory):
        self.directory = directory

    def config_for(self, name):
        return NamedConfig(f"{self.directory}/{name}.ini")


class Config:
    def __init__(self, config_path, output_path="output"):
        self.config_path = config_path
        json_config_path = f"{config_path}/json_priors"
        if not os.path.exists(json_config_path):
            convert(f"{config_path}/priors", json_config_path)
        self.prior_config = JSONPriorConfig.from_directory(json_config_path)

        self.non_linear = NonLinear(
            f"{config_path}/non_linear"
        )
        self.optimize = NonLinear(
            f"{config_path}/non_linear/optimize"
        )
        self.mcmc = NonLinear(
            f"{config_path}/non_linear/mcmc"
        )
        self.nest = NonLinear(
            f"{config_path}/non_linear/nest"
        )
        self.mock = NonLinear(
            f"{config_path}/non_linear/mock"
        )

        self.label = LabelConfig("{}/notation/label.ini".format(config_path))
        self.label_format = NamedConfig("{}/notation/label_format.ini".format(config_path))
        self.tag = LabelConfig("{}/notation/tags.ini".format(config_path))
        self.general = NamedConfig("{}/general.ini".format(config_path))
        self.visualize_general = NamedConfig(
            "{}/visualize/general.ini".format(config_path)
        )
        self.visualize_plots = NamedConfig("{}/visualize/plots.ini".format(config_path))
        self.visualize_figures = NamedConfig(
            "{}/visualize/figures.ini".format(config_path)
        )
        self.visualize_subplots = NamedConfig(
            "{}/visualize/subplots.ini".format(config_path)
        )
        self.interpolate = NamedConfig(
            "{}/grids/interpolate.ini".format(config_path)
        )
        self.radial_min = NamedConfig(
            "{}/grids/radial_minimum.ini".format(config_path)
        )
        self.output_path = output_path


def is_config_in(folder):
    return os.path.isdir("{}/config".format(folder))

"""
Search for default configuration and put output in the same folder as config.
The search is performed in this order:
1) autolens_workspace. This is assumed to be in the same directory as autolens in the Docker 
   container
2) current working directory. This is to allow for installation and use with pip where 
   users would expect the configuration in their current directory to be used.
3) relative. This is a backup for when no configuration is found. In this case it is 
   still assumed a autolens_workspace directory exists in the same directory as autofit.
"""

autofit_directory = os.path.dirname(os.path.realpath(__file__))
docker_workspace_directory = "/home/user/autolens_workspace"
current_directory = os.getcwd()

try:
    workspace_path = os.environ["WORKSPACE"]
    default = Config(
        "{}/config".format(workspace_path), "{}/output/".format(workspace_path)
    )
except KeyError:
    if is_config_in(docker_workspace_directory):
        CONFIG_PATH = "{}/config".format(docker_workspace_directory)
        default = Config(CONFIG_PATH, "{}/output/".format(docker_workspace_directory))
    elif is_config_in(current_directory):
        CONFIG_PATH = "{}/config".format(current_directory)
        default = Config(CONFIG_PATH, "{}/output/".format(current_directory))
    elif is_config_in("{}/../..".format(current_directory)):
        CONFIG_PATH = "{}/../../config".format(current_directory)
        default = Config(CONFIG_PATH, "{}/output/".format(current_directory))
    elif is_config_in("{}/../autolens_workspace".format(current_directory)):
        CONFIG_PATH = "{}/../autolens_workspace/config".format(current_directory)
        default = Config(
            CONFIG_PATH, "{}/../autolens_workspace/output/".format(current_directory)
        )
    else:
        CONFIG_PATH = "{}/../autolens_workspace/config".format(autofit_directory)
        default = Config(
            CONFIG_PATH, "{}/../autolens_workspace/output/".format(autofit_directory)
        )

instance = default