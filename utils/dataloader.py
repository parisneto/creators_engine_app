# 2025-05-02: Added @st.cache_data to read_parquet_local for universal caching of DataFrames. All DataFrame loading now benefits from Streamlit's cache.
# 2025-06-08: Added deduplicate_playlist_data function and improved type conversions to prevent Arrow serialization warnings
# 2025-05-05: Included df_playlist_full_dedup in timestamp and ID column conversion loops for consistency and reliability
# 2025-05-06: Added deprecation warning for tbl_vw_playlist and aliased it to tbl_playlist_full_dedup for backward compatibility
# 2025-06-10: Fixed issue with empty dataframes after data source change
# Mapping of table keys to local Parquet paths
import pandas as pd
import streamlit as st
from utils.config import APPMODE
from typing import Union, Tuple
import logging

# Configure logger
logger = logging.getLogger(__name__)

def read_parquet_local(file_path: str) -> pd.DataFrame:
    """
    Reads a local Parquet file using Pandas and returns a DataFrame.
    This function is cached using Streamlit's @st.cache_data to avoid redundant disk reads.
    """
    return pd.read_parquet(file_path)
read_parquet_local = st.cache_data(read_parquet_local, ttl="1d")

def deduplicate_playlist_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate playlist data based on the most appropriate keys.
    Uses playlist_unique_item_id if available, otherwise uses playlist_id + video_id.
    Always uses processing_timestamp column for determining the latest record.

    Args:
        df: DataFrame with playlist data

    Returns:
        Deduplicated DataFrame
    """
    if df is None or df.empty:
        return df

    # Use processing_timestamp column specifically
    timestamp_col = "processing_timestamp"

    if timestamp_col in df.columns:
        # Convert timestamp to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
            df[timestamp_col] = pd.to_datetime(
                df[timestamp_col],
                errors="coerce"
            )

        # Deduplicate using the best strategy based on available columns
        if "playlist_unique_item_id" in df.columns:
            # Sort by timestamp descending and keep first occurrence of each key
            df = df.sort_values(timestamp_col, ascending=False)
            # Group by key and get indices of first (latest) records
            latest_idx = df.groupby(["playlist_unique_item_id"])[timestamp_col].idxmax()
            return df.loc[latest_idx]
        elif "playlist_id" in df.columns and "video_id" in df.columns:
            # Sort by timestamp descending and keep first occurrence of each key
            df = df.sort_values(timestamp_col, ascending=False)
            # Group by key and get indices of first (latest) records
            latest_idx = df.groupby(["playlist_id", "video_id"])[timestamp_col].idxmax()
            return df.loc[latest_idx]
        else:
            # Simple deduplication based on video_id only as fallback
            return df.drop_duplicates(["video_id"])
    else:
        # If processing_timestamp column not found, use simple deduplication
        if "playlist_unique_item_id" in df.columns:
            return df.drop_duplicates(["playlist_unique_item_id"])
        elif "playlist_id" in df.columns and "video_id" in df.columns:
            return df.drop_duplicates(["playlist_id", "video_id"])
        else:
            return df.drop_duplicates() if len(df) > 0 else df

# Load base data with cache_resource for container-level caching
@st.cache_resource(ttl='1d')
def load_base_data():
    """
    Load all base dataframes with standard preprocessing.
    Returns a dictionary of clean DataFrames.

    This is cached at the container level and shared across all user sessions.
    Do NOT modify the returned dataframes directly.
    """
    if APPMODE == "DEV":
        #local DevContainer path
        PARQUET_TABLES = {
            "tbl_nerdalytics": "data/tbl_nerdalytics.parquet",
            "tbl_slope_full": "data/tbl_slope_full.parquet",
            "tbl_playlist_full_dedup": "data/tbl_playlist_full_dedup.parquet",
            "tbl_analytics_filters": "data/tbl_analytics_filters.parquet",
            "tbl_channels": "data/tbl_channels.parquet"
        }
    else:
        #remote prod path
        PARQUET_TABLES = {
            "tbl_nerdalytics": "data/tbl_nerdalytics.parquet",
            "tbl_slope_full": "data/tbl_slope_full.parquet",
            "tbl_playlist_full_dedup": "data/tbl_playlist_full_dedup.parquet",
            "tbl_analytics_filters": "data/tbl_analytics_filters.parquet",
            "tbl_channels": "data/tbl_channels.parquet"
        }

    # Load all dataframes
    df_nerdalytics = read_parquet_local(PARQUET_TABLES["tbl_nerdalytics"])
    df_slope_full = read_parquet_local(PARQUET_TABLES["tbl_slope_full"])
    df_playlist_full_dedup = read_parquet_local(PARQUET_TABLES["tbl_playlist_full_dedup"])
    df_analytics_filters = read_parquet_local(PARQUET_TABLES["tbl_analytics_filters"])
    df_channels = read_parquet_local(PARQUET_TABLES["tbl_channels"])

    # Convert date columns
    if "slope_date" in df_slope_full.columns:
        df_slope_full["slope_date"] = pd.to_datetime(df_slope_full["slope_date"], errors="coerce")
    if "slope_timestamp" in df_slope_full.columns:
        df_slope_full["slope_timestamp"] = pd.to_datetime(df_slope_full["slope_timestamp"], errors="coerce")
    if "published_at" in df_slope_full.columns:
        df_slope_full["published_at"] = pd.to_datetime(df_slope_full["published_at"], errors="coerce")
    if "published_at" in df_nerdalytics.columns:
        df_nerdalytics["published_at"] = pd.to_datetime(df_nerdalytics["published_at"], errors="coerce")

    # Process all timestamp columns
    timestamp_columns = [
        "processing_timestamp",
        "video_processing_timestamp",
        "video_statistics_processing_timestamp",
        "videosnippet_processing_timestamp",
        "video_contentDetails_processing_timestamp",
        "playlist_item_published_at",
        "playlist_published_at",
        "video_added_at",
        "inserted_at"
    ]

    # Apply datetime conversion to all dataframes for any timestamp columns
    for df in [df_nerdalytics, df_slope_full, df_playlist_full_dedup, df_analytics_filters]:
        for col in timestamp_columns:
            if col in df.columns:
                # For columns that might cause Arrow serialization issues, convert to string
                if col in ["video_processing_timestamp", "video_statistics_processing_timestamp"]:
                    df[col] = df[col].astype(str)
                else:
                    df[col] = pd.to_datetime(df[col], errors="coerce")

    # Fix for Streamlit Arrow serialization errors
    if "video_processing_timestamp" in df_nerdalytics.columns:
        df_nerdalytics["video_processing_timestamp"] = df_nerdalytics["video_processing_timestamp"].astype(str)
    if "video_statistics_processing_timestamp" in df_nerdalytics.columns:
        df_nerdalytics["video_statistics_processing_timestamp"] = df_nerdalytics["video_statistics_processing_timestamp"].astype(str)

    # Ensure all ID columns are always treated as string to prevent type conversion issues
    id_columns = [
        "channel_id", "video_id", "playlist_id", "item_channel_id",
        "playlist_unique_item_id", "category_id"
    ]
    # FIX: (df_nerdalytics["age_in_days"])) TO INT
    # df_nerdalytics["age_in_days"] = df_nerdalytics["age_in_days"].astype(int)

    for df in [df_nerdalytics, df_slope_full, df_playlist_full_dedup, df_analytics_filters]:
        for col in id_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)

    # Deduplicate playlist data - uncommented to fix empty dataframe issues
    df_playlist_full_dedup = deduplicate_playlist_data(df_playlist_full_dedup)

    # Return a dictionary of all dataframes
    return {
        "tbl_nerdalytics": df_nerdalytics,
        "tbl_slope_full": df_slope_full,
        "tbl_playlist_full_dedup": df_playlist_full_dedup,
        "tbl_analytics_filters": df_analytics_filters,
        "tbl_channels": df_channels,
        "tbl_vw_playlist": df_playlist_full_dedup  # Deprecated alias
    }

@st.cache_data(ttl='15m')
def get_user_dataframe(df_name):
    """
    Get a user-specific copy of a base dataframe for filtering and manipulation.

    Args:
        df_name: Name of the dataframe to retrieve

    Returns:
        A copy of the requested dataframe that can be safely modified
    """
    base_dfs = load_base_data()
    if df_name not in base_dfs:
        logger.warning(f"Requested dataframe '{df_name}' not found in base data")
        return None

    # Return a copy that can be safely modified
    return base_dfs[df_name].copy()

def load_data(dfname: str) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]]:
    """
    Load data from parquet files.

    Args:
        dfname: Name of the dataset to load

    Returns:
        Either a single DataFrame or a tuple of DataFrames depending on the dfname
    """
    # Get the user-specific copy of the requested dataframe
    return get_user_dataframe(dfname)
