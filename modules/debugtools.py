"""
# 2025-04-30: Official page template for modular Streamlit navigation framework.
# Copy this file to create a new app page in /modules.

This template demonstrates:
- The required `def render():` entrypoint for Streamlit navigation integration.
- How to define local blocks (sections/tabs) as functions.
- How to import and use external blocks from /modules/blocks/.
- How to configure which blocks appear using PAGE_BLOCKS.
- How to use the shared navigation UI from /utils/page_framework.py.

To create a new page:
1. Copy this file to /modules/your_page_name.py
2. Edit the docstring and block functions as needed.
3. Add/remove blocks in PAGE_BLOCKS.
4. (Optional) Import shared data, filters, or external blocks as needed.
"""

import gc
import os
import subprocess
from datetime import datetime, timezone
from typing import Callable, Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st

# ---- Example External Block Import ----
# from modules.blocks.hello_block import hello_block  # External block example
from modules.blocks.debugtools1 import debugtools1  # External block example
from modules.blocks.debugtools3 import debugtools3  # Internal block example
from modules.blocks.debugtools4 import debugtools4  # Internal block example
from modules.blocks.fileman import fileman  # Internal block example
from utils.auth import SHOW_DEBUG_INFO
from utils.dataloader import load_data
from utils.dataretriever import main as dataretriever_main
from utils.page_framework import render_page


# ---- Example Local Block Function ----
def intro_block():
    """A simple local block for demonstration."""
    st.header("Intro Block")
    st.write("This is a local block for Playlists")

    DATA_DIR = "/app/data"

    # st.write("• CWD:", os.getcwd())
    # st.write("• EXISTS:", os.path.exists(DATA_DIR))
    # st.write("• IS DIR:", os.path.isdir(DATA_DIR))
    # st.write("• PERMS:", oct(os.stat(DATA_DIR).st_mode)[-3:],
    #         "(writable?)", os.access(DATA_DIR, os.W_OK))
    # st.write("• /app contents:", os.listdir("/app"))
    # st.write("• . (current directory) contents:", os.listdir("."))
    # st.write("• / (root) contents:", os.listdir("/"))
    # st.write("• This file path:", __file__)

    st.button("Reset Cache", on_click=st.cache_data.clear)
    st.button("🔄 Force GC", on_click=gc.collect)

    st.divider()

    st.error("DO NOT CLICK THIS:", icon="🚨")

    # DATA_DIR = "/app/data"  # match your downloader’s LOCAL_DATA_DIR

    if st.button("Run Data Retriever 2 (subprocess)"):
        result = subprocess.run(
            ["python", "utils/dataretriever.py"], capture_output=True, text=True
        )
        st.write("**Return code:**", result.returncode)
        st.write("**Stdout:**", result.stdout or "_(none)_")
        st.write("**Stderr:**", result.stderr or "_(none)_")
        st.write("**Local files now in**", DATA_DIR, ":", os.listdir(DATA_DIR))

    if SHOW_DEBUG_INFO:
        st.divider()
        st.write("• CWD:", os.getcwd())
        st.write("• EXISTS:", os.path.exists(DATA_DIR))
        st.write("• IS DIR:", os.path.isdir(DATA_DIR))
        st.write(
            "• PERMS:",
            oct(os.stat(DATA_DIR).st_mode)[-3:],
            "(writable?)",
            os.access(DATA_DIR, os.W_OK),
        )
        st.write("• /app contents:", os.listdir("/app"))

    st.divider()

    if st.button("Run Data Retriever (subprocess)"):
        subprocess.run(["python", "utils/dataretriever.py"])
        st.write("Data Retriever script executed via subprocess!")

    if st.button("Run Data Retriever (import)"):
        dataretriever_main()
        st.write("Data Retriever executed via import!")


# ---- Example Local Block Function ----
def debugtools2():
    """A simple local block for demonstration."""
    st.header("Debugtools2 Block")
    st.write("This is a local block for Debugtools2")
    st.divider()
    df_channels = load_data("tbl_channels")
    st.write("df_channels.shape : ", df_channels.shape)
    st.write("df_channels.columns : ")
    st.code(df_channels.columns.tolist())
    st.dataframe(df_channels)
    # st.divider()

    # st.write("df_channels_sample : ")
    # st.divider()

    # radar plot

    df_channels_sample = df_channels[
        [
            "snippet_custom_url",
            "channel_title",
            "description",
            "channel_custom_url",
            "view_count",
            "subscriber_count",
            "video_count",
            "country",
            "channel_id",
            "channel_published_at",
        ]
    ].copy()
    # st.code(df_channels_sample.columns.tolist())
    # st.dataframe(df_channels_sample)
    # st.divider()

    # Calculate years since published (1 decimal)
    now = datetime(2025, 5, 12, tzinfo=timezone.utc)
    df_channels_sample["channel_published_at"] = pd.to_datetime(
        df_channels_sample["channel_published_at"], utc=True, errors="coerce"
    )
    df_channels_sample["years_since_published"] = (
        (now - df_channels_sample["channel_published_at"]).dt.total_seconds()
        / (365.25 * 24 * 3600)
    ).round(1)

    # st.write("df_channels_sample : ")

    # st.dataframe(df_channels_sample)
    # import os
    # st.write("OS write  : ")
    # os.write(1,b'some text @@@@@@ $$$$$ %%%%%%')
    # os.write(1,df_channels_sample.to_string().encode('utf-8'))
    # console.log(df_channels_sample)
    st.divider()
    # Define metrics to normalize
    radar_metrics = [
        "view_count",
        "subscriber_count",
        "video_count",
        "years_since_published",
    ]

    # Min-max normalization
    df_norm = df_channels_sample.copy()
    for col in radar_metrics:
        min_val = df_norm[col].min()
        max_val = df_norm[col].max()
        if max_val > min_val:
            df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
        else:
            df_norm[col] = 0.0  # Handle constant columns

    # Melt the normalized dataframe
    df_radar = df_norm.melt(
        id_vars=["snippet_custom_url"],
        value_vars=radar_metrics,
        var_name="Metric",
        value_name="Value",
    )

    # Plot as before
    fig = px.line_polar(
        df_radar,
        r="Value",
        theta="Metric",
        color="snippet_custom_url",
        line_close=True,
        template="plotly_dark",
        markers=True,
    )
    fig.update_traces(fill="toself", opacity=0.4)
    fig.update_layout(
        title="Channel Metrics Radar Plot (Normalized)", legend_title_text="Channel"
    )
    st.plotly_chart(fig, use_container_width=True)

    # # Prepare data for radar plot
    # radar_metrics = ['view_count', 'subscriber_count', 'video_count', 'years_since_published']

    # # Melt the dataframe for plotly express
    # df_radar = df_channels_sample.melt(
    #     id_vars=['snippet_custom_url'],
    #     value_vars=radar_metrics,
    #     var_name='Metric',
    #     value_name='Value'
    # )

    # fig = px.line_polar(
    #     df_radar,
    #     r='Value',
    #     theta='Metric',
    #     color='snippet_custom_url',
    #     line_close=True,
    #     template='plotly_dark',
    #     markers=True
    # )
    # fig.update_traces(fill='toself', opacity=0.4)
    # fig.update_layout(title="Channel Metrics Radar Plot", legend_title_text='Channel')
    # st.plotly_chart(fig, use_container_width=True)


def debugtools5():
    from utils.config import APPMODE

    st.header("APP MODE :")
    st.write("value : ", APPMODE)

    st.header("Debugtools4 Block")
    st.write("This is a local block for Debugtools4")

    st.subheader("Debian Version")
    process = subprocess.run(
        ["cat", "/etc/debian_version"], capture_output=True, text=True
    )
    st.code(process.stdout)
    st.subheader("OS Release")
    process = subprocess.run(["cat", "/etc/os-release"], capture_output=True, text=True)
    st.code(process.stdout)

    st.subheader("System Info")
    process = subprocess.run(["uname", "-a"], capture_output=True, text=True)
    st.code(process.stdout)


def debugtools6():
    st.header("Debugtools6 Block")
    st.write("This is a local block for Debugtools6")

    st.title("Environment Variable Viewer")

    st.header("1. Displaying a Specific Environment Variable (OPENAI_API_KEY)")

    # Get a specific environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if openai_api_key:
        st.code(
            f"**OPENAI_API_KEY:** `{openai_api_key[:5]}...{openai_api_key[-5:]}`"
            # f"\n\n**OPENAI_API_KEY FULL:** `{openai_api_key}`"
            # f"\n\n**OPENAI_API_KEY len:** `{len(openai_api_key)}`"
        )  # Display partially for security
        st.info("Note: Only showing first/last 5 characters for security reasons.")
    else:
        st.warning("`OPENAI_API_KEY` is not set in the environment.")

    st.markdown("---")

    st.header("2. Displaying All Environment Variables")

    # Get all environment variables
    all_env_vars = os.environ

    if all_env_vars:
        st.write("### All Environment Variables (Sensitive data may be present!)")
        st.warning(
            "Caution: Displaying all environment variables can expose sensitive information. Use with care, especially in public deployments."
        )

        # Sort for better readability
        sorted_env_vars = sorted(all_env_vars.items())

        # You can choose how to display them:

        # Option A: As a dictionary (simple, but can be long)
        # st.json(dict(sorted_env_vars))

        # Create two columns for Key and Value
        col1, col2 = st.columns([1, 2])  # Adjust column ratio if needed

        # Write headers to columns
        with col1:
            st.markdown("**Key**")
            st.markdown("---")
        with col2:
            st.markdown("**Value**")
            st.markdown("---")

        # Populate columns with environment variables
        for key, value in sorted_env_vars:
            # For security, you might want to mask sensitive values like API keys
            display_value = value
            if (
                "API_KEY" in key.upper()
                or "PASSWORD" in key.upper()
                or "SECRET" in key.upper()
            ):
                display_value = (
                    f"{value[:3]}...{value[-3:]}" if len(value) > 6 else "***"
                )

            with col1:
                st.code(key, language="text")  # Use st.code for mono-spaced font
            with col2:
                st.code(display_value, language="text")
    else:
        st.info("No environment variables found.")

    st.markdown("---")
    st.caption(
        "Environment variables are typically set outside the Python script (e.g., in your shell, .env file, or deployment platform settings)."
    )


# ---- Configurable Block List ----
PAGE_BLOCKS: List[Dict[str, Callable]] = [
    {"name": "DataLoad", "func": intro_block},
    {"name": "File Manager", "func": fileman},
    {"name": "1 debugtools1", "func": debugtools1},
    {"name": "2 debugtools2", "func": debugtools2},
    {"name": "3 debugtools3", "func": debugtools3},
    {"name": "4 DF inspector", "func": debugtools4},
    {"name": "5 OS Version", "func": debugtools5},
    {"name": "6 Env Variables", "func": debugtools6},
]


# ---- Required Entrypoint ----
def render():
    """
    Main entrypoint for this page. All Streamlit UI should be inside this function.
    The navigation/sidebar will call this function to render the page content.
    """
    # st.title("Template Page Example")
    render_page(PAGE_BLOCKS)


if __name__ == "__main__":
    render()
