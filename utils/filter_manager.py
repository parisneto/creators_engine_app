import streamlit as st
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FilterManager:
    """
    Manages filters for data pages with page-specific namespaces.
    Each page declares a main dataframe that determines the primary filter options.
    """

    def __init__(self, page_id, main_df_name):
        """
        Initialize the filter manager.

        Args:
            page_id: Unique identifier for the page
            main_df_name: Name of the main dataframe for this page
        """
        self.page_id = page_id
        self.main_df_name = main_df_name
        self.namespace = f"filters_{page_id}"
        self.init_filter_state()

    def init_filter_state(self):
        """Initialize filter state with defaults if not already set."""
        if self.namespace not in st.session_state:
            st.session_state[self.namespace] = {
                "channel": [],
                "video_type": [],
                "language": [],
                "date_range": None,
                "playlists": []
            }

    def reset_filters(self):
        """Reset filters to defaults."""
        st.session_state[self.namespace] = {
            "channel": [],
            "video_type": [],
            "language": [],
            "date_range": None,
            "playlists": []
        }

    def render_filters(self, dataframe):
        """
        Render filter UI elements based on available dataframe columns.

        Args:
            dataframe: The main dataframe to filter

        Returns:
            The current filter state
        """
        # Get filter state
        filters = st.session_state[self.namespace]

        # Add reset button
        st.button("Reset Filters", on_click=self.reset_filters, key=f"{self.namespace}_reset")

        # Create filter UI elements based on dataframe columns
        if dataframe is not None:
            col1, col2, col3 = st.columns(3)

            # Channel filter
            with col1:
                if "channel_title" in dataframe.columns:
                    channel_options = dataframe["channel_title"].dropna().unique().tolist()
                    filters["channel"] = st.multiselect(
                        "Filter by Channel",
                        options=channel_options,
                        default=filters["channel"],
                        key=f"{self.namespace}_channel"
                    )
                elif "playlist_channel_title" in dataframe.columns:
                    channel_options = dataframe["playlist_channel_title"].dropna().unique().tolist()
                    filters["channel"] = st.multiselect(
                        "Filter by Channel",
                        options=channel_options,
                        default=filters["channel"],
                        key=f"{self.namespace}_channel"
                    )

            # Video type filter
            with col2:
                if "video_type" in dataframe.columns:
                    type_options = dataframe["video_type"].dropna().unique().tolist()
                    filters["video_type"] = st.multiselect(
                        "Filter by Type",
                        options=type_options,
                        default=filters["video_type"],
                        key=f"{self.namespace}_video_type"
                    )

            # Language filter
            with col3:
                if "default_audio_language" in dataframe.columns:
                    lang_options = dataframe["default_audio_language"].dropna().unique().tolist()
                    filters["language"] = st.multiselect(
                        "Filter by Language",
                        options=lang_options,
                        default=filters["language"],
                        key=f"{self.namespace}_language"
                    )

            # Date range filter
            date_col = None
            for col in ["video_added_at", "playlist_published_at", "published_at"]:
                if col in dataframe.columns:
                    date_col = col
                    break

            if date_col:
                dataframe[date_col] = pd.to_datetime(dataframe[date_col], errors='coerce')
                min_date = dataframe[date_col].min()
                max_date = dataframe[date_col].max()

                min_date_slider = min_date.date() if pd.notnull(min_date) else datetime.today().date()
                max_date_slider = max_date.date() if pd.notnull(max_date) else datetime.today().date()

                filters["date_range"] = st.slider(
                    f"Filter by {date_col.replace('_', ' ').title()}",
                    min_value=min_date_slider,
                    max_value=max_date_slider,
                    value=(min_date_slider, max_date_slider),
                    format="YYYY-MM-DD",
                    key=f"{self.namespace}_date_range"
                )

            # Playlist filter for playlist dataframes
            if "playlist_id" in dataframe.columns and "playlist_title" in dataframe.columns:
                # Get unique playlists
                playlist_df = dataframe[["playlist_id", "playlist_title"]].drop_duplicates()
                playlist_options = playlist_df["playlist_title"].dropna().unique().tolist()

                # Apply channel filter to playlists if channel filter is active
                if filters["channel"] and "playlist_channel_title" in dataframe.columns:
                    filtered_df = dataframe[dataframe["playlist_channel_title"].isin(filters["channel"])]
                    playlist_options = filtered_df["playlist_title"].dropna().unique().tolist()

                filters["playlists"] = st.multiselect(
                    "Filter by Playlist",
                    options=playlist_options,
                    default=filters["playlists"],
                    key=f"{self.namespace}_playlists"
                )

        return filters

    def get_filter_state(self):
        """Get current filter state."""
        return st.session_state[self.namespace]

    def render_filter_summary(self):
        """Render a compact summary of active filters."""
        filters = self.get_filter_state()

        # Build summary parts
        summary_parts = []
        if filters["channel"]:
            summary_parts.append(f"Channel: {', '.join(filters['channel'])}")
        if filters["video_type"]:
            summary_parts.append(f"Type: {', '.join(filters['video_type'])}")
        if filters["language"]:
            summary_parts.append(f"Language: {', '.join(filters['language'])}")
        if filters["playlists"]:
            summary_parts.append(f"Playlists: {', '.join(filters['playlists'])}")
        if filters["date_range"]:
            start_date, end_date = filters["date_range"]
            summary_parts.append(f"Date: {start_date} to {end_date}")

        # Display summary
        summary = " | ".join(summary_parts) if summary_parts else "No filters selected."
        st.markdown(f"**Active filters:** {summary}")

    def apply_filters(self, df):
        """
        Apply current filters to a dataframe.

        Args:
            df: DataFrame to filter

        Returns:
            Filtered DataFrame
        """
        if df is None:
            return None

        filters = self.get_filter_state()
        df_filtered = df.copy()

        # Apply channel filter
        if filters["channel"]:
            if "channel_title" in df_filtered.columns:
                df_filtered = df_filtered[df_filtered["channel_title"].isin(filters["channel"])]
            elif "playlist_channel_title" in df_filtered.columns:
                df_filtered = df_filtered[df_filtered["playlist_channel_title"].isin(filters["channel"])]

        # Apply video type filter
        if filters["video_type"] and "video_type" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["video_type"].isin(filters["video_type"])]

        # Apply language filter
        if filters["language"] and "default_audio_language" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["default_audio_language"].isin(filters["language"])]

        # Apply playlist filter
        if filters["playlists"] and "playlist_title" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["playlist_title"].isin(filters["playlists"])]

        # Apply date range filter
        if filters["date_range"]:
            date_col = None
            for col in ["video_added_at", "playlist_published_at", "published_at"]:
                if col in df_filtered.columns:
                    date_col = col
                    break

            if date_col:
                start_date, end_date = filters["date_range"]
                df_filtered[date_col] = pd.to_datetime(df_filtered[date_col], errors='coerce')
                df_filtered = df_filtered[
                    (df_filtered[date_col].dt.date >= start_date) &
                    (df_filtered[date_col].dt.date <= end_date)
                ]

        return df_filtered
