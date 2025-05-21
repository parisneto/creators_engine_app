## 3. Core Components & Functionalities

The application is structured into several key modules, each providing distinct functionalities. Navigation between these modules is handled by a persistent sidebar, which also displays user information and application branding.

### Key Reusable Components

*   **Sidebar (`components/sidebar.py`):**
    *   Displays the application logo and title ("Creators Engine IA").
    *   Renders the main navigation menu using `components/navigation.py`, allowing users to switch between different modules/pages.
    *   Shows authenticated user information (e.g., email).
    *   Includes an optional "Debug Info" expander that provides details such as system information, Python/Streamlit versions, current time, and authentication status.
    *   Contains version information and copyright details in the footer.

*   **Navigation (`components/navigation.py`):**
    *   Generates navigation buttons within the sidebar based on the page configurations in `config/pages.py`.
    *   Manages the active page state using Streamlit's session state and URL query parameters (`st.query_params`), ensuring that the application's current view is correctly reflected and bookmarkable.
    *   Visually highlights the currently active page in the navigation menu.

*   **Filter Manager (`utils/filter_manager_v2.py` and `utils/filter_manager.py`):**
    *   Provides a robust and reusable framework for creating, rendering, and applying filters to Pandas DataFrames. This allows users to interactively narrow down data displayed in various modules.
    *   `filter_manager_v2.py` is utilized by `metadata`, `datastories`, and `datastories_playlist` modules, suggesting it's a newer or enhanced version.
    *   Supports various filter types based on DataFrame column properties (e.g., categorical, numerical, date ranges).
    *   Displays a summary of currently active filters, giving users clarity on the data subset they are viewing.

### Application Modules (Pages)

The following modules are defined in `config/pages.py` and represent the main sections and functionalities of the Creators Engine IA application:

*   **Home (`modules/home.py`):**
    *   Serves as the primary landing page for the application.
    *   Displays a welcome message to the user.
    *   Provides a high-level overview of the application's features and capabilities.
    *   Lists the available modules and tools accessible via the sidebar navigation.

*   **Metadata (`modules/metadata.py`):**
    *   Dedicated to analyzing YouTube video and channel metadata.
    *   The page is structured into multiple sub-sections or tabs, implemented as `metadata_1` through `metadata_5` blocks, allowing for organized presentation of different metadata aspects.
    *   Integrates `utils/filter_manager_v2.py` to enable users to filter the `tbl_nerdalytics` dataset for more focused and relevant metadata analysis.
    *   Includes functionality to display warnings or messages if the selected filters result in no data.

*   **Thumbnails Clinic (`modules/thumbs_safe.py`):**
    *   Offers tools to analyze YouTube video thumbnails for content safety and appropriateness.
    *   Allows users to input thumbnails via file upload, direct image URL, or by providing a YouTube video ID (which then fetches the thumbnail).
    *   Integrates with **Google Cloud Vision API** to perform `SAFE_SEARCH_DETECTION` (detecting adult content, violence, etc.) and `LABEL_DETECTION` (identifying objects, themes).
    *   Integrates with **OpenAI Moderation API** (using model `omni-moderation-2024-09-26`) for an additional layer of content safety analysis, providing moderation flags.
    *   Displays comprehensive results from both Google Cloud Vision and OpenAI APIs, including safety scores, detected labels, and moderation categories.
    *   Performs input validation for images (e.g., size limits, URL format checks).
    *   Caches analysis results in **Google Cloud Storage (GCS)** using `utils/gcs_uploader.py` to prevent redundant API calls for the same image by the same user. Cache paths incorporate user email for user-specific caching.

*   **Analytics2 New (`modules/analytics2.py`):**
    *   Provides advanced analytics capabilities for in-depth channel and video performance review.
    *   The content is organized into multiple tabs or sections: "Big Numbers", "Metadata", "Radar Charts", "TBD", "Playlists", "Tags Playground", and "Metadata 2", which are handled by `analytics2_section1` through `analytics2_section7` blocks.
    *   Utilizes data from `tbl_nerdalytics` and `tbl_playlist_full_dedup` Parquet files.
    *   Features its own namespaced filter state management (`FILTER_NAMESPACE = "analytics2_filters"`), indicating a dedicated filtering system for this module, though current UI filters are placeholders.
    *   Includes utility functions for resetting the data cache and forcing Python's garbage collection, likely for performance management during development or heavy use.

*   **Data Stories (`modules/datastories.py`):**
    *   Presents data-driven narratives and actionable insights derived primarily from the `tbl_nerdalytics` dataset.
    *   Content is divided into an "Overview" section (`dstories_1`) and a "More Analysis" section (`dstories_2`), likely presented as tabs.
    *   Employs `utils/filter_manager_v2.py` to allow users to filter the data, tailoring the presented stories and insights to their specific interests or channel segments.

*   **Data Stories Playlist (`modules/datastories_playlist.py`):**
    *   Similar in concept to "Data Stories" but focuses specifically on analyzing playlist performance and characteristics using data from `tbl_playlist_full_dedup`.
    *   Features sections such as "Playlist Overview" (`dstories_play1`) and "Playlist Analysis" (`dstories_play2`).
    *   Also utilizes `utils/filter_manager_v2.py` for interactive data filtering relevant to playlists.

*   **Template (`modules/templatedatapage.py`):**
    *   Serves as a generic, reusable page structure or a template for quickly creating new data-centric pages.
    *   Defines a `TemplateDataPage` class that can be configured with a specific DataFrame and a list of content blocks.
    *   The module provides an example instantiation of this page using `tbl_nerdalytics` and various template blocks (`template_nerdalytics_block`, `template_slope_block`, `template_playlist_block`, `template_channels_block`).
    *   Includes its own filter management system based on the older `utils/filter_manager.py`.
    *   This module demonstrates a standardized approach to building data display pages with common functionalities like filtering and tabbed content.

*   **Debug Tools (`modules/debugtools.py`):**
    *   A utility page primarily intended for developers and administrators for diagnostics and troubleshooting.
    *   Provides a range of debugging functionalities:
        *   Tools for testing data loading processes and resetting data caches.
        *   A file manager interface (`fileman` block) for interacting with the local file system (likely sandboxed).
        *   Access to various specific debug blocks (`debugtools1`, `debugtools3`, `debugtools4`).
        *   Display of operating system details, Debian version, and other system environment information.
        *   A viewer for environment variables, including sensitive ones like `OPENAI_API_KEY` (with partial masking for security).
        *   The capability to trigger data retrieval scripts (e.g., `utils/dataretriever.py`) either as a subprocess or by direct import and execution.
