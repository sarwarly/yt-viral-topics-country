import streamlit as st
import requests
from collections import Counter

API_KEY = "AIzaSyBnmylzZY6Up8JLXMokflSP3jGsIX0mCH4"

YOUTUBE_TRENDING_URL = "https://www.googleapis.com/youtube/v3/videos"

st.title("🌍 YouTube Viral Topics Finder (By Country)")

# -------- UI --------
country = st.selectbox(
    "Select Country",
    {
        "United States": "US",
        "India": "IN",
        "Bangladesh": "BD",
        "United Kingdom": "GB",
        "Canada": "CA"
    }
)

video_type = st.radio(
    "Video Type",
    ["Both", "Shorts", "Long"]
)

max_results = st.slider(
    "Number of trending videos to analyze",
    10, 50, 25
)

# -------- Fetch Button --------
if st.button("Find Viral Topics"):

    params = {
        "part": "snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "regionCode": country,
        "maxResults": max_results,
        "key": API_KEY
    }

    res = requests.get(YOUTUBE_TRENDING_URL, params=params).json()
    videos = res.get("items", [])

    if not videos:
        st.warning("No data found.")
        st.stop()

    topic_phrases = []

    for v in videos:
        duration = v["contentDetails"]["duration"]

        # Shorts / Long filtering
        is_short = "M" not in duration or duration.startswith("PT0")

        if video_type == "Shorts" and not is_short:
            continue
        if video_type == "Long" and is_short:
            continue

        title = v["snippet"]["title"].lower()

        words = [w for w in title.split() if len(w) > 3]
        topic_phrases.extend(words)

    counter = Counter(topic_phrases)
    common_topics = counter.most_common(15)

    st.subheader("🔥 Viral Topic Signals")

    for topic, count in common_topics:
        st.write(f"**{topic}** — appears in {count} trending videos")


