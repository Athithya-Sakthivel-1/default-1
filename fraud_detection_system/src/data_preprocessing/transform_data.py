import os
import duckdb
import pandas as pd
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.utils.config_loader import CONFIG

# Load paths from settings.yaml
DUCKDB_PATH = CONFIG["data"]["duckdb_path"]
TRANSACTIONS_CSV_PATH = os.path.join(CONFIG["data"]["raw_data_path"], "transactions.csv")
PROCESSED_DATA_PATH = os.path.join(CONFIG["data"]["processed_data_path"], "processed_batch_data.parquet")

# Ensure the processed data directory exists
os.makedirs(CONFIG["data"]["processed_data_path"], exist_ok=True)

def load_duckdb_data():
    """Loads transaction data from DuckDB."""
    conn = duckdb.connect(DUCKDB_PATH)
    query = "SELECT * FROM transactions"
    df_duckdb = conn.execute(query).fetch_df()
    conn.close()
    return df_duckdb

def load_csv_data():
    """Loads transaction data from CSV."""
    if os.path.exists(TRANSACTIONS_CSV_PATH):
        return pd.read_csv(TRANSACTIONS_CSV_PATH, parse_dates=["timestamp"])
    else:
        print(f"Warning: {TRANSACTIONS_CSV_PATH} not found. Returning empty DataFrame.")
        return pd.DataFrame()

def preprocess_data(df):
    """Cleans and standardizes transaction data."""
    # Ensure correct data types
    df["transaction_id"] = df["transaction_id"].astype(str)
    df["user_id"] = df["user_id"].astype(str)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["transaction_type"] = df["transaction_type"].astype(str)
    df["merchant"] = df["merchant"].astype(str)
    df["location"] = df["location"].astype(str)
    df["device"] = df["device"].astype(str)
    df["ip_address"] = df["ip_address"].astype(str)
    
    # Handle missing values
    df = df.dropna()

    # Remove duplicate transactions
    df = df.drop_duplicates(subset=["transaction_id"])

    return df

if __name__ == "__main__":
    print("Loading transaction data...")

    # Load data from both sources
    df_duckdb = load_duckdb_data()
    df_csv = load_csv_data()

    # Ensure both datasets have the same schema
    common_columns = list(set(df_duckdb.columns) & set(df_csv.columns))
    df_duckdb = df_duckdb[common_columns]
    df_csv = df_csv[common_columns]

    # Merge both datasets
    df_combined = pd.concat([df_duckdb, df_csv], ignore_index=True)

    # Preprocess data
    df_cleaned = preprocess_data(df_combined)

    # Store cleaned data
    df_cleaned.to_parquet(PROCESSED_DATA_PATH, index=False)
    print(f"Cleaned data saved to: {PROCESSED_DATA_PATH}")
