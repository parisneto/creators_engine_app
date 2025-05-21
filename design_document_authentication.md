## 7. Authentication

Authentication is managed by the `utils/auth.py` module and is enforced by the `require_auth()` function called at the start of `main.py`. The system supports multiple authentication methods depending on the environment:

### Authentication Mechanisms

1.  **Google Cloud Identity-Aware Proxy (IAP) (Primary):**
    *   In a production environment, the application expects to be fronted by Google Cloud's IAP.
    *   It checks for the `X-Goog-Authenticated-User-Email` HTTP header. If present, the email from this header is extracted (after stripping any "accounts.google.com:" prefix) and used to identify the authenticated user.
    *   The `get_iap_header()` function attempts to retrieve this header using `st.context.headers` (for newer Streamlit versions) or falls back to `get_script_run_ctx()` (for older Streamlit versions).

2.  **Fallback Password Authentication:**
    *   If the IAP header is not detected (e.g., during local development, if IAP is misconfigured, or if the app is accessed directly without IAP), a fallback password mechanism is triggered.
    *   A predefined password, stored in the `FALLBACK_PASSWORD` variable (current value: "yta"), must be entered by the user.
    *   The entered password is then hashed using `hash_password()` (which employs SHA-256) and compared against the hashed `FALLBACK_PASSWORD`.
    *   Upon successful password entry, the user is treated as authenticated. Their email is set to a default development email, `DEV_USER_EMAIL` (current value: "manolo@creatorsengine.com.br").
    *   The application displays a warning message if it expects IAP but doesn't find the necessary headers, guiding administrators on potential misconfigurations.

3.  **Development Mode Bypass (`APPMODE == "DEV"`):**
    *   If the `APPMODE` environment variable is set to `"DEV"`, the `require_auth()` function bypasses both IAP and password checks.
    *   The application automatically authenticates the user with the `DEV_USER_EMAIL` and sets the `is_dev_mode` flag in the session state to `True`. This facilitates a streamlined development experience.

4.  **URL Token Authentication:**
    *   After a successful fallback password authentication, a hash of the `FALLBACK_PASSWORD` (obtained via `get_password_hash()`) is set as an `auth` token in the URL query parameters (e.g., `/?auth=<hashed_password>`).
    *   If this valid `auth` token is present in the URL on subsequent visits or page reloads (and IAP is not active), the `check_url_token()` function validates it. If valid, the user is automatically authenticated using the `DEV_USER_EMAIL`. This provides a basic form of session persistence for the fallback authentication method, preventing users from having to re-enter the password on every page load.

### Session Management

*   Streamlit's session state (`st.session_state`) is used to manage the authentication status and user information throughout the user's session:
    *   `st.session_state["authenticated"]`: A boolean flag indicating whether the user is currently authenticated.
    *   `st.session_state["is_dev_mode"]`: A boolean flag indicating if the session is running in development mode (either `APPMODE == "DEV"` or after fallback password authentication).
    *   `st.session_state["user_email"]`: Stores the email address of the authenticated user.
*   The `init_session_state()` function is responsible for initializing these session state variables at the beginning of a session. It also calls `check_url_token()` to see if an existing valid token can authenticate the session.

### Enforcement

*   The `require_auth()` function is called at the very beginning of the `main()` function in `main.py`.
*   This function orchestrates the authentication process:
    *   It first initializes the session state.
    *   It then checks for `APPMODE == "DEV"`.
    *   If not in DEV mode, it attempts to authenticate via IAP.
    *   If IAP fails or is not present, it checks for a URL token.
    *   If none of the above methods result in authentication, it presents the fallback password login form using `login_form()`.
*   If authentication is not successfully established through any of these means, the application effectively halts further execution by not rendering the main content (due to `st.stop()` within `login_form` or by `require_auth` not setting `st.session_state["authenticated"]` to `True`).

### Debugging

*   The `SHOW_DEBUG_INFO` boolean variable in `utils/auth.py` (defaults to `False`) can be set to `True` to enable the display of debugging information.
*   When enabled, this will show details such as the presence and content of IAP headers, the email address extracted, and the method used to retrieve the headers. This is valuable for diagnosing issues with IAP integration or other authentication flows. The debug information is typically displayed in an expander in the UI.
