"""
External block example for modular Streamlit page framework.
"""
import streamlit as st
from utils.dataloader import load_data
from utils.config import APPMODE

def debugtools1():
    st.header("Debug Tools 1")
    st.write("Debug Tools 1 content here.")
    st.write("APPMODE : ", APPMODE)

    # st.balloons()


    st.markdown("---")
    df_nerdalytics = load_data("tbl_nerdalytics")
    st.divider()
    st.code(df_nerdalytics["view_count"].describe())
    st.divider()


    # Capture info() output as string using StringIO
    import io
    buffer = io.StringIO()
    df_nerdalytics.info(buf=buffer)
    nerdinfo = buffer.getvalue()
    st.write("nerdinfo : ")
    st.code(nerdinfo, language="python")


    st.markdown("---")


    st.markdown("---")
    st.write("df_nerdalytics.describe() : ", df_nerdalytics.describe())
    st.markdown("---")

    # Add safety check before using sample()
    if not df_nerdalytics.empty:
        st.write("df_nerdalytics.sample(5) : ", df_nerdalytics.sample(5))
    else:
        st.write("df_nerdalytics is empty - cannot show sample")
    st.markdown("---")




    st.markdown("---")
    df_vw_playlist = load_data("tbl_vw_playlist")
    # Capture info() output as string using StringIO
    import io
    buffer = io.StringIO()
    df_vw_playlist.info(buf=buffer)
    vw_playlistinfo = buffer.getvalue()
    st.write("vw_playlistinfo : ")
    st.code(vw_playlistinfo, language="python")


    st.markdown("---")


    st.markdown("---")
    st.write("df_vw_playlist.describe() : ", df_vw_playlist.describe())
    st.markdown("---")

    # Add safety check before using sample()
    if not df_vw_playlist.empty:
        st.write("df_vw_playlist.sample(5) : ", df_vw_playlist.sample(5))
    else:
        st.write("df_vw_playlist is empty - cannot show sample")
    st.markdown("---")



