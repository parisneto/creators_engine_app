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
        st.session_state[self.namespace] = default_state

    def render_filters(self, dataframe):
        """
        Render filter UI elements based on configuration.

        Args:
            dataframe: The dataframe to filter

        Returns:
            The current filter state
        """
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
                            if depends_on and depends_on in filters and filters[depends_on]:
                                # Filter the dataframe based on the dependency
                                filtered_df = dataframe[dataframe[depends_on].isin(filters[depends_on])]
                                if col_name in filtered_df.columns:
                                    options = filtered_df[col_name].dropna().unique().tolist()
                            elif not options and col_name in dataframe.columns:
                                options = dataframe[col_name].dropna().unique().tolist()
                                
                            # Apply any extra parameters from config
                            extra_params = config.get("extra_params", {})
                            
                            # Sort options if requested
                            if extra_params.get("sort", False):
                                options = sorted(options)
                                
                            # Use session state to store and retrieve multiselect values
                            # This prevents the widget from closing on selection
                            multiselect_key = f"{self.namespace}_{col_name}_value"
                            if multiselect_key not in st.session_state:
                                st.session_state[multiselect_key] = filters.get(col_name, [])
                                
                            # Get widget parameters
                            widget_kwargs = {
                                "label": label,
                                "options": options,
                                "default": st.session_state[multiselect_key],
                                "key": f"{self.namespace}_{col_name}",
                                "on_change": self._update_multiselect_value,
                                "args": (multiselect_key, f"{self.namespace}_{col_name}", col_name)
                            }
                            
                            # Add any extra parameters that are valid for this widget
                            for param, value in extra_params.items():
                                if param not in ["sort"]:
                                    widget_kwargs[param] = value
                            
                            # Render the multiselect widget
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
                                
                                # Handle both single date and date range selections
                                date_key = f"{self.namespace}_{col_name}"
                                selected_date = st.date_input(
                                    label,
                                    value=default_value,
                                    min_value=min_date,
                                    max_value=max_date,
                                    key=date_key,
                                )
                                
                                # Ensure we always have a tuple of (start_date, end_date)
                                if isinstance(selected_date, tuple) or isinstance(selected_date, list):
                                    filters[col_name] = selected_date
                                else:
                                    # If single date is selected, use it for both start and end
                                    filters[col_name] = (selected_date, selected_date)

                        # Boolean filter
                        elif filter_type == "boolean":
                            options = ["All", "Yes", "No"]
                            current_value = filters.get(col_name)
                            default_index = 0
                            if current_value is True:
                                default_index = 1
                            elif current_value is False:
                                default_index = 2
                                
                            # Apply any extra parameters from config
                            extra_params = config.get("extra_params", {})
                            
                            # Get widget parameters
                            widget_kwargs = {
                                "label": label,
                                "options": options,
                                "index": default_index,
                                "key": f"{self.namespace}_{col_name}",
                                "horizontal": True
                            }
                            
                            # Add any extra parameters that are valid for this widget
                            for param, value in extra_params.items():
                                widget_kwargs[param] = value
                                
                            selected = st.radio(**widget_kwargs)

                            # Convert to Python boolean or None
                            new_value = None
                            if selected == "Yes":
                                new_value = True
                            elif selected == "No":
                                new_value = False
                                
                            # Only update if the value has changed
                            if new_value != filters.get(col_name):
                                filters[col_name] = new_value

                        # Segmented button with "All" option
                        elif filter_type == "segmented":
                            # Use st.radio with horizontal=True for segmented button look
                            options = config.get("options", [])
                            if not options and col_name in dataframe.columns:
                                options = dataframe[col_name].dropna().unique().tolist()
                                
                            # Add "All" option at the beginning
                            display_options = ["All"] + options
                                
                            current_value = filters.get(col_name)
                            default_index = 0  # Default to "All"
                            
                            if current_value and current_value in options:
                                default_index = display_options.index(current_value)
                                
                            # Apply any extra parameters from config
                            extra_params = config.get("extra_params", {})
                            
                            # Get widget parameters
                            widget_kwargs = {
                                "label": label,
                                "options": display_options,
                                "index": default_index,
                                "key": f"{self.namespace}_{col_name}",
                                "horizontal": True,
                                "format_func": lambda x: x  # Identity function to display as is
                            }
                            
                            # Add any extra parameters that are valid for this widget
                            for param, value in extra_params.items():
                                widget_kwargs[param] = value
                                
                            selected = st.radio(**widget_kwargs)
                            
                            # Store actual value or None for "All"
                            new_value = None if selected == "All" else selected
                            if new_value != filters.get(col_name):
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

    def _update_multiselect_value(self, session_key, widget_key, col_name):
        """Update session state for multiselect value."""
        # Get the current value from the widget
        current_value = st.session_state[widget_key]
        # Update our session state
        st.session_state[session_key] = current_value
        # Update the filter state
        filters = st.session_state[self.namespace]
        filters[col_name] = current_value

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

            elif filter_type == "date_range" and value:
                # Convert column to datetime if needed
                if df_filtered[col_name].dtype != "datetime64[ns]":
                    df_filtered[col_name] = pd.to_datetime(
                        df_filtered[col_name], errors="coerce"
                    )

                # Handle both tuple and single date values
                if isinstance(value, tuple) or isinstance(value, list):
                    start_date, end_date = value
                else:
                    # If it's a single date, use it for both start and end
                    start_date = end_date = value
                
                # Filter by date range
                df_filtered = df_filtered[
                    (df_filtered[col_name].dt.date >= start_date)
                    & (df_filtered[col_name].dt.date <= end_date)
                ]

            elif filter_type == "boolean" and value is not None:
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
                "extra_params": {"sort": True}
            },
            "video_type": {
                "type": "segmented",  # Changed to segmented for better UX
                "label": "Video Type", 
                "default": None,
                "extra_params": {"help": "Filter by video type"}
            },
            "default_audio_language": {
                "type": "multiselect",
                "label": "Language",
                "default": [],
                "extra_params": {"sort": True}
            },
            "published_at": {
                "type": "date_range",
                "label": "Published Date",
                "default": None,
                "extra_params": {"help": "Filter videos by publication date"}
            },
            "caption": {
                "type": "boolean", 
                "label": "Has Caption", 
                "default": None,
                "extra_params": {"help": "Filter videos by caption availability"}
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
                "extra_params": {"sort": True}
            },
            "playlist_title": {
                "type": "multiselect",
                "label": "Playlist",
                "default": [],
                "depends_on": "playlist_channel_title",  # This makes playlists depend on channel selection
                "extra_params": {
                    "sort": True,
                    "help": "Select playlists to include",
                    "placeholder": "Choose one or more playlists"
                }
            },
            "default_audio_language": {
                "type": "multiselect",
                "label": "Language",
                "default": [],
                "extra_params": {"sort": True}
            },
            "playlist_item_published_at": {
                "type": "date_range",
                "label": "Published Date",
                "default": None,
                "extra_params": {"help": "Filter by when items were published"}
            },
            "video_added_at": {
                "type": "date_range",
                "label": "Added Date",
                "default": None,
                "extra_params": {"help": "Filter by when videos were added to playlists"}
            },
        }
        
        # Populate options from DataFrame if provided
        if df is not None:
            # First populate channel options
            if "playlist_channel_title" in df.columns and "playlist_channel_title" in config:
                config["playlist_channel_title"]["options"] = df["playlist_channel_title"].dropna().unique().tolist()
                
            # For other columns, populate options
            for col_name in ["default_audio_language"]:
                if col_name in df.columns and col_name in config:
                    config[col_name]["options"] = df[col_name].dropna().unique().tolist()
                    
            # For playlist_title, we'll handle this in the render_filters method
            # since it depends on the selected channel
        
        return config
    # Add more configurations for other DataFrames as needed
    return {}
