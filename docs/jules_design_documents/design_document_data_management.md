## 4. Data Management

Data management is a critical aspect of the Creators Engine IA application, handled primarily by the `utils/dataloader.py` module. This module is responsible for sourcing, processing, caching, and providing data to various application components.

### Data Sources and Storage

*   **Primary Data Format:** The application relies on **Parquet files** as its primary data storage format. Parquet is an efficient columnar storage format suitable for analytics workloads.
*   **Environment-Specific Paths:** Data file paths are determined by the `APPMODE` environment variable:
    *   If `APPMODE == "DEV"`, data is typically loaded from a local path such as `/app/data/` or a user-defined `DEV_DATA_DIR`.
    *   Otherwise (for production or other modes), paths are relative, such as `data/`.
*   **Key Data Tables:** The main data entities loaded from Parquet files include:
    *   `tbl_nerdalytics`: Contains core YouTube video analytics and metadata.
    *   `tbl_slope_full`: Stores time-series data, likely for trend analysis (e.g., "slope" charts).
    *   `tbl_playlist_full_dedup`: Contains detailed information about playlists and their constituent video items, with duplicates removed.
    *   `tbl_analytics_filters`: May store pre-calculated values or configurations for filtering in analytics views.
    *   `tbl_channels`: Stores information related to YouTube channels.

### Data Loading and Preprocessing

*   **Centralized Loading:** The `load_base_data()` function serves as the main entry point for loading all foundational datasets (e.g., `tbl_nerdalytics`, `tbl_slope_full`, etc.). These are loaded once and then cached.
*   **User-Specific Copies:** The `get_user_dataframe(df_name)` function provides a *copy* of a requested base DataFrame. This is crucial to ensure that any modifications or filtering operations performed within a specific user session do not alter the original cached DataFrame, thus maintaining data integrity across different sessions and users.
*   **Key Preprocessing Steps:** Upon loading, several important preprocessing and transformation steps are applied to the DataFrames:
    *   **Date/Datetime Conversions:** Columns representing dates or timestamps (e.g., `slope_date` in `tbl_slope_full`, `published_at` in `tbl_nerdalytics`, `playlist_item_published_at` in `tbl_playlist_full_dedup`) are converted to `datetime` objects using `pd.to_datetime()`. Errors encountered during conversion are typically coerced, resulting in `NaT` (Not a Time) values.
    *   **String Type Enforcement:** To prevent issues with Apache Arrow serialization and to ensure consistency, several columns are explicitly converted to string types (`.astype(str)`). This is applied to various ID columns (`channel_id`, `video_id`, `playlist_id`) and specific timestamp columns like `extract_date_yt` and `extract_date_gcp`.
    *   **Data Enrichment (Playlist Data):** The `tbl_playlist_full_dedup` DataFrame is enriched by merging it with `tbl_nerdalytics` on `video_id`. This merge adds key video analytics metrics (like view counts, like counts, comment counts, various `ss_*` sentiment/safety score columns) and video tags directly into the playlist dataset, facilitating more comprehensive playlist analysis.

### Caching Strategy

The application leverages Streamlit's caching mechanisms (`st.cache_data` and `st.cache_resource`) to optimize performance by reducing redundant data loading and processing operations:

*   **`@st.cache_data`:**
    *   This decorator is applied to the `read_parquet_local(file_path, GCS_CLIENT_VAR)` function with a Time-To-Live (TTL) of "1d" (1 day). This function is responsible for reading individual Parquet files. Caching here avoids repeated disk I/O or GCS calls for the same file within a 24-hour window.
    *   It is also applied to `get_user_dataframe(df_name)` with a TTL of "15m" (15 minutes). This caches the copies of DataFrames provided to user sessions, speeding up access if the same filtered or manipulated view of data is requested by a user within this timeframe.

*   **`@st.cache_resource`:**
    *   This decorator is applied to the `load_base_data()` function with a TTL of "1d" (1 day). Since `load_base_data()` handles the initial loading and preprocessing of *all* primary DataFrames, caching its output means that this entire setup process is performed only once per day per application instance. This significantly speeds up the application's startup and the initial load time for users.

This multi-layered caching strategy (caching raw data reads, caching the fully loaded and preprocessed base datasets, and caching user-specific DataFrame copies) effectively balances data freshness requirements with the need for a responsive user experience.
