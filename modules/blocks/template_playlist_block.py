import streamlit as st
import pandas as pd
import plotly.express as px
from utils.dataloader import get_user_dataframe

def template_playlist_block(df_nerdalytics, filter_manager):
    """
    Template block for playlist dataframe with visualizations.
    This block uses tbl_playlist_full_dedup as its main dataframe.

    Args:
        df_nerdalytics: Filtered nerdalytics dataframe (not used directly)
        filter_manager: Filter manager instance
    """
    st.subheader("Playlist Analysis")

    # Get playlist dataframe - this is the main dataframe for this block
    df_playlist = get_user_dataframe("tbl_playlist_full_dedup")

    if df_playlist is None:
        st.error("Could not load playlist dataframe")
        return

    # Apply filters
    filters = filter_manager.get_filter_state()
    filtered_df_playlist = df_playlist

    # Apply channel filter if it exists in the playlist dataframe
    if filters["channel"] and "playlist_channel_title" in filtered_df_playlist.columns:
        filtered_df_playlist = filtered_df_playlist[filtered_df_playlist["playlist_channel_title"].isin(filters["channel"])]

    # Apply playlist filter if specified
    if filters["playlists"] and "playlist_title" in filtered_df_playlist.columns:
        filtered_df_playlist = filtered_df_playlist[filtered_df_playlist["playlist_title"].isin(filters["playlists"])]

    # Show dataframe info
    st.write(f"Filtered playlist dataframe shape: \n{filtered_df_playlist.shape}")
    st.code(f"Filtered playlist dataframe columns: {filtered_df_playlist.columns}")

    # Show sample data
    with st.expander("Sample Data"):
        st.dataframe(filtered_df_playlist.head(10))

    # Basic metrics and visualizations
    if len(filtered_df_playlist) > 0:
        # Count unique playlists and videos
        unique_playlists = filtered_df_playlist["playlist_id"].nunique() if "playlist_id" in filtered_df_playlist.columns else 0
        unique_videos = filtered_df_playlist["video_id"].nunique() if "video_id" in filtered_df_playlist.columns else 0

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Unique Playlists", unique_playlists)
        with col2:
            st.metric("Unique Videos", unique_videos)

        # Playlist size distribution
        if "playlist_id" in filtered_df_playlist.columns and "video_id" in filtered_df_playlist.columns:
            playlist_sizes = filtered_df_playlist.groupby("playlist_id").size().reset_index(name="video_count")

            if "playlist_title" in filtered_df_playlist.columns:
                # Join with playlist titles
                playlist_titles = filtered_df_playlist[["playlist_id", "playlist_title"]].drop_duplicates()
                playlist_sizes = playlist_sizes.merge(playlist_titles, on="playlist_id", how="left")

                fig = px.bar(
                    playlist_sizes.sort_values("video_count", ascending=False).head(20),
                    x="playlist_title",
                    y="video_count",
                    title="Top 20 Playlists by Number of Videos"
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = px.bar(
                    playlist_sizes.sort_values("video_count", ascending=False).head(20),
                    x="playlist_id",
                    y="video_count",
                    title="Top 20 Playlists by Number of Videos"
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

        # Video overlap between playlists
        if "playlist_id" in filtered_df_playlist.columns and "video_id" in filtered_df_playlist.columns:
            # Count how many playlists each video appears in
            video_playlist_counts = filtered_df_playlist.groupby("video_id").size().reset_index(name="playlist_count")

            # Distribution of video appearances
            fig2 = px.histogram(
                video_playlist_counts,
                x="playlist_count",
                title="Distribution of Video Appearances Across Playlists",
                labels={"playlist_count": "Number of Playlists", "count": "Number of Videos"}
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No playlist data available after filtering.")
