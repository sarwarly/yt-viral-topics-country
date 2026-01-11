import streamlit as st
import requests
from collections import Counter

# =========================
# CONFIG
# =========================
API_KEY = "AIzaSyBnmylzZY6Up8JLXMokflSP3jGsIX0mCH4"

YOUTUBE_TRENDING_URL = "https://www.googleapis.com/youtube/v3/videos"

STOP_WORDS = {
    "the","a","an","and","or","of","to","in","for","on","with",
    "official","video","music","feat","ft","vs","from","by",
    "is","are","this","that","at","as","it","be","new"
}

# =========================
# UI
# =========================
st.title("🌍 YouTube Viral Topics Finder (By Country)")

country_map = {
    "United States": "US",
    "India": "IN",
    "Bangladesh": "BD",
    "United Kingdom": "GB",
    "Canada": "CA"
}

country_name = st.selectbox("Select Country", list(country_map.keys()))
country_code = country_map[country_name]

max_results = st.slider(
    "Number of trending videos to analyze",
    min_value=10,
    max_value=50,
    value=30
)

if st.button("Find Viral Topics"):

    params = {
        "part": "snippet",
        "chart": "mostPopular",
        "regionCode": country_code,
        "maxResults": max_results,
        "key": API_KEY
    }

    response = requests.get(YOUTUBE_TRENDING_URL, params=params, timeout=15)
    data = response.json()
    videos = data.get("items", [])

    # ---- Debug / safety ----
    st.write(f"Fetched {len(videos)} trending videos")

    if not videos:
        st.warning("No data returned from YouTube.")
        st.stop()

    # =========================
    # TOPIC EXTRACTION
    # =========================
    topic_words = []

    for v in videos:
        title = v["snippet"]["title"].lower()

        words = [
            w.strip(".,!?()[]{}")
            for w in title.split()
            if len(w) > 3 and w not in STOP_WORDS
        ]

        topic_words.extend(words)

    if not topic_words:
        st.warning("No usable words extracted from titles.")
        st.stop()

    counter = Counter(topic_words)
    common_topics = counter.most_common(15)

    # =========================
    # OUTPUT
    # =========================
    st.subheader(f"🔥 Viral Topic Signals in {country_name}")

    for topic, count in common_topics:
        st.write(f"**{topic}** — appears in {count} trending videos")

    st.info(
        "Tip: Repeated words across trending videos indicate rising or dominant topics. "
        "Ignore filler words and focus on intent words."
    )
