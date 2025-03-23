import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import dask.dataframe as dd
from feast import FeatureStore, Entity, FeatureView, Field, ValueType
from feast.repo_config import RepoConfig
from feast.infra.offline_stores.file_source import FileSource
from src.utils.config_loader import CONFIG

# Load paths dynamically from settings.yaml
PROCESSED_DATA_PATH = os.path.join(CONFIG["data"]["processed"], "processed_batch_data.parquet")
FEAST_REPO_PATH = os.path.join(os.getcwd(), "feature_repo")

# Ensure feature repo directory exists
os.makedirs(FEAST_REPO_PATH, exist_ok=True)

# Define the entity (user_id)
user_entity = Entity(
    name="user_id",
    value_type=ValueType.STRING,
    description="Unique identifier for a user"
)

# Define the Feature View schema
transactions_feature_view = FeatureView(
    name="transactions_features",
    entities=["user_id"],
    schema=[
        Field(name="amount", dtype=ValueType.FLOAT),
        Field(name="transaction_type", dtype=ValueType.STRING),
        Field(name="merchant", dtype=ValueType.STRING),
        Field(name="location", dtype=ValueType.STRING),
        Field(name="device", dtype=ValueType.STRING),
    ],
    source=FileSource(
        path=PROCESSED_DATA_PATH,
        event_timestamp_column="timestamp",
    ),
)

# Configure Feast Feature Store
feast_repo_config = RepoConfig(
    registry=os.path.join(FEAST_REPO_PATH, "registry.db"),
    project="fraud_detection_system",
    provider="local",
    offline_store="file",
)

def initialize_feature_store():
    """Initializes the Feast Feature Store with the defined schema."""
    store = FeatureStore(repo_path=FEAST_REPO_PATH)

    # Apply feature definitions
    store.apply([user_entity, transactions_feature_view])
    print("Feature store initialized and feature views applied.")

def ingest_data():
    """Loads processed batch data into Feast using Dask for efficiency."""
    store = FeatureStore(repo_path=FEAST_REPO_PATH)

    if os.path.exists(PROCESSED_DATA_PATH):
        df = dd.read_parquet(PROCESSED_DATA_PATH, engine="pyarrow")  # Load using Dask
        
        # Convert Dask dataframe to Pandas before ingesting (Feast requires Pandas)
        df = df.compute()

        # Ingest data into Feast
        store.ingest(transactions_feature_view, df)
        print("Features successfully ingested into Feast.")

    else:
        print(f"Error: Processed data file not found at {PROCESSED_DATA_PATH}")

if __name__ == "__main__":
    initialize_feature_store()
    ingest_data()
