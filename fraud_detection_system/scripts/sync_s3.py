import os
import sys
import subprocess
import argparse
from pathlib import Path

# Move up one directory to include `src` in Python path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.append(str(PROJECT_ROOT))  # Add project root to Python path

# Import configuration loader
from src.utils.config_loader import config

# Load AWS settings from `settings.yaml`
AWS_S3_BUCKET = config.get("data.s3_bucket", "robust-mlops-1")
AWS_S3_PREFIX = config.get("data.s3_prefix", "fraud_detection_system/data")
AWS_REGION = config.get("data.aws_region", "us-east-1")

# Define local data path (entire `data/` directory)
LOCAL_DATA_DIR = PROJECT_ROOT / "data"

def check_aws_cli():
    """Check if AWS CLI is installed and accessible."""
    try:
        subprocess.run(["aws", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        print("❌ AWS CLI is not installed. Install it and try again.")
        return False
    except subprocess.CalledProcessError:
        print("❌ AWS CLI encountered an issue. Check your AWS setup.")
        return False

def sync_to_s3():
    """Sync entire `data/` directory to S3 (Full Upload)."""
    if not check_aws_cli():
        return
    
    print(f"📤 Uploading {LOCAL_DATA_DIR} → s3://{AWS_S3_BUCKET}/{AWS_S3_PREFIX}")
    try:
        subprocess.run(
            [
                "aws", "s3", "sync",
                str(LOCAL_DATA_DIR), f"s3://{AWS_S3_BUCKET}/{AWS_S3_PREFIX}",
                "--region", AWS_REGION,
                "--delete", "--exact-timestamps"
            ],
            check=True,
        )
        print("✅ Successfully uploaded `data/` to S3.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error syncing to S3: {e}")

def sync_from_s3():
    """Sync entire `data/` directory from S3 (Full Download)."""
    if not check_aws_cli():
        return
    
    print(f"📥 Downloading s3://{AWS_S3_BUCKET}/{AWS_S3_PREFIX} → {LOCAL_DATA_DIR}")
    try:
        subprocess.run(
            [
                "aws", "s3", "sync",
                f"s3://{AWS_S3_BUCKET}/{AWS_S3_PREFIX}", str(LOCAL_DATA_DIR),
                "--region", AWS_REGION,
                "--delete", "--exact-timestamps"
            ],
            check=True,
        )
        print("✅ Successfully downloaded `data/` from S3.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error syncing from S3: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync full `data/` directory with AWS S3")
    parser.add_argument("--to-s3", action="store_true", help="Upload entire local `data/` directory to S3")
    parser.add_argument("--from-s3", action="store_true", help="Download entire `data/` directory from S3")

    args = parser.parse_args()

    if args.to_s3:
        sync_to_s3()
    elif args.from_s3:
        sync_from_s3()
    else:
        parser.print_help()
