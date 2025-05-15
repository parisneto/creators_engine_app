import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def analytics2_section2(df_nerdalytics, df_playlist_full_dedup):
    st.write("This is the page for Metadata 2")

    # st.dataframe(df)
    len1 = len(df_nerdalytics)
    st.write("df2 from df_nerdalytics.shape before dropNa + Duplicates: ", df_nerdalytics.shape)
    df2 = df_nerdalytics.dropna(subset=['view_count']).copy()
    df2.dropna(subset=['video_type'], inplace=True)
    len2 = len(df2)
    st.write("df2 from df_nerdalytics.shape after dropNa: ", df2.shape)
    df2.drop_duplicates(inplace=True)
    len3 = len(df2)
    st.write("df2 from df_nerdalytics.shape after dropNa + Duplicates: ", df2.shape)
    # df2.dropna(subset=['view_count'], inplace=True)
    # df2.dropna(subset=['like_count'], inplace=True)
    df2.dropna(subset=['comment_count'], inplace=True)
    len4 = len(df2)
    st.write("df2 from df_nerdalytics.shape after dropNa + Duplicates: ", df2.shape)
    st.write("len1: ", len1)
    st.write("len2: ", len2)
    st.write("len3: ", len3)
    st.write("len4: ", len4)
    percent = f"{len4/len1*100:.2f}%"
    st.write("len4/Len1: ", percent)
    st.subheader("Linhas Eliminadas " + percent)





    st.divider()

    chart_data = df2[['like_count', 'view_count', 'comment_count']]
    st.line_chart(chart_data)




    st.divider()

    st.line_chart(data = df2,
    x = 'age_in_days',
    y = 'view_count',
    x_label = 'age_in_days',
    y_label = 'view_count',
    color='video_type'
    )

    st.divider()

    # Assuming your DataFrame 'df2' is ready

    # Create a new column with the log-transformed view counts
    df2['log_view_count'] = np.log1p(df2['view_count']) # Use np.log1p to handle zero values

    fig, ax = plt.subplots()
    sns.histplot(data=df2,
                x='log_view_count', # Plot the log-transformed data
                bins=50,
                hue='video_type',
                shrink=0.8,
                kde=True, # Now the KDE will be calculated on the log-transformed data
                ax=ax)

    # Set appropriate x-axis labels (optional, but makes it more interpretable)
    xticks = np.log1p([0, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000, 500000000])
    xticklabels = ['0', '100', '1K', '10K', '100K', '1M', '10M', '100M', '500M']
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, rotation=45, ha='right')
    ax.set_xlabel("View Count (Log Scale)")
    ax.set_ylabel("Count")
    ax.set_title("Histogram of Video View Counts (Log Scaled with KDE)")
    st.pyplot(fig, use_container_width=False)
    st.divider()

    fig, ax = plt.subplots()
    sns.histplot(data=df2,
             x='view_count', # Use 'x' for the variable you want the histogram and KDE for
             bins=100, # Adjust the number of bins as needed
             kde=True, # This is what overlays the curve
             log_scale=True,
             ax=ax)
    ax.set_xlabel("view_count")
    ax.set_ylabel("Count")
    ax.set_title("Histogram of View Count with KDE")
    st.pyplot(fig)

    st.divider()

    fig, ax = plt.subplots()  # Create a Matplotlib figure and axes
    sns.histplot(data=df2,
    x='view_count',
    bins =100,
    # color='red',
    hue='video_type',
    shrink=0.8,

    kde=True,
    ax=ax,
    # log_scale=True) # Pass the axes object to seaborn
    log_scale=False) # Pass the axes object to seaborn
    ax.set_title("Histogram of Video View Counts")
    # ax.set_xlim(0, 51000000) # Example: Set x-axis limit to 1 million

    st.pyplot(fig, use_container_width=False) # Pass the Matplotlib figure to st.pyplot()

