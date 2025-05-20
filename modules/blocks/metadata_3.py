import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st


def render(df):
    """
    More Analysis block for Data Stories. Receives a filtered DataFrame.
    """

    if df is None or df.empty:
        st.warning("No data available after filtering. Try adjusting your filters.")
        return
    st.code(df.columns.tolist(), language="python")

    st.subheader("Missing Values by Column")

    nulls = df.isna().sum().sort_values(ascending=False)
    fig = px.bar(
        nulls[nulls > 0].reset_index(),
        x="index",
        y=0,
        labels={"index": "column", "0": "# missing"},
        title="Missing Values by Column",
    )
    st.plotly_chart(fig)

    st.subheader("Empty vs Non-Empty Tags")

    tag_empty = df["tags"].isna() | (df["tags"].str.len() == 0)
    df_tags = (
        tag_empty.value_counts().rename_axis("empty_tags").reset_index(name="count")
    )
    fig = px.pie(
        df_tags, names="empty_tags", values="count", title="Empty vs Non-Empty Tags"
    )
    st.plotly_chart(fig)

    st.subheader("Categorical Feature Distributions")
    for col in [
        "default_audio_language",
        "live_content",
        "video_type",
        "channel_group",
    ]:
        vc = (
            df[col]
            .fillna("‹missing›")
            .value_counts()
            .rename_axis(col)
            .reset_index(name="count")
        )
        fig = px.bar(vc, x=col, y="count", title=f"Distribution of {col}")
        st.plotly_chart(fig)

    st.subheader("Numeric Feature Distributions")
    for col in ["view_count", "like_count", "comment_count", "age_in_days"]:
        fig = px.histogram(df, x=col, nbins=50, title=f"{col} Distribution")
        fig.update_yaxes(type="log")
        st.plotly_chart(fig)
    fig = px.box(df, y="view_count", title="View-Count Boxplot")
    st.plotly_chart(fig)

    st.subheader("Temporal Trends")
    df["pub_date"] = pd.to_datetime(df["published_at"]).dt.date
    times = df.groupby("pub_date").size().reset_index(name="n_videos")
    fig = px.line(times, x="pub_date", y="n_videos", title="Videos Published Over Time")
    st.plotly_chart(fig)
    avg = df.groupby("age_in_days")["view_count"].mean().reset_index()
    fig = px.line(avg, x="age_in_days", y="view_count", title="Avg Views vs Age (days)")
    st.plotly_chart(fig)

    st.subheader("Feature Relationships & Correlation")
    fig = px.scatter(
        df, x="view_count", y="like_count", trendline="ols", title="Views vs Likes"
    )
    st.plotly_chart(fig)
    fig = px.scatter_matrix(
        df, dimensions=["view_count", "like_count", "comment_count", "age_in_days"]
    )
    st.plotly_chart(fig)
    corr = df[["view_count", "like_count", "comment_count", "age_in_days"]].corr()
    fig_corr, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig_corr)

    st.subheader("Content-Safety Flags")
    flags = ["ss_adult", "ss_spoof", "ss_medical", "ss_violence", "ss_racy"]
    df_flags = df[flags].sum().reset_index(name="count")
    fig = px.bar(df_flags, x="index", y="count", title="Content-Safety Flag Counts")
    st.plotly_chart(fig)

    # st.subheader("Tags & Caption Analysis")
    # df["n_tags"] = df["tags"].apply(lambda t: len(t) if isinstance(t, list) else 0)
    # fig = px.histogram(df, x="n_tags", nbins=20, title="Tags/Video")
    # st.plotly_chart(fig)
    # has_cap = df["caption"].notna()
    # df_cap = (
    #     has_cap.value_counts()
    #     .reset_index(name="count")
    #     .rename(columns={"index": "has_caption"})
    # )
    # fig = px.pie(
    #     df_cap,
    #     names="has_caption",
    #     values="count",
    #     title="Videos with/without Captions",
    # )
    # st.plotly_chart(fig)

    st.subheader("Tags & Caption Analysis")
    df["n_tags"] = df["tags"].apply(lambda t: len(t) if isinstance(t, list) else 0)
    fig = px.histogram(df, x="n_tags", nbins=20, title="Tags/Video")
    st.plotly_chart(fig)

    has_cap_series = df["caption"].notna()

    # Create df_cap with explicit string labels
    df_cap = (
        pd.DataFrame(
            {
                "has_caption": has_cap_series.map(
                    {True: "Has Caption", False: "No Caption"}
                ),
                "count": 1,  # A temporary placeholder for counting
            }
        )
        .groupby("has_caption")
        .count()
        .reset_index()
    )

    fig = px.pie(
        df_cap,
        names="has_caption",  # This column now contains "Has Caption" and "No Caption"
        values="count",
        title="Videos with/without Captions",
    )
    st.plotly_chart(fig)
