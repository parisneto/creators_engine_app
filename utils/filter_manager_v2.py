import datetime
import logging

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


class FilterManager:
    """
    Configurable filter manager for data pages with page-specific namespaces.
    Supports dynamic filter configuration based on DataFrame columns.
    """

    def __init__(self, page_id, df_name, filter_config=None):
        """
        Initialize the filter manager with configurable filters.

        Args:
            page_id: Unique identifier for the page
            df_name: Name of the dataframe for this page
            filter_config: Dictionary of filter configurations
                Format: {
                    "column_name": {
                        "type": "multiselect|slider|date_range|boolean",
                        "label": "User-friendly label",
                        "default": default_value,
                        "options": [list of options] (optional for multiselect),
                        "min": min_value (optional for slider),
                        "max": max_value (optional for slider)
                    }
                }
        """
        self.page_id = page_id
        self.df_name = df_name
        self.namespace = f"filters_{page_id}"
        self.filter_config = filter_config or {}
        self.init_filter_state()

    def init_filter_state(self):
        """Initialize filter state with defaults based on configuration."""
        for col_name, config in self.filter_config.items():
            key = f"{self.namespace}_{col_name}"
            if key not in st.session_state:
                st.session_state[key] = config.get("default")

    def reset_filters(self):
        """Reset filters to defaults."""
        for col_name, config in self.filter_config.items():
            key = f"{self.namespace}_{col_name}"
            st.session_state[key] = config.get("default")
        st.session_state[f"{self.namespace}_needs_rerun"] = True

    def render_filters(self, dataframe):
        """
        Render filter UI elements based on configuration.

        Args:
            dataframe: The dataframe to filter

        Returns:
            The current filter state
        """
        # Check if we need to rerun (set by reset_filters)
        rerun_key = f"{self.namespace}_needs_rerun"
        if rerun_key in st.session_state and st.session_state[rerun_key]:
            # Clear the flag and trigger rerun
            st.session_state[rerun_key] = False
            # st.rerun()

        # No longer using a nested dict for filters; use session_state keys directly

        # Add reset button
        st.button(
            "Reset Filters", on_click=self.reset_filters, key=f"{self.namespace}_reset"
        )

        # Create filter UI elements based on configuration
        if dataframe is not None:
            num_columns = min(3, len(self.filter_config))
            if num_columns > 0:
                cols = st.columns(num_columns)
                col_idx = 0
                for col_name, config in self.filter_config.items():
                    if col_name not in dataframe.columns and config["type"] != "custom":
                        continue
                    with cols[col_idx % num_columns]:
                        filter_type = config["type"]
                        label = config["label"]
                        widget_key = f"{self.namespace}_{col_name}"
                        # Multiselect filter
                        if filter_type == "multiselect":
                            options = config.get("options", [])
                            depends_on = config.get("depends_on", None)
                            # Cascading filters
                            if (
                                depends_on
                                and f"{self.namespace}_{depends_on}" in st.session_state
                                and st.session_state[f"{self.namespace}_{depends_on}"]
                            ):
                                filtered_df = dataframe[
                                    dataframe[depends_on].isin(
                                        st.session_state[
                                            f"{self.namespace}_{depends_on}"
                                        ]
                                    )
                                ]
                                if col_name in filtered_df.columns:
                                    options = (
                                        filtered_df[col_name].dropna().unique().tolist()
                                    )
                            elif not options and col_name in dataframe.columns:
                                options = dataframe[col_name].dropna().unique().tolist()
                            extra_params = config.get("extra_params", {})
                            if extra_params.get("sort", False):
                                options = sorted(options)
                            widget_kwargs = {
                                "label": label,
                                "options": options,
                                "key": widget_key,
                            }
                            for param, value in extra_params.items():
                                if param not in ["sort"]:
                                    widget_kwargs[param] = value
                            st.multiselect(**widget_kwargs)
                        # Slider filter
                        elif filter_type == "slider":
                            min_val = config.get("min", 0)
                            max_val = config.get("max", 100)
                            if col_name in dataframe.columns:
                                if min_val is None:
                                    min_val = float(dataframe[col_name].min())
                                if max_val is None:
                                    max_val = float(dataframe[col_name].max())
                            st.slider(
                                label,
                                min_value=min_val,
                                max_value=max_val,
                                key=widget_key,
                            )
                        # Date range filter
                        elif filter_type == "date_range":
                            widget_key = f"{self.namespace}_{col_name}"
                            # Ensure the column is datetime
                            if col_name in dataframe.columns:
                                dataframe[col_name] = pd.to_datetime(
                                    dataframe[col_name], errors="coerce"
                                )
                                min_date = dataframe[col_name].dt.date.min()
                                max_date = dataframe[col_name].dt.date.max()
                            else:
                                min_date = datetime.date(2020, 1, 1)
                                max_date = datetime.date.today()

                            # Render a single date_range widget (two-date picker)
                            st.date_input(
                                label,
                                value=st.session_state.get(widget_key),
                                min_value=min_date,
                                max_value=max_date,
                                key=widget_key,
                                help=config.get("extra_params", {}).get("help"),
                            )
                        # Boolean filter
                        elif filter_type == "boolean":
                            options = ["Yes", "No"]
                            widget_key_bool = f"{widget_key}_bool"
                            extra_params = config.get("extra_params", {})
                            widget_kwargs = {
                                "label": label,
                                "options": options,
                                "key": widget_key_bool,
                            }
                            if "help" in extra_params:
                                widget_kwargs["help"] = extra_params["help"]
                            st.segmented_control(**widget_kwargs)
                            selected = st.session_state.get(widget_key_bool)
                            if selected == "Yes":
                                st.session_state[widget_key] = True
                            elif selected == "No":
                                st.session_state[widget_key] = False
                            else:
                                st.session_state[widget_key] = None
                        elif filter_type == "segmented":
                            options = config.get("options", [])
                            if not options and col_name in dataframe.columns:
                                options = dataframe[col_name].dropna().unique().tolist()
                            display_options = ["All"] + options
                            widget_key_segmented = f"{widget_key}_segmented"
                            extra_params = config.get("extra_params", {})
                            widget_kwargs = {
                                "label": label,
                                "options": display_options,
                                "key": widget_key_segmented,
                            }
                            if "help" in extra_params:
                                widget_kwargs["help"] = extra_params["help"]
                            st.segmented_control(**widget_kwargs)
                            selected = st.session_state.get(widget_key_segmented)
                            if selected == "All":
                                st.session_state[widget_key] = None
                            else:
                                st.session_state[widget_key] = selected
                        elif filter_type == "custom":
                            if "render_func" in config:
                                st.session_state[widget_key] = config["render_func"](
                                    label,
                                    st.session_state.get(widget_key),
                                    dataframe,
                                    widget_key,
                                )
                    col_idx += 1
        # Return current filter state
        return self.get_filter_state()

    def get_filter_state(self):
        """Get current filter state."""
        state = {}
        for col_name, config in self.filter_config.items():
            key = f"{self.namespace}_{col_name}"
            state[col_name] = st.session_state.get(key, config.get("default"))
        return state

    def render_filter_summary(self):
        """Render a compact summary of active filters."""
        filters = self.get_filter_state()

        # Build summary parts
        summary_parts = []
        for col_name, value in filters.items():
            if col_name in self.filter_config:
                config = self.filter_config[col_name]

                # Skip if no value is set
                if value is None or (isinstance(value, list) and not value):
                    continue

                filter_type = config["type"]
                label = config["label"]

                if filter_type == "multiselect" and value:
                    summary_parts.append(f"{label}: {', '.join(str(v) for v in value)}")
                elif filter_type == "slider":
                    summary_parts.append(f"{label}: {value}")
                elif filter_type == "date_range" and value:
                    try:
                        start_date, end_date = value
                        if start_date == end_date:
                            summary_parts.append(f"{label}: {start_date}")
                        else:
                            summary_parts.append(f"{label}: {start_date} to {end_date}")
                    except (ValueError, TypeError):
                        # Handle case where value is a single date
                        summary_parts.append(f"{label}: {value}")
                elif filter_type == "segmented" and value is not None:
                    summary_parts.append(f"{label}: {value}")
                elif filter_type == "boolean" and value is not None:
                    summary_parts.append(f"{label}: {'Yes' if value else 'No'}")
                elif filter_type == "custom" and "summary_func" in config:
                    summary = config["summary_func"](value)
                    if summary:
                        summary_parts.append(f"{label}: {summary}")

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

        # Apply each configured filter
        for col_name, value in filters.items():
            # Skip if column doesn't exist or value is not set
            if col_name not in df_filtered.columns or value is None:
                continue

            if col_name not in self.filter_config:
                continue

            config = self.filter_config[col_name]
            filter_type = config["type"]

            # Apply based on filter type
            if filter_type == "multiselect" and value:
                df_filtered = df_filtered[df_filtered[col_name].isin(value)]

            elif filter_type == "slider":
                min_val, max_val = value
                df_filtered = df_filtered[
                    (df_filtered[col_name] >= min_val)
                    & (df_filtered[col_name] <= max_val)
                ]

            elif filter_type == "date_range" and value is not None:
                try:
                    # Handle date range - by this point, value should always be a tuple of (start_date, end_date)
                    # thanks to our normalization in the render_filters method
                    if isinstance(value, (tuple, list)) and len(value) == 2:
                        start_date, end_date = value
                    else:
                        # If somehow we got a single date, use it for both start and end
                        if isinstance(value, datetime.date):
                            start_date = end_date = value
                        else:
                            # Skip filtering if value is not in expected format
                            st.warning(
                                f"Unexpected date format for {col_name}: {value}. Skipping filter."
                            )
                            continue

                    # Apply filter
                    if col_name in df_filtered.columns:
                        # Convert column to datetime if it's not already
                        if df_filtered[col_name].dtype.kind not in ["M"]:
                            df_filtered[col_name] = pd.to_datetime(
                                df_filtered[col_name], errors="coerce"
                            )

                        # Handle NaT values - skip rows with missing dates
                        df_filtered = df_filtered.dropna(subset=[col_name])

                        # Apply date range filter - convert column dates to date objects for comparison
                        mask = (df_filtered[col_name].dt.date >= start_date) & (
                            df_filtered[col_name].dt.date <= end_date
                        )
                        df_filtered = df_filtered[mask]
                except Exception as e:
                    st.warning(f"Error applying date filter for {col_name}: {e}")
                    # Skip this filter if there's an error
                    continue

            elif filter_type == "boolean" and value is not None:
                # For boolean toggle, we filter by exact match (True or False)
                # Note: if value is None, we don't filter ("All" option)
                df_filtered = df_filtered[df_filtered[col_name] == value]

            elif filter_type == "segmented" and value is not None:
                # For segmented, we filter by the exact value (not a list)
                df_filtered = df_filtered[df_filtered[col_name] == value]

            elif filter_type == "custom" and "apply_func" in config:
                df_filtered = config["apply_func"](df_filtered, value)

        return df_filtered


# Helper function to create common filter configurations
def create_filter_config(df_name, df=None):
    """
    Create a filter configuration based on the DataFrame name.

    Args:
        df_name: Name of the DataFrame
        df: Optional DataFrame to extract unique values from

    Returns:
        Dictionary of filter configurations
    """
    if df_name == "df_nerdalytics" or df_name == "tbl_nerdalytics":
        config = {
            "channel_title": {
                "type": "multiselect",
                "label": "Channel",
                "default": [],
                "extra_params": {"sort": True},
            },
            "video_type": {
                "type": "segmented",  # Changed to segmented for better UX
                "label": "Video Type",
                "default": None,
                "extra_params": {"help": "Filter by video type"},
            },
            "default_audio_language": {
                "type": "multiselect",
                "label": "Language",
                "default": [],
                "extra_params": {"sort": True},
            },
            "published_at": {
                "type": "date_range",
                "label": "Published Date",
                "default": None,
                "extra_params": {"help": "Filter videos by publication date"},
            },
            "caption": {
                "type": "boolean",
                "label": "Has Caption",
                "default": None,
                "extra_params": {"help": "Filter videos by caption availability"},
            },
        }

        # Populate options from DataFrame if provided
        if df is not None:
            for col_name in ["channel_title", "video_type", "default_audio_language"]:
                if col_name in df.columns:
                    unique_values = df[col_name].dropna().unique().tolist()
                    if col_name in config:
                        if config[col_name]["type"] == "multiselect":
                            config[col_name]["options"] = unique_values
                        elif config[col_name]["type"] == "segmented":
                            config[col_name]["options"] = unique_values

        return config
    elif df_name == "df_playlist" or df_name == "tbl_playlist_full_dedup":
        config = {
            "playlist_channel_title": {
                "type": "multiselect",
                "label": "Channel",
                "default": [],
                "extra_params": {"sort": True},
            },
            "playlist_title": {
                "type": "multiselect",
                "label": "Playlist",
                "default": [],
                "depends_on": "playlist_channel_title",  # This makes playlists depend on channel selection
                "extra_params": {
                    "sort": True,
                    "help": "Select playlists to include",
                    "placeholder": "Choose one or more playlists",
                },
            },
            "default_audio_language": {
                "type": "multiselect",
                "label": "Language",
                "default": [],
                "extra_params": {"sort": True},
            },
            "playlist_item_published_at": {
                "type": "date_range",
                "label": "Published Date",
                "default": None,
                "extra_params": {"help": "Filter by when items were published"},
            },
            "video_added_at": {
                "type": "date_range",
                "label": "Added Date",
                "default": None,
                "extra_params": {
                    "help": "Filter by when videos were added to playlists"
                },
            },
        }

        # Populate options from DataFrame if provided
        if df is not None:
            # Populate all available options
            for col_name in config.keys():
                if col_name in df.columns:
                    # For all columns except those with dependencies, populate options directly
                    if "depends_on" not in config[col_name]:
                        config[col_name]["options"] = (
                            df[col_name].dropna().unique().tolist()
                        )

                        # Sort if requested
                        if "extra_params" in config[col_name] and config[col_name][
                            "extra_params"
                        ].get("sort", False):
                            config[col_name]["options"] = sorted(
                                config[col_name]["options"]
                            )

            # For playlist_title, we'll pre-populate but it will be filtered in render_filters
            if "playlist_title" in config and "playlist_title" in df.columns:
                config["playlist_title"]["options"] = (
                    df["playlist_title"].dropna().unique().tolist()
                )

            # Set full-range defaults for date filters so they include all data initially
            for date_col in ["playlist_item_published_at", "video_added_at"]:
                if date_col in config and date_col in df.columns:
                    series = pd.to_datetime(df[date_col], errors="coerce").dt.date
                    config[date_col]["default"] = (series.min(), series.max())

        return config
    # Add more configurations for other DataFrames as needed
    return {}
