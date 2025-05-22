## 4. Data Management

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
