import streamlit as st

from modules.blocks.metadata_1 import render as render_metadata1
from modules.blocks.metadata_2 import render as render_metadata2
from modules.blocks.metadata_3 import render as render_metadata3
from modules.blocks.metadata_4 import render as render_metadata4
from modules.blocks.metadata_5 import render as render_metadata5
from utils.dataloader import load_data
from utils.filter_manager_v2 import FilterManager, create_filter_config

# Configurable Block List
PAGE_BLOCKS = [
    {"name": "Overview 1", "func": render_metadata1},
    {"name": "Metadata part 2", "func": render_metadata2},
    {"name": "Metadata part 3", "func": render_metadata3},
    {"name": "part 4", "func": render_metadata4},
    {"name": "part 5", "func": render_metadata5},
]


def render():
    """
    Main entrypoint for Data Stories page. Loads required data and renders each section block.
    """
    # Load DataFrame (single df per page)
    df_nerdalytics = load_data("tbl_nerdalytics")

    # Set up FilterManager with configuration for this DataFrame
    filter_config = create_filter_config("tbl_nerdalytics", df_nerdalytics)
    filter_manager = FilterManager("datastories", "df_nerdalytics", filter_config)

    # Render filter popover and summary
    with st.popover("\U0001f50d Metadada Filters", use_container_width=True):
        filter_manager.render_filters(df_nerdalytics)
    filter_manager.render_filter_summary()

    # Apply filters to main df
    filtered_df = filter_manager.apply_filters(df_nerdalytics)

    # Check if filtered dataframe is empty
    if filtered_df is None or filtered_df.empty:
        st.warning(
            "No data matches your current filter selections. Try adjusting your filters."
        )
        # Still show tabs but with empty dataframe
        section_tabs = st.tabs([block["name"] for block in PAGE_BLOCKS])
        for idx, block in enumerate(PAGE_BLOCKS):
            with section_tabs[idx]:
                st.warning(block["name"])
                st.info(
                    "No data available with current filters. Please adjust your filter selections."
                )
    else:
        # Tab navigation for subpages with filtered data
        section_tabs = st.tabs([block["name"] for block in PAGE_BLOCKS])
        for idx, block in enumerate(PAGE_BLOCKS):
            with section_tabs[idx]:
                # st.header(block["name"]) ( repeated  from tabs title - not needed)
                block["func"](filtered_df)


if __name__ == "__main__":
    render()
