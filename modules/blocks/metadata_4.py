import streamlit as st
import plotly.express as px


def render(df):
    """
    Start here Analysis block for Data Stories. Receives a filtered DataFrame.
    """
    st.subheader("Start here Analysis")

    # Create a copy of the dataframe with selected columns
    selected_columns = [
        "channel_title",
        "published_at",
        "age_in_days",
        "title",
        "description",
        "view_count",
        "like_count",
        "comment_count",
        "category_id",
        "default_audio_language",
        "live_content",
        "tags",
        "video_type",
        "duration_formatted_seconds",
        "caption",
    ]

    # Create a smaller dataframe with only the selected columns
    df_small = df[selected_columns].copy()

    # Calculate lengths of title, description, and tags
    df_small["title_length"] = df_small["title"].str.len()
    df_small["description_length"] = df_small["description"].str.len()
    df_small["tags_length"] = df_small["tags"].str.len()  # Total length of all tags
    df_small["tags_count"] = df_small["tags"].str.count(",") + 1  # Count tags by counting commas + 1

    # Display basic info about the dataframe
    st.write("### DataFrame Info")
    st.write(f"Number of rows: {len(df_small)}")

    # Show statistics about the calculated fields
    st.write("### Text Length Statistics")
    length_stats = df_small[
        ["title_length", "description_length", "tags_length", "tags_count"]
    ].describe()
    st.dataframe(length_stats)

    # Create distribution plots
    st.write("### Distribution Plots")
    
    # Function to create and display distribution plot
    def plot_distribution(column, title, xaxis_title):
        fig = px.histogram(
            df_small[df_small[column] > 0],  # Filter out zeros for better visualization
            x=column,
            title=title,
            nbins=50,
            marginal="box"  # Add box plot on top
        )
        fig.update_layout(
            xaxis_title=xaxis_title,
            yaxis_title="Count",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Plot distributions
    plot_distribution("title_length", "Title Length Distribution", "Title Length (characters)")
    plot_distribution("description_length", "Description Length Distribution", "Description Length (characters)")
    plot_distribution("tags_length", "Total Tags Length Distribution", "Total Tags Length (characters)")
    plot_distribution("tags_count", "Number of Tags Distribution", "Number of Tags")

    # Show a sample of the data with the new calculated columns
    st.write("### Sample Data with Calculated Fields")
    st.dataframe(df_small.head())
