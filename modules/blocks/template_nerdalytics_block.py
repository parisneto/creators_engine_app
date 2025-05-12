import streamlit as st
import pandas as pd
import plotly.express as px
from utils.dataloader import get_user_dataframe

def template_nerdalytics_block(df, filter_manager):
    """
    Template block for nerdalytics dataframe with visualizations.

    Args:
        df: Filtered dataframe (nerdalytics)
        filter_manager: Filter manager instance
    """
    st.subheader("Nerdalytics Analysis")

    # Show dataframe info
    st.write(f"Filtered dataframe shape: {df.shape}")

    # Show sample data
    with st.expander("Sample Data"):
        st.dataframe(df.head(10))

    # Basic metrics
    if "view_count" in df.columns and "like_count" in df.columns and "comment_count" in df.columns:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Views", f"{df['view_count'].sum():,}")
        with col2:
            st.metric("Total Likes", f"{df['like_count'].sum():,}")
        with col3:
            st.metric("Total Comments", f"{df['comment_count'].sum():,}")

        # Engagement ratio
        if len(df) > 0:
            avg_like_per_view = df['like_count'].sum() / df['view_count'].sum() if df['view_count'].sum() > 0 else 0
            avg_comment_per_view = df['comment_count'].sum() / df['view_count'].sum() if df['view_count'].sum() > 0 else 0

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg. Likes per View", f"{avg_like_per_view:.2%}")
            with col2:
                st.metric("Avg. Comments per View", f"{avg_comment_per_view:.2%}")

        # Visualizations
        st.subheader("Visualizations")
        # st.write("Missing values:")
        # st.write("Missing values (na):")
        # st.write(df.isna().sum())
        # st.write("Missing values (null):")
        # st.write(df.isnull().sum())
        # st.write("Total missing values:")
        # st.write(df.isnull().sum().sum())
        st.divider()
        st.write("Before Dropping rows with missing values:")
        st.write(df.shape)
        df_clean = df.dropna(subset=["view_count", "like_count", "comment_count"])
        st.write("After Dropping rows with missing values:")
        st.write(df_clean.shape)

        # Views vs. Likes scatter plot
        fig1 = px.scatter(
            df_clean,
            x="view_count",
            y="like_count",
            size="comment_count" if "comment_count" in df.columns else None,
            hover_data=["title"] if "title" in df.columns else None,
            title="Views vs. Likes"
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Video type distribution
        if "video_type" in df.columns:
            video_type_counts = df["video_type"].value_counts().reset_index()
            video_type_counts.columns = ["video_type", "count"]

            fig2 = px.pie(
                video_type_counts,
                values="count",
                names="video_type",
                title="Video Type Distribution"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Required columns not available for metrics and visualizations.")
