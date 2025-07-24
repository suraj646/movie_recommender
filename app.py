import streamlit as st
import pandas as pd
import numpy as np
import pickle

# ✅ Page configuration
st.set_page_config(page_title="Movie Recommender 🎬", layout="centered", page_icon="🎞️")


# ✅ Load data
@st.cache_data
def load_data():
    movies_df = pickle.load(open('movies.pkl', 'rb'))
    similarities = pickle.load(open('similarity.pkl', 'rb'))
    return movies_df, similarities


movies_df, similarities = load_data()

# ✅ Custom style (basic light theme)
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;  /* For dark theme */
    }
    .recommend-box {
        background-color: #ffffff;
        color: #000000;  /* <- Make text visible */
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ App title and subtitle
st.markdown("<h1 style='text-align: center;'>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Find movies similar to your favorite ones!</p>", unsafe_allow_html=True)
st.markdown("---")

# ✅ Movie selection
movie_name = st.selectbox("📽️ Select a Movie:", sorted(movies_df['title'].unique()))


# ✅ Recommendation logic
def recommend(movie):
    matched_movies = movies_df[movies_df['title'].str.lower().str.strip() == movie.lower().strip()]

    if matched_movies.empty:
        return None

    movie_index = matched_movies.index[0]
    distances = similarities[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    return [movies_df.iloc[i[0]].title for i in movie_list]


# ✅ Recommend button
if st.button("🎯 Recommend"):
    recommendations = recommend(movie_name)
    if recommendations:
        st.markdown("### ✅ Top 5 Recommendations:")
        for i, movie in enumerate(recommendations, 1):
            st.markdown(f"<div class='recommend-box'><b>{i}. {movie}</b></div>", unsafe_allow_html=True)
    else:
        st.error("❌ Movie not found. Please try a different title.")

# ✅ Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Made with ❤️ using Streamlit</p>", unsafe_allow_html=True)
