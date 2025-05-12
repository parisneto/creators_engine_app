import streamlit as st

def analytics2_section5(df_nerdalytics, df_playlist_full_dedup):
    st.write("This is the page for Playlists")
    st.dataframe(df_playlist_full_dedup)
