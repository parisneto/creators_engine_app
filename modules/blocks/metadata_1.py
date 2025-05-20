import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


def render(df):
    """
    Overview block for Data Stories. Receives a filtered DataFrame.
    """

    if df is None or df.empty:
        st.warning("No data available after filtering. Try adjusting your filters.")
        return

    st.subheader("Metadata Intro : ")

    if "video_type" in df.columns:
        fig = px.histogram(df, x="video_type", title="Distribution of Video Types")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    if "video_type" in df.columns:
        fig = px.histogram(
            df,
            x="video_type",
            title="Distribution of Video Types",
            color="video_type",  # Different color for each type
            color_discrete_sequence=px.colors.qualitative.Set2,  # Better color palette
            text_auto=True,  # Show counts on bars
        )
        fig.update_layout(
            showlegend=False,  # Remove legend as it's redundant with x-axis
            xaxis_title="Video Type",
            yaxis_title="Count",
            plot_bgcolor="rgba(0,0,0,0.1)",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    if "video_type" in df.columns:
        # Get top N channels to avoid overcrowding
        top_n = 10
        top_channels = df["channel_title"].value_counts().nlargest(top_n).index

        # Create a new column for channel grouping
        df["channel_group"] = df["channel_title"].where(
            df["channel_title"].isin(top_channels), "Other"
        )

        fig = px.histogram(
            df,
            x="video_type",
            color="channel_group",
            title=f"Distribution of Video Types by Top {top_n} Channels",
            color_discrete_sequence=px.colors.qualitative.Plotly,
            barmode="stack",
            text_auto=True,
        )
        fig.update_layout(
            xaxis_title="Video Type",
            yaxis_title="Count",
            legend_title="Channel",
            plot_bgcolor="rgba(0,0,0,0.1)",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)
    st.divider()

    if "video_type" in df.columns:
        # Get value counts
        type_counts = df["video_type"].value_counts().reset_index()
        type_counts.columns = ["video_type", "count"]

        fig = px.pie(
            type_counts,
            names="video_type",
            values="count",
            title="Proportion of Video Types (count)",
            hole=0.3,  # Creates a donut chart
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    if "video_type" in df.columns:
        # Create subplots
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("Distribution by Type", "Type Distribution by Channel"),
            column_widths=[0.4, 0.6],
        )

        # First subplot - Simple bar chart
        type_counts = df["video_type"].value_counts()
        fig.add_trace(
            go.Bar(
                x=type_counts.index,
                y=type_counts.values,
                marker_color=px.colors.qualitative.Set3,
                text=type_counts.values,
                textposition="auto",
            ),
            row=1,
            col=1,
        )

        # Second subplot - Stacked bar chart by channel
        top_n = 5
        top_channels = df["channel_title"].value_counts().nlargest(top_n).index
        df["channel_group"] = df["channel_title"].where(
            df["channel_title"].isin(top_channels), "Other"
        )

        for channel in df["channel_group"].unique():
            channel_data = df[df["channel_group"] == channel]
            channel_type_counts = (
                channel_data["video_type"]
                .value_counts()
                .reindex(type_counts.index, fill_value=0)
            )
            fig.add_trace(
                go.Bar(
                    x=channel_type_counts.index,
                    y=channel_type_counts.values,
                    name=channel,
                    text=channel_type_counts.values,
                    textposition="auto",
                ),
                row=1,
                col=2,
            )

        fig.update_layout(
            barmode="stack",
            showlegend=True,
            height=500,
            plot_bgcolor="rgba(0,0,0,0.05)",
            margin=dict(t=50, l=0, r=0, b=0),
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    if "video_type" in df.columns:
        # Get top N channels
        top_n = 10
        top_channels = df["channel_title"].value_counts().nlargest(top_n).index
        df_plot = df[df["channel_title"].isin(top_channels)]

        fig = px.treemap(
            df_plot,
            path=["video_type", "channel_title"],
            title="Video Types Distribution by Channel",
            color="video_type",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            height=600,
        )

        fig.update_traces(
            textinfo="label+value+percent parent",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percentParent:.1%} of %{parent}",
        )

        st.plotly_chart(fig, use_container_width=True)

    # st.write(f"DataFrame shape: {df.shape}")
    # st.write(f"Columns: {list(df.columns)}")
    # with st.expander("Sample Data"):
    #     st.dataframe(df.head(10))
    # # Example: Show counts for key columns
    # if "channel_title" in df.columns:
    #     st.write(f"Unique Channels: {df['channel_title'].nunique()}")
    # if "video_type" in df.columns:
    #     st.write(f"Video Types: {df['video_type'].unique().tolist()}")
    # if "default_audio_language" in df.columns:
    #     st.write(f"Languages: {df['default_audio_language'].unique().tolist()}")
    # # Example plot (if plotly/matplotlib is available)
