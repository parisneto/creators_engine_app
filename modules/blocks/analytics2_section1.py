# HISTORY: 2025-05-09 Made filters fully interdependent, added Reset button, merged more columns from df_nerdalytics, and implemented more analytics sections. See previous history below.
# HISTORY: 2025-05-09 Fixed Streamlit slider date bug and enriched DataFrame with view/like/comment/video_type from df_nerdalytics. See previous history below.
# HISTORY: 2025-05-09 Added analytics dashboard sections and filters, with Streamlit widgets and Plotly Express, following user instructions. Previous history preserved below.
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st


def analytics2_section1(df_nerdalytics, df_playlist_full_dedup):
    """
    Streamlit page for Playlist Analytics: KPIs, visualizations, and advanced analytics.
    Args:
        df_nerdalytics: DataFrame with video-level analytics (must include view_count, like_count, comment_count, etc.)
        df_playlist_full_dedup: DataFrame with playlist and video metadata.
    """

    # # JOIN df_nerdalytics and df_playlist_full_dedup + Enrichment
    # # --- Enrich df_playlist_full_dedup with analytics columns from df_nerdalytics ---
    # # Collect all ss_* columns
    # ss_cols = [col for col in df_nerdalytics.columns if col.startswith('ss_')]
    # cols_to_add = [
    #     'view_count', 'like_count', 'comment_count', 'video_type',
    #     'duration_formatted_seconds', 'category_id', 'tags', 'default_audio_language'
    # ] + ss_cols
    # cols_missing = [col for col in cols_to_add if col not in df_playlist_full_dedup.columns]
    # merge_cols = ['video_id'] + [col for col in cols_to_add if col in df_nerdalytics.columns]
    # if 'video_id' in df_playlist_full_dedup.columns and 'video_id' in df_nerdalytics.columns:
    #     df_enriched = df_playlist_full_dedup.merge(df_nerdalytics[merge_cols], on='video_id', how='left')
    # else:
    #     df_enriched = df_playlist_full_dedup.copy()
    df_enriched = df_playlist_full_dedup.copy()

    # --- 1. High-Level KPIs & Filters Widgets ---
    st.divider()
    st.header("1. High-Level KPIs & Filters")

    with st.popover("🎯 Playlist Filters", use_container_width=True):
        # --- Filters ---
        # -- FILTERS: Interdependent with Reset Button --
        # Session state for filters and playlists
        if "filters_reset" not in st.session_state:
            st.session_state["filters_reset"] = False
        if "selected_playlists" not in st.session_state:
            st.session_state["selected_playlists"] = None

        # Defaults
        date_col = (
            "video_added_at"
            if "video_added_at" in df_enriched.columns
            else "playlist_published_at"
        )
        df_enriched[date_col] = pd.to_datetime(df_enriched[date_col], errors="coerce")
        min_date = df_enriched[date_col].min()
        max_date = df_enriched[date_col].max()
        min_date_slider = (
            min_date.date() if pd.notnull(min_date) else datetime.today().date()
        )
        max_date_slider = (
            max_date.date() if pd.notnull(max_date) else datetime.today().date()
        )
        channel_options = (
            df_enriched["playlist_channel_title"].dropna().unique().tolist()
        )

        # Set/reset state
        reset_triggered = (
            st.button("Reset filters") or st.session_state["filters_reset"]
        )
        if reset_triggered:
            selected_channels = channel_options.copy()
            st.session_state["filters_reset"] = False
            st.session_state["selected_playlists"] = None
            date_range = (min_date_slider, max_date_slider)
            video_type = "All"
        else:
            selected_channels = st.multiselect(
                "Select channels", channel_options, default=channel_options
            )
            date_range = st.slider(
                "Select date range",
                min_value=min_date_slider,
                max_value=max_date_slider,
                value=(min_date_slider, max_date_slider),
                format="YYYY-MM-DD",
            )

        # Playlists available for selected channels
        filtered_playlists = (
            df_enriched[df_enriched["playlist_channel_title"].isin(selected_channels)][
                "playlist_title"
            ]
            .dropna()
            .unique()
            .tolist()
        )
        # Only set session state if not already set or invalid
        if st.session_state["selected_playlists"] is None or not set(
            st.session_state["selected_playlists"]
        ).issubset(filtered_playlists):
            st.session_state["selected_playlists"] = filtered_playlists.copy()
        # Use session state as value, not default, to avoid Streamlit warning
        # Ensure session state is valid before widget instantiation
        if st.session_state["selected_playlists"] is None or not set(
            st.session_state["selected_playlists"]
        ).issubset(filtered_playlists):
            st.session_state["selected_playlists"] = filtered_playlists.copy()
        selected_playlists = st.multiselect(
            "Select playlists",
            filtered_playlists,
            default=st.session_state["selected_playlists"],
            key="selected_playlists",
        )
        # Do NOT set st.session_state['selected_playlists'] after the widget!

        # Video type radio
        video_type_options = ["All"]
        if "video_type" in df_enriched.columns:
            video_type_options += sorted(
                [
                    v
                    for v in df_enriched["video_type"].dropna().unique()
                    if v not in video_type_options
                ]
            )
        else:
            video_type_options += ["Regular", "Shorts"]
        video_type = st.radio("Video type", video_type_options)

        # Filter DataFrame
        df_filtered = df_enriched[
            (df_enriched[date_col].dt.date >= date_range[0])
            & (df_enriched[date_col].dt.date <= date_range[1])
            & (df_enriched["playlist_channel_title"].isin(selected_channels))
            & (df_enriched["playlist_title"].isin(selected_playlists))
        ].copy()
        if video_type != "All" and "video_type" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["video_type"] == video_type]

    st.subheader("Metrics Panel : ")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Views",
            int(df_filtered["view_count"].sum())
            if "view_count" in df_filtered
            else "N/A",
        )
        st.metric(
            "Total Likes",
            int(df_filtered["like_count"].sum())
            if "like_count" in df_filtered
            else "N/A",
        )
        st.metric(
            "Total Comments",
            int(df_filtered["comment_count"].sum())
            if "comment_count" in df_filtered
            else "N/A",
        )
    with col2:
        st.metric(
            "Avg Views per Video",
            round(df_filtered["view_count"].mean(), 1)
            if "view_count" in df_filtered
            else "N/A",
        )
        st.metric(
            "Avg Views per Playlist",
            round(df_filtered.groupby("playlist_id")["view_count"].sum().mean(), 1)
            if "view_count" in df_filtered and "playlist_id" in df_filtered
            else "N/A",
        )
    with col3:
        st.metric(
            "Unique Videos",
            df_filtered["video_id"].nunique() if "video_id" in df_filtered else "N/A",
        )
        st.metric(
            "Unique Playlists",
            df_filtered["playlist_id"].nunique()
            if "playlist_id" in df_filtered
            else "N/A",
        )

    # --- 2. Playlist-Level Performance ---
    st.divider()
    st.header("2. Playlist-Level Performance")
    # 2.1 Accumulated Views by Playlist
    st.subheader("2.1 Accumulated Views by Playlist")
    if "view_count" in df_filtered:
        playlist_views = (
            df_filtered.groupby(["playlist_title", "playlist_id"])["view_count"]
            .sum()
            .reset_index()
        )
        playlist_views = playlist_views.sort_values("view_count", ascending=True)
        fig1 = px.bar(
            playlist_views,
            x="view_count",
            y="playlist_title",
            orientation="h",
            hover_data=["playlist_id"],
            title="Total Views by Playlist",
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("view_count column not available for Playlist-Level Performance.")
    # 2.2 Engagement Ratios
    st.subheader("2.2 Engagement Ratios (Likes/Views vs Comments/Views)")
    if all(
        col in df_filtered
        for col in ["playlist_id", "view_count", "like_count", "comment_count"]
    ):
        playlist_eng = (
            df_filtered.groupby("playlist_id")
            .agg(
                {
                    "view_count": "sum",
                    "like_count": "sum",
                    "comment_count": "sum",
                    "playlist_title": "first",
                }
            )
            .reset_index()
        )
        playlist_eng["likes_per_view"] = (
            playlist_eng["like_count"] / playlist_eng["view_count"]
        )
        playlist_eng["comments_per_view"] = (
            playlist_eng["comment_count"] / playlist_eng["view_count"]
        )
        ratio_option = st.selectbox(
            "Select ratio to highlight", ["likes_per_view", "comments_per_view"]
        )
        fig2 = px.scatter(
            playlist_eng,
            x="likes_per_view",
            y="comments_per_view",
            size="view_count",
            color="playlist_title",
            hover_data=["playlist_id"],
            title="Engagement Ratios by Playlist",
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Required columns not available for Engagement Ratios.")

    # --- 3. Video-Level Distributions ---
    st.divider()
    st.header("3. Video-Level Distributions")
    # 3.1 Views vs Age
    st.subheader("3.1 Views vs Age")
    if "playlist_item_published_at" in df_filtered and "view_count" in df_filtered:
        df_filtered["playlist_item_published_at"] = pd.to_datetime(
            df_filtered["playlist_item_published_at"], errors="coerce"
        )
        df_filtered["age_in_days"] = (
            datetime.now() - df_filtered["playlist_item_published_at"]
        ).dt.days
        show_trend = st.checkbox("Show trendline (LOWESS)", value=False)
        fig3 = px.scatter(
            df_filtered,
            x="age_in_days",
            y="view_count",
            trendline="lowess" if show_trend else None,
            hover_data=["video_id", "playlist_title"],
            title="Views vs Video Age",
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Required columns not available for Views vs Age.")
    # 3.2 Duration Impact
    st.subheader("3.2 Duration Impact")
    if "duration_formatted_seconds" in df_filtered and "view_count" in df_filtered:
        duration_min = int(df_filtered["duration_formatted_seconds"].min())
        duration_max = int(df_filtered["duration_formatted_seconds"].max())
        duration_range = st.slider(
            "Duration range (seconds)",
            min_value=duration_min,
            max_value=duration_max,
            value=(duration_min, duration_max),
        )
        df_dur = df_filtered[
            (df_filtered["duration_formatted_seconds"] >= duration_range[0])
            & (df_filtered["duration_formatted_seconds"] <= duration_range[1])
        ]
        fig4 = px.density_heatmap(
            df_dur,
            x="duration_formatted_seconds",
            y="view_count",
            nbinsx=40,
            nbinsy=40,
            title="Duration vs View Count",
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("duration_formatted_seconds or view_count not found.")

    # --- 4. Overlap & Flow Analyses ---
    st.divider()
    st.header("4. Overlap & Flow Analyses")
    st.subheader("4.1 Playlist ↔ Video Sankey")
    # Sankey implementation: show video flow between playlists
    if "video_id" in df_filtered and "playlist_id" in df_filtered:
        # Build mapping: video_id -> playlists
        video_playlist = df_filtered[
            ["video_id", "playlist_id", "playlist_title"]
        ].drop_duplicates()
        # Count how many playlists each video is present in
        video_counts = (
            video_playlist.groupby("video_id").size().reset_index(name="playlist_count")
        )
        # For Sankey: source = playlist A, target = playlist B, value = count of shared videos
        # For simplicity: show top N playlists by number of shared videos
        top_playlists = (
            video_playlist["playlist_id"].value_counts().nlargest(15).index.tolist()
        )
        sankey_df = video_playlist[video_playlist["playlist_id"].isin(top_playlists)]
        pairs = sankey_df.merge(sankey_df, on="video_id")
        pairs = pairs[pairs["playlist_id_x"] != pairs["playlist_id_y"]]
        # Filter out very small flows for clarity
        sankey_links = (
            pairs.groupby(["playlist_title_x", "playlist_title_y"])
            .size()
            .reset_index(name="count")
        )
        sankey_links = sankey_links[
            sankey_links["count"] > 1
        ]  # Only show links with >1 shared video

        # Shorten/wrap long labels
        def short_label(label, maxlen=25):
            return label if len(label) <= maxlen else label[: maxlen - 3] + "..."

        sankey_links["playlist_title_x"] = sankey_links["playlist_title_x"].apply(
            lambda x: short_label(str(x))
        )
        sankey_links["playlist_title_y"] = sankey_links["playlist_title_y"].apply(
            lambda x: short_label(str(x))
        )
        labels = list(
            set(sankey_links["playlist_title_x"]).union(
                set(sankey_links["playlist_title_y"])
            )
        )
        label_idx = {label: i for i, label in enumerate(labels)}
        # Assign distinct colors for nodes using Plotly palette
        import plotly.colors as pc

        palette = pc.qualitative.Plotly
        node_colors = [palette[i % len(palette)] for i in range(len(labels))]
        import plotly.graph_objects as go

        sankey_data = dict(
            type="sankey",
            arrangement="snap",  # helps center the diagram
            node=dict(
                label=labels,
                pad=30,
                thickness=30,
                color=node_colors,
                line=dict(color="black", width=0.5),
            ),
            link=dict(
                source=[label_idx[src] for src in sankey_links["playlist_title_x"]],
                target=[label_idx[tgt] for tgt in sankey_links["playlist_title_y"]],
                value=sankey_links["count"].tolist(),
                color="rgba(180,180,180,0.25)",
            ),
        )
        fig_sankey = go.Figure(data=[sankey_data])
        fig_sankey.update_layout(
            title_text="Playlist ↔ Playlist Video Overlap Sankey (Top 15 Playlists)",
            font=dict(size=18),
            margin=dict(l=40, r=40, t=60, b=40),
            height=700,
            autosize=True,
        )
        # Center the diagram in the Streamlit container
        st.plotly_chart(fig_sankey, use_container_width=True)
    else:
        st.info(
            "Sankey diagram requires playlist/video overlap logic and view counts. Columns needed: video_id, playlist_id."
        )
    st.subheader("4.2 Bipartite Network Graph (placeholder)")
    st.info(
        "Bipartite graph requires networkx/pyvis and edge data. Implement if needed."
    )

    # --- 5. Temporal & Cohort Analysis ---
    st.divider()
    st.header("5. Temporal & Cohort Analysis")
    st.subheader("5.1 Time Series of Playlist Growth")
    if "playlist_item_published_at" in df_filtered and "view_count" in df_filtered:
        df_filtered["playlist_item_published_at"] = pd.to_datetime(
            df_filtered["playlist_item_published_at"], errors="coerce"
        )
        df_filtered = df_filtered.sort_values("playlist_item_published_at")
        df_filtered["cum_views"] = df_filtered.groupby("playlist_id")[
            "view_count"
        ].cumsum()
        fig7 = px.line(
            df_filtered,
            x="playlist_item_published_at",
            y="cum_views",
            color="playlist_title",
            title="Cumulative Views by Playlist Over Time",
        )
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.info("playlist_item_published_at or view_count not found.")
    st.subheader("5.2 Video Release Cohorts")
    if "playlist_item_published_at" in df_filtered and "view_count" in df_filtered:
        df_filtered["cohort_month"] = df_filtered[
            "playlist_item_published_at"
        ].dt.to_period("M")
        df_filtered["days_since_release"] = (
            df_filtered["playlist_item_published_at"]
            - df_filtered["playlist_item_published_at"].min()
        ).dt.days
        cohort_group = (
            df_filtered.groupby(["cohort_month", "days_since_release"])["view_count"]
            .median()
            .reset_index()
        )
        fig8 = px.line(
            cohort_group,
            x="days_since_release",
            y="view_count",
            color=cohort_group["cohort_month"].astype(str),
            title="Median Views by Cohort Month",
        )
        st.plotly_chart(fig8, use_container_width=True)
    else:
        st.info(
            "playlist_item_published_at or view_count not found for cohort analysis."
        )

    # --- 6. Content & Category Breakdown ---
    st.divider()
    st.header("6. Content & Category Breakdown")
    st.subheader("6.1 Treemap by Category/Tags")
    # # Drop rows with None/NaN in category_id or playlist_title for treemap
    # treemap_df = df_filtered.dropna(subset=['category_id', 'playlist_title', 'view_count']) <--- NEEDS .copy()
    # treemap_df['category_id'] = treemap_df['category_id'].astype(str)
    # treemap_df['playlist_title'] = treemap_df['playlist_title'].astype(str)
    # beeter version with copy and astype properly
    treemap_df = (
        df_filtered.dropna(subset=["category_id", "playlist_title", "view_count"])
        .copy()
        .astype({"category_id": str, "playlist_title": str})
    )

    if (
        not treemap_df.empty
        and "category_id" in treemap_df
        and "view_count" in treemap_df
    ):
        fig5 = px.treemap(
            treemap_df,
            path=["category_id", "playlist_title"],
            values="view_count",
            title="Treemap by Category",
        )
        st.plotly_chart(fig5, use_container_width=True)
    elif "tags" in df_filtered and "view_count" in df_filtered:
        # Optional: parse tags if comma-separated
        st.info("Tags-based treemap not implemented; add tag parsing if needed.")
    else:
        st.info("category_id/tags column not found. Add these to enable treemap.")
    st.subheader("6.2 Language & Content Sensitivity")
    ss_cols_present = [col for col in df_filtered.columns if col.startswith("ss_")]
    if (
        "default_audio_language" in df_filtered or ss_cols_present
    ) and "view_count" in df_filtered:
        cols = ["default_audio_language"] + ss_cols_present
        melted = df_filtered.melt(
            id_vars=["view_count"],
            value_vars=cols,
            var_name="feature",
            value_name="value",
        )
        fig6 = px.bar(
            melted,
            x="feature",
            y="view_count",
            color="value",
            barmode="group",
            title="Language & Content Sensitivity",
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info(
            "default_audio_language or ss_* columns not found. Add these to enable this section."
        )

    # --- 7. Comparative & Predictive Modeling ---
    st.divider()
    st.header("7. Comparative & Predictive Modeling")
    st.subheader("7.1 Channel-to-Channel Benchmark (placeholder)")
    st.info(
        "Implement: Radar chart of channel metrics. Requires more channel-level data."
    )
    st.subheader("7.2 Forecasting Future Views (placeholder)")
    st.info("Implement: Time-series forecasting for playlists/videos.")

    # --- 8. Advanced Drill-Down & Recommendations ---
    st.divider()
    st.header("8. Advanced Drill-Down & Recommendations")
    st.subheader("8.1 Video Clustering (placeholder)")
    clustering_features = [
        col
        for col in ["view_count", "like_count", "duration_formatted_seconds"]
        if col in df_filtered
    ]
    if len(clustering_features) >= 2:
        st.info(
            f"Ready for clustering: features available: {clustering_features}. Implement t-SNE/UMAP for 2D embedding."
        )
        # Placeholder for clustering implementation
    else:
        st.info(
            "Requires clustering features (view_count, like_count, duration, tags embedding, etc.)."
        )
    st.subheader("8.2 'Next Best Playlist' Suggestion (placeholder)")
    st.info("Requires tag similarity + performance metrics. Add logic as needed.")

    # --- ADVANCED SECTION REQUIREMENTS (EXPLANATIONS) ---
    # Sankey: Need playlist-video mapping, views per video/playlist, and how to define 'flow'. Use Plotly Sankey.
    # Bipartite: Need playlist_id <-> video_id edges, edge weights (views/position), top N nodes. Use networkx/pyvis.
    # Radar chart: Need channel-level aggregates (avg views/video, engagement), and which metrics/channels to compare.
    # Forecasting: Need time series of views per playlist/video. Use Prophet or statsmodels.
    # Next Best Playlist: Need tags and metrics for videos, tags for new video, and a similarity/optimization method.
