from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import pandas as pd
from ast import literal_eval

credits_df = pd.read_csv("./tmdb-movie-metadata/tmdb_5000_credits.csv")
movies_df = pd.read_csv("./tmdb-movie-metadata/tmdb_5000_movies.csv")

credits_df = credits_df.rename(columns={"movie_id": "id"}).drop(columns=["title"])

# remove the features that are not useful when recommending a movie to someone
important_features = [
    "genres",
    "id",
    "keywords",
    "title",
    "overview",
    # "popularity", # ? could be important factor, but we'll not keep it as CBR systems do not use numeric features very much
    # "release_date",
    "cast",
    "crew",
]

data = pd.merge(movies_df, credits_df, left_on="id", right_on="id")[important_features]

data.dropna(inplace=True)


def process_genres(genres: str) -> list[str]:
    _genres = literal_eval(genres)
    ret = []
    for item in _genres:
        ret.append(item["name"])
    return ret


process_keywords = process_genres


def process_cast(cast: str, n=3) -> list[str]:
    _cast = literal_eval(cast)
    counter = 0

    ret = []
    for item in _cast:
        if counter < n:
            counter += 1
            ret.append(item["character"])
    return ret


def fetch_director(crew: str) -> list[str]:
    ret = []
    _crew = literal_eval(crew)
    for item in _crew:
        if item["job"].lower() == "director":
            ret.append(item["name"])

    return ret


data["cast"] = data["cast"].apply(process_cast)
data["genres"] = data["genres"].apply(process_genres)
data["keywords"] = data["keywords"].apply(process_keywords)
data["crew"] = data["crew"].apply(fetch_director)
data["overview"] = data["overview"].apply(lambda s: s.split())

data["genres"] = data["genres"].apply(lambda x: [s.replace(" ", "") for s in x])
data["cast"] = data["cast"].apply(lambda x: [s.replace(" ", "") for s in x])
data["crew"] = data["crew"].apply(lambda x: [s.replace(" ", "") for s in x])
data["tags"] = (
    data["overview"] + data["genres"] + data["keywords"] + data["cast"] + data["crew"]
)


new_df = data[["id", "title", "tags"]]

new_df["tags"] = new_df["tags"].apply(lambda x: " ".join(x).lower())


cv = TfidfVectorizer(max_features=5000, stop_words="english")
ps = PorterStemmer()


def stem(text):
    y = []
    for i in text.split():
        y.append(ps.stem(i))

    return " ".join(y)


new_df["tags"] = new_df["tags"].apply(stem)

vectors = cv.fit_transform(new_df["tags"]).toarray()


similarities = cosine_similarity(vectors)


data[data["id"] == new_df["id"]][["id", "title"]].set_index("id").to_csv("movies.csv")
pickle.dump(similarities, open("similarities.csv", "wb"))
