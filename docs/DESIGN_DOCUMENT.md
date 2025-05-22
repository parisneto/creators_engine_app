# Design Document: Creators Engine IA

## 1. Introduction & Overview

Creators Engine IA is a comprehensive web application designed to empower YouTube content creators with advanced analytics and content optimization tools. The primary goal of this application is to provide actionable, data-driven insights that help creators understand their channel's performance, optimize their video metadata and thumbnails, and ultimately grow their audience and engagement on YouTube.

The application caters to YouTube creators of all levels who are looking to leverage data and AI-powered analysis to enhance their content strategy.

## 2. Architecture

The Creators Engine IA application employs a multi-tiered architecture:

*   **Frontend:** A dynamic and interactive user interface built with **Streamlit**. This framework allows for rapid development of data-centric web applications. The application is structured as a multi-page experience, with different functionalities or views presented as separate pages.
*   **Backend & Data Layer:**
    *   **Data Storage:** The primary data sources are **Parquet files** stored locally. Data processing and manipulation rely on these files.
    *   **Data Processing:** Core data manipulation and analysis are performed using the **Pandas** library. This includes loading data from Parquet files, transformations, cleaning, and preparing data for display or further analysis.
*   **External Services Integration:**
    *   **Google Cloud Platform (GCP):** The application leverages several GCP services:
        *   **Google Cloud Vision API:** Utilized for image analysis tasks, such as analyzing YouTube video thumbnails for optimization insights.
        *   **Google Cloud Storage:** Used for storing and accessing larger data files or assets that might not be suitable for local storage, or for more persistent storage needs.
        *   **Google Cloud AI Platform:** Integrated for accessing more advanced AI models and machine learning functionalities,
potentially for predictive analytics or deeper content analysis.
    *   **OpenAI API:** Integrated for leveraging OpenAI's powerful language models. This can be used for tasks like generating video titles and descriptions, suggesting content ideas, or analyzing text-based content for sentiment and engagement potential.
*   **Application Structure:**
    *   **Modular Design:** The application is designed with modularity in mind. Different features or sections of the application are organized into separate modules. Pages are defined and managed in `config/pages.py`, which likely maps page names to their corresponding Python modules that render the page content.
    *   **Reusable Components:** UI elements and logic that are common across multiple pages (e.g., navigation bars, specific data display widgets) are encapsulated as reusable components within the `components/` directory.
    *   **Utility Functions:** Common helper functions, such as data loading utilities, API interaction clients, or other shared functionalities, are organized in the `utils/` directory to promote code reuse and maintainability.

## 3. Data Management

Data management is a critical aspect of the Creators Engine IA application, handled primarily by the `utils/dataloader.py` module. This module is responsible for sourcing, processing, caching, and providing data to various application components. The `data/dataset_feature_map.py` file provides a schema and descriptions for key datasets.

### Data Sources and Storage

*   **Primary Data Format:** The application relies on **Parquet files** as its primary data storage format. Parquet is an efficient columnar storage format suitable for analytics workloads.
*   **Environment-Specific Paths:** Data file paths are determined by the `APPMODE` environment variable:
    *   If `APPMODE == "DEV"`, data is typically loaded from a local path such as `/app/data/` or a user-defined `DEV_DATA_DIR`.
    *   Otherwise (for production or other modes), paths are relative, such as `data/`.

### Key Data Tables

The main data entities loaded from Parquet files include:

*   **`tbl_nerdalytics` (`df_nerdalytics` in `DATASET_FEATURE_MAP`):**
    *   **Description:** Video-level summary table. One row per `video_id`. Used for ABC, quantile, and categorical analysis.
    *   **Key Features (from `DATASET_FEATURE_MAP`):**
        *   `video_id` (text, id): e.g., 'IAyu0JMb_1U'. Use: label, join.
        *   `channel_id` (text, id): e.g., 'UCKHhA5hN2UohhFDfNXB_cvQ'. Use: label, join.
        *   `channel_title` (text, name): e.g., 'Manual do Mundo'. Use: label.
        *   `title` (text, title): e.g., 'Como é feito o TRATAMENTO DE ESGOTO #Boravê'. Use: label, tooltip.
        *   `video_type` (categorical, nominal): e.g., 'Short'. Use: group, filter.
        *   `live_content` (categorical, nominal): e.g., 'Live'. Use: group, filter.
        *   `category_id` (categorical, nominal): e.g., '22'. Use: group, filter. (See "Data Dictionary and Utilities" for category name mapping).
        *   `published_at` (datetime, date): e.g., '2024-06-04 21:00:11'. Use: filter, time.
        *   `age_in_days` (numerical, continuous): e.g., 315. Use: plot, filter.
        *   `view_count` (numerical, continuous): e.g., 1211722. Use: plot, agg.
        *   `like_count` (numerical, continuous): e.g., 61273. Use: plot, agg.
        *   `comment_count` (numerical, continuous): e.g., 264. Use: plot, agg.
        *   `ss_adult`, `ss_spoof`, `ss_medical`, `ss_violence`, `ss_racy` (numerical, discrete): e.g., 2, 1, 0, 3, 0 respectively. These represent Google Cloud Vision SafeSearch scores. Use: group, filter.
        *   `caption` (boolean): e.g., True. Use: filter.
        *   `description` (text, desc): e.g., 'Conheça a CESAN: http://www.cesan.com.br\n\nVo...'. Use: tooltip, nlp.
        *   `tags` (text, list): e.g., 'fun,cat'. Use: filter, nlp.
        *   `thumbnail_url` (text, url): e.g., 'http://...'. Use: display.

*   **`tbl_slope_full` (`df_slope_full` in `DATASET_FEATURE_MAP`):**
    *   **Description:** Time-series table. Multiple rows per `video_id`, includes slope and prediction features.
    *   **Key Features (from `DATASET_FEATURE_MAP`):**
        *   `video_id` (text, id): e.g., 'NU8mh3h7Vh4'. Use: label, join.
        *   `channel_id` (text, id): e.g., 'UCKHhA5hN2UohhFDfNXB_cvQ'. Use: label, join.
        *   `published_at` (datetime, date): e.g., '2025-02-26 20:00:12'. Use: filter, time.
        *   `age_in_days` (numerical, continuous): e.g., 48. Use: plot, filter.
        *   `category_id` (categorical, nominal): e.g., '28'. Use: group, filter. (See "Data Dictionary and Utilities" for category name mapping).
        *   `slope_timestamp` (datetime, timestamp): e.g., '2025-02-26 20:00:12'. Use: time, index.
        *   `slope_date` (datetime, date): e.g., '2025-02-26'. Use: time, index.
        *   `view_count_slope` (numerical, continuous): e.g., 534272.59. Use: plot, trend.
        *   `like_count_slope` (numerical, continuous): e.g., 572710.01. Use: plot, trend.
        *   `comment_count_slope` (numerical, continuous): e.g., 14.19. Use: plot, trend.
        *   `linear_view_count_speed`, `slope_view_count_speed` (numerical, continuous): e.g., 2363.73, 123.62. Use: plot, trend.
        *   `predicted_view_count_7d`, `predicted_view_count_30d`, `predicted_view_count_365d` (numerical, continuous): e.g., 534272.59, 572710.01, 1132559.44. Use: predict, plot.
        *   `growth_view_count_7d_percent`, `growth_view_count_30d_percent`, `growth_view_count_365d_percent` (numerical, continuous): e.g., 2.37, 9.73, 117.00. Use: growth, plot.

*   **`tbl_playlist_full_dedup`:** Contains detailed information about playlists and their constituent video items, with duplicates removed. This table is enriched by merging with `tbl_nerdalytics` (see "Data Loading and Preprocessing").
*   **`tbl_analytics_filters`:** May store pre-calculated values or configurations for filtering in analytics views.
*   **`tbl_channels`:** Stores information related to YouTube channels.

### Data Dictionary and Utilities (`data/dataset_feature_map.py`)

The `data/dataset_feature_map.py` file provides valuable metadata and utility functions for understanding and working with the datasets:

*   **`DATASET_FEATURE_MAP`:** A Python dictionary that defines the schema for key DataFrames like `df_nerdalytics` and `df_slope_full`. For each feature (column), it specifies:
    *   `type`: General data type (e.g., 'text', 'categorical', 'numerical', 'datetime', 'boolean').
    *   `subtype`: More specific data type or characteristic (e.g., 'id', 'title', 'continuous', 'date').
    *   `example`: An example value for the feature.
    *   `use`: Intended usage of the feature (e.g., 'label', 'join', 'filter', 'plot', 'nlp').
*   **`CATEGORY_ID_MAP`:** A dictionary mapping YouTube category IDs (as strings) to their human-readable names in Portuguese (e.g., '1': "Filmes e Animação", '22': "Pessoas e Blogs"). This is used to provide more meaningful category labels in the application.
*   **`get_category_name(category_id, language='pt')`:** A utility function that takes a `category_id` and an optional language code (defaulting to Portuguese 'pt') and returns the corresponding category name using internal mappings (like `categories_br` and `categories_en`, which are expected to be defined in `config/VideoCategorieslist.py` and imported into `dataset_feature_map.py`). This is used to display user-friendly category names instead of raw IDs.

### Data Loading and Preprocessing

*   **Centralized Loading:** The `load_base_data()` function in `utils/dataloader.py` serves as the main entry point for loading all foundational datasets. These are loaded once and then cached.
*   **User-Specific Copies:** The `get_user_dataframe(df_name)` function provides a *copy* of a requested base DataFrame. This is crucial to ensure that any modifications or filtering operations performed within a specific user session do not alter the original cached DataFrame.
*   **Key Preprocessing Steps (in `utils/dataloader.py`):**
    *   **Date/Datetime Conversions:** Columns representing dates or timestamps (e.g., `slope_date` in `tbl_slope_full`, `published_at` in `tbl_nerdalytics`, `playlist_item_published_at` in `tbl_playlist_full_dedup`) are converted to `datetime` objects using `pd.to_datetime()`. Errors encountered during conversion are typically coerced, resulting in `NaT` (Not a Time) values.
    *   **String Type Enforcement:** To prevent issues with Apache Arrow serialization and to ensure consistency, several columns are explicitly converted to string types (`.astype(str)`). This is applied to various ID columns (`channel_id`, `video_id`, `playlist_id`) and specific timestamp columns like `extract_date_yt` and `extract_date_gcp`.
    *   **Data Enrichment (Playlist Data):** The `tbl_playlist_full_dedup` DataFrame is enriched by merging it with `tbl_nerdalytics` on `video_id`. This merge adds key video analytics metrics (like view counts, like counts, comment counts, various `ss_*` sentiment/safety score columns) and video tags directly into the playlist dataset, facilitating more comprehensive playlist analysis.
    *   **(No new data cleaning or preprocessing steps were identified for this update beyond those already known from `utils/dataloader.py`.)**

### Caching Strategy

The application leverages Streamlit's caching mechanisms (`st.cache_data` and `st.cache_resource`) to optimize performance:

*   **`@st.cache_data`:**
    *   Applied to `read_parquet_local(file_path, GCS_CLIENT_VAR)` (TTL "1d"): Caches individual Parquet file reads.
    *   Applied to `get_user_dataframe(df_name)` (TTL "15m"): Caches user-specific copies of DataFrames.
*   **`@st.cache_resource`:**
    *   Applied to `load_base_data()` (TTL "1d"): Caches the fully loaded and preprocessed base datasets.

This multi-layered caching strategy effectively balances data freshness with user experience responsiveness.

## 4. Core Components & Functionalities

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

## 5. Key Technologies & Libraries

The Creators Engine IA application is built using Python and leverages a range of powerful libraries and external services to deliver its functionalities.

### Core Platform

*   **Python:** (Version implicitly defined by environment, typically 3.x) The primary programming language used for the application.
*   **Streamlit (`streamlit>=1.44.1`):** The core web application framework, used for building the interactive user interface and managing application flow.

### Data Handling and Analysis

*   **Pandas:** (Version not specified in `requirements.txt` but a core dependency) Essential for data manipulation and analysis, providing high-performance data structures (DataFrames) and tools.
*   **NumPy:** (Implicitly used by Pandas and other scientific libraries) For numerical operations.
*   **Statsmodels (`statsmodels>=0.14.4`):** Used for statistical data analysis and modeling, likely for trend analysis or more complex data insights.
*   **Orjson (`orjson>=3.10.17`):** A fast JSON library, likely used for efficient serialization and deserialization of JSON data, potentially in API interactions or configuration file handling.

### External Service Integrations

*   **Google Cloud Platform (GCP):**
    *   **`google-cloud-vision>=3.10.1`:** Client library for Google Cloud Vision API, used for image analysis tasks like safe search detection and label detection on thumbnails.
    *   **`google-cloud-storage>=2.19.0`:** Client library for Google Cloud Storage, used for storing and retrieving cached analysis results (e.g., from the Thumbnails Clinic) and potentially other assets.
    *   **`google-cloud-aiplatform>=1.90.0`:** Client library for Google Cloud AI Platform, enabling access to more advanced AI models and machine learning functionalities.
*   **OpenAI:**
    *   **`openai>=1.79.0`:** Client library for interacting with OpenAI's API, used for tasks such as content moderation in the Thumbnails Clinic and potentially other generative AI features.

### Visualization

*   **Plotly (`plotly>=6.0.1`):** Used for creating interactive charts and data visualizations, prominent in analytics and data stories modules.
*   **Seaborn (`seaborn>=0.13.2`):** A high-level interface for drawing attractive and informative statistical graphics, often used in conjunction with Matplotlib.
*   **Matplotlib (`matplotlib>=3.10.1`):** A foundational library for creating static, animated, and interactive visualizations in Python.

### Web Interaction & Image Processing

*   **Requests (`requests==2.31.0`):** For making HTTP requests, used to fetch images from URLs for thumbnail analysis or interact with external APIs.
*   **BeautifulSoup4 (`beautifulsoup4>=4.13.4`):** A library for parsing HTML and XML documents. While listed in requirements, its direct prominent use in the core application logic reviewed (like page modules) was less evident than other libraries. It might be used in specific data retrieval scripts or less frequently accessed utilities.
*   **Pillow (`pillow>=11.2.1`):** A fork of PIL (Python Imaging Library), used for opening, manipulating, and saving various image file formats, essential for processing thumbnails before analysis.

### Standard Libraries & Utilities

*   **Logging:** The standard Python `logging` module is used for application-wide logging, helping in debugging and monitoring.
*   **Base64:** Used for encoding/decoding data, for instance, when handling image data for API submissions.
*   **Tempfile:** Used for creating temporary files and directories, which can be useful for handling intermediate data like downloaded images before processing.
*   **OS, Pathlib:** Standard Python libraries for interacting with the operating system, managing file paths, and environment variables.
*   **Datetime:** Standard Python module for working with dates and times, crucial for handling time-series data and timestamps in analytics.
*   **Re (Regular Expressions):** Used for pattern matching in strings, for instance, in input validation or text processing.
*   **Typing:** Used for type hinting, improving code readability and maintainability.
*   **Functools:** Provides higher-order functions, like `lru_cache` which could be used for custom caching, or `wraps` for decorators.
*   **Pyarrow:** (Implicit dependency for Parquet file handling with Pandas) Apache Arrow's Python library, essential for efficient reading and writing of Parquet files.

## 6. Deployment & Environment

### Containerization with Docker

The application is designed to be deployed using **Docker**, ensuring consistency and reproducibility across different environments. This is evidenced by the presence of several Docker-related files within the project:

*   **`Dockerfile.dev` (located in `.devcontainer/` and `dev-ci/`) and `Dockerfile.prod` (located in `.devcontainer/`):** These files define the Docker image configurations tailored for development and production environments, respectively. This separation allows for environment-specific dependencies, tools, or settings. For instance, development containers might include debugging tools or different data mounting strategies, while production containers are optimized for performance and security. There is also a `Dockerfile copy.prod` in `.devcontainer/` which might be a backup or variant.
*   **`docker-compose.yml`:** This file is used to define and manage multi-container Docker applications. It simplifies the setup and orchestration of the application and any supporting services (like databases or other backend components, though not explicitly detailed for this application).
*   **`.dockerignore`:** This file specifies intentionally untracked files and directories that should be excluded from the Docker build context. This helps in creating smaller, more efficient Docker images by omitting unnecessary files like local development configurations, caches, or documentation.
*   **Cloud Build Configuration (`cloudbuild.yaml`):** The presence of `cloudbuild.yaml` suggests that Google Cloud Build is likely used as part of the CI/CD pipeline for building Docker images and potentially deploying the application, particularly in a Google Cloud environment. Specific Cloud Build configurations for development (`dev-ci/cloudbuild.dev-app.yaml`, `dev-ci/cloudbuild.dev-base.yaml`) further underscore a sophisticated, automated build process.

Containerization via Docker ensures that the application runs in a predictable and isolated environment, from a developer's machine to staging and production systems.

### Environment Configuration (`APPMODE`)

A crucial environment variable, **`APPMODE`**, plays a significant role in tailoring the application's behavior to the specific deployment context (development, production, etc.):

*   **`APPMODE = "DEV"`:** When this variable is set to "DEV", the application activates development-specific configurations. A key example, observed in `utils/dataloader.py`, is the adjustment of data loading paths to point to local development directories (e.g., `/app/data/` or a user-defined `DEV_DATA_DIR`). This mode is intended for local development, debugging, and testing.
*   **Production Mode (e.g., `APPMODE` not set to "DEV", or explicitly set to "PROD" or another value):** In a production or non-development setting, the application defaults to configurations suitable for a deployed environment. For data loading, this means using relative paths (e.g., `data/`) that are expected to be structured within the deployed application package or a mounted volume.

This `APPMODE` mechanism allows the same codebase to operate correctly across different environments without requiring code modifications. It externalizes environment-specific settings, ensuring that data sources, API endpoints, or feature flags can be managed appropriately for each stage of the deployment lifecycle. Other parts of the application may also key off this variable for different behaviors or settings. The `startup.sh` script likely plays a role in setting or utilizing this environment variable when the application starts.

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
