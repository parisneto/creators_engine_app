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
    with st.expander("Sample Data"):
        st.dataframe(df.head(10))
    # Example: Show counts for key columns
    if "channel_title" in df.columns:
        st.write(f"Unique Channels: {df['channel_title'].nunique()}")
    if "video_type" in df.columns:
        st.write(f"Video Types: {df['video_type'].unique().tolist()}")
    if "default_audio_language" in df.columns:
        st.write(f"Languages: {df['default_audio_language'].unique().tolist()}")
    # Example plot (if plotly/matplotlib is available)
    if "video_type" in df.columns:
        import plotly.express as px

        fig = px.histogram(df, x="video_type", title="Distribution of Video Types")
        st.plotly_chart(fig, use_container_width=True)
