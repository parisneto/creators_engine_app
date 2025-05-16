import streamlit as st


def render(df):
    """
    Overview block for Data Stories. Receives a filtered DataFrame.
    """
    st.subheader("Filtered Data Overview - Playlists")
    if df is None or df.empty:
        st.warning("No data available after filtering. Try adjusting your filters.")
        return
    st.write(f"DataFrame shape: {df.shape}")
    st.write(f"Columns: {list(df.columns)}")
    # with st.expander("Sample Data"):
    # st.json(df.head(10).to_dict())
    # Example: Show counts for key columns
    if "playlist_channel_title" in df.columns:
        st.write(f"Unique Channels: {df['playlist_channel_title'].nunique()}")
    if "playlist_title" in df.columns:
        st.write(f"Unique Playlists: {df['playlist_title'].nunique()}")
    if "default_audio_language" in df.columns:
        st.write(f"Languages: {df['default_audio_language'].unique().tolist()}")
    # Example plot (if plotly/matplotlib is available)

    if "video_type" in df.columns:
        import plotly.express as px

        fig = px.histogram(df, x="video_type", title="Distribution of Video Types")
        st.plotly_chart(fig, use_container_width=True)
