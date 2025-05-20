import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from config.VideoCategorieslist import categories_br


def render(df):
    """
    Enhanced visualization block for metadata analysis with metric selection.

    Features:
    - Interactive metric selection (Count, Views, Likes, Comments)
    - Configurable top N items to display
    - Multiple visualization types (Pie, Treemap, Bar charts)
    - Category ID mapping to human-readable names

    Parameters:
    df (pd.DataFrame): Input dataframe containing video metadata
    """
    if df is None or df.empty:
        st.warning("No data available after filtering. Try adjusting your filters.")
        return

    # Add configuration options in sidebar
    st.sidebar.subheader("Chart Configuration")
    top_n = st.sidebar.slider(
        "Number of top items to show:",
        min_value=5,
        max_value=30,
        value=10,  # Default value
        help="Adjust the number of top items to display in the charts",
    )

    # Define available metrics
    metric_options = {
        "Count": "count",
        "Total Views": "view_count",
        "Total Likes": "like_count",
        "Total Comments": "comment_count",
    }

    # Add a metric selector
    selected_metric = st.radio(
        "Select Metric:",
        options=list(metric_options.keys()),
        horizontal=True,
        index=0,  # Default to 'Count'
    )

    st.divider()
    st.subheader("Pie Chart of video types")

    # Pie Chart
    if "video_type" in df.columns:
        if selected_metric == "Count":
            # For count, we can use value_counts
            type_data = df["video_type"].value_counts().reset_index()
            type_data.columns = ["video_type", "value"]
            values_col = "value"
        else:
            # For other metrics, we need to group and sum
            type_data = df.groupby("video_type", as_index=False)[
                metric_options[selected_metric]
            ].sum()
            values_col = metric_options[selected_metric]

        # Sort and limit to top N
        type_data = type_data.sort_values("value", ascending=False).head(top_n)

        fig = px.pie(
            type_data,
            names="video_type",
            values=values_col,
            title=f"Proportion of Video Types by {selected_metric} (Top {min(top_n, len(type_data))} shown)",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="%{label}: %{value:,.0f} (%{percent})",
            texttemplate="%{label}<br>%{percent:.1%}",
            textfont=dict(size=14),
        )
        fig.update_layout(
            height=500,
            showlegend=False,
            margin=dict(t=50, b=20, l=20, r=20),
            title_font=dict(size=16),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Video Types by Channel")

    # Treemap Chart with improved styling
    if "video_type" in df.columns and "channel_title" in df.columns:
        if selected_metric == "Count":
            top_channels = df["channel_title"].value_counts().nlargest(top_n).index
        else:
            top_channels = (
                df.groupby("channel_title")[metric_options[selected_metric]]
                .sum()
                .nlargest(top_n)
                .index
            )

        df_plot = df[df["channel_title"].isin(top_channels)].copy()

        if not df_plot.empty:
            # Create a color map for channels
            unique_channels = df_plot["channel_title"].unique()
            colors = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24
            channel_colors = {
                channel: colors[i % len(colors)]
                for i, channel in enumerate(unique_channels)
            }

            if selected_metric == "Count":
                # For count, we can use the raw data
                fig = px.treemap(
                    df_plot,
                    path=["video_type", "channel_title"],
                    title=f"Video Types by Channel (Top {top_n} channels by {selected_metric})",
                    color="channel_title",
                    color_discrete_map=channel_colors,
                    height=700,
                )
            else:
                # For other metrics, we need to aggregate
                agg_df = df_plot.groupby(
                    ["video_type", "channel_title"], as_index=False
                )[metric_options[selected_metric]].sum()
                fig = px.treemap(
                    agg_df,
                    path=["video_type", "channel_title"],
                    values=metric_options[selected_metric],
                    title=f"Video Types by Channel (Top {top_n} channels by {selected_metric})",
                    color="channel_title",
                    color_discrete_map=channel_colors,
                    height=700,
                )

            fig.update_traces(
                textinfo="label+value+percent parent",
                hovertemplate="<b>%{label}</b><br>"
                + f"{selected_metric}: %{{value:,.0f}}<br>"
                + "%{percentParent:.1%} of parent",
                texttemplate="%{label}<br>%{value:,.0f}",
                textfont=dict(size=14, family="Arial"),
                marker_line_width=1,
                marker_line_color="white",
            )
            fig.update_layout(
                margin=dict(t=70, l=0, r=0, b=0),
                title_font=dict(size=16),
                legend=dict(
                    title="Channels", font=dict(size=12), itemsizing="constant"
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Detailed Analysis")

    # Detailed visualization with subplots - Only video type and language
    if all(col in df.columns for col in ["video_type", "default_audio_language"]):
        # Create subplots
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=(
                f"Video Type Distribution ({selected_metric})",
                f"Language Distribution ({selected_metric})",
            ),
            column_widths=[0.5, 0.5],
            horizontal_spacing=0.1,
        )

        # Function to create a bar chart for a given column
        def create_bar_chart(col, row, col_pos, title):
            if selected_metric == "Count":
                data = df[col].value_counts().reset_index()
                data.columns = [col, "value"]
            else:
                data = df.groupby(col, as_index=False)[
                    metric_options[selected_metric]
                ].sum()
                data = data.rename(columns={metric_options[selected_metric]: "value"})

            # Sort by value in descending order and limit to top_n
            data = data.sort_values("value", ascending=False).head(top_n)

            # For language, replace empty strings with "Not specified"
            if col == "default_audio_language":
                data[col] = data[col].replace("", "Not specified")

            fig.add_trace(
                go.Bar(
                    x=data[col],
                    y=data["value"],
                    name=title,
                    text=data["value"].apply(lambda x: f"{x:,.0f}"),
                    textposition="auto",
                    marker_color=px.colors.qualitative.Pastel[: len(data)],
                    hovertemplate="%{x}<br>"
                    + f"{selected_metric}: %{{y:,.0f}}<extra></extra>",
                ),
                row=row,
                col=col_pos,
            )

            # Update x-axis title and styling
            fig.update_xaxes(
                title_text=title,
                row=row,
                col=col_pos,
                tickangle=-45,
                tickfont=dict(size=12),
            )
            fig.update_yaxes(
                title_text=selected_metric, row=row, col=col_pos, tickfont=dict(size=12)
            )

        # Create bar charts for video type and language
        create_bar_chart("video_type", 1, 1, "Video Type")
        create_bar_chart("default_audio_language", 1, 2, "Language")

        # Update layout
        fig.update_layout(
            height=500,
            showlegend=False,
            margin=dict(t=80, b=120, l=50, r=50),
            title_font=dict(size=16),
            hoverlabel=dict(font_size=14),
        )

        # Adjust subplot spacing and title font
        fig.update_annotations(font_size=14)
        st.plotly_chart(fig, use_container_width=True)

    # Add a separate section for category mapping
    if "category_id" in df.columns:
        st.divider()
        st.subheader("Category ID Mapping")

        # Create a mapping of category IDs to their descriptions
        category_mapping = pd.DataFrame(
            [(k, v) for k, v in categories_br.items()],
            columns=["Category ID", "Description"],
        )

        # Get unique category IDs from the data
        unique_categories = df["category_id"].astype(str).unique()
        category_mapping = category_mapping[
            category_mapping["Category ID"].isin(unique_categories)
        ]

        # Show the mapping in an expandable section
        with st.expander("Show Category ID Mappings", expanded=False):
            st.table(category_mapping)

        # Show category distribution as a bar chart
        st.subheader("Category Distribution")

        if selected_metric == "Count":
            category_data = df["category_id"].astype(str).value_counts().reset_index()
            category_data.columns = ["Category ID", "Count"]
        else:
            category_data = df.groupby("category_id", as_index=False)[
                metric_options[selected_metric]
            ].sum()
            category_data = category_data.rename(
                columns={metric_options[selected_metric]: "Count"}
            )
            category_data["Category ID"] = category_data["Category ID"].astype(str)

        # Merge with category descriptions
        category_data = category_data.merge(
            category_mapping, on="Category ID", how="left"
        )

        # Sort and limit to top N
        category_data = category_data.sort_values("Count", ascending=False).head(top_n)

        # Create bar chart
        fig = px.bar(
            category_data,
            x="Description",
            y="Count",
            title=f"Top {min(top_n, len(category_data))} Categories by {selected_metric}",
            labels={"Description": "Category", "Count": selected_metric},
            color="Description",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )

        fig.update_traces(
            texttemplate="%{y:,.0f}",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>"
            + f"{selected_metric}: %{{y:,.0f}}<extra></extra>",
            textfont=dict(size=12),
        )

        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_tickangle=-45,
            margin=dict(t=50, b=150, l=50, r=50),
            xaxis_title="",
            yaxis_title=selected_metric,
            title_font=dict(size=16),
            xaxis=dict(tickfont=dict(size=12)),
            yaxis=dict(tickfont=dict(size=12)),
        )

        st.plotly_chart(fig, use_container_width=True)
