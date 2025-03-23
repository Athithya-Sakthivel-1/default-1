import os
import duckdb
import pandas as pd
from faker import Faker
from src.utils.config_loader import CONFIG

# Initialize Faker instance
fake = Faker()

# Get file paths from settings.yaml
RAW_DATA_PATH = CONFIG["data"]["raw_data_path"]
DUCKDB_PATH = CONFIG["data"]["duckdb_path"]

# Ensure directories exist
os.makedirs(RAW_DATA_PATH, exist_ok=True)
os.makedirs(os.path.dirname(DUCKDB_PATH), exist_ok=True)

def generate_synthetic_data(num_records=10000):
    """Generates synthetic transaction data."""
    data = []
    for _ in range(num_records):
        data.append({
            "transaction_id": fake.uuid4(),
            "timestamp": fake.date_time_this_decade(),
            "user_id": fake.uuid4(),
            "amount": round(fake.random_number(digits=5), 2),
            "transaction_type": fake.random_element(elements=("credit", "debit")),
            "merchant": fake.company(),
            "location": fake.city(),
            "device": fake.random_element(elements=("mobile", "desktop", "tablet")),
            "ip_address": fake.ipv4(),
        })
    
    return pd.DataFrame(data)

def store_in_duckdb(df):
    """Stores synthetic transactions in DuckDB."""
    conn = duckdb.connect(DUCKDB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id STRING,
            timestamp TIMESTAMP,
            user_id STRING,
            amount FLOAT,
            transaction_type STRING,
            merchant STRING,
            location STRING,
            device STRING,
            ip_address STRING
        )
    """)
    conn.register("df_temp", df)
    conn.execute("INSERT INTO transactions SELECT * FROM df_temp")
    conn.close()

if __name__ == "__main__":
    print("Generating synthetic transactions...")
    df = generate_synthetic_data(num_records=10000)
    
    # Save locally as CSV (raw data)
    csv_path = os.path.join(RAW_DATA_PATH, "transactions.csv")
    df.to_csv(csv_path, index=False)
    
    print(f"Synthetic data saved at: {csv_path}")
    
    # Store in DuckDB
    store_in_duckdb(df)
    print(f"Data successfully stored in DuckDB at: {DUCKDB_PATH}")
