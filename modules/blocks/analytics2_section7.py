"""
# 2025-06-10: Created playlist section 6 for text analysis of titles and descriptions
# 2025-06-10: Added word frequency analysis and word cloud visualization using Plotly
# 2025-05-05: Extended text analysis to optionally include tags column in all analysis tabs (Title, Description, Custom)
# 2025-05-05: Improved Plotly word cloud layout (denser, larger text); clarified tag data processing; added channel/tag completeness visualization at page bottom
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import re
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from utils.dataloader import load_data

def clean_text(text):
    """
    Clean text by removing special characters, converting to lowercase,
    and splitting into words.

    Args:
        text: String to clean

    Returns:
        List of cleaned words
    """
    if not isinstance(text, str):
        return []

    # Convert to lowercase
    text = text.lower()

    # Remove special characters and keep only alphanumeric and spaces
    text = re.sub(r'[^\w\s]', ' ', text)

    # Split into words
    words = text.split()

    return words

def get_word_counts(texts, min_word_length=3, stopwords=None):
    """
    Get word frequency counts from a list of texts.

    Args:
        texts: List of text strings
        min_word_length: Minimum word length to include
        stopwords: Set of words to exclude

    Returns:
        Counter object with word frequencies
    """
    if stopwords is None:
        stopwords = set()

    all_words = []
    for text in texts:
        words = clean_text(text)
        # Filter short words and stopwords
        words = [word for word in words if len(word) >= min_word_length and word not in stopwords]
        all_words.extend(words)

    return Counter(all_words)

def plot_word_frequency(word_counts, title, n=20):
    """
    Create a horizontal bar chart of word frequencies using Plotly.

    Args:
        word_counts: Counter object with word frequencies
        title: Chart title
        n: Number of top words to display

    Returns:
        Plotly figure
    """
    # Get top N words
    top_words = word_counts.most_common(n)
    words, counts = zip(*top_words) if top_words else ([], [])

    # Create bar chart
    fig = px.bar(
        x=counts,
        y=words,
        orientation='h',
        title=title,
        labels={'x': 'Count', 'y': 'Word'},
        height=500
    )

    # Update layout
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})

    return fig

def plot_word_cloud(word_counts, title, max_words=100):
    """
    Create a word cloud using Plotly.
    This is a simple implementation that uses a scatter plot with text.
    Improved for denser layout and larger text.

    Args:
        word_counts: Counter object with word frequencies
        title: Chart title
        max_words: Maximum number of words to display

    Returns:
        Plotly figure
    """
    # Get words and their frequencies
    words_freq = word_counts.most_common(max_words)
    if not words_freq:
        return None

    words, counts = zip(*words_freq)

    # Normalize sizes for better visualization
    min_count = min(counts)
    max_count = max(counts)

    # Scale sizes between 24 and 90 for better readability
    sizes = [24 + (66 * (count - min_count) / (max_count - min_count) if max_count > min_count else 1) for count in counts]

    # Generate tighter random positions for words
    np.random.seed(42)  # For reproducibility
    x_pos = np.random.uniform(-0.5, 0.5, len(words))
    y_pos = np.random.uniform(-0.5, 0.5, len(words))

    # Create scatter plot with text
    fig = go.Figure()

    for i, (word, count, size) in enumerate(zip(words, counts, sizes)):
        fig.add_trace(go.Scatter(
            x=[x_pos[i]],
            y=[y_pos[i]],
            mode='text',
            text=[word],
            textfont=dict(size=size, color=px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]),
            hoverinfo='text',
            hovertext=f"{word}: {count}",
            showlegend=False
        ))

    # Update layout for denser, more readable cloud
    fig.update_layout(
        title=title,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
        hovermode='closest',
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=60, b=10),
        height=500,
        width=900,
    )
    return fig

def create_wordcloud_matplotlib(word_counts, title, max_words=100):
    """
    Create a word cloud visualization using matplotlib.

    Args:
        word_counts: Counter object with word frequencies
        title: Chart title
        max_words: Maximum number of words to display

    Returns:
        Matplotlib figure
    """
    # Get words and their frequencies
    words_freq = word_counts.most_common(max_words)
    if not words_freq:
        return None

    words, counts = zip(*words_freq)

    # Create a dataframe for seaborn
    df = pd.DataFrame({'word': words, 'count': counts})

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create a word cloud-like visualization using a scatter plot
    sns.scatterplot(
        x=np.random.uniform(0, 10, len(words)),
        y=np.random.uniform(0, 10, len(words)),
        size=df['count'],
        hue=df['count'],
        legend=False,
        sizes=(100, 2000),
        ax=ax
    )

    # Add word labels
    for i, row in df.iterrows():
        ax.text(
            np.random.uniform(0, 10),
            np.random.uniform(0, 10),
            row['word'],
            fontsize=np.log1p(row['count']) * 5,
            ha='center',
            va='center',
            alpha=0.8
        )

    # Remove axes and labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title(title, fontsize=16)
    ax.grid(False)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    return fig

def analytics2_section7(df_nerdalytics, df_playlist_full_dedup):
    """
    Text analysis section for playlist analytics.
    Analyzes video titles and descriptions for word frequencies and patterns.
    """
    st.header("Text Analysis")
    st.write("This section analyzes text content in video titles and descriptions.")

    # # Use filtered data from session state if available
    # if "filtered_playlist_df" in st.session_state:
    #     df_playlist_full_dedup = st.session_state["filtered_playlist_df"]
    # else:
    #     # Load playlist data if not available in session state
    #     df_playlist_full_dedup = load_data("tbl_playlist_full_dedup")

    # Check if dataframe is empty and show warning if it is
    if df_playlist_full_dedup is None or df_playlist_full_dedup.empty:
        st.warning("No playlist data available for text analysis. Please check your data source or filters.")
        return

    # Create tabs for different text analyses
    text_tabs = st.tabs(["Title Analysis", "Description Analysis", "Custom Analysis", "New Metadata Tab "   ])

    # Common parameters for word analysis
    # --- Common stopwords: English and Portuguese ---
    common_english_stopwords = {
        'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from',
        'by', 'with', 'in', 'out', 'of', 'this', 'that', 'these', 'those', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could', 'it',
        'its', 'i', 'you', 'he', 'she', 'they', 'them', 'we', 'us', 'my', 'your', 'his',
        'her', 'their', 'our', 'as', 'if', 'so', 'than', 'then', 'not', 'no', 'yes'
    }
    common_portuguese_stopwords = {
        # Articles (Artigos)
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
        # Prepositions (Preposições) + Contractions (Contrações)
        'de', 'do', 'da', 'dos', 'das',
        'em', 'no', 'na', 'nos', 'nas',
        'a', 'ao', 'à', 'aos', 'às',
        'por', 'pelo', 'pela', 'pelos', 'pelas',
        'com', 'sem', 'sob', 'sobre', 'para', 'pra',
        # Conjunctions (Conjunções)
        'e', 'ou', 'mas', 'se', 'que', 'porque', 'enquanto', 'logo', 'pois', 'como',
        # Pronouns (Pronomes)
        'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas', 'você', 'vocês',
        'me', 'te', 'se', 'lhe', 'nos', 'vos', 'lhes',
        'meu', 'minha', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas',
        'seu', 'sua', 'seus', 'suas', 'nosso', 'nossa', 'nossos', 'nossas',
        'este', 'esta', 'estes', 'estas', 'isto',
        'esse', 'essa', 'esses', 'essas', 'isso',
        'aquele', 'aquela', 'aqueles', 'aquelas', 'aquilo',
        # Common Verbs
        'ser', 'sido', 'sendo', 'é', 'são', 'foi', 'fui', 'foram', 'era', 'eram', 'será', 'serão',
        'estar', 'estado', 'estando', 'está', 'estão', 'esteve', 'estive', 'estiveram', 'estava', 'estavam',
        'ter', 'tido', 'tendo', 'tem', 'têm', 'teve', 'tive', 'tiveram', 'tinha', 'tinham',
        'haver', 'havido', 'havendo', 'há', 'houve', 'hão', 'havia', 'haviam',
        # Adverbs/Others
        'não', 'sim', 'mais', 'menos', 'muito', 'pouco', 'também', 'já', 'ainda', 'aqui', 'aí', 'lá', 'ali', 'agora'
    }
    all_stopwords = common_english_stopwords | common_portuguese_stopwords

    # First tab - Title Analysis
    with text_tabs[0]:
        st.subheader("Video Title Analysis")

        # Filter settings
        col1, col2 = st.columns(2)
        with col1:
            min_word_length = st.slider("Minimum Word Length", 2, 10, 3, help="Filter out words shorter than this length")
            max_words = st.slider("Number of Top Words", 10, 100, 30, help="Number of most frequent words to display")

        with col2:
            use_stopwords = st.checkbox("Filter Common Stopwords (EN + PT-BR)", value=True, help=None)
            custom_stopwords = st.text_input("Additional Words to Filter (comma-separated)",
                                            placeholder="video,youtube,etc",
                                            help="Add your own words to filter out")
            # Popover for stopwords
            with st.popover("Show Stopword List (EN + PT-BR)"):
                st.write(", ".join(sorted(all_stopwords)))

        # Process stopwords
        stopwords_set = set()
        if use_stopwords:
            stopwords_set.update(all_stopwords)

        if custom_stopwords:
            custom_words = [word.strip().lower() for word in custom_stopwords.split(',')]
            stopwords_set.update(custom_words)

        # Extract titles and get word counts
        titles = df_playlist_full_dedup["video_title"].dropna().tolist()

        # --- Step: Optionally include tags in Title analysis ---
        include_tags_title = st.checkbox("Include Tags in Analysis", value=False, help="Include tags as additional words for analysis.")
        if include_tags_title and "tags" in df_playlist_full_dedup.columns:
            tag_texts = df_playlist_full_dedup["tags"].dropna().astype(str).tolist()
            # Split each tag string by comma, flatten to a list of words
            tag_words = []
            for tag_str in tag_texts:
                tag_words.extend([t.strip() for t in tag_str.split(",") if t.strip()])
            titles.extend(tag_words)

        if not titles:
            st.warning("No video titles found for analysis.")
        else:
            # Count words
            word_counts = get_word_counts(titles, min_word_length, stopwords_set)

            # Display total unique words and total titles
            st.info(f"Analyzed {len(titles)} video titles with {len(word_counts)} unique words (after filtering).")

            # Plot word frequency
            st.subheader("Most Common Words in Titles")
            freq_fig = plot_word_frequency(word_counts, f"Top {max_words} Words in Video Titles", max_words)
            st.plotly_chart(freq_fig, use_container_width=True)

            # Word cloud visualization
            st.subheader("Title Word Cloud")

            viz_type = st.radio("Visualization Type", ["Plotly Interactive", "Matplotlib Static"], index=0)

            if viz_type == "Plotly Interactive":
                cloud_fig = plot_word_cloud(word_counts, "Word Cloud of Video Titles", max_words)
                if cloud_fig:
                    st.plotly_chart(cloud_fig, use_container_width=True)
                else:
                    st.warning("Not enough data to create word cloud.")
            else:
                mpl_fig = create_wordcloud_matplotlib(word_counts, "Word Cloud of Video Titles", max_words)
                if mpl_fig:
                    st.pyplot(mpl_fig)
                else:
                    st.warning("Not enough data to create word cloud.")

    # Second tab - Description Analysis
    with text_tabs[1]:
        st.subheader("Video Description Analysis")

        # Filter settings (same as title tab but with different defaults)
        col1, col2 = st.columns(2)
        with col1:
            min_word_length_desc = st.slider("Minimum Word Length", 2, 10, 4, help="Filter out words shorter than this length", key="desc_min_len")
            max_words_desc = st.slider("Number of Top Words", 10, 100, 50, help="Number of most frequent words to display", key="desc_max_words")

        with col2:
            use_stopwords_desc = st.checkbox("Filter Common Stopwords (EN + PT-BR)", value=True, help=None, key="desc_stopwords")
            custom_stopwords_desc = st.text_input("Additional Words to Filter (comma-separated)",
                                                 placeholder="video,youtube,etc",
                                                 help="Add your own words to filter out",
                                                 key="desc_custom_stopwords")
            # Popover for stopwords
            with st.popover("Show Stopword List (EN + PT-BR)"):
                st.write(", ".join(sorted(all_stopwords)))

        # Process stopwords
        stopwords_set_desc = set()
        if use_stopwords_desc:
            stopwords_set_desc.update(all_stopwords)

        if custom_stopwords_desc:
            custom_words_desc = [word.strip().lower() for word in custom_stopwords_desc.split(',')]
            stopwords_set_desc.update(custom_words_desc)

        # Check if description column exists
        if "video_description" not in df_playlist_full_dedup.columns:
            st.warning("No video description column found in the dataset.")
        else:
            # Extract descriptions and get word counts
            descriptions = df_playlist_full_dedup["video_description"].dropna().tolist()

            # --- Step: Optionally include tags in Description analysis ---
            include_tags_desc = st.checkbox("Include Tags in Analysis", value=False, help="Include tags as additional words for analysis.", key="desc_include_tags")
            if include_tags_desc and "tags" in df_playlist_full_dedup.columns:
                tag_texts = df_playlist_full_dedup["tags"].dropna().astype(str).tolist()
                tag_words = []
                for tag_str in tag_texts:
                    tag_words.extend([t.strip() for t in tag_str.split(",") if t.strip()])
                descriptions.extend(tag_words)

            if not descriptions:
                st.warning("No video descriptions found for analysis.")
            else:
                # Count words
                word_counts_desc = get_word_counts(descriptions, min_word_length_desc, stopwords_set_desc)

                # Display total unique words and total descriptions
                st.info(f"Analyzed {len(descriptions)} video descriptions with {len(word_counts_desc)} unique words (after filtering).")

                # Plot word frequency
                st.subheader("Most Common Words in Descriptions")
                freq_fig_desc = plot_word_frequency(word_counts_desc, f"Top {max_words_desc} Words in Video Descriptions", max_words_desc)
                st.plotly_chart(freq_fig_desc, use_container_width=True)

                # Word cloud visualization
                st.subheader("Description Word Cloud")

                viz_type_desc = st.radio("Visualization Type", ["Plotly Interactive", "Matplotlib Static"], index=0, key="desc_viz_type")

                if viz_type_desc == "Plotly Interactive":
                    cloud_fig_desc = plot_word_cloud(word_counts_desc, "Word Cloud of Video Descriptions", max_words_desc)
                    if cloud_fig_desc:
                        st.plotly_chart(cloud_fig_desc, use_container_width=True)
                    else:
                        st.warning("Not enough data to create word cloud.")
                else:
                    mpl_fig_desc = create_wordcloud_matplotlib(word_counts_desc, "Word Cloud of Video Descriptions", max_words_desc)
                    if mpl_fig_desc:
                        st.pyplot(mpl_fig_desc)
                    else:
                        st.warning("Not enough data to create word cloud.")

    # Third tab - Custom Analysis
    with text_tabs[2]:
        st.subheader("Custom Text Analysis")
        st.write("Analyze any text field or combination of fields.")

        # Select which text fields to analyze
        available_text_columns = []
        for col in df_playlist_full_dedup.columns:
            if df_playlist_full_dedup[col].dtype == 'object':
                # Check if column has string values (sample a few rows)
                sample = df_playlist_full_dedup[col].dropna().head(10)
                if any(isinstance(val, str) and len(val) > 10 for val in sample) or col == "tags":
                    available_text_columns.append(col)

        if not available_text_columns:
            st.warning("No suitable text columns found for analysis.")
        else:
            selected_columns = st.multiselect(
                "Select Text Fields to Analyze",
                options=available_text_columns,
                default=["video_title"] if "video_title" in available_text_columns else []
            )

            if not selected_columns:
                st.info("Please select at least one text field to analyze.")
            else:
                # Filter settings
                col1, col2 = st.columns(2)
                with col1:
                    min_word_length_custom = st.slider("Minimum Word Length", 2, 10, 3, help="Filter out words shorter than this length", key="custom_min_len")
                    max_words_custom = st.slider("Number of Top Words", 10, 150, 50, help="Number of most frequent words to display", key="custom_max_words")

                with col2:
                    use_stopwords_custom = st.checkbox("Filter Common Stopwords (EN + PT-BR)", value=True, help=None, key="custom_stopwords")
                    custom_stopwords_custom = st.text_input("Additional Words to Filter (comma-separated)",
                                                         placeholder="video,youtube,etc",
                                                         help="Add your own words to filter out",
                                                         key="custom_custom_stopwords")
                    # Popover for stopwords
                    with st.popover("Show Stopword List (EN + PT-BR)"):
                        st.write(", ".join(sorted(all_stopwords)))

                # Process stopwords
                stopwords_set_custom = set()
                if use_stopwords_custom:
                    stopwords_set_custom.update(all_stopwords)

                if custom_stopwords_custom:
                    custom_words_custom = [word.strip().lower() for word in custom_stopwords_custom.split(',')]
                    stopwords_set_custom.update(custom_words_custom)

                # Collect all text from selected columns
                all_texts = []
                for col in selected_columns:
                    if col == "tags":
                        # Split tags by comma for each row
                        tag_texts = df_playlist_full_dedup["tags"].dropna().astype(str).tolist()
                        for tag_str in tag_texts:
                            all_texts.extend([t.strip() for t in tag_str.split(",") if t.strip()])
                    else:
                        texts = df_playlist_full_dedup[col].dropna().astype(str).tolist()
                        all_texts.extend(texts)

                if not all_texts:
                    st.warning("No text data found in the selected columns.")
                else:
                    # Count words
                    word_counts_custom = get_word_counts(all_texts, min_word_length_custom, stopwords_set_custom)

                    # Display total unique words and total texts
                    st.info(f"Analyzed {len(all_texts)} text entries with {len(word_counts_custom)} unique words (after filtering).")

                    # Plot word frequency
                    st.subheader("Most Common Words in Selected Fields")
                    freq_fig_custom = plot_word_frequency(word_counts_custom, f"Top {max_words_custom} Words", max_words_custom)
                    st.plotly_chart(freq_fig_custom, use_container_width=True)

                    # Word cloud visualization
                    st.subheader("Custom Word Cloud")

                    viz_type_custom = st.radio("Visualization Type", ["Plotly Interactive", "Matplotlib Static"], index=0, key="custom_viz_type")

                    if viz_type_custom == "Plotly Interactive":
                        cloud_fig_custom = plot_word_cloud(word_counts_custom, "Word Cloud of Selected Fields", max_words_custom)
                        if cloud_fig_custom:
                            st.plotly_chart(cloud_fig_custom, use_container_width=True)
                        else:
                            st.warning("Not enough data to create word cloud.")
                    else:
                        mpl_fig_custom = create_wordcloud_matplotlib(word_counts_custom, "Word Cloud of Selected Fields", max_words_custom)
                        if mpl_fig_custom:
                            st.pyplot(mpl_fig_custom)
                        else:
                            st.warning("Not enough data to create word cloud.")

    # First tab - Title Analysis
    with text_tabs[3]:
        st.subheader("Title Analysis")
        st.write("This section analyzes text content in video titles.")

        st.write("check df's loaded and print shape of each")
        st.write("df_nerdalytics shape: ", str(df_nerdalytics.shape))
        st.write("df_playlist_full_dedup shape: ", str(df_playlist_full_dedup.shape))

        # --- TAG DATA PROCESSING EXPLANATION ---
        # If "Include Tags" is checked for Titles or Descriptions:
        #   - All tag words (split by comma) are appended to the list of titles/descriptions.
        #   - The combined list is analyzed together (not separated).
        # In Custom Analysis, if "tags" is selected, all tag words are included as additional text entries.
        # This means tag words are counted alongside the selected text fields in all word frequency and word cloud visualizations.
        # Channels/videos without tags simply contribute nothing from tags.

        # --- CHANNEL TAG COMPLETENESS VISUALIZATION ---
        st.markdown("---")
        st.header("Channel Tag Completeness")
        st.write("This chart shows which channels have videos with tags filled versus empty.")
        if "channel_title" in df_nerdalytics.columns and "tags" in df_nerdalytics.columns:
            tag_status_df = df_nerdalytics.copy()
            # tag_status_df = df_playlist_full_dedup.copy()
            tag_status_df["tags_filled"] = tag_status_df["tags"].apply(lambda x: bool(isinstance(x, str) and x.strip()))
            summary = tag_status_df.groupby("channel_title").agg(
                videos_with_tags = ("tags_filled", "sum"),
                videos_without_tags = ("tags_filled", lambda x: (~x).sum()),
                total_videos = ("tags_filled", "count")
            ).reset_index()
            summary["percent_with_tags"] = (summary["videos_with_tags"] / summary["total_videos"] * 100).round(1)
            # Sort by % with tags descending
            summary = summary.sort_values("percent_with_tags", ascending=False)
            # Bar chart
            fig_tag = px.bar(
                summary,
                x="channel_title",
                y=["videos_with_tags", "videos_without_tags"],
                title="Videos With vs. Without Tags by Channel",
                labels={"value": "Video Count", "channel_title": "Channel", "variable": "Tag Status"},
                barmode="stack",
                height=400
            )
            st.plotly_chart(fig_tag, use_container_width=True)
            st.dataframe(summary[["channel_title", "videos_with_tags", "videos_without_tags", "percent_with_tags"]], use_container_width=True)
        else:
            st.info("Channel or tags column not found in the data.")