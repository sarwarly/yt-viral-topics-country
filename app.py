import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs

# =========================
# CONFIG
# =========================
API_KEY = "AIzaSyBnmylzZY6Up8JLXMokflSP3jGsIX0mCH4"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

# =========================
# PAGE CONFIG (IMPORTANT)
# =========================
st.set_page_config(
    page_title="YouTube Video Analyzer",
    page_icon="🎬",
    layout="wide"
)

# =========================
# HELPERS
# =========================
def extract_video_id(url: str):
    parsed = urlparse(url)
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed.query).get("v", [None])[0]
    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/")
    return None

# =========================
# SIDEBAR (INPUTS)
# =========================
with st.sidebar:
    st.markdown("## 🎯 Video Analyzer")
    st.markdown(
        "Analyze any YouTube video to extract **title, description, thumbnail, "
        "and available tags**.\n\n"
        "Built for **faceless creators**."
    )

    video_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=XXXXXXXX"
    )

    analyze = st.button("🔍 Analyze Video", use_container_width=True)

# =========================
# MAIN HEADER
# =========================
st.markdown(
    """
    <h1 style="margin-bottom: 0;">🎬 YouTube Video Intelligence</h1>
    <p style="color: #888; margin-top: 4px;">
        Clean metadata extraction for faceless & automation channels
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =========================
# ANALYSIS
# =========================
if analyze:

    video_id = extract_video_id(video_url)

    if not video_id:
        st.error("❌ Invalid YouTube URL")
        st.stop()

    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": API_KEY
    }

    res = requests.get(YOUTUBE_VIDEO_URL, params=params, timeout=15).json()
    items = res.get("items", [])

    if not items:
        st.error("Video not found or API error.")
        st.stop()

    video = items[0]
    snippet = video["snippet"]
    stats = video.get("statistics", {})

    # =========================
    # VIDEO PREVIEW CARD
    # =========================
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.image(
            snippet["thumbnails"]["high"]["url"],
            use_container_width=True
        )

    with col2:
        st.markdown("### 🎬 Video Title")
        st.code(snippet.get("title", ""), language="text")

        st.markdown("**Channel:** " + snippet.get("channelTitle", "N/A"))
        st.markdown("**Published:** " + snippet.get("publishedAt", "N/A")[:10])

    st.divider()

    # =========================
    # DESCRIPTION
    # =========================
    st.markdown("### 📝 Description (Click to copy)")
    st.code(snippet.get("description", ""), language="text")

    # =========================
    # TAGS
    # =========================
    st.markdown("### 🏷 Tags")
    tags = snippet.get("tags", [])

    if tags:
        st.code(", ".join(tags), language="text")
    else:
        st.warning("Tags not publicly available for this video.")

    # =========================
    # STATS ROW
    # =========================
    st.divider()
    st.markdown("### 📊 Performance")

    s1, s2, s3 = st.columns(3)

    s1.metric("Views", stats.get("viewCount", "N/A"))
    s2.metric("Likes", stats.get("likeCount", "N/A"))
    s3.metric("Comments", stats.get("commentCount", "N/A"))

    st.info(
        "Use this data for **analysis and inspiration only**. "
        "Always rewrite titles and descriptions in your own words."
    )
