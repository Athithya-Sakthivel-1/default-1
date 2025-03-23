import yaml
import os

# Determine the project root dynamically
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# Path to settings.yaml inside the project
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config/settings.yaml")

def load_config():
    """Loads configuration settings from YAML file and resolves paths correctly."""
    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)

    # Convert relative paths to absolute paths
    config["data"]["raw_data_path"] = os.path.abspath(os.path.join(PROJECT_ROOT, config["data"]["raw_data_path"]))
    config["data"]["processed_data_path"] = os.path.abspath(os.path.join(PROJECT_ROOT, config["data"]["processed_data_path"]))
    config["data"]["duckdb_path"] = os.path.abspath(os.path.join(PROJECT_ROOT, config["data"]["duckdb_path"]))
    config["data"]["neo4j_db_path"] = os.path.abspath(os.path.join(PROJECT_ROOT, config["data"]["neo4j_db_path"]))

    return config

# Load settings globally
CONFIG = load_config()
