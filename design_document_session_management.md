## 8. Session Management & State

The application leverages Streamlit's built-in session management capabilities, primarily through `st.session_state`, to maintain user-specific data and state across interactions and page navigations within a single session. This allows for a stateful user experience, where choices and data persist as users move between different parts of the application.

### Key Uses of `st.session_state`:

*   **Authentication Status:**
    *   As detailed in the "Authentication" section, `st.session_state` is fundamental for managing user authentication. It stores:
        *   `authenticated`: A boolean flag indicating if the user has successfully authenticated.
        *   `is_dev_mode`: A boolean flag set to `True` if the application is running in development mode (either `APPMODE == "DEV"` or after successful fallback password authentication).
        *   `user_email`: Stores the email address of the authenticated user, which is used for personalization and potentially for logging or API interactions (e.g., GCS caching in `thumbs_safe.py`).

*   **Navigation State:**
    *   The application tracks the currently active page or module using `st.session_state`.
    *   In `main.py`, the `nav_active_page` variable, derived from `st.query_params.get("page", [default_page])[0]`, determines which page to display.
    *   The navigation component (`components/navigation.py`) updates the URL query parameter `page` when a navigation button is clicked. Streamlit's architecture ensures that changes to `st.query_params` can trigger reruns and update the `nav_active_page` effectively, reflecting the current view. `st.session_state` might be used internally by components or for more complex navigation logic if needed, but the primary mechanism observed is via URL query parameters.

*   **User Inputs and Intermediate Data:**
    *   Various modules utilize `st.session_state` to temporarily store data related to user inputs, selections, or the results of intermediate processing steps. This is crucial for multi-step operations or for preserving state within a page across reruns.
    *   For example, in `modules/thumbs_safe.py`:
        *   `st.session_state.image_content`: Stores the byte content of an image that a user has uploaded or that has been fetched from a URL.
        *   `st.session_state.analysis_results`: Holds the structured results obtained from Google Cloud Vision and OpenAI Moderation APIs after analyzing a thumbnail.
        *   `st.session_state.selected_input_method`: Tracks the user's chosen method for providing a thumbnail (e.g., "Upload", "URL", "YouTube ID").
        *   Other session state keys like `st.session_state.yt_video_id`, `st.session_state.image_url` store the respective user inputs.

*   **Filter States:**
    *   Interactive data filtering is a core feature, and `st.session_state` is essential for managing the state of these filters.
    *   The `utils/filter_manager_v2.py` (and its predecessor `utils/filter_manager.py`) extensively use `st.session_state` to store the current filter values for different DataFrames. These managers often create namespaced keys within `st.session_state` (e.g., using the `page_id` or a specific namespace string) to prevent collisions between filter sets used on different pages or for different datasets.
    *   Modules like `modules/analytics2.py` explicitly define a `FILTER_NAMESPACE` (e.g., `"analytics2_filters"`) to segregate their filter states within `st.session_state`. This allows filter selections to persist as users interact with charts and tables, and even when they navigate away from and return to a page within the same session.

*   **UI Element State (Implicit and Explicit):**
    *   Streamlit widgets (e.g., text inputs, dropdowns, checkboxes) can have their state automatically managed by Streamlit if a unique `key` argument is provided. This key is used to store the widget's current value in `st.session_state`.
    *   This is leveraged by many modules to preserve user input across script reruns, for example, when a form is submitted or when other parts of the UI update.

By utilizing `st.session_state`, the Creators Engine IA provides a continuous and stateful experience. Data specific to a user's current session, such as their authentication status, navigation choices, inputs, and filter settings, is maintained in memory and isolated to that session. This data typically does not persist beyond the session's lifetime unless explicitly saved to a more permanent external store, such as the Google Cloud Storage caching mechanism implemented in the Thumbnails Clinic for API results.
