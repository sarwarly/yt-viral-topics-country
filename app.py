import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs

# =========================
# CONFIG
# =========================
API_KEY = "AIzaSyBnmylzZY6Up8JLXMokflSP3jGsIX0mCH4"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

# =========================
# HELPERS
# =========================
def extract_video_id(url: str):
    """Extract video ID from YouTube URL"""
    parsed = urlparse(url)

    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed.query).get("v", [None])[0]

    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/")

    return None

# =========================
# UI
# =========================
st.title("🔍 YouTube Video Analyzer (For Faceless Channels)")

st.markdown(
    "Paste a **YouTube video URL** to extract metadata like "
    "**title, description, thumbnail, and tags**. "
    "Useful for studying formats and rewriting safely."
)

video_url = st.text_input(
    "Enter YouTube Video URL",
    placeholder="https://www.youtube.com/watch?v=XXXXXXXXXXX"
)

if st.button("Analyze Video"):

    video_id = extract_video_id(video_url)

    if not video_id:
        st.error("Invalid YouTube URL. Please check and try again.")
        st.stop()

    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": API_KEY
    }

    res = requests.get(YOUTUBE_VIDEO_URL, params=params, timeout=15).json()
    items = res.get("items", [])

    if not items:
        st.error("Video not found or API access issue.")
        st.stop()

    video = items[0]
    snippet = video["snippet"]
    stats = video.get("statistics", {})

    # =========================
# OUTPUT
# =========================
st.subheader("📌 Video Details")

st.markdown("### 🎬 Title (Click copy)")
st.code(snippet.get("title", "N/A"), language="text")

st.markdown("### 📺 Channel")
st.write(snippet.get("channelTitle", "N/A"))

st.markdown("### 🖼 Thumbnail")
st.image(snippet["thumbnails"]["high"]["url"])

st.markdown("### 📝 Description (Click copy)")
st.code(snippet.get("description", "N/A"), language="text")

st.markdown("### 🏷 Tags (Click copy)")
tags = snippet.get("tags", [])

if tags:
    st.code(", ".join(tags), language="text")
else:
    st.warning("No tags found (uploader may have hidden them).")

st.markdown("### 📊 Statistics")
st.write({
    "Views": stats.get("viewCount", "N/A"),
    "Likes": stats.get("likeCount", "N/A"),
    "Comments": stats.get("commentCount", "N/A"),
})

st.info(
    "You can copy **title, description, and tags** using the copy button. "
    "Rewrite everything in your own words before using."
)

