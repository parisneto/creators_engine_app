#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# 2024-04-22: Added page query parameter handling
# 2024-04-14: Fixed button parameter to remove use_container_width
# 2024-03-27: Componente de navegação simplificado
"""

from urllib.parse import quote

import streamlit as st


def render_navigation(options, active_page=None, on_change=None):
    """
    Renderiza os botões de navegação na sidebar e gerencia query parameters.

    Args:
        options (list): Lista de tuplas (nome, ícone, chave)
        active_page (str): Página ativa atual
        on_change (callable): Função callback para mudança de página

    Returns:
        str: Página selecionada
    """
    selected = active_page

    # Check if we have a page in query params
    if "page" in st.query_params:
        page_param = st.query_params["page"]
        # Verify if it's a valid page
        valid_pages = [key for _, _, key in options]
        if page_param in valid_pages and page_param != active_page:
            selected = page_param
            if on_change:
                on_change(page_param)

    for name, icon, key in options:
        is_active = selected == key
        button_text = f"{icon} {name}"

        if st.sidebar.button(
            button_text, key=f"nav_{key}", type="primary" if is_active else "secondary"
        ):
            selected = key
            # Update query parameter when page changes
            st.query_params["page"] = quote(key)
            # st.experimental_set_query_params(page=key)
            if on_change:
                on_change(key)
                st.rerun()  # this fixes the issue with active button color

    # Ensure query parameter is always set
    if selected and "page" not in st.query_params:
        st.query_params["page"] = quote(selected)
    # st.rerun()
    return selected
