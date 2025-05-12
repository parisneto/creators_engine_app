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
import streamlit as st
import subprocess, os
from typing import Callable, List, Dict
from utils.page_framework import render_page
from utils.dataretriever import main as dataretriever_main
from utils.auth import SHOW_DEBUG_INFO
from utils.dataloader import load_data
import gc
# ---- Example External Block Import ----
# from modules.blocks.hello_block import hello_block  # External block example
from modules.blocks.debugtools1 import debugtools1  # External block example
from modules.blocks.fileman import fileman  # External block example


# ---- Example Local Block Function ----
def intro_block():
    """A simple local block for demonstration."""
    st.header("Intro Block")
    st.write("This is a local block for Playlists")

    import  stat

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
            ["python", "utils/dataretriever.py"],
            capture_output=True,
            text=True
        )
        st.write("**Return code:**", result.returncode)
        st.write("**Stdout:**", result.stdout or "_(none)_")
        st.write("**Stderr:**", result.stderr or "_(none)_")
        st.write("**Local files now in**", DATA_DIR, ":", os.listdir(DATA_DIR))

    if  SHOW_DEBUG_INFO:
        st.divider()
        st.write("• CWD:", os.getcwd())
        st.write("• EXISTS:", os.path.exists(DATA_DIR))
        st.write("• IS DIR:", os.path.isdir(DATA_DIR))
        st.write("• PERMS:", oct(os.stat(DATA_DIR).st_mode)[-3:],
                    "(writable?)", os.access(DATA_DIR, os.W_OK))
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

    st.markdown("---")
    df_playlist_full_dedup = load_data("tbl_playlist_full_dedup")
    # Capture info() output as string using StringIO
    import io
    buffer = io.StringIO()
    df_playlist_full_dedup.info(buf=buffer)
    playlist_full_dedupinfo = buffer.getvalue()
    st.write("playlist_full_dedupinfo : ")
    st.code(playlist_full_dedupinfo, language="python")

def debugtools3():

    from utils.config import APPMODE

    st.header("APP MODE :")
    st.write("value : ", APPMODE)

    st.header("Debugtools3 Block")
    st.write("This is a local block for Debugtools3")

    st.subheader("Debian Version")
    process = subprocess.run(["cat", "/etc/debian_version"],
                            capture_output=True, text=True)
    st.code(process.stdout)
    st.subheader("OS Release")
    process = subprocess.run(["cat", "/etc/os-release"],
                            capture_output=True, text=True)
    st.code(process.stdout)

    st.subheader("System Info")
    process = subprocess.run(["uname", "-a"],
                            capture_output=True, text=True)
    st.code(process.stdout)



# ---- Configurable Block List ----
PAGE_BLOCKS: List[Dict[str, Callable]] = [
    {"name": "DataLoad", "func": intro_block},
    {"name": "File Manager", "func": fileman},
    {"name": "debugtools1", "func": debugtools1},
    {"name": "debugtools2", "func": debugtools2},
    {"name": "OS Version", "func": debugtools3},
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
