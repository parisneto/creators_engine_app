import streamlit as st
import pandas as pd
import gc
import logging
from utils.dataloader import get_user_dataframe
from utils.filter_manager import FilterManager

# Import individual block functions
from modules.blocks.template_nerdalytics_block import template_nerdalytics_block
from modules.blocks.template_slope_block import template_slope_block
from modules.blocks.template_playlist_block import template_playlist_block

logger = logging.getLogger(__name__)

class TemplateDataPage:
    """
    Template for data pages with standardized layout, filtering, and tab navigation.
    Each page declares a main dataframe and can have multiple blocks (subpages).
    """

    def __init__(self, page_id, title, main_df_name, blocks=None):
        """
        Initialize the template data page.

        Args:
            page_id: Unique identifier for the page
            title: Page title
            main_df_name: Name of the main dataframe for this page
            blocks: List of block dictionaries with "name" and "func" keys
        """
        self.page_id = page_id
        self.title = title
        self.main_df_name = main_df_name
        self.blocks = blocks or []
        self.filter_manager = FilterManager(page_id, main_df_name)


    cache_tip = """
    streamlit.runtime.caching.cache_errors.UnhashableParamError: Cannot hash argument 'self' (of type modules.templatedatapage.TemplateDataPage) in '_get_filtered_dataframe'.
    To address this, you can tell Streamlit not to hash this argument by adding a leading underscore to the argument's name in the function signature:
    @st.cache_data
    def _get_filtered_dataframe(_self, ...):
        ..."""


    # Fix the caching issue by adding underscore to self parameter
    @st.cache_data(ttl='15m')
    def _get_filtered_dataframe(_self, df_name, filters):
        """
        Get a filtered copy of a dataframe.

        Args:
            df_name: Name of the dataframe to filter
            filters: Filter state dictionary

        Returns:
            Filtered dataframe
        """
        # Get the base dataframe
        df = get_user_dataframe(df_name)
        if df is None:
            return None

        # Apply filters
        if filters:
            # Create a filter manager just for applying filters (not for UI)
            temp_filter_manager = FilterManager(f"{_self.page_id}_temp", df_name)
            # Set the filter state manually
            st.session_state[temp_filter_manager.namespace] = filters
            # Apply filters
            df = temp_filter_manager.apply_filters(df)

        return df

    def get_dataframe(self, df_name=None):
        """
        Get a dataframe by name, using the main dataframe if none specified.

        Args:
            df_name: Name of the dataframe to get (defaults to main_df_name)

        Returns:
            The requested dataframe
        """
        df_name = df_name or self.main_df_name

        # Get the current filter state
        filters = self.filter_manager.get_filter_state()

        # Get the filtered dataframe
        return self._get_filtered_dataframe(df_name, filters)

    def render_dataframe_info(self):
        """Render information about available dataframes."""
        with st.popover("🎯 DataFrames", use_container_width=True):
            # Get main dataframe
            main_df = get_user_dataframe(self.main_df_name)
            if main_df is not None:
                st.write(f"{self.main_df_name}: {main_df.shape}")

            # Add buttons for cache management
            col1, col2 = st.columns(2)
            with col1:
                st.button("Reset Cache", on_click=st.cache_data.clear)
            with col2:
                st.button("🔄 Force GC", on_click=gc.collect)

    def _render(self):
        """Internal render method for the page."""
        # Set page title
        st.title(self.title)

        # Render dataframe info
        self.render_dataframe_info()

        # Get main dataframe
        main_df = get_user_dataframe(self.main_df_name)

        if main_df is None:
            st.error(f"Could not load main dataframe: {self.main_df_name}")
            return

        # Render filters in popover
        with st.popover("🎯 Filters", use_container_width=True):
            self.filter_manager.render_filters(main_df)

        # Show filter summary
        self.filter_manager.render_filter_summary()

        # If no blocks, show a message
        if not self.blocks:
            st.info("No blocks defined for this page.")
            return

        # Create tabs for each block
        tabs = st.tabs([block["name"] for block in self.blocks])

        # Get filtered dataframe
        filtered_df = self.get_dataframe()

        # Render blocks
        for i, block in enumerate(self.blocks):
            with tabs[i]:
                st.header(block["name"])
                block["func"](filtered_df, self.filter_manager)


def create_template_page():
    """Create and render a template data page."""
    page = TemplateDataPage(
        page_id="template_example",
        title="Template Data Page Example",
        main_df_name="tbl_nerdalytics",
        blocks=[
            {"name": "Nerdalytics", "func": template_nerdalytics_block},
            {"name": "Slope Data", "func": template_slope_block},
            {"name": "Playlists", "func": template_playlist_block},
        ]
    )
    page._render()


# Required for project navigation
def render():
    """Main entry point for the page, required by the navigation system."""
    create_template_page()


if __name__ == "__main__":
    render()
