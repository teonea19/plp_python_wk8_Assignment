
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re

# Page configuration
st.set_page_config(
    page_title="CORD-19 Data Explorer",
    page_icon="🔬",
    layout="wide"
)

# Title and description
st.title("🔬 CORD-19 COVID-19 Research Explorer")
st.write("Explore the metadata of COVID-19 research papers from the CORD-19 dataset")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('metadata.csv')
        # Basic cleaning
        df_clean = df.dropna(subset=['title']).copy()
        if 'publish_time' in df_clean.columns:
            df_clean['publish_time'] = pd.to_datetime(df_clean['publish_time'], errors='coerce')
            df_clean['publication_year'] = df_clean['publish_time'].dt.year
        return df_clean
    except:
        return None

df = load_data()

if df is None:
    st.error("Could not load metadata.csv. Please ensure it's in the same directory.")
else:
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Year filter
    if 'publication_year' in df.columns:
        min_year = int(df['publication_year'].min())
        max_year = int(df['publication_year'].max())
        year_range = st.sidebar.slider(
            "Select publication year range:",
            min_year, max_year, (min_year, max_year)
        )
        filtered_df = df[(df['publication_year'] >= year_range[0]) & 
                        (df['publication_year'] <= year_range[1])]
    else:
        filtered_df = df
    
    # Journal filter
    if 'journal' in df.columns:
        journals = ['All'] + df['journal'].dropna().unique().tolist()[:20]  # Top 20 journals
        selected_journal = st.sidebar.selectbox("Select journal:", journals)
        if selected_journal != 'All':
            filtered_df = filtered_df[filtered_df['journal'] == selected_journal]
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dataset Overview")
        st.write(f"**Total papers:** {len(filtered_df):,}")
        st.write(f"**Columns:** {len(filtered_df.columns)}")
        
        if 'publication_year' in filtered_df.columns:
            st.write(f"**Year range:** {filtered_df['publication_year'].min()} - {filtered_df['publication_year'].max()}")
    
    with col2:
        st.subheader("Sample Data")
        st.dataframe(filtered_df[['title', 'journal', 'publication_year']].head(10) 
                    if 'journal' in filtered_df.columns else filtered_df[['title']].head(10))
    
    # Visualizations
    st.subheader("Visualizations")
    
    # Publications by year
    if 'publication_year' in filtered_df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        year_counts = filtered_df['publication_year'].value_counts().sort_index()
        ax.bar(year_counts.index, year_counts.values, color='skyblue')
        ax.set_title('Publications by Year')
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of Papers')
        st.pyplot(fig)
    
    # Top journals
    if 'journal' in filtered_df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        top_journals = filtered_df['journal'].value_counts().head(10)
        top_journals.plot(kind='barh', ax=ax, color='lightgreen')
        ax.set_title('Top 10 Journals')
        ax.set_xlabel('Number of Publications')
        ax.invert_yaxis()
        st.pyplot(fig)
    
    # Word cloud
    if 'title' in filtered_df.columns:
        st.subheader("Title Word Cloud")
        all_titles = ' '.join(filtered_df['title'].dropna().astype(str))
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_titles.lower())
        stop_words = set(['the', 'and', 'of', 'in', 'to', 'a', 'for', 'with', 'on'])
        filtered_words = [word for word in words if word not in stop_words]
        
        if filtered_words:
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(filtered_words))
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)

# Instructions to run
st.sidebar.markdown("---")
st.sidebar.info("To run this app: streamlit run app.py")
