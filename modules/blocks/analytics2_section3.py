# HISTORY: 2025-05-09 Added channel-level radar chart analytics page with channel filter, metric calculations, and Plotly radar chart. See previous history below.
import pandas as pd
import plotly.express as px
import streamlit as st


def analytics2_section3(df_nerdalytics, df_playlist_full_dedup):
    """
    Streamlit page for channel-level radar chart analytics.
    Args:
        df_nerdalytics: DataFrame with video-level analytics.
        df_playlist_full_dedup: DataFrame with playlist and video metadata.
    """
    # Use the pre-enriched dataframe
    df_enriched = df_playlist_full_dedup.copy()

    # Step 2: Channel filter (shared with analytics2)
    filters = st.session_state.get("analytics2_filters", {})
    selected_channels = filters.get("channel", [])
    channel_options = df_enriched["playlist_channel_title"].dropna().unique().tolist()
    if not selected_channels:
        selected_channels = channel_options
    df_filtered = df_enriched[
        df_enriched["playlist_channel_title"].isin(selected_channels)
    ]

    st.header("Channel Radar Chart Comparison")
    st.write(f"Comparing channels: {', '.join(selected_channels)}")

    # Step 3: Channel-level metric calculations
    # --- Helper: Safe division ---
    def safe_div(a, b):
        return a / b if b else 0

    # --- Step 3.1: Prepare groupby ---
    channel_group = df_filtered.groupby("playlist_channel_title")
    radar_metrics = []
    for channel, group in channel_group:
        # --- 1. Size & Breadth ---
        n_playlists = group["playlist_id"].nunique()
        total_videos = group["video_id"].count()
        unique_videos = group["video_id"].nunique()
        avg_playlist_size = safe_div(total_videos, n_playlists)
        # --- 2. Overlap & Redundancy ---
        overlap_ratio = 1 - safe_div(unique_videos, total_videos)
        avg_appearances_per_video = safe_div(total_videos, unique_videos)
        # --- 3. Engagement Sums & Averages ---
        total_views = group["view_count"].sum()
        total_likes = group["like_count"].sum()
        total_comments = group["comment_count"].sum()
        avg_views_per_video = safe_div(total_views, total_videos)
        avg_like_to_view = safe_div(total_likes, total_views)
        avg_comment_to_view = safe_div(total_comments, total_views)
        # --- 4. Growth & Velocity ---
        group_dates = pd.to_datetime(
            group["video_added_at"], errors="coerce"
        ).sort_values()
        playlist_lifespan_days = (
            (group_dates.max() - group_dates.min()).days if not group_dates.empty else 0
        )
        playlist_lifespan_months = safe_div(playlist_lifespan_days, 30.44)
        avg_time_between_adds = (
            group_dates.diff().dt.days.mean() if len(group_dates) > 1 else 0
        )
        new_playlists_per_month = safe_div(n_playlists, playlist_lifespan_months)
        videos_per_month = safe_div(total_videos, playlist_lifespan_months)
        # --- 5. Efficiency & Reach ---
        views_per_month = safe_div(total_views, playlist_lifespan_months)
        views_per_video_added = safe_div(total_views, total_videos)
        # --- 6. Diversity & Topical Coverage ---
        n_categories = group["category_id"].nunique() if "category_id" in group else 0
        # Tags: explode and count unique
        tags_series = (
            group["tags"]
            .dropna()
            .apply(lambda x: x if isinstance(x, list) else str(x).split(","))
        )
        n_tags = (
            len(set([tag.strip() for tags in tags_series for tag in tags]))
            if not tags_series.empty
            else 0
        )
        # Language mix
        lang_counts = group["default_audio_language"].value_counts(normalize=True)
        lang_ptbr = lang_counts.get("pt-BR", 0)
        # --- 7. Relative Channel-Level Ratios ---
        channel_total_videos = df_nerdalytics[
            df_nerdalytics["channel_title"] == channel
        ]["video_id"].nunique()
        channel_total_views = df_nerdalytics[
            df_nerdalytics["channel_title"] == channel
        ]["view_count"].sum()
        pct_videos_in_playlists = safe_div(unique_videos, channel_total_videos)
        pct_views_in_playlists = safe_div(total_views, channel_total_views)
        # --- Collect ---
        radar_metrics.append(
            {
                "channel": channel,
                "n_playlists": n_playlists,
                "total_videos": total_videos,
                "unique_videos": unique_videos,
                "avg_playlist_size": avg_playlist_size,
                "overlap_ratio": overlap_ratio,
                "avg_appearances_per_video": avg_appearances_per_video,
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "avg_views_per_video": avg_views_per_video,
                "avg_like_to_view": avg_like_to_view,
                "avg_comment_to_view": avg_comment_to_view,
                "playlist_lifespan_months": playlist_lifespan_months,
                "avg_time_between_adds": avg_time_between_adds,
                "new_playlists_per_month": new_playlists_per_month,
                "videos_per_month": videos_per_month,
                "views_per_month": views_per_month,
                "views_per_video_added": views_per_video_added,
                "n_categories": n_categories,
                "n_tags": n_tags,
                "lang_ptbr": lang_ptbr,
                "pct_videos_in_playlists": pct_videos_in_playlists,
                "pct_views_in_playlists": pct_views_in_playlists,
            }
        )

    df_radar = pd.DataFrame(radar_metrics)
    if df_radar.empty:
        st.info("No data for selected channels.")
        return

    # Step 4: Select metrics for radar chart
    metric_labels = {
        "avg_playlist_size": "Avg Playlist Size",
        "overlap_ratio": "Overlap Ratio",
        "avg_appearances_per_video": "Appearances/Video",
        "avg_views_per_video": "Avg Views/Video",
        "avg_like_to_view": "Like-to-View",
        "avg_comment_to_view": "Comment-to-View",
        "videos_per_month": "Videos/Month",
        "views_per_month": "Views/Month",
        "n_categories": "Categories",
        "n_tags": "Tags",
        "lang_ptbr": "% pt-BR",
        "pct_videos_in_playlists": "% Videos in Playlists",
        "pct_views_in_playlists": "% Views in Playlists",
    }
    selected_metrics = st.multiselect(
        "Select metrics for radar chart",
        options=list(metric_labels.keys()),
        default=[
            "avg_playlist_size",
            "avg_views_per_video",
            "overlap_ratio",
            "videos_per_month",
            "n_categories",
        ],
        format_func=lambda x: metric_labels.get(x, x),
    )
    if not selected_metrics:
        st.warning("Select at least one metric.")
        return

    # Step 5: Normalize metrics for radar (min-max per metric)
    df_radar_norm = df_radar.copy()
    for m in selected_metrics:
        minv, maxv = df_radar[m].min(), df_radar[m].max()
        if minv == maxv:
            df_radar_norm[m] = 0.5  # identical values
        else:
            df_radar_norm[m] = (df_radar[m] - minv) / (maxv - minv)

    # Step 6: Plotly radar chart (reshape to long-form for Plotly)
    radar_long = df_radar_norm.melt(
        id_vars=["channel"],
        value_vars=selected_metrics,
        var_name="metric",
        value_name="value",
    )
    radar_long["metric_label"] = radar_long["metric"].map(metric_labels)
    fig = px.line_polar(
        radar_long,
        r="value",
        theta="metric_label",
        color="channel",
        line_close=True,
        template="plotly_dark",
        markers=True,
    )
    fig.update_traces(fill="toself")
    st.plotly_chart(fig, use_container_width=True)

    # Step 7: Show raw metrics table
    with st.expander("Show raw channel metrics"):
        df_display = (
            df_radar.set_index("channel")[selected_metrics]
            .rename(columns=metric_labels)
            .copy()
        )
        # Format overlap ratio as percent, others as 2 decimals
        formatters = {col: "{:,.2f}".format for col in df_display.columns}
        overlap_label = metric_labels.get("overlap_ratio", "Overlap Ratio")
        if overlap_label in df_display.columns:
            formatters[overlap_label] = (
                lambda x: f"{x * 100:,.2f}%" if pd.notnull(x) else ""
            )
        st.dataframe(df_display.style.format(formatters))

    # Step 8: Notes
    st.caption("""
    Metrics are normalized per metric for radar chart comparability. Raw values are shown below. For definitions, see the page plan or hover metric names.
    """)
