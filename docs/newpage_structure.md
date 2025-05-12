# Template Data Page Architecture

This document outlines the architecture for creating new data pages using the template pattern. Follow these guidelines to create consistent, efficient, and maintainable data pages.

## 1. Core Components

### 1.1 Enhanced Data Loader (`data/dataloader.py`)

- Uses `@st.cache_resource(ttl='1d')` for base data loading
- Loads parquet files once per container start
- Performs all permanent preprocessing (type fixes, joins, computed columns)
- Returns immutable dataframes (DO NOT mutate later)

```python
# Example implementation - enhanced load_data
@st.cache_resource(ttl='1d')
def load_base_data():
    """
    Load all base dataframes with standard preprocessing.
    Returns a dictionary of clean DataFrames.
    """
    # Load raw data
    df_nerdalytics = read_parquet_local(PARQUET_TABLES["tbl_nerdalytics"])
    df_playlist_full_dedup = read_parquet_local(PARQUET_TABLES["tbl_playlist_full_dedup"])

    # Apply standard preprocessing
    # (type fixes, standard joins, common computed columns)

    return {
        "tbl_nerdalytics": df_nerdalytics,
        "tbl_playlist_full_dedup": df_playlist_full_dedup,
        # Add other dataframes as needed
    }
```

### 1.2 User-Level Data Manager
<!-- (`utils/user_data_manager.py`) DO not implement this externally yet it is locally per main page. -->

- Uses `@st.cache_data(ttl='15m')` for per-user data
- Gets filtered copies of base dataframes
- Handles expensive per-user derivations (group-bys, stats)
- Always uses `.copy()` before mutating

```python
# Example implementation - user data manager
@st.cache_data(ttl='15m')
def get_user_dataframe(df_name, filters=None):
    """Get a filtered copy of a base dataframe."""
    # Get base dataframe
    base_dfs = load_base_data()
    if df_name not in base_dfs:
        return None

    # Create a copy for user-level operations
    df = base_dfs[df_name].copy()

    # Apply filters if provided
    if filters:
        df = apply_filters(df, filters)

    return df
```

### 1.3 Filter Manager (`utils/filter_manager.py`)

- Knows which dataframes are being used
- Has standard layouts for each dataframe type
- Handles session persistence with page-unique namespaces
- Each page declares a main dataframe for filtering

```python
# Example implementation - filter manager
class FilterManager:
    def __init__(self, page_id, main_df_name):
        self.page_id = page_id
        self.main_df_name = main_df_name
        self.namespace = f"filters_{page_id}"
        self.init_filter_state()

    def init_filter_state(self):
        """Initialize filter state if not already set."""
        if self.namespace not in st.session_state:
            st.session_state[self.namespace] = {}

    def render_filters(self, dataframe):
        """Render filters for the main dataframe."""
        # Standard filter layouts based on df_name
        # Returns the current filter state
        pass

    def get_filter_state(self):
        """Get current filter state."""
        return st.session_state[self.namespace]
```

## 2. Template Data Page Structure

### 2.1 Main Page (`modules/templatedatapage.py`)

```python
# Example template data page
class TemplateDataPage:
    def __init__(self, page_id, title, main_df_name, blocks=None):
        self.page_id = page_id
        self.title = title
        self.main_df_name = main_df_name
        self.blocks = blocks or []
        self.filter_manager = FilterManager(page_id, main_df_name)

    def render(self):
        """Render the main page."""
        st.title(self.title)

        # Get main dataframe
        main_df = get_user_dataframe(self.main_df_name)

        # Render filters in popover
        with st.popover("🎯 Filters", use_container_width=True):
            self.filter_manager.render_filters(main_df)

        # Show filter summary
        filter_state = self.filter_manager.get_filter_state()
        self._render_filter_summary(filter_state)

        # Create tabs
        tabs = st.tabs([block["name"] for block in self.blocks])

        # Render blocks
        for i, block in enumerate(self.blocks):
            with tabs[i]:
                block["func"](main_df, self.filter_manager)

    def _render_filter_summary(self, filter_state):
        """Render summary of active filters."""
        # Compact display of active filters
        pass
```

### 2.2 Block Template (`modules/blocks/template_block.py`)

```python
# Example template block
def template_block(main_df, filter_manager):
    """
    Template block for data visualization.

    Args:
        main_df: The main dataframe for this page
        filter_manager: The filter manager for this page
    """
    st.header("Block Title")

    # Get any additional dataframes needed (with local filtering if required)
    # additional_df = get_user_dataframe("another_table")

    # Visualize data
    # ...
```

## 3. Filtering Rules

1. Each page declares a main dataframe that determines primary filter options
2. Filters are specific to each page (using page_id namespace)
3. Standard filters are provided for common dataframe types
4. Filter UI is presented in a popover element
5. Filter state is persisted in session state
6. Filter summary is displayed below the filter popover
7. Advanced filtering for secondary dataframes is handled locally in blocks

## 4. Using the Template

To create a new data page:

1. Define your blocks in `modules/blocks/`
2. Create your page in `modules/your_page.py`
3. Initialize with a unique page_id, title, main_df_name
4. Add your blocks to the blocks list
5. Call render() to display the page

Example:

```python
# modules/your_page.py
from modules.templatedatapage import TemplateDataPage
from modules.blocks.your_block1 import your_block1
from modules.blocks.your_block2 import your_block2

def create_your_page():
    page = TemplateDataPage(
        page_id="your_page",
        title="Your Data Page",
        main_df_name="tbl_nerdalytics",
        blocks=[
            {"name": "First Analysis", "func": your_block1},
            {"name": "Second Analysis", "func": your_block2},
        ]
    )
    page.render()

if __name__ == "__main__":
    create_your_page()
```

## 5. Memory Management

1. Base dataframes are loaded once per container (st.cache_resource)
2. User dataframes are cached for 15 minutes (st.cache_data)
3. Always use .copy() before modifying dataframes
4. Reset cache explicitly when new data is loaded
5. Use the Force GC button for memory debugging

## 6. Implementation Steps

1. **First Phase**:
   - Create `utils/user_data_manager.py`
   - Enhance `data/dataloader.py` with cache_resource
   - Create `utils/filter_manager.py`
   - Create `modules/templatedatapage.py`

2. **Second Phase**:
   - Create example blocks in `modules/blocks/template_blocks.py`
   - Create an example page using the template
   - Test integration with existing data structures

3. **Final Phase**:
   - Update filtering rules in `.windsurf.yml`
   - Add documentation with example usage
   - Refactor existing pages to use the template (optional)

## 7. Filtering Rules for `.windsurf.yml`

```yaml
filtering:
  rules:
    - Each page declares a main dataframe which determines the primary filter options
    - Filters are namespaced by page_id to prevent cross-page conflicts
    - Standard filter layouts are provided for common dataframe types
    - Filters are presented in a popover element with clear labels
    - Filter state is persisted in session state using the page_id namespace
    - Filter summary is displayed below the filter popover for visibility
    - Additional dataframes used in a page can have local filtering logic if needed
    ```