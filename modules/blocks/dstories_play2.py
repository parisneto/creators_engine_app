import streamlit as st


def render(df):
    """
    More Analysis block for Data Stories. Receives a filtered DataFrame.
    """
    st.subheader("Further Analysis - Playlists")
    if df is None or df.empty:
        st.warning("No data available after filtering. Try adjusting your filters.")
        return
    st.write(f"DataFrame shape: {df.shape}")
    # Example: Show a value count for a column if it exists
    if "channel_title" in df.columns:
        st.bar_chart(df["channel_title"].value_counts())
    # Example: Show a table of the top 10 videos by views (if column exists)
    if "view_count" in df.columns:
        top_videos = df.sort_values("view_count", ascending=False).head(10)
        st.write("Top 10 Videos by View Count:")
        st.dataframe(top_videos)
