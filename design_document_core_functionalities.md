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
    *   Supports various filter types based on DataFrame column properties (e.g., categorical like `category_id`, numerical like `view_count`, date ranges like `published_at`).
    *   Displays a summary of currently active filters, giving users clarity on the data subset they are viewing.

### Application Modules (Pages)

The following modules are defined in `config/pages.py` and represent the main sections and functionalities of the Creators Engine IA application:

*   **Home (`modules/home.py`):**
    *   Serves as the primary landing page for the application.
    *   Displays a welcome message to the user.
    *   Provides a high-level overview of the application's features and capabilities.
    *   Lists the available modules and tools accessible via the sidebar navigation.

*   **Metadata (`modules/metadata.py`):**
    *   Dedicated to analyzing YouTube video and channel metadata from the `tbl_nerdalytics` dataset.
    *   The page is structured into multiple sub-sections or tabs, implemented as `metadata_1` through `metadata_5` blocks, allowing for organized presentation of different metadata aspects such as video `title`, `description`, `tags`, and `category_id` (utilizing `get_category_name` for display).
    *   Integrates `utils/filter_manager_v2.py` to enable users to filter `tbl_nerdalytics` for more focused and relevant metadata analysis.
    *   Includes functionality to display warnings or messages if the selected filters result in no data.

*   **Thumbnails Clinic (`modules/thumbs_safe.py`):**
    *   Offers tools to analyze YouTube video thumbnails for content safety and appropriateness. Users can provide thumbnails by uploading a file, giving an image URL, or a YouTube `video_id` (from which the `thumbnail_url` in `tbl_nerdalytics` can be fetched or a new one derived).
    *   Integrates with **Google Cloud Vision API** to perform `SAFE_SEARCH_DETECTION` (detecting adult content, violence, etc., results of which might be comparable to `ss_*` fields in `tbl_nerdalytics`) and `LABEL_DETECTION`.
    *   Integrates with **OpenAI Moderation API** for an additional layer of content safety analysis.
    *   Displays comprehensive results from both APIs.
    *   Caches analysis results in **Google Cloud Storage (GCS)**.

*   **Analytics2 New (`modules/analytics2.py`):**
    *   Provides advanced analytics capabilities for in-depth channel and video performance review.
    *   The content is organized into multiple tabs or sections, handled by `analytics2_section1` through `analytics2_section7` blocks.
    *   Utilizes data from `tbl_nerdalytics` (for video-level metrics like `view_count`, `like_count`, `comment_count`, `age_in_days`, and metadata like `title`, `category_id`) and `tbl_playlist_full_dedup` (for playlist structure and aggregated performance). It may also implicitly use `tbl_slope_full` for trend indicators like `view_count_slope` or `predicted_view_count_7d` if these are part of the "Big Numbers" or "Radar Charts" sections.
    *   Features its own namespaced filter state management (`FILTER_NAMESPACE = "analytics2_filters"`).
    *   Includes utility functions for resetting data caches.

*   **Data Stories (`modules/datastories.py`):**
    *   Presents data-driven narratives and actionable insights derived primarily from the `tbl_nerdalytics` dataset, focusing on video performance metrics (e.g., `view_count`, `like_count`, `age_in_days`), content characteristics (e.g., `category_id`, `video_type`), and safety/content scores (e.g., `ss_adult`, `ss_violence`).
    *   Content is divided into an "Overview" section (`dstories_1`) and a "More Analysis" section (`dstories_2`), likely presented as tabs.
    *   Employs `utils/filter_manager_v2.py` to allow users to filter `tbl_nerdalytics`, tailoring the presented stories and insights.

*   **Data Stories Playlist (`modules/datastories_playlist.py`):**
    *   Similar in concept to "Data Stories" but focuses specifically on analyzing playlist performance and characteristics using data from `tbl_playlist_full_dedup`. This includes analyzing aggregated metrics from videos within playlists (e.g., total views, average duration) by leveraging the enrichment of `tbl_playlist_full_dedup` with data from `tbl_nerdalytics`.
    *   Features sections such as "Playlist Overview" (`dstories_play1`) and "Playlist Analysis" (`dstories_play2`).
    *   Also utilizes `utils/filter_manager_v2.py` for interactive data filtering relevant to playlists.

*   **Template (`modules/templatedatapage.py`):**
    *   Serves as a generic, reusable page structure for creating new data-centric pages.
    *   Defines a `TemplateDataPage` class that can be configured with a specific DataFrame and content blocks.
    *   The module provides an example instantiation using `tbl_nerdalytics` (showcasing video data like `title`, `view_count`, `published_at`), and template blocks that could potentially draw from `tbl_slope_full` (`template_slope_block`), `tbl_playlist_full_dedup` (`template_playlist_block`), and `tbl_channels` (`template_channels_block`).
    *   Includes its own filter management system based on the older `utils/filter_manager.py`.

*   **Debug Tools (`modules/debugtools.py`):**
    *   A utility page for developers for diagnostics and troubleshooting.
    *   Provides tools for testing data loading (all tables including `tbl_nerdalytics`, `tbl_slope_full`, etc.), resetting caches, file management, and viewing environment information.
    *   Capability to trigger data retrieval scripts (e.g., `utils/dataretriever.py`).
