import yaml
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config/settings.yaml"

class Config:
    def __init__(self, config_path=CONFIG_PATH):
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def get(self, key_path, default=None):
        """Retrieve value from YAML based on dot notation path."""
        keys = key_path.split(".")
        value = self.config
        for key in keys:
            value = value.get(key, {})
        return value if value else default

config = Config()
