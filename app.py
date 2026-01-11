import streamlit as st
import requests
from collections import defaultdict

# =========================
# CONFIG
# =========================
API_KEY = "AIzaSyBnmylzZY6Up8JLXMokflSP3jGsIX0mCH4"
YOUTUBE_TRENDING_URL = "https://www.googleapis.com/youtube/v3/videos"

# Strong AI / faceless indicators
AI_KEYWORDS = {
    "did you know", "facts", "explained", "ai", "artificial intelligence",
    "history", "mystery", "unknown", "top", "list", "why", "how", "secrets",
    "space", "universe", "psychology", "money", "rich", "luxury"
}

PERSONAL_WORDS = {"i", "we", "my", "our", "me", "us"}

# =========================
# UI
# =========================
st.title("🤖 AI Faceless YouTube Trend Finder")

country_map = {
    "United States": "US",
    "United Kingdom": "GB",
    "Canada": "CA"
}

country_name = st.selectbox("Target Country (High RPM)", list(country_map.keys()))
country_code = country_map[country_name]

video_type = st.radio(
    "Video Type",
    ["Both", "Shorts", "Long"]
)

max_results = st.slider(
    "Trending videos to analyze",
    min_value=20,
    max_value=50,
    value=30
)

if st.button("Find AI / Faceless Trends"):

    params = {
        "part": "snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "regionCode": country_code,
        "maxResults": max_results,
        "key": API_KEY
    }

    data = requests.get(YOUTUBE_TRENDING_URL, params=params, timeout=15).json()
    videos = data.get("items", [])

    st.write(f"Fetched {len(videos)} trending videos")

    if not videos:
        st.warning("No trending data found.")
        st.stop()

    # =========================
    # FORMAT DETECTION
    # =========================
    format_groups = defaultdict(list)

    for v in videos:
        title = v["snippet"]["title"].lower()
        description = v["snippet"].get("description", "").lower()
        text = f"{title} {description}"

        # Skip personal / face-based content
        if any(p in text.split() for p in PERSONAL_WORDS):
            continue

        # Detect Shorts (simple but effective)
        duration = v["contentDetails"]["duration"]
        is_short = "M" not in duration

        if video_type == "Shorts" and not is_short:
            continue
        if video_type == "Long" and is_short:
            continue

        # AI / faceless confidence
        matched = [k for k in AI_KEYWORDS if k in text]
        if len(matched) < 1:
            continue

        # Classify format
        if "did you know" in text or "facts" in text:
            format_name = "AI Facts / Curiosity"
        elif "history" in text:
            format_name = "AI History Explainers"
        elif "mystery" in text or "unknown" in text:
            format_name = "Mystery / Unexplained"
        elif "money" in text or "rich" in text or "luxury" in text:
            format_name = "Money / Luxury Facts"
        elif "space" in text or "universe" in text:
            format_name = "Space / Science AI"
        else:
            format_name = "Generic AI Explainers"

        format_groups[format_name].append({
            "title": v["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={v['id']}",
            "channel": v["snippet"]["channelTitle"],
            "short": is_short
        })

    # =========================
    # OUTPUT
    # =========================
    if not format_groups:
        st.warning("No strong AI / faceless formats found. Try another country or 'Both'.")
        st.stop()

    st.subheader(f"🔥 AI / Faceless Formats Trending in {country_name}")

    for fmt, vids in sorted(format_groups.items(), key=lambda x: len(x[1]), reverse=True):
        st.markdown(f"## 🤖 {fmt}  ({len(vids)} videos)")

        for v in vids[:3]:
            tag = "Short" if v["short"] else "Long"
            st.markdown(
                f"- [{v['title']}]({v['url']})  \n"
                f"  *Channel:* {v['channel']} | *Type:* {tag}"
            )

    st.info(
        "These formats show signs of AI or faceless production. "
        "Study structure, hooks, pacing, and repetition — not the exact content."
    )
