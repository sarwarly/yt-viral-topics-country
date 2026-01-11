import streamlit as st
import requests
from collections import Counter, defaultdict

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

    st.write(f"Fetched {len(videos)} trending videos")

    if not videos:
        st.warning("No data returned from YouTube.")
        st.stop()

    # =========================
    # TOPIC EXTRACTION + VIDEO MAP
    # =========================
    topic_counter = Counter()
    topic_videos = defaultdict(list)

    for v in videos:
        title = v["snippet"]["title"].lower()
        video_url = f"https://www.youtube.com/watch?v={v['id']}"
        channel = v["snippet"]["channelTitle"]

        words = [
            w.strip(".,!?()[]{}")
            for w in title.split()
            if len(w) > 3 and w not in STOP_WORDS
        ]

        for w in set(words):
            topic_counter[w] += 1
            topic_videos[w].append({
                "title": v["snippet"]["title"],
                "url": video_url,
                "channel": channel
            })

    common_topics = topic_counter.most_common(10)

    # =========================
    # OUTPUT
    # =========================
    st.subheader(f"🔥 Viral Topic Signals in {country_name}")

    for topic, count in common_topics:
        st.markdown(f"## 🔹 **{topic}**  ({count} videos)")

        examples = topic_videos[topic][:3]  # show max 3 examples

        for ex in examples:
            st.markdown(
                f"- [{ex['title']}]({ex['url']})  \n"
                f"  *Channel:* {ex['channel']}"
            )

    st.info(
        "Tip: Topics with multiple examples from different channels "
        "indicate real momentum. Study format, hooks, and length — not just views."
    )
