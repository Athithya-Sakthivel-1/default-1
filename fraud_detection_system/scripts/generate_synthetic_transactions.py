import duckdb
import faker
import random
import uuid
from datetime import datetime, timedelta

# Initialize Faker
fake = faker.Faker()

# Database file
DB_PATH = "data/database/fraud_data.duckdb"

# Generate synthetic transaction data
def generate_synthetic_transactions(num_records=10000, fraud_ratio=0.02):
    transactions = []
    
    for _ in range(num_records):
        transaction_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        merchant_id = str(uuid.uuid4())
        device_id = str(uuid.uuid4())
        ip_address = fake.ipv4()
        location = fake.city()
        timestamp = fake.date_time_between(start_date="-1y", end_date="now")
        transaction_amount = round(random.uniform(1, 10000), 2)
        transaction_type = random.choice(["purchase", "transfer", "withdrawal"])
        
        # Simulate fraud based on fraud ratio
        is_fraud = 1 if random.random() < fraud_ratio else 0

        transactions.append((
            transaction_id, user_id, merchant_id, device_id, ip_address,
            location, timestamp, transaction_amount, transaction_type, is_fraud
        ))

    return transactions

# Store data in DuckDB
def store_in_duckdb(data):
    conn = duckdb.connect(DB_PATH)
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id VARCHAR PRIMARY KEY,
        user_id VARCHAR,
        merchant_id VARCHAR,
        device_id VARCHAR,
        ip_address VARCHAR,
        location VARCHAR,
        timestamp TIMESTAMP,
        transaction_amount FLOAT,
        transaction_type VARCHAR,
        is_fraud BOOLEAN
    )
    """)

    conn.executemany("""
    INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.close()
    print(f"✅ {len(data)} synthetic transactions stored in DuckDB.")

if __name__ == "__main__":
    data = generate_synthetic_transactions(num_records=50000, fraud_ratio=0.05)
    store_in_duckdb(data)
