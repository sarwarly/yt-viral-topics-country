import streamlit as st
import requests
from collections import defaultdict
from datetime import datetime, timezone

# =========================
# CONFIG
# =========================
API_KEY = "AIzaSyBnmylzZY6Up8JLXMokflSP3jGsIX0mCH4"
YOUTUBE_TRENDING_URL = "https://www.googleapis.com/youtube/v3/videos"

# Rescue + emotion keywords (channel-specific)
RESCUE_KEYWORDS = {
    "rescue", "rescued", "saved", "saving",
    "trapped", "abandoned", "injured", "dying",
    "found", "starving", "survived", "last breath",
    "helped", "crying", "alone"
}

# Words that indicate personal / face-based content
PERSONAL_WORDS = {"i", "we", "my", "our", "me", "us"}

# =========================
# UI
# =========================
st.title("🐾 Last Breath Rescue – Trend & Format Finder")

st.markdown(
    "This tool finds **faceless, replicable rescue video formats** "
    "that are currently working in **high-RPM countries**."
)

country_map = {
    "United States": "US",
    "United Kingdom": "GB",
    "Canada": "CA"
}

country_name = st.selectbox(
    "Target Audience Country",
    list(country_map.keys())
)
country_code = country_map[country_name]

days = st.selectbox(
    "Time window",
    [7, 14, 30],
    index=1
)

video_type = st.radio(
    "Video Type",
    ["Both", "Shorts", "Long"],
    index=0
)

max_results = st.slider(
    "Trending videos to analyze",
    min_value=20,
    max_value=50,
    value=30
)

if st.button("Find Formats for Last Breath Rescue"):

    params = {
        "part": "snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "regionCode": country_code,
        "maxResults": max_results,
        "key": API_KEY
    }

    res = requests.get(YOUTUBE_TRENDING_URL, params=params, timeout=15).json()
    videos = res.get("items", [])

    st.write(f"Fetched {len(videos)} trending videos")

    if not videos:
        st.warning("No trending videos returned.")
        st.stop()

    # =========================
    # FORMAT ANALYSIS
    # =========================
    format_groups = defaultdict(list)
    now = datetime.now(timezone.utc)

    for v in videos:
        title = v["snippet"]["title"].lower()
        description = v["snippet"].get("description", "").lower()
        text = f"{title} {description}"

        # --- Rescue relevance filter ---
        if not any(k in text for k in RESCUE_KEYWORDS):
            continue

        # --- Faceless filter ---
        if any(p in text.split() for p in PERSONAL_WORDS):
            continue

        # --- Time window filter ---
        published_at = datetime.fromisoformat(
            v["snippet"]["publishedAt"].replace("Z", "+00:00")
        )
        days_old = (now - published_at).days
        if days_old > days:
            continue

        # --- Shorts / Long detection (safe heuristic) ---
        duration = v["contentDetails"]["duration"]
        is_short = "M" not in duration

        if video_type == "Shorts" and not is_short:
            continue
        if video_type == "Long" and is_short:
            continue

        # --- Format classification ---
        if "before" in text and "after" in text:
            format_name = "Before → After Rescue"
        elif "no one" in text or "left to die" in text:
            format_name = "Hopeless → Saved Story"
        elif "found" in text and "alone" in text:
            format_name = "Found Alone Rescue"
        elif "injured" in text or "dying" in text:
            format_name = "Critical Condition Rescue"
        elif "rescued" in text or "saved" in text:
            format_name = "Direct Rescue Clip"
        else:
            format_name = "Emotional Rescue Short"

        format_groups[format_name].append({
            "title": v["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={v['id']}",
            "channel": v["snippet"]["channelTitle"],
            "type": "Short" if is_short else "Long",
            "days_old": days_old
        })

    # =========================
    # OUTPUT
    # =========================
    if not format_groups:
        st.warning(
            "No strong rescue formats found. "
            "Try increasing the time window or selecting 'Both'."
        )
        st.stop()

    st.subheader(f"🔥 What’s Working for *Last Breath Rescue* ({country_name})")

    for fmt, vids in sorted(
        format_groups.items(),
        key=lambda x: len(x[1]),
        reverse=True
    ):
        st.markdown(f"## 🟢 {fmt}  ({len(vids)} videos)")

        for v in vids[:3]:
            st.markdown(
                f"- [{v['title']}]({v['url']})  \n"
                f"  *Channel:* {v['channel']} | "
                f"*Type:* {v['type']} | "
                f"*Age:* {v['days_old']} days"
            )

    st.info(
        "Focus on formats that appear multiple times across different channels. "
        "Copy the **structure**, **length**, and **emotional arc** — not the video."
    )
