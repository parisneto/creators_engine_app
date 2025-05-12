#%%
# Feature map for datasets used in analytics and storytelling
# Expandable for multiple tables (e.g., df_nerdalytics, df_slope_full)
#
# USAGE INSTRUCTIONS:
# - Use the 'example' field in each feature for real sample values from your data.
# - The code in the __main__ block demonstrates classification, plotting, and feature engineering.
# - To run plotting/engineering examples, set the 'if False:' blocks to 'if True:' and load your DataFrame.
# - Use the auto_plot_all(df, feature_map) utility to automatically plot all valid feature pairs.
# - Expand feature maps for new tables by following the provided template and real data examples.
#
# Example DataFrame columns and dtypes for df_nerdalytics/df_slope_full:
# (see below for full structure and sample values)

# from config.VideoCategorieslist import categories_en, categories_br

# Declare the dictionary mapping integer IDs to titles
# Enhanced with complete category data from VideoCategorieslist.py
CATEGORY_ID_MAP = {
    '1': "Filmes e Animação",
    '2': "Automóveis e Veículos",
    '10': "Música",
    '15': "Animais de Estimação",
    '17': "Esportes",
    '18': "Filmes Curtos",
    '19': "Viagens e Eventos",
    '20': "Jogos",
    '21': "Videoblogs",
    '22': "Pessoas e Blogs",
    '23': "Comédia",
    '24': "Entretenimento",
    '25': "Notícias e Política",
    '26': "Como & Estilo",
    '27': "Educação",
    '28': "Ciência e Tecnologia",
    '29': "Organizações sem fins lucrativos e ativismo",
    '30': "Filmes",
    '31': "Anime/Animação",
    '32': "Ação/Aventura",
    '33': "Clássicos",
    '34': "Comédia",
    '35': "Documentário",
    '36': "Drama",
    '37': "Família",
    '38': "Estrangeiro",
    '39': "Terror",
    '40': "Ficção Científica/Fantasia",
    '41': "Suspense",
    '42': "Shorts",
    '43': "Séries",
    '44': "Trailers"
}

# Function to get category name based on ID and language preference
def get_category_name(category_id, language='pt'):
    """
    Returns the category name for a given category ID in the specified language.

    Args:
        category_id: The YouTube category ID (string or int)
        language: Language code ('en' for English, 'pt' for Portuguese)

    Returns:
        Category name string or "Unknown Category" if not found
    """
    category_id = str(category_id)  # Ensure the ID is a string

    if language == 'en':
        return categories_en.get(category_id, f"Unknown Category ({category_id})")
    else:
        return categories_br.get(category_id, f"Categoria Desconhecida ({category_id})")

DATASET_FEATURE_MAP = {
    'df_nerdalytics': {
        'description': 'Video-level summary table. One row per video_id. Used for ABC, quantile, and categorical analysis.',
        'features': {
            'video_id': {
                'type': 'text',
                'subtype': 'id',
                'example': 'IAyu0JMb_1U',
                'use': 'label, join'
            },
            'channel_id': {
                'type': 'text',
                'subtype': 'id',
                'example': 'UCKHhA5hN2UohhFDfNXB_cvQ',
                'use': 'label, join'
            },
            'channel_title': {
                'type': 'text',
                'subtype': 'name',
                'example': 'Manual do Mundo',
                'use': 'label'
            },
            'title': {
                'type': 'text',
                'subtype': 'title',
                'example': 'Como é feito o TRATAMENTO DE ESGOTO #Boravê',
                'use': 'label, tooltip'
            },
            'video_type': {
                'type': 'categorical',
                'subtype': 'nominal',
                'example': 'Short',
                'use': 'group, filter'
            },
            'live_content': {
                'type': 'categorical',
                'subtype': 'nominal',
                'example': 'Live',
                'use': 'group, filter'
            },
            'default_audio_language': {
                'type': 'categorical',
                'subtype': 'nominal',
                'example': 'en',
                'use': 'group, filter'
            },
            'category_id': {
                'type': 'categorical',
                'subtype': 'nominal',
                'example': '22',
                'use': 'group, filter'
            },
            'published_at': {
                'type': 'datetime',
                'subtype': 'date',
                'example': '2024-06-04 21:00:11',
                'use': 'filter, time'
            },
            'age_in_days': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 315,
                'use': 'plot, filter'
            },
            'view_count': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 1211722,
                'use': 'plot, agg'
            },
            'like_count': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 61273,
                'use': 'plot, agg'
            },
            'comment_count': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 264,
                'use': 'plot, agg'
            },
            'ss_adult': {
                'type': 'numerical',
                'subtype': 'discrete',
                'example': 2,
                'use': 'group, filter'
            },
            'ss_spoof': {
                'type': 'numerical',
                'subtype': 'discrete',
                'example': 1,
                'use': 'group, filter'
            },
            'ss_medical': {
                'type': 'numerical',
                'subtype': 'discrete',
                'example': 0,
                'use': 'group, filter'
            },
            'ss_violence': {
                'type': 'numerical',
                'subtype': 'discrete',
                'example': 3,
                'use': 'group, filter'
            },
            'ss_racy': {
                'type': 'numerical',
                'subtype': 'discrete',
                'example': 0,
                'use': 'group, filter'
            },
            'caption': {
                'type': 'boolean',
                'subtype': None,
                'example': True,
                'use': 'filter'
            },
            'description': {
                'type': 'text',
                'subtype': 'desc',
                'example': 'Conheça a CESAN: http://www.cesan.com.br\n\nVo...',
                'use': 'tooltip, nlp'
            },
            'tags': {
                'type': 'text',
                'subtype': 'list',
                'example': 'fun,cat',
                'use': 'filter, nlp'
            },
            'thumbnail_url': {
                'type': 'text',
                'subtype': 'url',
                'example': 'http://...',
                'use': 'display'
            }
        }
    },
    'df_slope_full': {
        'description': 'Time-series table. Multiple rows per video_id, includes slope and prediction features.',
        'features': {
            'video_id': {
                'type': 'text',
                'subtype': 'id',
                'example': 'NU8mh3h7Vh4',
                'use': 'label, join'
            },
            'channel_id': {
                'type': 'text',
                'subtype': 'id',
                'example': 'UCKHhA5hN2UohhFDfNXB_cvQ',
                'use': 'label, join'
            },
            'channel_title': {
                'type': 'text',
                'subtype': 'name',
                'example': 'Manual do Mundo',
                'use': 'label'
            },
            'published_at': {
                'type': 'datetime',
                'subtype': 'date',
                'example': '2025-02-26 20:00:12',
                'use': 'filter, time'
            },
            'age_in_days': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 48,
                'use': 'plot, filter'
            },
            'title': {
                'type': 'text',
                'subtype': 'title',
                'example': 'O jeito mais INSANO de fazer FOGO: com ESPELHO!',
                'use': 'label, tooltip'
            },
            'description': {
                'type': 'text',
                'subtype': 'desc',
                'example': 'E se te dissesse que dá para acender fogo sem ...',
                'use': 'tooltip, nlp'
            },
            'category_id': {
                'type': 'categorical',
                'subtype': 'nominal',
                'example': '28',
                'use': 'group, filter'
            },
            'thumbnail_url': {
                'type': 'text',
                'subtype': 'url',
                'example': 'https://i.ytimg.com/vi/NU8mh3h7Vh4/hqdefault.jpg',
                'use': 'display'
            },
            'default_audio_language': {
                'type': 'categorical',
                'subtype': 'nominal',
                'example': 'pt',
                'use': 'group, filter'
            },
            'live_content': {
                'type': 'categorical',
                'subtype': 'nominal',
                'example': 'Não',
                'use': 'group, filter'
            },
            'tags': {
                'type': 'text',
                'subtype': 'list',
                'example': 'fogo,espelho,experiência',
                'use': 'filter, nlp'
            },
            'duration_formatted_seconds': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 2363.73,
                'use': 'plot, filter'
            },
            'caption': {
                'type': 'boolean',
                'subtype': None,
                'example': True,
                'use': 'filter'
            },
            'ss_adult': {
                'type': 'numerical',
                'subtype': 'discrete',
                'example': 0.0,
                'use': 'group, filter'
            },
            'ss_spoof': {
                'type': 'numerical',
                'subtype': 'discrete',
                'example': 0.0,
                'use': 'group, filter'
            },
            'ss_medical': {
                'type': 'numerical',
                'subtype': 'discrete',
                'example': 0.0,
                'use': 'group, filter'
            },
            'ss_violence': {
                'type': 'numerical',
                'subtype': 'discrete',
                'example': 0.0,
                'use': 'group, filter'
            },
            'ss_racy': {
                'type': 'numerical',
                'subtype': 'discrete',
                'example': 0.0,
                'use': 'group, filter'
            },
            'slope_timestamp': {
                'type': 'datetime',
                'subtype': 'timestamp',
                'example': '2025-02-26 20:00:12',
                'use': 'time, index'
            },
            'slope_date': {
                'type': 'datetime',
                'subtype': 'date',
                'example': '2025-02-26',
                'use': 'time, index'
            },
            'view_count_slope': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 534272.59,
                'use': 'plot, trend'
            },
            'like_count_slope': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 572710.01,
                'use': 'plot, trend'
            },
            'comment_count_slope': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 14.19,
                'use': 'plot, trend'
            },
            'linear_view_count_speed': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 2363.73,
                'use': 'plot, trend'
            },
            'slope_view_count_speed': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 123.62,
                'use': 'plot, trend'
            },
            'linear_like_count_speed': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 2363.73,
                'use': 'plot, trend'
            },
            'slope_like_count_speed': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 123.62,
                'use': 'plot, trend'
            },
            'linear_comment_count_speed': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 14.19,
                'use': 'plot, trend'
            },
            'slope_comment_count_speed': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 0.15,
                'use': 'plot, trend'
            },
            'predicted_view_count_7d': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 534272.59,
                'use': 'predict, plot'
            },
            'predicted_view_count_30d': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 572710.01,
                'use': 'predict, plot'
            },
            'predicted_view_count_365d': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 1132559.44,
                'use': 'predict, plot'
            },
            'growth_view_count_7d_percent': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 2.37,
                'use': 'growth, plot'
            },
            'growth_view_count_30d_percent': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 9.73,
                'use': 'growth, plot'
            },
            'growth_view_count_365d_percent': {
                'type': 'numerical',
                'subtype': 'continuous',
                'example': 117.00,
                'use': 'growth, plot'
            }
        }
    }
}

# --- Advanced Automation Utilities ---
def auto_plot_all(df, feature_map):
    """
    Automatically plot all valid pairs using the feature map.
    - Jointplot for pairs of continuous features
    - Violin plot for discrete vs categorical
    - Countplot for categoricals
    Each plot is automatically titled with the feature names.
    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    continuous = [k for k, v in feature_map.items() if v['type'] == 'numerical' and v['subtype'] == 'continuous']
    discrete = [k for k, v in feature_map.items() if v['type'] == 'numerical' and v['subtype'] == 'discrete']
    categorical = [k for k, v in feature_map.items() if v['type'] == 'categorical']

    # 1. Jointplots for all pairs of continuous features
    for i in range(len(continuous)):
        for j in range(i + 1, len(continuous)):
            x, y = continuous[i], continuous[j]
            print(f"\n[auto_plot_all] Jointplot: {x} vs {y}")
            g = sns.jointplot(data=df, x=x, y=y, kind='scatter')
            g.fig.suptitle(f"Jointplot: {x} vs {y}", fontsize=14)
            plt.tight_layout()
            plt.show()

    # 2. Violin plots for each discrete vs each categorical
    for d in discrete:
        for c in categorical:
            print(f"\n[auto_plot_all] Violin plot: {d} by {c}")
            plt.figure()
            sns.violinplot(data=df, x=c, y=d)
            plt.title(f"Violin plot: {d} by {c}")
            plt.tight_layout()
            plt.show()

    # 3. Countplots for each categorical
    for c in categorical:
        print(f"\n[auto_plot_all] Countplot: {c}")
        plt.figure()
        sns.countplot(data=df, x=c)
        plt.title(f"Countplot: {c}")
        plt.tight_layout()
        plt.show()

# --- Advanced/Optional Features ---
def auto_detect_feature_types(df):
    """
    Automatically detect feature types for new tables.
    Returns a dict with column names and guessed types.
    """
    import pandas as pd
    types = {}
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_bool_dtype(dtype):
            types[col] = {'type': 'boolean', 'subtype': None}
        elif pd.api.types.is_numeric_dtype(dtype):
            # Guess discrete vs continuous
            nunique = df[col].nunique()
            if nunique < 15:
                types[col] = {'type': 'numerical', 'subtype': 'discrete'}
            else:
                types[col] = {'type': 'numerical', 'subtype': 'continuous'}
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            types[col] = {'type': 'datetime', 'subtype': 'date'}
        else:
            types[col] = {'type': 'text', 'subtype': None}
    return types

# --- Summary Reporting Example ---
def print_summary_report(df, feature_map):
    """
    Print a summary report of the DataFrame, including:
    - Number of rows/columns
    - List of features by type (continuous, discrete, categorical, boolean, datetime, text)
    - Missing value counts
    """
    print("\n===== SUMMARY REPORT =====")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    for t in ['continuous', 'discrete', 'categorical', 'boolean', 'datetime', 'text']:
        features = [k for k, v in feature_map.items() if (v['type'] == t or v.get('subtype') == t)]
        print(f"{t.title()} features: {features}")
    print("\nMissing values per column:")
    print(df.isnull().sum())
    print("==========================\n")

# --- Advanced Plotting Examples ---
def plot_with_confidence_interval(df, x, y, groupby=None, ci=95):
    """
    Plot y vs x with a confidence interval (uses seaborn lineplot).
    If groupby is provided, plot separate lines per group.
    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    plt.figure()
    if groupby:
        sns.lineplot(data=df, x=x, y=y, hue=groupby, ci=ci)
        plt.title(f"Lineplot with CI: {y} vs {x} by {groupby}")
    else:
        sns.lineplot(data=df, x=x, y=y, ci=ci)
        plt.title(f"Lineplot with CI: {y} vs {x}")
    plt.tight_layout()
    plt.show()

def scatter_with_clusters(df, x, y, color=None, size=None):
    """
    Scatter plot for clustering exploration.
    - x, y: axes
    - color: column name for color grouping (e.g., categorical)
    - size: column name for point size (optional)
    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    plt.figure()
    sns.scatterplot(data=df, x=x, y=y, hue=color, size=size, palette='tab10', alpha=0.7)
    plt.title(f"Scatter: {y} vs {x}" + (f" by {color}" if color else ""))
    plt.tight_layout()
    plt.show()

# --- Example Usage Code Below ---
if __name__ == "__main__":
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pprint
    import os
    from sklearn.preprocessing import LabelEncoder

    # INSTRUCTIONS:
    # 1. Uncomment and set the correct path to load your DataFrame.
    # 2. Set the 'if False:' blocks to 'if True:' to run code interactively.
    # 3. Use the auto_plot_all(df, feature_map) utility for automated visualizations.
    # 4. Expand the feature map as your data grows.
    # 5. Use print_summary_report(df, feature_map) to get a quick overview.
    # 6. Use plot_with_confidence_interval and scatter_with_clusters for advanced plots.

    # df = pd.read_parquet('path/to/df_nerdalytics.parquet')
    # df_slope_full = pd.read_parquet('../ce_app.lab/data/tbl_slope_full.parquet')
    print("Current working directory:", os.getcwd())
    df = pd.read_parquet('../ce_app.lab/data/tbl_nerdalytics.parquet')

    # 1. CLASSIFY COLUMNS USING THE MAP
    table = 'df_nerdalytics'
    feature_map = DATASET_FEATURE_MAP[table]['features']

    # Example: Get all continuous numerical features
    continuous = [k for k, v in feature_map.items() if v['type'] == 'numerical' and v['subtype'] == 'continuous']
    print('Continuous features:', continuous)

    # Example: Get all discrete numerical features
    discrete = [k for k, v in feature_map.items() if v['type'] == 'numerical' and v['subtype'] == 'discrete']
    print('Discrete features:', discrete)

    # Example: Get all categorical features
    categorical = [k for k, v in feature_map.items() if v['type'] == 'categorical']
    print('Categorical features:', categorical)

    # 2. AUTOMATED PLOTTING EXAMPLES
    if True:  # Set to True to run examples
        # a) Jointplot for two continuous features
        if len(continuous) >= 2:
            sns.jointplot(data=df, x=continuous[0], y=continuous[1], kind='scatter').fig.suptitle(f"Jointplot: {continuous[0]} vs {continuous[1]}")
            plt.tight_layout()
            plt.show()

        # b) Violin plot for a discrete numerical vs. categorical
        if discrete and categorical:
            plt.figure()
            sns.violinplot(data=df, x=categorical[0], y=discrete[0])
            plt.title(f"Violin plot: {discrete[0]} by {categorical[0]}")
            plt.tight_layout()
            plt.show()

        # c) Countplot for a categorical feature
        if categorical:
            plt.figure()
            sns.countplot(data=df, x=categorical[0])
            plt.title(f"Countplot: {categorical[0]}")
            plt.tight_layout()
            plt.show()

        # d) Auto-plot all valid pairs
        auto_plot_all(df, feature_map)

        # e) Advanced: Scatter with clusters (e.g., view_count vs age_in_days, color by video_type)
        scatter_with_clusters(df, x='view_count', y='age_in_days', color='video_type')

        # f) Advanced: Lineplot with confidence interval (e.g., like_count vs age_in_days by video_type)
        plot_with_confidence_interval(df, x='age_in_days', y='like_count', groupby='video_type', ci=95)

    # 3. FEATURE ENGINEERING EXAMPLES
    if True:  # Set to True to run examples
        # a) Normalization (Min-Max scaling) for continuous features
        for col in continuous:
            df[f'{col}_norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
        print('Normalized columns:', [f'{col}_norm' for col in continuous])

        # b) One-hot encoding for categoricals
        df_encoded = pd.get_dummies(df, columns=categorical)
        print('Encoded columns:', df_encoded.columns)

        # c) Label encoding for ordinal features (if any)
        ordinal = [k for k, v in feature_map.items() if v['type'] == 'categorical' and v.get('subtype') == 'ordinal']
        for col in ordinal:
            le = LabelEncoder()
            df[f'{col}_encoded'] = le.fit_transform(df[col])
        print('Ordinal encoded columns:', [f'{col}_encoded' for col in ordinal])

    # 4. Print feature map for reference
    pprint.pprint(DATASET_FEATURE_MAP)

    # 5. Summary reporting
    print_summary_report(df, feature_map)

    # 6. Auto-detect feature types for new tables (example)
    if False:
        detected_types = auto_detect_feature_types(df)
        pprint.pprint(detected_types)
# %%
