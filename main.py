#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# 2024-04-22: Added authentication requirement before rendering content
# 2024-04-19: Added configuration to disable debug info in sidebar
# 2024-04-19: Updated navigation options to use "Creators Engine IA" instead of "Computer Vision AI"
# 2024-04-14: Fixed image paths and improved navigation
# 2024-03-27: Aplicativo principal do MDM Vision AI

"""

# =================================================================
# TIMEOUT CONFIG (added 2024-04-26)
# =================================================================
SHOW_TIMEOUT_COUNTDOWN = True  # Set to False to hide countdown in sidebar
INACTIVITY_TIMEOUT_SECONDS = 60  # 1 minute for testing
TIMEOUT_REDIRECT_URL = "https://creatorsengine.com.br/timeout"

# =================================================================
# CONFIGURAÇÃO DO APLICATIVO
# =================================================================
from utils.auth import SHOW_DEBUG_INFO, require_auth

# =================================================================
# IMPORTS
# =================================================================
import streamlit as st
import importlib
from config.pages import PAGE_CONFIG
from components.navigation import render_navigation
from components.sidebar import render_sidebar
from utils.google_tag_manager import inject_gtm

# =================================================================
# CONFIGURAÇÃO DA PÁGINA
# =================================================================
st.set_page_config(
    page_title="Creators Engine IA - Lab",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================================
# OPÇÕES DE NAVEGAÇÃO
# =================================================================
# Build NAVIGATION_OPTIONS from config
NAVIGATION_OPTIONS = [
    (display, icon, key)
    for key, (display, icon, _) in PAGE_CONFIG.items()
]

# =================================================================
# FUNÇÃO PRINCIPAL
# =================================================================
def main():
    """
    Função principal que renderiza o aplicativo completo
    """
    # Inject GTM script
    # inject_gtm() - FAILED HERE.

    # Requer autenticação antes de prosseguir
    user_email = require_auth()

    # Se chegamos aqui, o usuário está autenticado
    # Renderiza a sidebar com as opções de navegação
    render_sidebar(NAVIGATION_OPTIONS)



    # Renderiza o conteúdo adequado com base na navegação ativa
    nav_active = st.session_state.get("nav_active", "home")
    module_name = PAGE_CONFIG.get(nav_active, PAGE_CONFIG["home"])[2]
    page_module = importlib.import_module(module_name)
    page_module.render()


    #TODO: TEST check to migrate here     # Inject GTM script    inject_gtm()

# =================================================================
# EXECUÇÃO PRINCIPAL
# =================================================================
if __name__ == "__main__":
    # Inicializa variáveis de estado de navegação se não existirem
    if "nav_active" not in st.session_state:
        st.session_state["nav_active"] = "home"

    # Executa  o aplicativo
    main()