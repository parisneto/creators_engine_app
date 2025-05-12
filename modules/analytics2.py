"""
# 2025-05-06: Initial scaffolding for analytics2 page with six sections (Big numbers, Metadata, SEO+, Correlações, Playlists, Slope)
# Structure based on playlists.py, with shared imports and page framework.
# Data loading only: df_nerdalytics, df_slope_full, df_playlist_full_dedup via load_data.
"""
import gc
import streamlit as st
import pandas as pd
from utils.page_framework import render_page
from utils.dataloader import load_data

# Import all section modules
from modules.blocks.analytics2_section1 import analytics2_section1
from modules.blocks.analytics2_section2 import analytics2_section2
from modules.blocks.analytics2_section3 import analytics2_section3
from modules.blocks.analytics2_section4 import analytics2_section4
from modules.blocks.analytics2_section5 import analytics2_section5
from modules.blocks.analytics2_section6 import analytics2_section6

# Set to True to show debug information
# DEBUG = True
DEBUG = False

# Configurable Block List
PAGE_BLOCKS = [
    {"name": "Playlist Playground", "func": analytics2_section1},
    {"name": "Metadata", "func": analytics2_section2},
    {"name": "Radar Charts", "func": analytics2_section3},
    {"name": "Correlações", "func": analytics2_section4},
    {"name": "Playlists", "func": analytics2_section5},
    {"name": "Slope", "func": analytics2_section6},
]

# --- FILTER HEADER LOGIC (namespaced, modular, robust) ---
FILTER_NAMESPACE = "analytics2_filters"

# Default filter values (update as needed for your actual filter fields)
FILTER_DEFAULTS = {
    "channel": [],
    "video_type": [],
    "language": [],
}

def init_filter_state():
    """Initialize analytics2 filter state with defaults if not already set."""
    if FILTER_NAMESPACE not in st.session_state:
        st.session_state[FILTER_NAMESPACE] = FILTER_DEFAULTS.copy()

def reset_filters():
    """Reset analytics2 filters to defaults."""
    st.session_state[FILTER_NAMESPACE] = FILTER_DEFAULTS.copy()


def analytics2_filter_header(df_nerdalytics):
    """Shared filter header for analytics2 page. Only handles persistence and display, not actual filtering."""
    init_filter_state()
    filters = st.session_state[FILTER_NAMESPACE]

    with st.popover("🎯 Future Filters", use_container_width=True):
                        # st.subheader("Playlist Filters")
                        # col1, col2, col3 = st.columns(3)
                        # with col1:
                        #     filters["channel"] = st.multiselect(
                        #         "Filter by Channel",
                        #         options=df_nerdalytics["channel_title"].unique(),
                        #         default=filters["channel"],
                        #         key=f"{FILTER_NAMESPACE}_channel"
                        #     )
                        # with col2:
                        #     filters["video_type"] = st.multiselect(
                        #         "Filter by Type",
                        #         options=df_nerdalytics["video_type"].unique(),
                        #         default=filters["video_type"],
                        #         key=f"{FILTER_NAMESPACE}_video_type"
                        #     )
                        # with col3:
                        #     filters["language"] = st.multiselect(
                        #         "Filter by Language",
                        #         options=df_nerdalytics["default_audio_language"].unique(),
                        #         default=filters["language"],
                        #         key=f"{FILTER_NAMESPACE}_language"
                        #     )
        st.button("Reset Filters", on_click=reset_filters, key=f"{FILTER_NAMESPACE}_reset_top")

    # Single-line summary for active filters
    summary_parts = []
    if filters["channel"]:
        summary_parts.append(f"Channel: {', '.join(filters['channel'])}")
    if filters["video_type"]:
        summary_parts.append(f"Type: {', '.join(filters['video_type'])}")
    if filters["language"]:
        summary_parts.append(f"Language: {', '.join(filters['language'])}")
    summary = " | ".join(summary_parts) if summary_parts else "No filters selected."
    st.markdown(f"**Active filters:** {summary}")

def render():
    """
    Main entrypoint for the analytics2 page. Loads required data and renders each section block.
    """
    # Data loading only (no filters or joins yet)
    df_nerdalytics = load_data("tbl_nerdalytics")
    # df_slope_full = load_data("tbl_slope_full")
    df_playlist_full_dedup = load_data("tbl_playlist_full_dedup")

    with st.popover("🎯 DataFrames", use_container_width=True):
        st.write(" dataframes loaded (shape)")
        st.write("df_nerdalytics : ", df_nerdalytics.shape)
        # st.write("df_slope_full : ", df_slope_full.shape)
        st.write("df_playlist_full_dedup : ", df_playlist_full_dedup.shape)
        st.button("Reset Cache", on_click=st.cache_data.clear)
        st.button("Reset Filters", on_click=reset_filters, key=f"{FILTER_NAMESPACE}_reset")
        st.button("🔄 Force GC", on_click=gc.collect)
    # st.title("Analytics2 home page Title ")

    # --- SHARED FILTER HEADER ---
    analytics2_filter_header(df_nerdalytics)

    # Create tabs for each PAGE_BLOCKS entry
    section_tabs = st.tabs([block["name"] for block in PAGE_BLOCKS])

    # Render each section block in its corresponding tab
    for idx, block in enumerate(PAGE_BLOCKS):
        with section_tabs[idx]:
            st.header(block["name"])
            block["func"](df_nerdalytics, df_playlist_full_dedup)

    # check for the content in analytics2_section1-6 .py files in blocks folder.


if __name__ == "__main__":
    render()
