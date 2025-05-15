import streamlit as st
import pandas as pd
import plotly.express as px
from utils.dataloader import get_user_dataframe

def template_slope_block(df_nerdalytics, filter_manager):
    """
    Template block for slope dataframe with visualizations.
    This block uses tbl_slope_full as its main dataframe.

    Args:
        df_nerdalytics: Filtered nerdalytics dataframe (not used directly)
        filter_manager: Filter manager instance
    """
    st.subheader("Slope Data Analysis")

    # Get slope dataframe - this is the main dataframe for this block
    df_slope = get_user_dataframe("tbl_slope_full")
    st.divider()
    st.write("df_slope shape:", df_slope.shape)

    if df_slope is None:
        st.error("Could not load slope dataframe")
        return

    # Apply filters if applicable
    filters = filter_manager.get_filter_state()
    st.divider()
    st.write("filters:", filters)

    # If channel filter is active and channel_id exists in both dataframes,
    # we can use it to filter the slope dataframe
    filtered_df_slope = df_slope
    st.divider()
    st.write("filtered_df_slope shape:", filtered_df_slope.shape)
    if filters["channel"] and "channel_title" in df_nerdalytics.columns and "channel_id" in df_nerdalytics.columns and "channel_id" in df_slope.columns:
        # Get channel IDs from nerdalytics
        channel_ids = df_nerdalytics[df_nerdalytics["channel_title"].isin(filters["channel"])]["channel_id"].unique()
        # Filter slope dataframe
        filtered_df_slope = df_slope[df_slope["channel_id"].isin(channel_ids)]

    # Show dataframe info
    st.write(f"filtered_df_slope dataframe shape: {filtered_df_slope.shape}")
    st.code(f"filtered_df_slope columns: {filtered_df_slope.columns}")

    # Show sample data
    with st.expander("Sample Data"):
        st.dataframe(filtered_df_slope.head(10))

    # Basic metrics and visualizations
    if "slope_view_count_speed" in filtered_df_slope.columns and "slope_date" in filtered_df_slope.columns:
        # Metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Slope", f"{filtered_df_slope['slope_view_count_speed'].mean():.4f}")
        with col2:
            st.metric("Median Slope", f"{filtered_df_slope['slope_view_count_speed'].median():.4f}")

        # Time series plot
        if len(filtered_df_slope) > 0:
            # Ensure slope_date is datetime
            filtered_df_slope["slope_date"] = pd.to_datetime(filtered_df_slope["slope_date"], errors="coerce")

            # Group by date and calculate average slope
            slope_by_date = filtered_df_slope.groupby(filtered_df_slope["slope_date"].dt.date)["slope_view_count_speed"].mean().reset_index()

            fig = px.line(
                slope_by_date,
                x="slope_date",
                y="slope_view_count_speed",
                title="Average Slope Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Histogram of slopes
            fig2 = px.histogram(
                filtered_df_slope,
                x="slope_view_count_speed",
                title="Distribution of Slopes"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Required columns not available for slope analysis.")
