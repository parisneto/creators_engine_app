#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# 2024-04-22: Fixed authentication to always require password when IAP is not present
# 2024-04-22: Fixed password authentication to always show login form when no IAP header is found
# 2024-04-22: Simplified auth to only use X-Goog-Authenticated-User-Email header
# 2024-04-19: Fixed IAP authentication to correctly extract email with prefix
# 2024-04-19: Added configuration option to control debug info display
# 2024-04-19: Added compatibility for older Streamlit versions without st.context
# 2024-04-19: Simplified header access to directly use st.context.headers
# 2024-04-19: Fixed authentication logic to ensure password is requested when no IAP header is found
# 2024-04-19: Simplified authentication to use st.context.headers with proper IAP header
# 2024-04-19: Added auto-fallback to dev mode when running in production with no IAP headers
# 2024-04-19: Added validation for experimental_user email to prevent incorrect authentication
# 2024-04-19: Updated query string email example to use DEV_USER_EMAIL
# 2024-04-14: Fixed headers access method to use get_script_run_ctx
# 2024-03-27: Utilitário de autenticação com IAP e senha de fallback
"""

import streamlit as st
import json
import base64
import hashlib
import os
from utils.google_tag_manager import inject_gtm
# Fallback - for older Streamlit versions
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
except ImportError:
    # Older versions of Streamlit have a different import path
    try:
        from streamlit.script_run_context import get_script_run_ctx
    except ImportError:
        # For very old versions, create a dummy function
        def get_script_run_ctx():
            return None

# Senha de fallback para desenvolvimento
FALLBACK_PASSWORD = "yta"

# Email padrão para modo de desenvolvimento
DEV_USER_EMAIL = "manolo@creatorsengine.com.br"

# Nome do cookie para armazenar estado de autenticação
AUTH_COOKIE_NAME = "mdm_auth_state"

# IAP header para email do usuário
IAP_EMAIL_HEADER = "X-Goog-Authenticated-User-Email"

# Configuração para exibir/ocultar debug info
SHOW_DEBUG_INFO = False  # False  # Pode ser modificado via código


def get_password_hash():
    """Generate a hash of the fallback password"""
    return hashlib.sha256(FALLBACK_PASSWORD.encode()).hexdigest()[:8]


def init_session_state():
    """Initialize session state variables if they don't exist"""
    if "authenticated" not in st.session_state:
        # Check URL parameters for auth token
        auth_token = st.query_params.get("auth")

        if auth_token and auth_token == get_password_hash():
            st.session_state["authenticated"] = True
            st.session_state["is_dev_mode"] = True
            st.session_state["user_email"] = DEV_USER_EMAIL
        else:
            st.session_state["authenticated"] = False
            st.session_state["is_dev_mode"] = False
            st.session_state["user_email"] = None



def get_iap_header():
    """
    Get IAP header using either st.context (new Streamlit) or
    get_script_run_ctx (older Streamlit)

    Returns:
        tuple: (raw_email, headers_dict, method_used)
    """
    # Try using modern st.context first (Streamlit 1.44.0+)
    if hasattr(st, 'context') and hasattr(st.context, 'headers'):
        try:
            raw_email = st.context.headers.get(IAP_EMAIL_HEADER, "")
            return raw_email, dict(st.context.headers), "st.context"
        except Exception as e:
            pass

    # Fallback to older method with get_script_run_ctx
    try:
        ctx = get_script_run_ctx()
        if ctx and hasattr(ctx, 'request') and hasattr(ctx.request, 'headers'):
            headers = ctx.request.headers
            raw_email = headers.get(IAP_EMAIL_HEADER, "")
            return raw_email, dict(headers), "get_script_run_ctx"
    except Exception as e:
        pass

    # Return empty values if all methods fail
    return "", {}, "none"


def extract_email_from_iap(raw_value):
    """
    Extract the email from the IAP header value, handling the prefix if present.

    Args:
        raw_value (str): Raw header value from IAP

    Returns:
        str: Extracted email
    """
    if not raw_value:
        return ""

    # IAP typically prefixes the email with "accounts.google.com:"
    if ":" in raw_value:
        return raw_value.split(":", 1)[1]

    return raw_value


def require_auth():
    """
    Verifica autenticação via IAP ou senha de fallback.
    Se não houver cabeçalho IAP, exige senha sempre.

    Returns:
        str: Email do usuário
    """
    # Check if in DEV mode
    from utils.config import APPMODE
    if APPMODE == "DEV":
        st.session_state["authenticated"] = True
        st.session_state["is_dev_mode"] = True
        st.session_state["user_email"] = DEV_USER_EMAIL
        return DEV_USER_EMAIL

    # Initialize session state
    init_session_state()

    # Get IAP headers using the appropriate method for this Streamlit version
    raw_email, all_headers, method_used = get_iap_header()

    # Extract actual email from IAP format
    email = extract_email_from_iap(raw_value=raw_email)

    if SHOW_DEBUG_INFO:
        st.caption(f"raw_email: {raw_email}\n email: {email}")
        st.json(all_headers)
        st.caption(f"method_used: {method_used}")
        st.caption(f"email: {email}")

    # CASE 1: IAP authentication is present - use it directly
    if email:
        st.session_state["authenticated"] = True
        st.session_state["is_dev_mode"] = False
        st.session_state["user_email"] = email
        return email

    # CASE 2: Authentication via URL param is present
    auth_token = st.query_params.get("auth")
    if auth_token and auth_token == get_password_hash():
        st.session_state["authenticated"] = True
        st.session_state["is_dev_mode"] = True
        st.session_state["user_email"] = DEV_USER_EMAIL
        return DEV_USER_EMAIL

    # CASE 3: No IAP or token - show password form
    # Reset authentication state to ensure form is shown
    st.session_state["authenticated"] = False
    st.session_state["is_dev_mode"] = False
    st.session_state["user_email"] = None

    # Display login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:

        # Inject GTM script
        inject_gtm()

        st.title("🔐 Login")
        st.subheader("v2.1.9 t15")
        st.markdown("---")

        # Warning about IAP if in production
        if True : # is_prod:
            st.warning("""
            ⚠️ Este aplicativo deve ser acessado via IAP, mas não foram detectados cabeçalhos de autenticação.

            Possíveis causas:
            - O IAP não está configurado corretamente
            - Existe um proxy ou serviço intermediário removendo os cabeçalhos
            - A aplicação está sendo acessada diretamente, sem passar pelo IAP
            """)

        password = st.text_input("Senha de acesso:", type="password", value="yta ")

        if password:
            if password == FALLBACK_PASSWORD:
                # Set auth token in URL
                st.query_params["auth"] = get_password_hash()

                st.session_state["authenticated"] = True
                st.session_state["is_dev_mode"] = True
                st.session_state["user_email"] = DEV_USER_EMAIL
                st.rerun()
            else:
                st.error("Senha incorreta!")
                st.stop()

    # If we got here without authenticating, stop execution
    st.stop()

    # This should never be reached, but just in case
    return None