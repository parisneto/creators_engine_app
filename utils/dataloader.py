# 2025-05-02: Added @st.cache_data to read_parquet_local for universal caching of DataFrames. All DataFrame loading now benefits from Streamlit's cache.
# 2025-06-08: Added deduplicate_playlist_data function and improved type conversions to prevent Arrow serialization warnings
# 2025-05-05: Included df_playlist_full_dedup in timestamp and ID column conversion loops for consistency and reliability
# 2025-05-06: Added deprecation warning for tbl_vw_playlist and aliased it to tbl_playlist_full_dedup for backward compatibility
# 2025-06-10: Fixed issue with empty dataframes after data source change
# Mapping of table keys to local Parquet paths
import logging
from typing import Tuple, Union

import pandas as pd
import streamlit as st

from utils.config import APPMODE

# Configure logger
logger = logging.getLogger(__name__)


def read_parquet_local(file_path: str) -> pd.DataFrame:
    """
    Reads a local Parquet file using Pandas and returns a DataFrame.
    This function is cached using Streamlit's @st.cache_data to avoid redundant disk reads.
    """
    return pd.read_parquet(file_path)


read_parquet_local = st.cache_data(read_parquet_local, ttl="1d")


# Load base data with cache_resource for container-level caching
@st.cache_resource(ttl="1d")
def load_base_data():
    """
    Load all base dataframes with standard preprocessing.
    Returns a dictionary of clean DataFrames.

    This is cached at the container level and shared across all user sessions.
    Do NOT modify the returned dataframes directly.
    """
    if APPMODE == "DEV":
        # local DevContainer path
        PARQUET_TABLES = {
            "tbl_nerdalytics": "/app/data/tbl_nerdalytics.parquet",
            "tbl_slope_full": "/app/data/tbl_slope_full.parquet",
            "tbl_playlist_full_dedup": "/app/data/tbl_playlist_full_dedup.parquet",
            "tbl_analytics_filters": "/app/data/tbl_analytics_filters.parquet",
            "tbl_channels": "/app/data/tbl_channels_full.parquet",
        }
    else:
        # remote prod path
        PARQUET_TABLES = {
            "tbl_nerdalytics": "data/tbl_nerdalytics.parquet",
            "tbl_slope_full": "data/tbl_slope_full.parquet",
            "tbl_playlist_full_dedup": "data/tbl_playlist_full_dedup.parquet",
            "tbl_analytics_filters": "data/tbl_analytics_filters.parquet",
            "tbl_channels": "data/tbl_channels_full.parquet",
        }

    # ------------------------------
    # SECTION 1: Load all dataframes
    # ------------------------------
    df_nerdalytics = read_parquet_local(PARQUET_TABLES["tbl_nerdalytics"])
    df_slope_full = read_parquet_local(PARQUET_TABLES["tbl_slope_full"])
    df_playlist_full_dedup = read_parquet_local(
        PARQUET_TABLES["tbl_playlist_full_dedup"]
    )
    df_analytics_filters = read_parquet_local(PARQUET_TABLES["tbl_analytics_filters"])
    df_channels = read_parquet_local(PARQUET_TABLES["tbl_channels"])

    # ---------------------------------------------------
    # SECTION 2: Per-DF Date/Datetime Conversion (Primary)
    # ---------------------------------------------------
    # df_slope_full: Convert date columns
    if "slope_date" in df_slope_full.columns:
        df_slope_full["slope_date"] = pd.to_datetime(
            df_slope_full["slope_date"], errors="coerce"
        )
    if "slope_timestamp" in df_slope_full.columns:
        df_slope_full["slope_timestamp"] = pd.to_datetime(
            df_slope_full["slope_timestamp"], errors="coerce"
        )
    if "published_at" in df_slope_full.columns:
        df_slope_full["published_at"] = pd.to_datetime(
            df_slope_full["published_at"], errors="coerce"
        )

    # df_nerdalytics: Convert date columns
    if "published_at" in df_nerdalytics.columns:
        df_nerdalytics["published_at"] = pd.to_datetime(
            df_nerdalytics["published_at"], errors="coerce"
        )

    # df_playlist_full_dedup: Convert date columns
    if "playlist_item_published_at" in df_playlist_full_dedup.columns:
        df_playlist_full_dedup["playlist_item_published_at"] = pd.to_datetime(
            df_playlist_full_dedup["playlist_item_published_at"], errors="coerce"
        )
    if "playlist_published_at" in df_playlist_full_dedup.columns:
        df_playlist_full_dedup["playlist_published_at"] = pd.to_datetime(
            df_playlist_full_dedup["playlist_published_at"], errors="coerce"
        )
    if "video_added_at" in df_playlist_full_dedup.columns:
        df_playlist_full_dedup["video_added_at"] = pd.to_datetime(
            df_playlist_full_dedup["video_added_at"], errors="coerce"
        )

    # ------------------------------------------------------
    # SECTION 3: Universal Timestamp Conversion (All DFs)
    # ------------------------------------------------------
    timestamp_columns = [
        "processing_timestamp",
        "video_processing_timestamp",
        "video_statistics_processing_timestamp",
        "videosnippet_processing_timestamp",
        "video_contentDetails_processing_timestamp",
        "playlist_item_published_at",
        "playlist_published_at",
        "video_added_at",
        "inserted_at",
    ]
    for df in [
        df_nerdalytics,
        df_slope_full,
        df_playlist_full_dedup,
        df_analytics_filters,
    ]:
        for col in timestamp_columns:
            if col in df.columns:
                # For columns that might cause Arrow serialization issues, convert to string
                if col in [
                    "video_processing_timestamp",
                    "video_statistics_processing_timestamp",
                ]:
                    df[col] = df[col].astype(str)
                else:
                    df[col] = pd.to_datetime(df[col], errors="coerce")

    # ------------------------------------------------------
    # SECTION 4: Ensure all relevant columns are strings (Arrow serialization & ID normalization)
    # ------------------------------------------------------
    # Columns that need to be string for Arrow/Streamlit serialization issues
    arrow_string_columns = [
        "video_processing_timestamp",
        "video_statistics_processing_timestamp",
    ]
    # Columns that should always be strings for ID normalization and consistency
    id_columns = [
        "channel_id",
        "video_id",
        "playlist_id",
        "item_channel_id",
        "playlist_unique_item_id",
        "category_id",
    ]
    # Combine all columns that need to be string
    all_string_columns = set(arrow_string_columns + id_columns)
    # Apply .astype(str) to all relevant columns in all DFs
    for df in [
        df_nerdalytics,
        df_slope_full,
        df_playlist_full_dedup,
        df_analytics_filters,
    ]:
        for col in all_string_columns:
            if col in df.columns:
                # Arrow serialization fix or ID normalization
                df[col] = df[col].astype(str)

    # ------------------------------------------------------
    # SECTION 6: Data Enrichment (Join Analytics Columns)
    # ------------------------------------------------------
    # Enrich df_playlist_full_dedup with selected analytics columns from df_nerdalytics by video_id
    # Collect all ss_* columns from df_nerdalytics
    ss_cols = [col for col in df_nerdalytics.columns if col.startswith("ss_")]
    cols_to_add = [
        "view_count",
        "like_count",
        "comment_count",
        "video_type",
        "duration_formatted_seconds",
        "category_id",
        "tags",
        "default_audio_language",
    ] + ss_cols
    # Only add columns not already present in df_playlist_full_dedup
    cols_missing = [
        col for col in cols_to_add if col not in df_playlist_full_dedup.columns
    ]
    merge_cols = ["video_id"] + [
        col for col in cols_to_add if col in df_nerdalytics.columns
    ]
    if (
        "video_id" in df_playlist_full_dedup.columns
        and "video_id" in df_nerdalytics.columns
    ):
        df_playlist_full_dedup = df_playlist_full_dedup.merge(
            df_nerdalytics[merge_cols],
            on="video_id",
            how="left",
            suffixes=("", "_analytics"),
        )
    # else: if video_id missing, skip enrichment (df_playlist_full_dedup remains unchanged)

    # Return a dictionary of all dataframes
    return {
        "tbl_nerdalytics": df_nerdalytics,
        "tbl_slope_full": df_slope_full,
        "tbl_playlist_full_dedup": df_playlist_full_dedup,
        "tbl_analytics_filters": df_analytics_filters,
        "tbl_channels": df_channels,
        # "tbl_vw_playlist": df_playlist_full_dedup  # Deprecated alias
    }


# Import the treat_nulls function
from utils.treat_nulls import treat_nulls


@st.cache_data(ttl="15m")
def get_user_dataframe(df_name):
    """
    Get a user-specific copy of a base dataframe for filtering and manipulation.
    Also treats null values in string columns by converting string representations
    like "null", "N/A", etc. to actual np.nan values.

    Args:
        df_name: Name of the dataframe to retrieve

    Returns:
        A copy of the requested dataframe that can be safely modified with nulls treated
    """
    base_dfs = load_base_data()
    if df_name not in base_dfs:
        logger.warning(f"Requested dataframe '{df_name}' not found in base data")
        return None

    # Get a copy that can be safely modified
    df_copy = base_dfs[df_name].copy()

    # Treat null values in string columns
    df_copy = treat_nulls(df_copy)

    return df_copy


def load_data(
    dfname: str,
) -> Union[
    pd.DataFrame,
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame],
]:
    """
    Load data from parquet files.

    Args:
        dfname: Name of the dataset to load

    Returns:
        Either a single DataFrame or a tuple of DataFrames depending on the dfname
    """
    # Get the user-specific copy of the requested dataframe
    return get_user_dataframe(dfname)
