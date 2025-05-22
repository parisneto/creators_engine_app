"""
Utility functions for treating null values in DataFrames.
"""
import numpy as np
import pandas as pd
import streamlit as st

def treat_nulls(df, verbose=False):
    """
    Treat various string representations of null values in a DataFrame.
    
    Args:
        df: The DataFrame to treat
        verbose: If True, print diagnostic information
        
    Returns:
        The treated DataFrame (modified in-place)
    """
    # Create a copy to avoid modifying the original if needed
    # df = df.copy()
    
    # Define null representations
    null_representations = [
        "null", 
        "N/A", 
        "None", 
        "na", 
        "n/a", 
        "none", 
        "NULL", 
        "NA", 
        ""
    ]
    
    # Get columns with object dtype (strings)
    object_columns = df.select_dtypes(include=['object']).columns.tolist()
    
    # Track changes
    changes_made = {}
    
    # Process each column
    for col in object_columns:
        if col in df.columns:
            # Count before replacement
            before_count = df[col].isnull().sum()
            
            # Replace various null representations with np.nan
            # Use infer_objects() to explicitly handle downcasting behavior
            # This addresses the FutureWarning about silent downcasting in replace()
            df[col] = df[col].replace(null_representations, np.nan).infer_objects(copy=False)
            
            # Count after replacement
            after_count = df[col].isnull().sum()
            new_nulls = after_count - before_count
            
            if new_nulls > 0:
                changes_made[col] = new_nulls
                
    # Print diagnostic information if requested
    if verbose and changes_made:
        for col, count in changes_made.items():
            print(f"Column '{col}': Converted {count} string null representations to NaN")
    
    return df
