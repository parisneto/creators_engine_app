"""
Shared navigation/render logic for modular Streamlit pages.
Call render_page(blocks_config) from your page's render() function.
"""
import streamlit as st
from typing import List, Dict, Callable

def render_page(blocks_config: List[Dict[str, Callable]]):
    tab_names = [block["name"] for block in blocks_config]
    selected_tab = st.radio("Select Section", tab_names, horizontal=True, key="page_tab", label_visibility="collapsed")
    for block in blocks_config:
        if block["name"] == selected_tab:
            block["func"]()
            break
