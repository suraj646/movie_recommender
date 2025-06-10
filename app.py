import streamlit as st
import pickle
import pandas as pd
import requests
from PIL import Image
import time
from streamlit-lottie import st-lottie


# --- Load Data ---
@st.cache_data
def load_data():
    movies_df = pickle.load(open('movies.pkl', 'rb'))
    similarities = pickle.load(open('similarity.pkl', 'rb'))
    return movies_df, similarities


movies_df, similarities = load_data()

# --- OMDB API Setup ---
OMDB_API_KEY = "15a168c3"


# --- Load Lottie Animation ---
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_movie = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_5tkzkblw.json")

# --- Custom CSS ---
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }
    .stSelectbox > div > div {
        background-color: #2d2d2d !important;
        color: white !important;
    }
    .movie-card {
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        background: rgba(45, 45, 45, 0.7);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
    .title {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #ff8a00, #e52e71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 20px;
    }
    .recommend-btn {
        width: 100%;
        padding: 12px;
        border-radius: 25px;
        background: linear-gradient(90deg, #ff8a00, #e52e71);
        color: white;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .recommend-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(255, 138, 0, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- App Header ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<h1 class="title">🍿 Movie Magic Recommender</h1>', unsafe_allow_html=True)
    if lottie_movie:
        st_lottie(lottie_movie, height=200, key="movie")


# --- Movie Poster Fetch ---
@st.cache_data(ttl=3600)
def fetch_poster(movie_title):
    try:
        formatted_title = movie_title.replace(" ", "+")
        url = f"http://www.omdbapi.com/?t={formatted_title}&apikey={OMDB_API_KEY}"
        response = requests.get(url).json()
        return response['Poster'] if 'Poster' in response and response['Poster'] != 'N/A' else None
    except:
        return None


# --- Recommendation Engine ---
def recommend(movie):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarities[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    return [movies_df.iloc[i[0]].title for i in movies_list]


# --- Main App ---
with st.container():
    selected_movie = st.selectbox(
        "🎬 Select a movie you love:",
        movies_df['title'].values,
        index=0,
        help="Choose a movie to get similar recommendations"
    )

    if st.button("✨ Get Magic Recommendations", key="recommend_btn", help="Click to see recommendations"):
        with st.spinner('🔮 Finding cinematic treasures...'):
            time.sleep(1)  # Simulate loading
            recommendations = recommend(selected_movie)

            # Selected Movie Display
            st.success("Here's what we found!")
            poster_url = fetch_poster(selected_movie)

            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f'<div class="movie-card">', unsafe_allow_html=True)
                st.image(poster_url if poster_url else "https://via.placeholder.com/300x450?text=No+Poster",
                         use_container_width=True)  # Fixed: Replaced use_column_width
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                try:
                    movie_data = requests.get(
                        f"http://www.omdbapi.com/?t={selected_movie.replace(' ', '+')}&apikey={OMDB_API_KEY}"
                    ).json()

                    st.markdown(f"""
                    <div class="movie-card">
                        <h3>{selected_movie}</h3>
                        <p>⭐ <b>Rating:</b> {movie_data.get('imdbRating', 'N/A')}</p>
                        <p>📅 <b>Year:</b> {movie_data.get('Year', 'N/A')}</p>
                        <p>⏱️ <b>Runtime:</b> {movie_data.get('Runtime', 'N/A')}</p>
                        <p>🎭 <b>Genre:</b> {movie_data.get('Genre', 'N/A')}</p>
                        <p>📜 <b>Plot:</b> {movie_data.get('Plot', 'Not available')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                except:
                    st.warning("Couldn't fetch additional details for this movie")

            # Recommendations Display
            st.markdown("## 🎥 You Might Also Enjoy...")
            cols = st.columns(5)

            for i, movie in enumerate(recommendations):
                with cols[i]:
                    poster = fetch_poster(movie)
                    st.markdown(f'<div class="movie-card">', unsafe_allow_html=True)
                    st.image(poster if poster else "https://via.placeholder.com/200x300?text=No+Poster",
                             caption=movie,
                             use_container_width=True)  # Fixed: Replaced use_column_width
                    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <p>Made with ❤️ using Streamlit | Movie data from OMDB API</p>
</div>
""", unsafe_allow_html=True)
