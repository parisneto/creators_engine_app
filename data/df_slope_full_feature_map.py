# placeholder for df_slope_full feature map

import os
import sys

import numpy as np
import pandas as pd

# ─────────────────────────────────────────────────
# ensure `/app` (one level up) is on the module search path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# ─────────────────────────────────────────────────


import streamlit as st

from utils.dataloader import load_data

df_slope_full = load_data("tbl_slope_full")

DATASET_FEATURE_MAP = {
    "df_slope_full": {
        "description": "DataFrame containing video data with calculated slopes for metrics like views, likes, and comments, along with future predictions. One row per video_id, representing the latest state and calculated trends.",
        "features": {
            "channel_title": {
                "type": "text",
                "subtype": "name",
                "example": "Example Channel",
                "use": "label, display",
                "description": "Title of the YouTube channel. (Dtype: object)",
            },
            "channel_id": {
                "type": "text",
                "subtype": "id",
                "example": "UCxxxxxx",
                "use": "identifier, join, filter",
                "description": "Unique ID of the YouTube channel. (Dtype: object)",
            },
            "video_id": {
                "type": "text",
                "subtype": "id",
                "example": "dQw4w9WgXcQ",
                "use": "identifier, join, filter, primary_key",
                "description": "Unique ID of the YouTube video. (Dtype: object)",
            },
            "published_at": {
                "type": "datetime",
                "subtype": "timestamp_ns",
                "example": "2023-01-15T10:00:00Z",
                "use": "time_series_analysis, filter, sorting",
                "description": "Date and time when the video was published. (Dtype: datetime64[ns])",
            },
            "age_in_days": {
                "type": "numerical",
                "subtype": "discrete",
                "example": 365,
                "use": "analysis, model_feature, x_axis",
                "description": "Age of the video in days since publication, calculated at the time of slope computation. (Dtype: Int32)",
            },
            "position": {
                "type": "text",
                "subtype": "generic",
                "example": "N/A",
                "use": "contextual_information",
                "description": "Positional or ranking data for the video; specific meaning may vary (e.g., playlist position, search rank). Clarification might be needed. (Dtype: object)",
            },
            "title": {
                "type": "text",
                "subtype": "title",
                "example": "My Awesome Video",
                "use": "display, search, nlp_feature",
                "description": "Title of the YouTube video. (Dtype: object)",
            },
            "description": {
                "type": "text",
                "subtype": "description_long",
                "example": "A long description of the video content...",
                "use": "display, search, nlp_feature",
                "description": "Description of the YouTube video. (Dtype: object)",
            },
            "category_id": {
                "type": "categorical",
                "subtype": "id_nominal",
                "example": "22",
                "use": "grouping, filter, analysis",
                "description": "ID of the YouTube category the video belongs to. Use get_category_name() to get the title. (Dtype: object)",
            },
            "thumbnail_url": {
                "type": "text",
                "subtype": "url_image",
                "example": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                "use": "display, preview",
                "description": "URL of the video thumbnail image. (Dtype: object)",
            },
            "default_audio_language": {
                "type": "categorical",
                "subtype": "language_code",
                "example": "en-US",
                "use": "filter, analysis",
                "description": 'Default audio language of the video (e.g., "en", "pt-BR"). (Dtype: object)',
            },
            "live_content": {
                "type": "categorical",
                "subtype": "nominal",
                "example": "none",
                "use": "filter, analysis",
                "description": 'Indicates if the video is/was a live broadcast (e.g., "live", "upcoming", "none"). (Dtype: object)',
            },
            "tags": {
                "type": "text",
                "subtype": "list_of_strings_pipe_separated",
                "example": "tag1|tag2|funny",
                "use": "nlp_feature, search, analysis",
                "description": "Pipe-separated list of tags associated with the video. (Dtype: object, Nullable)",
            },
            "duration_formatted_seconds": {
                "type": "numerical",
                "subtype": "discrete",
                "example": 180,
                "use": "analysis, model_feature",
                "description": "Duration of the video in seconds. (Dtype: Int32)",
            },
            "caption": {
                "type": "boolean",
                "subtype": "flag",
                "example": True,
                "use": "filter, analysis",
                "description": "Indicates if the video has captions (True/False). (Dtype: boolean)",
            },
            "ss_adult": {
                "type": "numerical",
                "subtype": "ordinal_score",
                "example": 3,
                "use": "filter, analysis, risk_assessment",
                "description": "Google Vision API SafeSearch score for adult content. Mapped to an integer from 0 (Unknown) to 5 (Very Likely) based on LIKELIHOOD_VALUES in config.py. (Dtype: float64, Nullable)",
            },
            "ss_spoof": {
                "type": "numerical",
                "subtype": "ordinal_score",
                "example": 1,
                "use": "filter, analysis, risk_assessment",
                "description": "Google Vision API SafeSearch score for spoof content. Mapped to an integer from 0 (Unknown) to 5 (Very Likely) based on LIKELIHOOD_VALUES in config.py. (Dtype: float64, Nullable)",
            },
            "ss_medical": {
                "type": "numerical",
                "subtype": "ordinal_score",
                "example": 0,
                "use": "filter, analysis, risk_assessment",
                "description": "Google Vision API SafeSearch score for medical content. Mapped to an integer from 0 (Unknown) to 5 (Very Likely) based on LIKELIHOOD_VALUES in config.py. (Dtype: float64, Nullable)",
            },
            "ss_violence": {
                "type": "numerical",
                "subtype": "ordinal_score",
                "example": 2,
                "use": "filter, analysis, risk_assessment",
                "description": "Google Vision API SafeSearch score for violence content. Mapped to an integer from 0 (Unknown) to 5 (Very Likely) based on LIKELIHOOD_VALUES in config.py. (Dtype: float64, Nullable)",
            },
            "ss_racy": {
                "type": "numerical",
                "subtype": "ordinal_score",
                "example": 4,
                "use": "filter, analysis, risk_assessment",
                "description": "Google Vision API SafeSearch score for racy content. Mapped to an integer from 0 (Unknown) to 5 (Very Likely) based on LIKELIHOOD_VALUES in config.py. (Dtype: float64, Nullable)",
            },
            "video_type": {
                "type": "categorical",
                "subtype": "nominal",
                "example": "Normal",
                "use": "filter, grouping, analysis",
                "description": 'Type of the video (e.g., "Normal", "Short"). (Dtype: object)',
            },
            "slope_timestamp": {
                "type": "datetime",
                "subtype": "timestamp_us",
                "example": "2024-05-20T12:00:00.000000Z",
                "use": "reference_time, analysis",
                "description": "Timestamp (microsecond precision) when the slope calculations were performed. (Dtype: datetime64[us])",
            },
            "slope_date": {
                "type": "datetime",
                "subtype": "date",
                "example": "2024-05-20",
                "use": "reference_date, grouping, analysis",
                "description": "Date part of slope_timestamp, when slope calculations were performed. (Dtype: datetime64[ns])",
            },
            "view_count_slope": {
                "type": "numerical",
                "subtype": "continuous_rate",
                "example": 100.5,
                "use": "trend_analysis, model_feature, y_axis",
                "description": "Calculated slope (rate of change per day) for view_count based on historical data using custom linear regression. (Dtype: int64, treated as continuous)",
            },
            "like_count_slope": {
                "type": "numerical",
                "subtype": "continuous_rate",
                "example": 10.2,
                "use": "trend_analysis, model_feature, y_axis",
                "description": "Calculated slope (rate of change per day) for like_count based on historical data using custom linear regression. (Dtype: int64, treated as continuous)",
            },
            "comment_count_slope": {
                "type": "numerical",
                "subtype": "continuous_rate",
                "example": 1.5,
                "use": "trend_analysis, model_feature, y_axis",
                "description": "Calculated slope (rate of change per day) for comment_count based on historical data using custom linear regression. (Dtype: int64, treated as continuous)",
            },
            "linear_view_count_speed": {
                "type": "numerical",
                "subtype": "continuous_rate",
                "example": 90.0,
                "use": "comparison, analysis, benchmark",
                "description": "Simple linear speed for view_count (e.g., total views / age_in_days at slope calculation time). (Dtype: float64)",
            },
            "slope_view_count_speed": {
                "type": "numerical",
                "subtype": "continuous_rate",
                "example": 100.5,
                "use": "trend_analysis, model_feature, comparison",
                "description": "Slope of view_count (views per day), derived from custom regression. Identical to view_count_slope. (Dtype: float64)",
            },
            "linear_like_count_speed": {
                "type": "numerical",
                "subtype": "continuous_rate",
                "example": 8.0,
                "use": "comparison, analysis, benchmark",
                "description": "Simple linear speed for like_count. (Dtype: float64, Nullable)",
            },
            "slope_like_count_speed": {
                "type": "numerical",
                "subtype": "continuous_rate",
                "example": 10.2,
                "use": "trend_analysis, model_feature, comparison",
                "description": "Slope of like_count (likes per day), derived from custom regression. Identical to like_count_slope. (Dtype: float64, Nullable)",
            },
            "linear_comment_count_speed": {
                "type": "numerical",
                "subtype": "continuous_rate",
                "example": 1.0,
                "use": "comparison, analysis, benchmark",
                "description": "Simple linear speed for comment_count. (Dtype: float64)",
            },
            "slope_comment_count_speed": {
                "type": "numerical",
                "subtype": "continuous_rate",
                "example": 1.5,
                "use": "trend_analysis, model_feature, comparison",
                "description": "Slope of comment_count (comments per day), derived from custom regression. Identical to comment_count_slope. (Dtype: float64)",
            },
            "predicted_view_count_7d": {
                "type": "numerical",
                "subtype": "continuous_prediction",
                "example": 700.0,
                "use": "forecasting, analysis, kpi",
                "description": "Predicted total view_count in the next 7 days based on the current slope. (Dtype: float64)",
            },
            "predicted_view_count_30d": {
                "type": "numerical",
                "subtype": "continuous_prediction",
                "example": 3000.0,
                "use": "forecasting, analysis, kpi",
                "description": "Predicted total view_count in the next 30 days based on the current slope. (Dtype: float64)",
            },
            "predicted_view_count_365d": {
                "type": "numerical",
                "subtype": "continuous_prediction",
                "example": 36500.0,
                "use": "forecasting, analysis, kpi",
                "description": "Predicted total view_count in the next 365 days based on the current slope. (Dtype: float64)",
            },
            "growth_view_count_7d_percent": {
                "type": "numerical",
                "subtype": "continuous_percentage",
                "example": 5.5,
                "use": "growth_analysis, kpi, forecasting",
                "description": "Predicted percentage growth in view_count over the next 7 days. (Dtype: float64)",
            },
            "growth_view_count_30d_percent": {
                "type": "numerical",
                "subtype": "continuous_percentage",
                "example": 25.0,
                "use": "growth_analysis, kpi, forecasting",
                "description": "Predicted percentage growth in view_count over the next 30 days. (Dtype: float64)",
            },
            "growth_view_count_365d_percent": {
                "type": "numerical",
                "subtype": "continuous_percentage",
                "example": 300.0,
                "use": "growth_analysis, kpi, forecasting",
                "description": "Predicted percentage growth in view_count over the next 365 days. (Dtype: float64)",
            },
        },
    }
}


def diagnose_nulls(df, apply_to_global=False):
    """Diagnose and treat null values in a DataFrame.

    Args:
        df: The DataFrame to diagnose and treat
        apply_to_global: If True, apply changes to the global df_slope_full variable

    Returns:
        The treated DataFrame
    """
    global df_slope_full

    # BEFORE: Diagnose nulls before treatment
    st.subheader("BEFORE Treatment: Missing Values Diagnosis")
    null_counts_before = df.isnull().sum()
    null_percentages_before = (null_counts_before / len(df)) * 100
    null_info_before = pd.DataFrame(
        {"Null Count": null_counts_before, "Null Percentage": null_percentages_before}
    )
    # Filter to only show columns with null values
    null_info_before = null_info_before[null_info_before["Null Count"] > 0]
    if not null_info_before.empty:
        st.write("Columns with missing values (before treatment):")
        st.code(null_info_before)
    else:
        st.write("No missing values  found in the dataset before treatment.")

    # Treatment: Replace various null representations with np.nan for columns with missing values
    null_representations = [
        "null",
        "N/A",
        "None",
        "na",
        "n/a",
        "none",
        "NULL",
        "NA",
        "",
    ]

    # Only process columns that have missing values
    columns_with_nulls = null_info_before.index.tolist()

    # Determine which DataFrame to modify
    target_df = df_slope_full if apply_to_global else df

    if columns_with_nulls:
        st.subheader("Treatment Applied")
        for col in columns_with_nulls:
            if col in target_df.columns:
                # Check if column is of object type (string) before replacing
                if target_df[col].dtype == "object":
                    # Count before replacement
                    before_count = target_df[col].isnull().sum()

                    # Replace various null representations with np.nan
                    target_df[col] = target_df[col].replace(
                        null_representations, np.nan
                    )

                    # Count after replacement
                    after_count = target_df[col].isnull().sum()
                    new_nulls = after_count - before_count

                    if new_nulls > 0:
                        st.write(
                            f"Column '{col}': Converted {new_nulls} string null representations to NaN"
                        )

    # AFTER: Diagnose nulls after treatment
    st.subheader("AFTER Treatment: Missing Values Diagnosis")
    null_counts_after = target_df.isnull().sum()
    null_percentages_after = (null_counts_after / len(target_df)) * 100
    null_info_after = pd.DataFrame(
        {"Null Count": null_counts_after, "Null Percentage": null_percentages_after}
    )
    # Filter to only show columns with null values
    null_info_after = null_info_after[null_info_after["Null Count"] > 0]
    if not null_info_after.empty:
        st.write("Columns with missing values (after treatment):")
        st.code(null_info_after)
    else:
        st.write("No missing values found in the dataset after treatment.")

    return target_df


def render():
    import os

    st.header("df_slope_full_feature_map")

    st.write("Running from", os.path.abspath(os.getcwd()))

    # st.write("df_slope_full.shape", df_slope_full.shape)
    # st.write("df_slope_full[[published_at, slope_date, slope_timestamp]].sample(5)")
    # st.code(df_slope_full[["published_at", "slope_date", "slope_timestamp"]].sample(5))
    # st.write("df_slope_full.columns.tolist()", df_slope_full.columns.tolist())
    # st.write("df_slope_full.describe()", df_slope_full.describe())

    # Null treatment is now handled in the dataloader.py get_user_dataframe function
    # and is cached for 15 minutes
    
    # We can still diagnose nulls to show the current state without modifying the DataFrame
    st.subheader("Current Null Values Diagnosis")
    null_counts = df_slope_full.isnull().sum()
    null_percentages = (null_counts / len(df_slope_full)) * 100
    null_info = pd.DataFrame({"Null Count": null_counts, "Null Percentage": null_percentages})
    null_info = null_info[null_info["Null Count"] > 0]
    if not null_info.empty:
        st.write("Columns with missing values:")
        st.code(null_info)
    else:
        st.write("No missing values found in the dataset.")

    st.divider()
    st.subheader("Feature Map output examples")
    st.code(df_slope_full[df_slope_full["tags"].notnull()]["tags"].sample(11))
    st.divider()

    # st.selectbox("Select a column", df_slope_full.columns.tolist())
    st.selectbox("Select a column", (1, 2, 3))

    if False:
        # Show verification of the treatment
        st.subheader("Verification After Treatment")
        if "tags" in df_slope_full.columns:
            st.write(
                f"Number of 'null' string values in tags column: {df_slope_full[df_slope_full['tags'] == 'null'].shape[0]}"
            )
            if len(df_slope_full[df_slope_full["tags"].notnull()]) > 0:
                st.write("Sample of non-null tag values:")
                st.code(
                    df_slope_full[df_slope_full["tags"].notnull()]["tags"].sample(
                        min(
                            5,
                            len(df_slope_full[df_slope_full["tags"].notnull()]),
                        )
                    )
                )

        # The global df_slope_full has been modified in-place
        # No need to return anything in a Streamlit app


# =================================================================
# EXECUÇÃO PRINCIPAL
# =================================================================
if __name__ == "__main__":
    render()
