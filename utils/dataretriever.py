# HISTORY:
# 2025-04-28: Created script to copy two parquet files from GCS to /app/data2 using ADC and google-cloud-storage.
# 2025-04-28: Moved dataretriever to config directory and centralized GCP/GCS parameters in config.py.
# 2025-04-28: Moved dataretriever to utils and updated to use centralized GCP/GCS config from utils/config.py.
# 2025-04-28: Fixed import to use local config import for script execution compatibility.
# 2025-04-28: Added support for bucket override to match original prompt and improved error reporting for missing files or wrong bucket.
# 2025-04-29: Refactored to expose main() for import/run flexibility, supporting Streamlit and CLI use.
# 2025-04-29: Made config import robust for local, production, and terminal use (tries utils.config, then env, then fallback).
# 2025-05-07: Updated playlist data references to use tbl_playlist_full_dedup instead of tbl_vw_playlistfull

"""
Script to download specific parquet files from Google Cloud Storage (GCS) to a local directory using Application Default Credentials (ADC).
Requirements:
- google-cloud-storage
- ADC must be configured (e.g., running on GCP or with GOOGLE_APPLICATION_CREDENTIALS set)

Steps:
1. Set up GCS client using ADC
2. Copy the following files to /app/data:
   - gs://yta_mdm_production/data/duckdb_mirror/tbl_nerdalytics.parquet
   - gs://yta_mdm_production/data/duckdb_mirror/tbl_slope_full.parquet
   - gs://yta_mdm_production/data/duckdb_mirror/tbl_playlist_full_dedup.parquet
"""

import os
from google.cloud import storage

# Try to import project ID from utils.config, then config, then environment
try:
    from utils.config import GCP_PROJECT_ID
except ImportError:
    try:
        from config import GCP_PROJECT_ID
    except ImportError:
        GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "fleet-gamma-448616-m1")

# Allow override of bucket for specific retrieval tasks
import sys

try:
    from utils.config import GCS_BUCKET
except ImportError:
    try:
        from config import GCS_BUCKET
    except ImportError:
        GCS_BUCKET = os.environ.get("GCS_BUCKET", "yta_mdm_production")

# Manual override for this prompt
# PROMPT_BUCKET = "yta_mdm_production"
PROMPT_BUCKET = "creators_engine_production"

PROMPT_PARQUET_FILES = [
    "data/duckdb_mirror/tbl_nerdalytics.parquet",
    "data/duckdb_mirror/tbl_slope_full.parquet",
    "data/duckdb_mirror/tbl_analytics_filters.parquet",
    "data/duckdb_mirror/tbl_playlist_full_dedup.parquet",
    "data/duckdb_mirror/tbl_channels.parquet"
]
    # "data/duckdb_mirror/tbl_vw_playlistfull.parquet",
# "data/duckdb_mirror/tbl_playlists.parquet",
# data/duckdb_mirror/tbl_analytics_filters

LOCAL_DATA_DIR = os.environ.get("LOCAL_DATA_DIR", "/app/data")

def download_files_from_gcs(bucket_name, file_paths, local_dir):
    """
    Downloads files from a GCS bucket to a local directory using ADC.
    Prints errors if files are missing or bucket is incorrect.
    """
    # Step 1: Ensure local directory exists
    os.makedirs(local_dir, exist_ok=True)

    # Step 2: Create GCS client (uses ADC by default)
    client = storage.Client(project=GCP_PROJECT_ID)
    bucket = client.bucket(bucket_name)

    # Step 3: Download each file
    for file_path in file_paths:
        blob = bucket.blob(file_path)
        local_path = os.path.join(local_dir, os.path.basename(file_path))
        print(f"Downloading gs://{bucket_name}/{file_path} to {local_path} ...")
        try:
            blob.download_to_filename(local_path)
            print(f"Downloaded {local_path}")
        except Exception as e:
            print(f"ERROR: Could not download gs://{bucket_name}/{file_path}: {e}")

def main():
    """
    Main entry point to download files from GCS to local directory.
    Can be called from CLI or imported as a function.
    """
    download_files_from_gcs(PROMPT_BUCKET, PROMPT_PARQUET_FILES, LOCAL_DATA_DIR)

if __name__ == "__main__":
    main()
