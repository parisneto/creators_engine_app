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
