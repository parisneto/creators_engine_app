"""
External block example for modular Streamlit page framework.
"""
import streamlit as st
from utils.dataloader import load_data
from utils.config import APPMODE


import pandas as pd
import numpy as np

def assess_dataframe(df):
    """
    Generates a summary assessment of a Pandas DataFrame.

    The assessment includes information about data types, missing values (NaN, None),
    zero values (for numeric columns), unique values, and inferred data types
    for each column. It also reports the total number of duplicate rows.

    Args:
        df (pd.DataFrame): The DataFrame to assess.

    Returns:
        pd.DataFrame: A DataFrame summarizing the assessment for each column.
                      Also prints the total number of duplicate rows.
    """
    assessment_list = []

    print(f"DataFrame Shape: {df.shape}")
    print(f"Total Duplicate Rows: {df.duplicated().sum()}\n")
    print("Column-wise Assessment:")

    for col in df.columns:
        # Data type
        dtype = df[col].dtype

        # Inferred data type (more specific, e.g., 'integer', 'string', 'mixed')
        inferred_dtype = pd.api.types.infer_dtype(df[col], skipna=True)

        # Missing values
        missing_values = df[col].isnull().sum()
        missing_percentage = (missing_values / len(df)) * 100

        # Zero values (for numeric types)
        zero_values = 0
        zero_percentage = 0.0
        if pd.api.types.is_numeric_dtype(df[col]):
            zero_values = (df[col] == 0).sum()
            if len(df) > 0: # Avoid division by zero for empty DataFrame
                 zero_percentage = (zero_values / len(df)) * 100
        elif inferred_dtype == 'integer' or inferred_dtype == 'floating': # Check inferred for initially object columns
            try:
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                zero_values = (numeric_col == 0).sum()
                if len(df) > 0:
                    zero_percentage = (zero_values / len(df)) * 100
            except Exception: # Handle cases where conversion is not possible
                pass


        # Unique values
        unique_values = df[col].nunique()
        unique_percentage = (unique_values / len(df)) * 100 if len(df) > 0 else 0


        assessment_list.append({
            'Column': col,
            'Data Type': dtype,
            'Inferred Type': inferred_dtype,
            'Missing Values': missing_values,
            'Missing %': f"{missing_percentage:.2f}%",
            'Zero Values': zero_values if pd.api.types.is_numeric_dtype(df[col]) or inferred_dtype in ['integer', 'floating'] else 'N/A',
            'Zero %': f"{zero_percentage:.2f}%" if pd.api.types.is_numeric_dtype(df[col]) or inferred_dtype in ['integer', 'floating'] else 'N/A',
            'Unique Values': unique_values,
            'Unique %': f"{unique_percentage:.2f}%"
        })

    assessment_df = pd.DataFrame(assessment_list)
    return assessment_df

# # --- Example Usage ---
# if __name__ == '__main__':
#     # Create a sample DataFrame with various data issues
#     data = {
#         'col_a': [1, 2, 0, 4, np.nan, 6, 0, 8, 9, 10],
#         'col_b': ['x', 'y', 'z', 'x', None, 'y', 'w', 'x', 'y', 'z'],
#         'col_c': [1.1, 2.2, 0.0, 4.4, 5.5, np.nan, 7.7, 0.0, 9.9, 10.0],
#         'col_d': [True, False, True, False, True, True, False, True, False, True],
#         'col_e': ['apple', 'banana', 'apple', 'orange', 'banana', 'grape', 'apple', 'kiwi', 'plum', 'orange'],
#         'col_f': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # Low variance
#         'col_g': [None, np.nan, pd.NaT, None, np.nan, pd.NaT, None, np.nan, pd.NaT, None], # All missing
#         'col_h': ['10', '20', '30', '40', '50', '0', '70', '80', '90', '100'], # Numeric stored as string
#         'col_i': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] # Clean integer
#     }
#     sample_df = pd.DataFrame(data)

#     # Add some duplicate rows
#     sample_df = pd.concat([sample_df, sample_df.head(2)], ignore_index=True)

#     print("--- DataFrame Assessment ---")
#     assessment_summary = assess_dataframe(sample_df)
#     print(assessment_summary.to_string())

#     print("\n\n--- Further Checks/Suggestions ---")
#     # 1. Descriptive Statistics
#     print("\nDescriptive Statistics (Overall):")
#     print(sample_df.describe(include='all').to_string())

#     # 2. Memory Usage
#     print(f"\nTotal Memory Usage: {sample_df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")
#     print("\nMemory Usage per Column (bytes):")
#     print(sample_df.memory_usage(deep=True))

#     # 3. Correlation Matrix for numeric columns
#     numeric_df = sample_df.select_dtypes(include=np.number)
#     if not numeric_df.empty:
#         print("\nCorrelation Matrix (Numeric Columns):")
#         print(numeric_df.corr().to_string())

#     # 4. Value Counts for Categorical Columns with few unique values
#     print("\nValue Counts for High-Frequency Categorical Columns (example 'col_b'):")
#     if 'col_b' in sample_df.columns and sample_df['col_b'].nunique() < 10: # Arbitrary threshold
#         print(sample_df['col_b'].value_counts(dropna=False).to_string())

#     # 5. Check for columns with only one unique value (low variance)
#     low_variance_cols = [col for col in sample_df.columns if sample_df[col].nunique(dropna=False) == 1]
#     if low_variance_cols:
#         print(f"\nColumns with only one unique value (low variance): {low_variance_cols}")

#     # 6. Identify potential mixed-type columns that aren't obviously numeric/string
#     # The 'Inferred Type' in the main summary already helps with this.
#     # For a more targeted check:
#     print("\nPotentially problematic inferred types (e.g., 'mixed', 'mixed-integer-float'):")
#     problematic_types = assessment_summary[assessment_summary['Inferred Type'].isin(['mixed', 'mixed-integer-float'])]
#     if not problematic_types.empty:
#         print(problematic_types[['Column', 'Data Type', 'Inferred Type']].to_string())
#     else:
#         print("No columns with 'mixed' or 'mixed-integer-float' inferred types found.")



def debugtools4():
    st.header("Debug Tools 4")
    st.write("Dataframe inspector content here.")
    st.divider()
    # st.markdown("---")

    df_nerdalytics = load_data("tbl_nerdalytics")

    # st.code(df_nerdalytics["view_count"].describe())
    if False:
        st.write("Shape for Nerdalytics:")
        st.write(df_nerdalytics.shape)
        st.write("Null Count for Nerdalytics:")
        st.code(df_nerdalytics.isnull().sum())

    st.divider()
    print("--- DataFrame Assessment ---")
    assessment_summary = assess_dataframe(df_nerdalytics)
    st.dataframe(assessment_summary)
    st.code(assessment_summary.to_string())

    print("\n\n--- Further Checks/Suggestions ---")
    # 1. Descriptive Statistics
    st.write("\nDescriptive Statistics (Overall):")
    st.code(df_nerdalytics.describe(include='all').to_string())

    # 2. Memory Usage
    st.write(f"\nTotal Memory Usage: {df_nerdalytics.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")
    st.write("\nMemory Usage per Column (bytes):")
    st.code(df_nerdalytics.memory_usage(deep=True))

    # 3. Correlation Matrix for numeric columns
    numeric_df = df_nerdalytics.select_dtypes(include=np.number)
    if not numeric_df.empty:
        st.write("\nCorrelation Matrix (Numeric Columns):")
        st.code(numeric_df.corr().to_string())

    # 4. Value Counts for Categorical Columns with few unique values
    st.write("\nValue Counts for High-Frequency Categorical Columns (example 'col_b'):")
    if 'col_b' in df_nerdalytics.columns and df_nerdalytics['col_b'].nunique() < 10: # Arbitrary threshold
        st.code(df_nerdalytics['col_b'].value_counts(dropna=False).to_string())

    # 5. Check for columns with only one unique value (low variance)
    low_variance_cols = [col for col in df_nerdalytics.columns if df_nerdalytics[col].nunique(dropna=False) == 1]
    if low_variance_cols:
        st.write(f"\nColumns with only one unique value (low variance): {low_variance_cols}")

    # 6. Identify potential mixed-type columns that aren't obviously numeric/string
    # The 'Inferred Type' in the main summary already helps with this.
    # For a more targeted check:
    st.write("\nPotentially problematic inferred types (e.g., 'mixed', 'mixed-integer-float'):")
    problematic_types = assessment_summary[assessment_summary['Inferred Type'].isin(['mixed', 'mixed-integer-float'])]
    if not problematic_types.empty:
        st.code(problematic_types[['Column', 'Data Type', 'Inferred Type']].to_string())
    else:
        st.code("No columns with 'mixed' or 'mixed-integer-float' inferred types found.")


    st.divider()
    st.write("sample inspections")

    st.write(df_nerdalytics["view_count"].sample(5))
    st.write(df_nerdalytics[df_nerdalytics["view_count"] == 0][["view_count", "video_id"]].sample(10, replace=True))

    # st.write("Count of NaN : ", [df_nerdalytics["view_count"].isna()].count())
    st.divider()
    st.write(df_nerdalytics[df_nerdalytics["view_count"].isna()][["view_count", "title", "video_id", "channel_title"]].sample(10, replace=True))
    # st.write(df_nerdalytics[df_nerdalytics["view_count"] == np.nan][["view_count", "video_id"]].sample(10, replace=True))
    # st.write("count of NaN :")
    # st.dataframe(df_nerdalytics[df_nerdalytics["view_count"] == np.nan].count())
    # st.write(df_nerdalytics["like_count"].sample(5))
    # st.write(df_nerdalytics["dislike_count"].sample(5))
    # st.write(df_nerdalytics["comment_count"].sample(5))
    # st.write(df_nerdalytics["subscriber_count"].sample(5))
    # st.write(df_nerdalytics["subscriber_count"].sample(5))



    st.markdown("---")

    df_playlists = load_data("tbl_playlist_full_dedup")
    st.divider()
    if df_playlists is None:
        st.warning("Failed to load 'tbl_playlists'. DataFrame is None. Please check your data source or logs for more information.")
    else:
        st.code(df_playlists.shape)
    st.markdown("---")

    df_channels = load_data("tbl_channels")
    st.divider()
    if df_channels is None:
        st.warning("Failed to load 'tbl_channels'. DataFrame is None. Please check your data source or logs for more information.")
    else:
        st.code(df_channels.shape)

    # st.code(df_channels.columns())
    # st.code(df_channels["view_count"].describe())
    st.divider()


