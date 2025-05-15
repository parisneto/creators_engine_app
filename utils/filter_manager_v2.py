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
        if self.namespace not in st.session_state:
            # Create default state based on filter_config
            default_state = {}
            for col_name, config in self.filter_config.items():
                default_state[col_name] = config.get("default")
            st.session_state[self.namespace] = default_state

    def reset_filters(self):
        """Reset filters to defaults."""
        # Reset to defaults from filter_config
        default_state = {}
        for col_name, config in self.filter_config.items():
            default_state[col_name] = config.get("default")

        # Update the session state with defaults
        st.session_state[self.namespace] = default_state.copy()

        # st.rerun was here before causing eventual infinite loop: Calling st.rerun() within a callback is a no-op
        # Set a flag to trigger rerun after the callback completes
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

        # Get filter state
        filters = st.session_state[self.namespace]

        # Add reset button
        st.button(
            "Reset Filters", on_click=self.reset_filters, key=f"{self.namespace}_reset"
        )

        # Create filter UI elements based on configuration
        if dataframe is not None:
            # Create columns for layout
            num_columns = min(3, len(self.filter_config))
            if num_columns > 0:
                cols = st.columns(num_columns)

                # Track which column to place each filter in
                col_idx = 0

                # Render each configured filter
                for col_name, config in self.filter_config.items():
                    # Skip if column doesn't exist in dataframe
                    if col_name not in dataframe.columns and config["type"] != "custom":
                        continue

                    with cols[col_idx % num_columns]:
                        filter_type = config["type"]
                        label = config["label"]

                        # Multiselect filter
                        if filter_type == "multiselect":
                            # Check for dependencies to implement cascading filters
                            options = config.get("options", [])
                            depends_on = config.get("depends_on", None)

                            # If this filter depends on another filter (e.g., playlists depend on channel)
                            if (
                                depends_on
                                and depends_on in filters
                                and filters[depends_on]
                            ):
                                # Filter the dataframe based on the dependency
                                filtered_df = dataframe[
                                    dataframe[depends_on].isin(filters[depends_on])
                                ]
                                if col_name in filtered_df.columns:
                                    options = (
                                        filtered_df[col_name].dropna().unique().tolist()
                                    )
                            elif not options and col_name in dataframe.columns:
                                options = dataframe[col_name].dropna().unique().tolist()

                            # Apply any extra parameters from config
                            extra_params = config.get("extra_params", {})

                            # Sort options if requested
                            if extra_params.get("sort", False):
                                options = sorted(options)

                            # Get widget parameters - use direct approach without callbacks
                            widget_kwargs = {
                                "label": label,
                                "options": options,
                                "default": filters.get(col_name, []),
                                "key": f"{self.namespace}_{col_name}",
                            }

                            # Add any extra parameters that are valid for this widget
                            for param, value in extra_params.items():
                                if param not in ["sort"]:
                                    widget_kwargs[param] = value

                            # Render the multiselect widget and update filters directly
                            selection = st.multiselect(**widget_kwargs)
                            filters[col_name] = selection

                        # Slider filter
                        elif filter_type == "slider":
                            min_val = config.get("min", 0)
                            max_val = config.get("max", 100)
                            if col_name in dataframe.columns:
                                if min_val is None:
                                    min_val = float(dataframe[col_name].min())
                                if max_val is None:
                                    max_val = float(dataframe[col_name].max())
                            filters[col_name] = st.slider(
                                label,
                                min_value=min_val,
                                max_value=max_val,
                                value=filters.get(col_name, (min_val, max_val)),
                                key=f"{self.namespace}_{col_name}",
                            )

                        # Date range filter
                        elif filter_type == "date_range":
                            if col_name in dataframe.columns:
                                # Convert to datetime if needed
                                if dataframe[col_name].dtype != "datetime64[ns]":
                                    dataframe[col_name] = pd.to_datetime(
                                        dataframe[col_name], errors="coerce"
                                    )

                                min_date = dataframe[col_name].min().date()
                                max_date = dataframe[col_name].max().date()

                                # Default to full range if not set
                                default_value = filters.get(
                                    col_name, (min_date, max_date)
                                )

                                # Handle date range selection safely

                                try:
                                    # Convert to datetime if not already
                                    if dataframe[col_name].dtype.kind == "O":
                                        date_series = pd.to_datetime(
                                            dataframe[col_name]
                                        )
                                    else:
                                        date_series = dataframe[col_name]

                                    # Get min/max dates
                                    min_date = date_series.min().date()
                                    max_date = date_series.max().date()
                                except Exception as e:
                                    st.warning(
                                        f"Error getting date range for {col_name}: {e}"
                                    )
                                    min_date = datetime.date(2020, 1, 1)
                                    max_date = datetime.date.today()
                            else:
                                # Default date range if column not in dataframe
                                min_date = datetime.date(2020, 1, 1)
                                max_date = datetime.date.today()

                            # Get current value from filters
                            current_value = filters.get(col_name)

                            # Set default value
                            if current_value is None:
                                default_value = None
                            else:
                                default_value = current_value

                            # Apply any extra parameters from config
                            extra_params = config.get("extra_params", {})

                            # Get widget parameters
                            widget_kwargs = {
                                "label": label,
                                "min_value": min_date,
                                "max_value": max_date,
                                "value": default_value,
                                "key": f"{self.namespace}_{col_name}",
                            }

                            # Add any extra parameters that are valid for this widget
                            for param, value in extra_params.items():
                                if param not in ["sort"]:
                                    widget_kwargs[param] = value

                            # Create a unique key for this widget
                            widget_key = f"{self.namespace}_{col_name}_date"

                            # Get widget parameters
                            widget_kwargs = {
                                "label": label,
                                "min_value": min_date,
                                "max_value": max_date,
                                "key": widget_key,
                            }

                            # Add help if provided
                            if "help" in extra_params:
                                widget_kwargs["help"] = extra_params["help"]

                            # Set value only if we have a current value or it's the first render
                            if current_value is not None:
                                widget_kwargs["value"] = current_value
                            elif widget_key not in st.session_state:
                                # First render with no value - use None to allow proper range selection
                                widget_kwargs["value"] = None

                            # Add any extra parameters that are valid for this widget
                            for param, value in extra_params.items():
                                if param not in ["sort"]:
                                    widget_kwargs[param] = value

                            # Render the date input widget
                            date_value = st.date_input(**widget_kwargs)

                            # Normalize the date value to always be a tuple of (start_date, end_date)
                            # This prevents issues when applying filters
                            if isinstance(date_value, datetime.date):
                                # Single date selected - convert to tuple with same start and end date
                                filters[col_name] = (date_value, date_value)
                            elif isinstance(date_value, (list, tuple)):
                                if len(date_value) == 1:
                                    # Single date in a list/tuple - convert to tuple with same start and end date
                                    filters[col_name] = (date_value[0], date_value[0])
                                elif len(date_value) == 2:
                                    # Proper date range - store as tuple
                                    filters[col_name] = (date_value[0], date_value[1])
                                else:
                                    # Unexpected format - skip
                                    pass
                            else:
                                # None or unexpected type - remove filter
                                filters[col_name] = None

                        # Boolean filter
                        elif filter_type == "boolean":
                            # For boolean columns, use a segmented control with just Yes/No options
                            options = ["Yes", "No"]
                            current_value = filters.get(col_name)

                            # Create a unique key for this widget
                            widget_key = f"{self.namespace}_{col_name}_bool"

                            # Apply any extra parameters from config
                            extra_params = config.get("extra_params", {})

                            # Get widget parameters for segmented control
                            widget_kwargs = {
                                "label": label,
                                "options": options,
                                "key": widget_key,
                            }

                            # Set default value based on current filter value
                            # Only set on first render or after reset to avoid state issues
                            if widget_key not in st.session_state:
                                if current_value is True:
                                    widget_kwargs["default"] = "Yes"
                                elif current_value is False:
                                    widget_kwargs["default"] = "No"
                                # If None (not filtered), don't set a default

                            # Add help text if provided
                            if "help" in extra_params:
                                widget_kwargs["help"] = extra_params["help"]

                            # Render the segmented control
                            selected = st.segmented_control(**widget_kwargs)

                            # Convert selection to boolean value
                            # If something is selected, use that value
                            if selected == "Yes":
                                filters[col_name] = True
                            elif selected == "No":
                                filters[col_name] = False
                            # If nothing is selected (initial state), keep as None

                        elif filter_type == "segmented":
                            # Get options from config or dataframe
                            options = config.get("options", [])
                            if not options and col_name in dataframe.columns:
                                options = dataframe[col_name].dropna().unique().tolist()

                            # Add "All" option at the beginning
                            display_options = ["All"] + options

                            # Get current value or default to "All"
                            current_value = filters.get(col_name)

                            # For segmented control, we need to handle the "All" option specially
                            # If the filter value is None (default or reset state), we should select "All"
                            selected_value = (
                                "All" if current_value is None else current_value
                            )
                            if (
                                selected_value not in options
                                and selected_value != "All"
                            ):
                                selected_value = "All"

                            # Apply any extra parameters from config
                            extra_params = config.get("extra_params", {})

                            # Create a unique key for this widget that doesn't change on reruns
                            # This helps prevent the widget from losing state on second click
                            widget_key = f"{self.namespace}_{col_name}_segmented"

                            # Prepare parameters for segmented_control
                            widget_kwargs = {
                                "label": label,
                                "options": display_options,
                                "key": widget_key,
                            }

                            # Only set default on first render or after reset
                            # This prevents the widget from resetting on every interaction
                            if widget_key not in st.session_state:
                                widget_kwargs["default"] = selected_value

                            # Add help text if provided
                            if "help" in extra_params:
                                widget_kwargs["help"] = extra_params["help"]

                            # Render the segmented control widget
                            selected = st.segmented_control(**widget_kwargs)

                            # Store actual value or None for "All"
                            new_value = None if selected == "All" else selected
                            filters[col_name] = new_value

                        # Custom filter (for special cases)
                        elif filter_type == "custom":
                            # Custom filters need to be handled by the config's render_func
                            if "render_func" in config:
                                filters[col_name] = config["render_func"](
                                    label,
                                    filters.get(col_name),
                                    dataframe,
                                    f"{self.namespace}_{col_name}",
                                )

                    # Move to next column
                    col_idx += 1

        return filters

    def get_filter_state(self):
        """Get current filter state."""
        return st.session_state[self.namespace]

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

        return config
    # Add more configurations for other DataFrames as needed
    return {}
