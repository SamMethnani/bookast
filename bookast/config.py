import os
import toml


class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = toml.load(f)

    def __getattr__(self, name):
        return self.config[name]


# get the absolute path of the current script
script_path = os.path.abspath(__file__)

# get the directory containing the script
script_dir = os.path.dirname(script_path)

# construct the path to the config.toml file
config_path = os.path.join(script_dir, "config.toml")

# load the config.toml file
config = Config(config_path)
