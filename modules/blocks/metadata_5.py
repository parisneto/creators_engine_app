import re
from collections import Counter

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- Utility Functions for Text Analysis ---


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
    text = re.sub(r"[^\w\s]", " ", text)

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
        words = [
            word
            for word in words
            if len(word) >= min_word_length and word not in stopwords
        ]
        all_words.extend(words)

    return Counter(all_words)


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
    sizes = [
        24
        + (
            66 * (count - min_count) / (max_count - min_count)
            if max_count > min_count
            else 1
        )
        for count in counts
    ]

    # Generate tighter random positions for words
    np.random.seed(42)  # For reproducibility
    x_pos = np.random.uniform(-0.5, 0.5, len(words))
    y_pos = np.random.uniform(-0.5, 0.5, len(words))

    # Create scatter plot with text
    fig = go.Figure()

    for i, (word, count, size) in enumerate(zip(words, counts, sizes)):
        fig.add_trace(
            go.Scatter(
                x=[x_pos[i]],
                y=[y_pos[i]],
                mode="text",
                text=[word],
                textfont=dict(
                    size=size,
                    color=px.colors.qualitative.Plotly[
                        i % len(px.colors.qualitative.Plotly)
                    ],
                ),
                hoverinfo="text",
                hovertext=f"{word}: {count}",
                showlegend=False,
            )
        )

    # Update layout for denser, more readable cloud
    fig.update_layout(
        title=title,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
        hovermode="closest",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=60, b=10),
        height=500,
        width=900,
    )
    return fig


def render(df):
    """
    Video Title Analysis block with Word Cloud visualization.
    Receives a filtered DataFrame with video data.
    """
    st.header("Video Title Analysis")
    st.write("Analyze word frequencies in video titles with an interactive word cloud.")

    # Check if dataframe is empty
    if df is None or df.empty:
        st.warning(
            "No data available for analysis. Please check your data source or filters."
        )
        return

    # Show available columns for debugging
    st.sidebar.caption("Available columns:")
    st.sidebar.code("\n".join([f"- {col}" for col in df.columns.tolist()]))

    # Check if required columns exist
    if "title" not in df.columns:
        st.warning("No 'title' column found in the dataset.")
        st.info("Available columns: " + ", ".join(df.columns.tolist()))
        return

    # Common stopwords (English and Portuguese)
    common_english_stopwords = {
        "a",
        "an",
        "the",
        "and",
        "but",
        "or",
        "for",
        "nor",
        "on",
        "at",
        "to",
        "from",
        "by",
        "with",
        "in",
        "out",
        "of",
        "this",
        "that",
        "these",
        "those",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "shall",
        "should",
        "may",
        "might",
        "must",
        "can",
        "could",
        "it",
        "its",
        "i",
        "you",
        "he",
        "she",
        "they",
        "them",
        "we",
        "us",
        "my",
        "your",
        "his",
        "her",
        "their",
        "our",
        "as",
        "if",
        "so",
        "than",
        "then",
        "not",
        "no",
        "yes",
    }
    common_portuguese_stopwords = {
        "o",
        "a",
        "os",
        "as",
        "um",
        "uma",
        "uns",
        "umas",
        "de",
        "do",
        "da",
        "dos",
        "das",
        "em",
        "no",
        "na",
        "nos",
        "nas",
        "a",
        "ao",
        "à",
        "aos",
        "às",
        "por",
        "pelo",
        "pela",
        "pelos",
        "pelas",
        "com",
        "sem",
        "sob",
        "sobre",
        "para",
        "pra",
        "e",
        "ou",
        "mas",
        "se",
        "que",
        "porque",
        "enquanto",
        "logo",
        "pois",
        "como",
        "eu",
        "tu",
        "ele",
        "ela",
        "nós",
        "vós",
        "eles",
        "elas",
        "você",
        "vocês",
        "me",
        "te",
        "se",
        "lhe",
        "nos",
        "vos",
        "lhes",
        "meu",
        "minha",
        "meus",
        "minhas",
        "teu",
        "tua",
        "teus",
        "tuas",
        "seu",
        "sua",
        "seus",
        "suas",
        "nosso",
        "nossa",
        "nossos",
        "nossas",
        "este",
        "esta",
        "estes",
        "estas",
        "isto",
        "esse",
        "essa",
        "esses",
        "essas",
        "isso",
        "aquele",
        "aquela",
        "aqueles",
        "aquelas",
        "aquilo",
        "ser",
        "sido",
        "sendo",
        "é",
        "são",
        "foi",
        "fui",
        "foram",
        "era",
        "eram",
        "será",
        "serão",
        "estar",
        "estado",
        "estando",
        "está",
        "estão",
        "esteve",
        "estive",
        "estiveram",
        "estava",
        "estavam",
        "ter",
        "tido",
        "tendo",
        "tem",
        "têm",
        "teve",
        "tive",
        "tiveram",
        "tinha",
        "tinham",
        "haver",
        "havido",
        "havendo",
        "há",
        "houve",
        "hão",
        "havia",
        "haviam",
        "não",
        "sim",
        "mais",
        "menos",
        "muito",
        "pouco",
        "também",
        "já",
        "ainda",
        "aqui",
        "aí",
        "lá",
        "ali",
        "agora",
    }
    all_stopwords = common_english_stopwords | common_portuguese_stopwords

    # Filter settings
    col1, col2 = st.columns(2)
    with col1:
        min_word_length = st.slider(
            "Minimum Word Length",
            2,
            10,
            3,
            help="Filter out words shorter than this length",
        )
        max_words = st.slider(
            "Number of Top Words",
            10,
            150,
            30,
            help="Number of most frequent words to display",
        )

    with col2:
        use_stopwords = st.checkbox(
            "Filter Common Stopwords (EN + PT-BR)",
            value=True,
            help="Exclude common words from analysis",
        )
        custom_stopwords = st.text_input(
            "Additional Words to Filter (comma-separated)",
            placeholder="video,youtube,etc",
            help="Add your own words to filter out",
        )

        # Show stopwords list in a popover
        with st.popover("View Stopword List (EN + PT-BR)"):
            st.write(", ".join(sorted(all_stopwords)))

    # Process stopwords
    stopwords_set = set()
    if use_stopwords:
        stopwords_set.update(all_stopwords)

    if custom_stopwords:
        custom_words = [word.strip().lower() for word in custom_stopwords.split(",")]
        stopwords_set.update(custom_words)

    # Option to include tags in analysis
    include_tags = False
    if "tags" in df.columns:
        include_tags = st.checkbox(
            "Include Tags in Analysis",
            value=False,
            help="Include video tags in the word frequency analysis",
        )

    # Extract titles and process tags if needed
    titles = df["title"].dropna().tolist()

    if include_tags:
        tag_texts = df["tags"].dropna().astype(str).tolist()
        # Split each tag string by comma and add to titles
        for tag_str in tag_texts:
            titles.extend([t.strip() for t in tag_str.split(",") if t.strip()])

    if not titles:
        st.warning("No video titles found for analysis.")
        return

    # Count words
    word_counts = get_word_counts(titles, min_word_length, stopwords_set)

    # Display summary
    st.info(
        f"Analyzed {len(titles)} video titles with {len(word_counts)} unique words (after filtering)."
    )

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Word cloud visualization
        st.subheader("Title Word Cloud")
        cloud_fig = plot_word_cloud(word_counts, "", max_words)
        if cloud_fig:
            st.plotly_chart(cloud_fig, use_container_width=True)
        else:
            st.warning("Not enough data to create word cloud.")

    with col2:
        # Display top words table
        st.subheader(f"Top {min(20, len(word_counts))} Words")
        top_words = word_counts.most_common(20)
        if top_words:
            word_df = pd.DataFrame(top_words, columns=["Word", "Count"])
            st.dataframe(
                word_df,
                column_config={
                    "Word": "Word",
                    "Count": st.column_config.NumberColumn("Count", format="%d"),
                },
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No words to display after filtering.")

    # Add some space at the bottom
    st.markdown("---")
    
    # --- Video Description Analysis ---
    st.header("Video Description Analysis")
    st.write("Analyze word frequencies in video descriptions with an interactive word cloud.")

    # Check if description column exists
    if "description" not in df.columns:
        st.warning("No 'description' column found in the dataset.")
        st.info("Available columns: " + ", ".join(df.columns.tolist()))
        return
        
    # Filter settings for description analysis
    desc_col1, desc_col2 = st.columns(2)
    with desc_col1:
        desc_min_word_length = st.slider(
            "Minimum Word Length",
            2, 10, 4,
            help="Filter out words shorter than this length",
            key="desc_min_len"
        )
        desc_max_words = st.slider(
            "Number of Top Words",
            10, 200, 50,
            help="Number of most frequent words to display",
            key="desc_max_words"
        )

    with desc_col2:
        desc_use_stopwords = st.checkbox(
            "Filter Common Stopwords (EN + PT-BR)",
            value=True,
            help="Exclude common words from analysis",
            key="desc_stopwords"
        )
        desc_custom_stopwords = st.text_input(
            "Additional Words to Filter (comma-separated)",
            placeholder="video,youtube,etc",
            help="Add your own words to filter out",
            key="desc_custom_stopwords"
        )

    # Process stopwords for description
    desc_stopwords_set = set()
    if desc_use_stopwords:
        desc_stopwords_set.update(all_stopwords)

    if desc_custom_stopwords:
        custom_words = [word.strip().lower() for word in desc_custom_stopwords.split(",")]
        desc_stopwords_set.update(custom_words)

    # Option to include tags in description analysis
    desc_include_tags = False
    if "tags" in df.columns:
        desc_include_tags = st.checkbox(
            "Include Tags in Analysis",
            value=False,
            help="Include video tags in the word frequency analysis",
            key="desc_include_tags"
        )

    # Extract descriptions and process tags if needed
    descriptions = df["description"].dropna().tolist()
    
    if desc_include_tags:
        tag_texts = df["tags"].dropna().astype(str).tolist()
        # Split each tag string by comma and add to descriptions
        for tag_str in tag_texts:
            descriptions.extend([t.strip() for t in tag_str.split(",") if t.strip()])

    if not descriptions:
        st.warning("No video descriptions found for analysis.")
    else:
        # Count words in descriptions
        desc_word_counts = get_word_counts(descriptions, desc_min_word_length, desc_stopwords_set)

        # Display summary
        st.info(
            f"Analyzed {len(descriptions)} video descriptions with {len(desc_word_counts)} "
            "unique words (after filtering)."
        )

        # Create two columns for layout
        desc_col1, desc_col2 = st.columns([2, 1])

        with desc_col1:
            # Word cloud visualization
            st.subheader("Description Word Cloud")
            desc_cloud_fig = plot_word_cloud(desc_word_counts, "", desc_max_words)
            if desc_cloud_fig:
                st.plotly_chart(desc_cloud_fig, use_container_width=True)
            else:
                st.warning("Not enough data to create word cloud.")

        with desc_col2:
            # Display top words table
            st.subheader(f"Top {min(20, len(desc_word_counts))} Words")
            top_desc_words = desc_word_counts.most_common(20)
            if top_desc_words:
                desc_word_df = pd.DataFrame(top_desc_words, columns=["Word", "Count"])
                st.dataframe(
                    desc_word_df,
                    column_config={
                        "Word": "Word",
                        "Count": st.column_config.NumberColumn("Count", format="%d"),
                    },
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.info("No words to display after filtering.")
        
        # Add some space at the bottom
        st.markdown("---")
