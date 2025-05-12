#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# 2024-04-22: Added user email to sidebar footer
# 2024-04-22: Created sidebar component with debug info toggle
"""

import streamlit as st
import platform
from datetime import datetime
from utils.auth import SHOW_DEBUG_INFO, DEV_USER_EMAIL, get_iap_header, extract_email_from_iap
from components.navigation import render_navigation
from utils.google_tag_manager import inject_gtm


def render_sidebar(navigation_options):
    """
    Renders the application sidebar with logo, user information, and optional debug information
    """
    # # Inject GTM script
    inject_gtm()

    # === Step 1: Add logo and title ===
    with st.sidebar:
        # Logo using st.image
        # st.image("img/logo.png", width=120)
        # st.title("Creators Engine IA")

        # Add divider for visual separation
        # st.divider()

        # === Step 2: Add navigation buttons here ===
        nav_active = st.session_state.get("nav_active", "home")
        selected = render_navigation(
            navigation_options,
            active_page=nav_active,
            on_change=lambda key: st.session_state.update({"nav_active": key})
        )

        if selected != nav_active:
            st.session_state["nav_active"] = selected
        st.image("img/logo.png", width=120)
        # === Step 3: Show user information ===
        if st.session_state.get("authenticated", False):
            user_email = st.session_state.get("user_email", "Usuário não identificado")
            st.info(f"👤 Usuário: {user_email}")

            # Show development mode indicator if applicable
            if st.session_state.get("is_dev_mode", False):
                st.warning("⚠️ Modo: Compartilhamento de Usuário")

        # Add divider at the bottom of sidebar
        st.divider()

        # === Step 4: Show debug information if enabled ===
        if SHOW_DEBUG_INFO:
            with st.sidebar.expander("🔍 Debug Info", expanded=False):
                # System information
                st.write("**Sistema**")
                st.text(f"OS: {platform.system()} {platform.release()}")
                st.text(f"Python: {platform.python_version()}")
                st.text(f"Streamlit: {st.__version__}")

                # Date and time information
                st.write("**Data e Hora**")
                now = datetime.now()
                st.text(f"Data: {now.strftime('%d/%m/%Y')}")
                st.text(f"Hora: {now.strftime('%H:%M:%S')}")

                # Authentication information
                st.write("**Autenticação**")
                raw_email, _, method_used = get_iap_header()
                email = extract_email_from_iap(raw_email)

                auth_state = {
                    "Auth": st.session_state.get("authenticated", False),
                    "Dev": st.session_state.get("is_dev_mode", False),
                    "Email": email or "Não encontrado",
                    "Headers": method_used,
                    "IAP Header": raw_email
                }

                for key, value in auth_state.items():
                    st.text(f"{key}: {value}")

        # === Step 5: Add footer with version information ===
        if st.session_state.get("authenticated", False):
            user_email = st.session_state.get("user_email", "Usuário não identificado")
            st.caption(f"{user_email}")

        st.caption("Creators Engine IA v2.1.9 t15")
        st.caption("2025 ©️ CreatorsEngine.com.br")