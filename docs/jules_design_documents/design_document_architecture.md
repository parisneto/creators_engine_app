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
        *   **Google Cloud AI Platform:** Integrated for accessing more advanced AI models and machine learning functionalities, potentially for predictive analytics or deeper content analysis.
    *   **OpenAI API:** Integrated for leveraging OpenAI's powerful language models. This can be used for tasks like generating video titles and descriptions, suggesting content ideas, or analyzing text-based content for sentiment and engagement potential.
*   **Application Structure:**
    *   **Modular Design:** The application is designed with modularity in mind. Different features or sections of the application are organized into separate modules. Pages are defined and managed in `config/pages.py`, which likely maps page names to their corresponding Python modules that render the page content.
    *   **Reusable Components:** UI elements and logic that are common across multiple pages (e.g., navigation bars, specific data display widgets) are encapsulated as reusable components within the `components/` directory.
    *   **Utility Functions:** Common helper functions, such as data loading utilities, API interaction clients, or other shared functionalities, are organized in the `utils/` directory to promote code reuse and maintainability.
