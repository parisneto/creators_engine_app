import streamlit as st

from modules.blocks.dstories_play1 import render as render_dstories1
from modules.blocks.dstories_play2 import render as render_dstories2
from utils.dataloader import load_data
from utils.filter_manager_v2 import FilterManager, create_filter_config

# Configurable Block List
PAGE_BLOCKS = [
    {"name": "Playlist Overview", "func": render_dstories1},
    {"name": "Playlist Analysis", "func": render_dstories2},
]


def render():
    """
    Main entrypoint for Playlist Data Stories page. Loads required data and renders each section block.
    """
    # Load DataFrame (single df per page)
    df_playlist = load_data("tbl_playlist_full_dedup")

    # Set up FilterManager with configuration for this DataFrame
    filter_config = create_filter_config("tbl_playlist_full_dedup", df_playlist)
    filter_manager = FilterManager("datastories_playlist", "df_playlist", filter_config)

    # Render filter popover and summary
    with st.popover("\U0001f50d Filtros Do Datalake", use_container_width=True):
        filter_manager.render_filters(df_playlist)
    filter_manager.render_filter_summary()

    # Apply filters to main df
    filtered_df = filter_manager.apply_filters(df_playlist)

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
        # Show debug info
        with st.expander("Debug Info"):
            st.json(st.session_state)
            st.divider()
            st.code(filtered_df.columns)
            st.dataframe(
                filtered_df[["video_added_at", "playlist_published_at"]].head(10)
            )

        # Tab navigation for subpages with filtered data
        section_tabs = st.tabs([block["name"] for block in PAGE_BLOCKS])
        for idx, block in enumerate(PAGE_BLOCKS):
            with section_tabs[idx]:
                # st.write(block["name"]) ( repeated  from tabs title - not needed)
                block["func"](filtered_df)


if __name__ == "__main__":
    render()
