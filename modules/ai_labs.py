import datetime

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from utils.dataloader import load_data
from utils.google_tag_manager import inject_gtm

# ==== CONFIGURABLE VARIABLES ====
SHOW_LEGEND = True  # Set to True to show legend
PLOT_HEIGHT = 850  # Use more vertical space on mobile
# ================================

# @st.cache_data
# def cached_labs_load(table_name: str):
#     df = labs_load(table_name)
#     return df


# # Load cached DataFrame
# df_slope_full = cached_labs_load("tbl_slope_full")

# new global cached , pre-cleaned ( casted columns date, ids) df
df_slope_full = load_data("tbl_slope_full")


def render():
    """
    Renderiza a página AI Labs (placeholder).
    """
    inject_gtm()
    st.title("🧪 AI Labs")

    st.divider()

    st.subheader("Data")
    code_block = f"""
    df_slope_full.shape : {df_slope_full.shape} \n
    df_slope_full.columns.tolist() : {df_slope_full.columns.tolist()} \n
    df_slope_full.describe() : {df_slope_full.describe()}
    """
    # df_slope_full.info()  : {df_slope_full.info()} \n <-- not supported

    st.code(code_block, language="python")
    st.divider()

    # --- Header Filters ---
    min_pub = df_slope_full["published_at"].min()
    max_pub = df_slope_full["published_at"].max()
    # Default date range: last year
    one_year_ago = max_pub.date() - datetime.timedelta(days=365)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        published_at_range = st.date_input(
            "Published At Range",
            value=(one_year_ago, max_pub.date()),
            min_value=min_pub.date(),
            max_value=max_pub.date(),
        )
        # Multi-select for default_audio_language
        lang_options = (
            df_slope_full["default_audio_language"].dropna().unique().tolist()
        )
        default_audio_language_selected = st.multiselect(
            "Audio Language", options=lang_options, default=lang_options
        )
    with col2:
        video_types = df_slope_full["video_type"].dropna().unique().tolist()
        video_type_selected = st.multiselect(
            "Video Type", options=video_types, default="Regular"
        )
        st.write("Select the channel : ")
        channel_selected = df_slope_full["channel_title"].dropna().unique().tolist()
        channel_selected = st.multiselect(
            "Channel", options=channel_selected, default=channel_selected
        )
    with col3:
        top_n = st.slider("Top N Results", min_value=1, max_value=50, value=10)
    # Duration slider (full-width below)
    min_duration = int(df_slope_full["duration_formatted_seconds"].min())
    max_duration = int(df_slope_full["duration_formatted_seconds"].max())
    duration_range = st.slider(
        "Duration (seconds)",
        min_value=min_duration,
        max_value=max_duration,
        value=(min_duration, max_duration),
        step=1,
    )
    # --- Text input filters ---
    col4, col5, col6 = st.columns(3)
    with col4:
        title_search = st.text_input("Title contains")
    with col5:
        description_search = st.text_input("Description contains")
    with col6:
        video_id_search = st.text_input("Video ID contains")

    # --- Normalization Toggle ---
    normalize_metrics = st.checkbox("Normalize metrics (x, y, z)", value=False)

    # Filter DataFrame based on selections
    filtered = df_slope_full[
        (df_slope_full["published_at"].dt.date >= published_at_range[0])
        & (df_slope_full["published_at"].dt.date <= published_at_range[1])
        & (df_slope_full["video_type"].isin(video_type_selected))
        & (df_slope_full["duration_formatted_seconds"] >= duration_range[0])
        & (df_slope_full["duration_formatted_seconds"] <= duration_range[1])
        & (
            df_slope_full["default_audio_language"].isin(
                default_audio_language_selected
            )
        )
        & (df_slope_full["channel_title"].isin(channel_selected))
    ]
    if title_search:
        filtered = filtered[
            filtered["title"].str.contains(title_search, case=False, na=False)
        ]
    if description_search:
        filtered = filtered[
            filtered["description"].str.contains(
                description_search, case=False, na=False
            )
        ]
    if video_id_search:
        filtered = filtered[
            filtered["video_id"].str.contains(video_id_search, case=False, na=False)
        ]

    # Get top N video_ids by max view_count_slope at latest slope_date (after filters)
    latest = (
        filtered.sort_values("slope_date").groupby("video_id", as_index=False).last()
    )
    top_ids = latest.nlargest(top_n, "view_count_slope")["video_id"]

    # Get all slope points for these video_ids
    df_top20 = filtered[filtered["video_id"].isin(top_ids)].copy()
    df_top20 = df_top20.sort_values(["video_id", "slope_date"])

    # Prepare data for plotting
    plot_df = df_top20.copy()
    if normalize_metrics and not plot_df.empty:
        for col in ["view_count_slope", "comment_count_slope", "like_count_slope"]:
            min_val = plot_df[col].min()
            max_val = plot_df[col].max()
            if max_val > min_val:
                plot_df[f"{col}_norm"] = (plot_df[col] - min_val) / (max_val - min_val)
            else:
                plot_df[f"{col}_norm"] = 0.0
        x_col = "view_count_slope_norm"
        y_col = "comment_count_slope_norm"
        z_col = "like_count_slope_norm"
        label_prefix = "[NORM] "
    else:
        x_col = "view_count_slope"
        y_col = "comment_count_slope"
        z_col = "like_count_slope"
        label_prefix = ""

    fig = go.Figure()

    valscount = 5
    vals = np.linspace(
        plot_df["slope_view_count_speed"].min(),
        plot_df["slope_view_count_speed"].max(),
        valscount,
    )

    for idx, (vid, group) in enumerate(plot_df.groupby("video_id")):
        hover_dates = (
            group["slope_date"].dt.strftime("%Y-%m-%d")
            if "slope_date" in group
            else [""] * len(group)
        )
        colorbar_dict = dict(
            title="Slope Speed",
            tickvals=vals,
            ticktext=[f"{v:,.0f}" for v in vals],  # Add thousands separator for clarity
            tickmode="array",
            showticklabels=True,
            tickfont=dict(size=11, family="Arial", color="black"),
            thickness=12,
            len=0.4,
            outlinewidth=1,
        )
        if SHOW_LEGEND:
            colorbar_dict.update(
                dict(
                    x=1.02,
                    y=0.5,
                    orientation="v",  # vertical, right
                )
            )
        else:
            colorbar_dict.update(
                dict(
                    x=0.5,
                    y=-0.25,
                    orientation="h",
                    xanchor="center",
                    yanchor="bottom",  # horizontal, below
                )
            )
        # Build hover label values for each row
        hover_texts = []
        for (_, row), date in zip(group.iterrows(), hover_dates):
            if normalize_metrics:
                view_val = f"{row[x_col]:.3f}"
                comment_val = f"{row[y_col]:.3f}"
                like_val = f"{row[z_col]:.3f}"
            else:
                view_val = f"{int(row[x_col]):,}"
                comment_val = f"{int(row[y_col]):,}"
                like_val = f"{int(row[z_col]):,}"
            hover_texts.append(
                f"{label_prefix}Title: {row['title']}<br><br>SPEED COUNTS:<br>Linear ViewSPD: {row['linear_view_count_speed']:.0f}<br>Slope ViewSPD: {row['slope_view_count_speed']:.0f}<br><br>METADATA:<br>Age in Days: {row['age_in_days']:.0f}<br>Observed Date: {date}<br><br>METRICS:<br>View count: {view_val}<br>Comment count: {comment_val}<br>Like count: {like_val}"
            )
        fig.add_trace(
            go.Scatter3d(
                x=group[x_col],
                y=group[y_col],
                z=group[z_col],
                mode="lines+markers",
                name=group["title"].iloc[0] if "title" in group.columns else vid,
                text=hover_texts,
                hoverinfo="text",
                marker=dict(
                    size=5,
                    color=group["slope_view_count_speed"],
                    coloraxis="coloraxis",
                    colorscale="solar",  # https://plotly.com/python/builtin-colorscales/ rainbow, turbo, viridis, sunsetdark
                    showscale=(idx == 0),
                    colorbar=colorbar_dict if idx == 0 else None,
                    opacity=0.8,
                ),
                line=dict(width=2),
            )
        )

    fig.update_layout(
        title="3D Slope Evolution:<br><sup>Top N Videos by View Count<br>(published after 2025)</sup>",
        scene=dict(
            xaxis=dict(
                title="View Count (slope)"
                if not normalize_metrics
                else "Normalized View Count (slope)",
                showbackground=True,
                backgroundcolor="#e6f0fa",
                gridcolor="#b0c4de",
                zerolinecolor="#b0c4de",
                showgrid=True,
                zeroline=True,
                showticklabels=True,
            ),
            yaxis=dict(
                title="Comment Count (slope)"
                if not normalize_metrics
                else "Normalized Comment Count (slope)",
                showbackground=True,
                backgroundcolor="#e6f0fa",
                gridcolor="#b0c4de",
                zerolinecolor="#b0c4de",
                showgrid=True,
                zeroline=True,
                showticklabels=True,
            ),
            zaxis=dict(
                title="Like Count (slope)"
                if not normalize_metrics
                else "Normalized Like Count (slope)",
                showbackground=True,
                backgroundcolor="#e6f0fa",
                gridcolor="#b0c4de",
                zerolinecolor="#b0c4de",
                showgrid=True,
                zeroline=True,
                showticklabels=True,
            ),
            aspectmode="cube",
        ),
        coloraxis=dict(
            colorscale="Plasma",
            colorbar=dict(
                title="Slope Speed",
                tickvals=vals,
                ticktext=[f"{v:,.0f}" for v in vals],
                tickmode="array",
                tickfont=dict(size=11, family="Arial", color="black"),
                thickness=12,
                len=0.4,
                x=1.02,
                y=0.5,
                orientation="v",
                outlinewidth=1,
                showticklabels=True,
            ),
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=8),
            title="",
            bgcolor="rgba(255,255,255,0.8)",
            itemwidth=80,
        ),
        showlegend=SHOW_LEGEND,
        autosize=False,
        height=PLOT_HEIGHT,
        width=None,
        margin=dict(l=0, r=0, t=60, b=0),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displayModeBar": True,
            "modeBarButtonsToAdd": [
                "zoomIn3d",
                "zoomOut3d",
                "resetCameraDefault3d",
                "resetCameraLastSave3d",
            ],
        },
    )

    # --- Show filtered results table ---
    st.markdown("### Filtered Results Table")
    st.dataframe(
        filtered[["video_id", "title", "published_at", "video_type"]]
        .sort_values("published_at", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )
