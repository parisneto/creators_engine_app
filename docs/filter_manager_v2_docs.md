# FilterManager V2 Documentation

## Table of Contents

1. [Overview](#overview)
2. [Files and Classes](#files-and-classes)
3. [Logic and Use Cases](#logic-and-use-cases)
4. [Filter Types and UI Components](#filter-types-and-ui-components)
5. [Data Type Handling](#data-type-handling)
6. [Known Issues and Solutions](#known-issues-and-solutions)
7. [Configuration Examples](#configuration-examples)

## Overview

FilterManager V2 is a configurable filtering system for Streamlit applications that allows users to filter DataFrames using various UI components. It supports multiple filter types, cascading filters, and handles complex data types safely. The system is designed to be modular, reusable, and easy to configure for different DataFrames.

## Files and Classes

### Core Files

- **`/app/utils/filter_manager_v2.py`**: Main implementation file containing the FilterManager class and helper functions
- **`/app/modules/datastories.py`**: Example main page using FilterManager with nerdalytics DataFrame
- **`/app/modules/datastories_playlist.py`**: Example main page using FilterManager with playlist DataFrame
- **`/app/modules/blocks/*.py`**: Subpage modules that receive filtered DataFrames from main pages

### Key Classes and Functions

#### FilterManager Class

The core class that manages filter state, UI rendering, and filter application.

**Key Methods:**
- `__init__(self, page_id, df_name, filter_config=None)`: Initialize with unique namespace and configuration
- `render_filters(self, dataframe)`: Render filter UI components based on configuration
- `apply_filters(self, df)`: Apply current filter state to a DataFrame
- `render_filter_summary(self)`: Display a compact summary of active filters
- `reset_filters(self)`: Reset all filters to their defaults
- `get_filter_state(self)`: Get the current filter state from session state

#### Helper Functions

- `create_filter_config(df_name, df=None)`: Create filter configuration for a specific DataFrame

## Logic and Use Cases

### Core Principles

1. **Single DataFrame Per Page**: Each main page loads a single DataFrame and manages filters for it
2. **Filtered DataFrame for Subpages**: Main page passes the filtered DataFrame to all subpages/blocks
3. **Namespace Isolation**: Each page has a unique namespace to avoid filter state conflicts
4. **Declarative Configuration**: Filter behavior is defined through configuration dictionaries
5. **Cascading Filters**: Filters can depend on other filters (e.g., playlists filtered by selected channels)

### Data Flow and Tight Coupling

Each main page (e.g., `datastories.py`, `datastories_playlist.py`) and its subpages share a single DataFrame that is tightly coupled with the filter UI. This means:

- The main page loads a specific DataFrame (e.g., `df_nerdalytics` or `df_playlist`)
- The FilterManager applies filters to this DataFrame
- The filtered DataFrame is passed to all subpages/blocks
- Any changes to filters affect everything downstream (plots, visualizations, tables)
- Each main page has its own dedicated subpages/blocks that are designed to work with its specific DataFrame

This tight coupling ensures consistency across the application but requires careful consideration when adding or removing filters, as these changes will impact all visualizations and components that use the filtered data.

### Typical Flow

1. **Main Page Initialization**:
   - Load DataFrame using `load_data()`
   - Create filter configuration with `create_filter_config()`
   - Initialize FilterManager with page ID, DataFrame name, and configuration

2. **Filter UI Rendering**:
   - Render filter UI in a popover or directly on the page
   - Display filter summary showing active filters

3. **Filter Application**:
   - Apply filters to the DataFrame
   - Pass filtered DataFrame to subpages/blocks

4. **Subpage Rendering**:
   - Subpages receive and use the filtered DataFrame
   - No filter logic in subpages - they just consume the filtered data

### Use Cases

- **Data Exploration**: Filter large datasets to focus on specific subsets
- **Dashboard Navigation**: Apply filters across multiple visualizations/tabs
- **Dependent Selections**: Filter options based on previous selections (cascading filters)
- **User Preferences**: Save and restore filter states for personalized views

## Filter Types and UI Components

### Available Filter Types

| Filter Type | UI Component | Description | Configuration |
|-------------|--------------|-------------|---------------|
| `multiselect` | `st.multiselect` | Multiple selection from a list of options | `{"type": "multiselect", "label": "Label", "default": []}` |
| `segmented` | `st.radio` with horizontal=True | Single selection with "All" option | `{"type": "segmented", "label": "Label", "default": None}` |
| `slider` | `st.slider` | Range selection for numeric values | `{"type": "slider", "label": "Label", "default": (min, max)}` |
| `date_range` | `st.date_input` | Date range selection | `{"type": "date_range", "label": "Label", "default": None}` |
| `boolean` | `st.radio` | Yes/No/All selection | `{"type": "boolean", "label": "Label", "default": None}` |
| `custom` | Custom function | Custom UI and logic | `{"type": "custom", "label": "Label", "render_func": func, "apply_func": func}` |

### Customizing Filter UI

Each filter can be customized using the `extra_params` dictionary:

```python
"channel_title": {
    "type": "multiselect",
    "label": "Channel",
    "default": [],
    "extra_params": {
        "sort": True,  # Sort options alphabetically
        "help": "Select channels to include",  # Tooltip
        "placeholder": "Choose one or more channels"  # Placeholder text
    }
}
```

The `extra_params` dictionary can include any parameter supported by the corresponding Streamlit widget.

### Adding/Removing Filter Columns

The FilterManager system allows for both development-time and runtime configuration of filters. Here's how to manage filter columns:

#### Development-Time Configuration

To add or remove filter columns during development, modify the filter configuration in `create_filter_config()`:

```python
# First, identify which DataFrame you're configuring filters for
def create_filter_config(df_name, df=None):
    if df_name == "df_nerdalytics":
        config = {
            # Existing filters...
        }

        # Add a new filter
        config["new_column"] = {
            "type": "multiselect",
            "label": "New Filter",
            "default": []
        }

        # Remove a filter
        if "unwanted_column" in config:
            del config["unwanted_column"]

    elif df_name == "df_playlist":
        # Different configuration for playlist DataFrame
        # ...

    return config
```

#### Runtime Configuration

The FilterManager also supports modifying filters at runtime, though this adds some complexity:

```python
# Get the current filter configuration
filter_config = filter_manager.filter_config

# Add a new filter at runtime
filter_config["new_column"] = {
    "type": "multiselect",
    "label": "New Filter",
    "default": []
}

# Remove a filter at runtime
if "unwanted_column" in filter_config:
    del filter_config["unwanted_column"]

# Update session state to reflect changes
st.session_state[filter_manager.namespace] = {}
```

**Note on Complexity**: While runtime filter modification is supported, it adds complexity and potential for bugs. For most use cases, configuring filters during development is simpler and safer. Runtime modifications should be used only when necessary for advanced use cases.

## Data Type Handling

### Date and Datetime

Date filters require special handling due to Streamlit's date_input widget behavior:

- **Input Validation**: Ensure date values are valid before using them
- **Type Conversion**: Convert between datetime64[ns] and Python date objects
- **Range Handling**: Handle both single dates and date ranges
- **Error Recovery**: Provide fallback values when date parsing fails

```python
# Safe date handling example
try:
    if isinstance(value, (tuple, list)) and len(value) == 2:
        start_date, end_date = value
    elif value is not None:
        start_date = end_date = value
    else:
        # Skip filtering if no date is selected
        continue
except Exception:
    # Skip filtering if there's an error
    continue
```

### Null and Missing Values

- **Null Handling**: Use `dropna()` when collecting unique values
- **Empty Selection**: Treat empty lists as "select all" (no filtering)
- **Default Values**: Provide sensible defaults for all filter types

### Numeric Ranges

- **Min/Max Detection**: Automatically detect min/max values from DataFrame
- **Type Conversion**: Handle conversion between numeric types
- **Range Validation**: Ensure min <= max for sliders and ranges

## Source Data and Caching

The FilterManager works with DataFrames that are loaded and cached according to specific patterns:

### Caching Strategy

1. **Base Data Loading** (`@st.cache_resource(ttl='1d')`)
   - Loads parquet files once per container start
   - Performs permanent preprocessing (type fixes, joins, computed columns)
   - Returns a dictionary of clean DataFrames
   - These DataFrames should NOT be mutated after loading

2. **User Session Data** (`@st.cache_data(ttl='15m')`)
   - Creates per-user session copies of DataFrames with `.copy()`
   - These copies are used for filtering and other session-specific operations
   - Always calls `.copy()` before mutating data
   - Used for expensive per-user derivations (group-bys, stats)

### Integration with FilterManager

The FilterManager expects to work with user session copies of DataFrames, not the base cached DataFrames. This ensures that:

1. Original data remains untouched for other users
2. Filters apply only to the current user's session
3. Multiple users can apply different filters simultaneously

#### Advanced Reset Behavior

In a typical use case, clicking on "Reset Filters" will reset the filter state to its original configuration, but the underlying DataFrame remains the same. However, in more advanced scenarios where you've transformed the local DataFrame copies (e.g., added calculated columns, dropped NA values, normalized data), you might want to completely refresh the data as well.

To implement this more comprehensive reset:

```python
# In your page's render function
def reset_all():
    # Reset filter state
    filter_manager.reset_filters()
    # Reload fresh data from cache
    st.session_state["df_nerdalytics"] = load_data()
    # Force UI update
    st.rerun()

# Add a button for complete reset
st.button("Reset Data and Filters", on_click=reset_all)
```

This approach allows you to reset both the filter state and the underlying data when needed.

```python
# Example of proper data loading pattern
def load_data():
    # Get base data (cached across all users)
    base_data = load_base_data()

    # Create user-specific copies for filtering
    df_nerdalytics = base_data["nerdalytics"].copy()

    return df_nerdalytics
```

## Known Issues and Solutions

### Current Active Bugs

1 Cascade Filters not working, when I select playlists and later a different channel, the playlist filter is not updated to show only playlists from that channel. and error : streamlit.errors.StreamlitAPIException: The default value '7 DICAS PARA TUDO' is not part of the options. Please make sure that every default values also exists in the options.

2 Reset Filters issues :
- not applying to Has Captions ( t.segmented_control)
- reset shows Active filters: No filters selected. But ui keeps Video Type = ALL , Has Caption = ALL and after changing pages, only Video Type shows ALL selected ( red color )


### Previous Bugs

1. **Multiselect Closing on Second Click**
   - **Issue**: The multiselect dropdown would close after the second selection
   - **Solution**: Use direct assignment instead of callbacks for multiselect values
   - **Failed Approach**: Using session state variables and callbacks caused rerun issues
   - **Current Status**: Partially resolved, but some ghost clicks still occur in certain scenarios

2. **Reset Filters Not Working**
   - **Issue**: Reset button didn't clear all filters properly
   - **Solution**: Add `st.rerun()` after resetting filter state to force UI update
   - **Failed Approach**: Updating only the session state without forcing a rerun
   - **Current Status**: Resolved

3. **Date Range Filter Errors**
   - **Issue**: Single date selection caused unpacking errors
   - **Solution**: Add robust error handling and type checking for date values
   - **Failed Approach**: Assuming date_input always returns a tuple
   - **Current Status**: Partially resolved, but still has issues with certain combinations like:
     ```
     Active filters: Video Type: Regular | Published Date: (datetime.date(2024, 7, 1),) | Has Caption: Yes
     ```
     which causes `TypeError: '>=' not supported between instances of 'datetime.date' and 'tuple'`

4. **Cascading Filters Not Working**
   - **Issue**: Dependent filters weren't updating based on parent selections
   - **Solution**: Properly implement dependency checking and filter options based on parent values
   - **Failed Approach**: Using static options instead of dynamically filtering them
   - **Current Status**: Resolved

5. **Empty DataFrame Handling**
   - **Issue**: Empty filtered DataFrames would cause errors in subpages
   - **Solution**: Add explicit checks for empty DataFrames and show helpful messages
   - **Failed Approach**: Assuming filtered DataFrames always contain data
   - **Current Status**: Resolved

### Current Limitations

1. **Performance with Large DataFrames**: Filtering large DataFrames can be slow
2. **Complex Dependencies**: Only simple parent-child dependencies are supported
3. **Session State Persistence**: Filters reset when navigating between pages
4. **Limited Custom Filter Support**: Custom filters require more boilerplate code

## Roadmap

### Planned Features

1. **Basic/Advanced Filter Sets**
   - Support for multiple filter sets (e.g., basic and advanced) for the same DataFrame
   - Toggle between different filter configurations without changing the underlying data
   - Ability to save and load filter presets

2. **DataFrame Size Warnings**
   - Implement warnings when filtered DataFrames exceed certain size thresholds
   - Set configurable boundaries for number of rows or memory usage
   - Provide optimization suggestions when filters result in large datasets

3. **Text Search Columns**
   - Add support for free-text search filters (e.g., search in video titles)
   - Show matching count and preview of matching items
   - Optional UI element to display matching items when clicked

4. **Filter Suggestions Carousel**
   - Add a carousel of predefined filter combinations that can be applied with one click
   - Examples: "Last Month Shorts", "This Year Regular Videos", "High Engagement Content"
   - Allow users to save their own filter combinations as suggestions

5. **Enhanced Date Handling**
   - Improve robustness of date filters to handle all edge cases
   - Add relative date options (last 7 days, last month, year to date)
   - Fix remaining issues with single date selection

6. **Multiselect Improvements**
   - Fix remaining issues with ghost clicks and dropdown behavior
   - Add search functionality for long option lists
   - Implement "Select All/None" options

## Configuration Examples

### Nerdalytics DataFrame Configuration

```python
config = {
    "channel_title": {
        "type": "multiselect",
        "label": "Channel",
        "default": [],
        "extra_params": {"sort": True}
    },
    "video_type": {
        "type": "segmented",
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
```

### Playlist DataFrame Configuration

```python
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
        "depends_on": "playlist_channel_title",  # Cascading dependency
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
```


### Extra - prompts used to diagnosticate :

@filter_manager_v2.py implements a reusable filter element documented in the @filter_manager_v2_docs.md

I need to fix a bug that is afecting multiple functionalities that seems to be related to how Streamlit handles Widgets, reruns, Session and how the @FilterManager was implemented.

It's affecting the widgets behavior with "ghost clicks" that sometimes seems that you have added a element to a filter ( ie: choosed one channel to filter ) and when you try to add the 2nd it fails (doesnt add at all , closing and without errors). Sometimes the 1st click closes the widget that is a multiselect, sometimes works and I've seen the unexpected behavior happen  in the 1st or 2nd click in the same widget in different cases.

Due to many changes in the Streamlit widgets, reset filters that need to keep the state and clean filters, It's becoming clear it's a underlying issue ( not specific to a single ST widget ) that is hard to understand or fix.

Please inspect carefully the code, review the latest streamlit documentation @webhttps://docs.streamlit.io/develop/api-reference
to help find the root cause and propose strategies to fix ?

Aditional information :
- I am using Streamlit server version 1.45.1 installed via pip and run in a DevContainer on Debian 12 bookworm.
- I have changed the following  Streamlit server config.toml without any effects on the bug in [runner] :
    - enforceSerializableSessionState
    - fastReruns
Each one tested on  true / false without impact.  Currently both false.
