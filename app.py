import streamlit as st
import pandas as pd
import pickle
import os
import re
import requests

BEARER_TOKEN = os.environ.get("TMDB_BEARER_TOKEN")

similarities = pickle.load(open("similarities.csv", "rb"))
movies = pd.read_csv("./movies.csv")
movies_title = movies["title"].values
movies_id = movies["id"].values
movies_display_list = [
    f"{movies_title[i]} (id={movies_id[i]})" for i in range(len(movies_title))
]
pattern = re.compile(r"(.+) \(id=.+\)")


def fetch_poster(movie_id):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }

    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}&language=en-US",
        headers=headers,
    )
    data = response.json()
    # st.text(data)
    return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"


def recommend(movie: str, movies_df: pd.DataFrame, k=5):
    assert k > 0, ""
    movie_index = movies_df[movies_df["title"] == movie].index[0]
    recommended_movies = sorted(
        list(enumerate(similarities[movie_index])),
        key=lambda x: x[1],
        reverse=True,
    )[1 : k + 1]
    ret = []
    rec_posters = []
    for recommendation in recommended_movies:
        movie_id = movies_df.iloc[recommendation[0]].id
        title = movies_df.iloc[recommendation[0]].title
        # fetch movie poster
        try:
            poster = fetch_poster(movie_id)
            rec_posters.append(poster)
        except Exception:
            st.text(f"Failed to fetch poster for {title}")
            rec_posters.append(
                "https://image.tmdb.org/t/p/w500/d7px1FQxW4tngdACVRsCSaZq0Xl.jpg"
            )
        ret.append(title)

    # ret = [movies_df.iloc[id].title for id, _ in recommended_movies]
    return ret, rec_posters


st.title("Movie Recommender System")

option = st.selectbox("Recommend movie similar to:", movies_display_list)
k = st.selectbox("How many movies to recommend?", range(1, 11))
if st.button("Recommend"):
    option = pattern.match(option)
    ref_movie = option.group(1) if option else "Unknown Movie"
    if ref_movie != "Unknown Movie":
        recommendations, posters = recommend(ref_movie, movies, k=k)

        cols = st.columns(3)
        for i in range(len(recommendations)):
            with cols[i % 3]:
                st.text(recommendations[i])
                if posters[i]:
                    st.image(posters[i])
