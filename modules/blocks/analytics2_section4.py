import streamlit as st

def analytics2_section4(df_nerdalytics, df_playlist_full_dedup):
    st.write("This is the page for Correlações")
    st.dataframe(df_playlist_full_dedup)
