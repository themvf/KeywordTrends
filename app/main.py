import streamlit as st

from app.analysis.keywords import merge_platform_counts
from app.config import get_settings
from app.firecrawl_client import FirecrawlClient
from app.sources.etsy import extract_listings, find_listing_urls
from app.sources.instagram import InstagramClient, fetch_hashtag_posts
from app.sources.youtube import YouTubeClient, fetch_videos
from app.storage.db import init_db, get_session
from app.storage.repository import (
    create_search,
    get_recent_search,
    load_results,
    platforms_key,
    list_recent_searches,
    store_etsy,
    store_instagram,
    store_youtube,
)
from app.ui.components import keyword_bar, price_histogram, render_table, stat_cards


st.set_page_config(page_title="Niche Research", layout="wide")

settings = get_settings()
init_db()


def key_banner() -> None:
    missing = []
    active = []
    if settings.firecrawl_api_key:
        active.append("Firecrawl")
    else:
        missing.append("Firecrawl (Etsy/Web)")
    if settings.youtube_api_key:
        active.append("YouTube")
    else:
        missing.append("YouTube")
    if settings.instagram_token and settings.instagram_user_id:
        active.append("Instagram")
    else:
        missing.append("Instagram")
    st.caption(f"Active keys: {', '.join(active) if active else 'none'}")
    if missing:
        st.warning("Missing keys: " + ", ".join(missing))


def fetch_youtube_rows(keyword: str, max_results: int = 12) -> list[dict]:
    if not settings.youtube_api_key:
        raise ValueError("YouTube API key missing")
    client = YouTubeClient(settings.youtube_api_key)
    items = fetch_videos(client, keyword, max_results=max_results, language=settings.default_language)
    rows = []
    for item in items:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        video_id = item.get("id")
        rows.append(
            {
                "Title": snippet.get("title"),
                "Channel": snippet.get("channelTitle"),
                "Views": int(stats.get("viewCount", 0)) if stats.get("viewCount") else None,
                "Published": snippet.get("publishedAt"),
                "Tags": snippet.get("tags", []),
                "Link": f"https://www.youtube.com/watch?v={video_id}",
                "video_id": video_id,
            }
        )
    return rows


def fetch_etsy_rows(keyword: str, max_results: int = 12) -> list[dict]:
    if not settings.firecrawl_api_key:
        raise ValueError("Firecrawl API key missing")
    client = FirecrawlClient(settings.firecrawl_api_key)
    urls = find_listing_urls(client, keyword, limit=max_results)
    listings = extract_listings(client, urls)
    rows = []
    for lis in listings:
        rows.append(
            {
                "Title": lis.get("title"),
                "Price": lis.get("price"),
                "Currency": lis.get("currency"),
                "Rating": lis.get("rating"),
                "#Reviews": lis.get("review_count"),
                "Tags": lis.get("tags") or [],
                "URL": lis.get("url"),
            }
        )
    return rows


def fetch_instagram_rows(keyword: str, max_results: int = 20) -> list[dict]:
    if not (settings.instagram_token and settings.instagram_user_id):
        raise ValueError("Instagram token or user id missing")
    client = InstagramClient(settings.instagram_token)
    hashtag = keyword.replace(" ", "")
    posts = fetch_hashtag_posts(client, hashtag=hashtag, user_id=settings.instagram_user_id, limit=max_results)
    rows = []
    for post in posts:
        caption = post.get("caption", "")
        hashtags = [word for word in caption.split() if word.startswith("#")]
        rows.append(
            {
                "Caption": caption,
                "Likes": post.get("like_count"),
                "Comments": post.get("comments_count"),
                "Hashtags": hashtags,
                "Link": post.get("permalink"),
                "Thumbnail": post.get("media_url"),
                "post_id": post.get("id"),
            }
        )
    return rows


def run_search(keyword: str, toggles: dict, freshness_hours: int = 48) -> dict:
    key = platforms_key(toggles)
    cached = get_recent_search(keyword, key, freshness_hours=freshness_hours)
    if cached:
        st.success(f"Loaded cached results from {cached.created_at.isoformat()} (UTC)")
        return load_results(cached.id)

    search = create_search(keyword, key)
    results = {"youtube": [], "etsy": [], "instagram": []}

    if toggles.get("youtube"):
        with st.spinner("Fetching YouTube videos..."):
            try:
                yt_rows = fetch_youtube_rows(keyword)
                store_youtube(search.id, yt_rows)
                results["youtube"] = yt_rows
            except Exception as exc:
                st.error(f"YouTube error: {exc}")

    if toggles.get("etsy"):
        with st.spinner("Fetching Etsy listings via Firecrawl..."):
            try:
                etsy_rows = fetch_etsy_rows(keyword)
                store_etsy(search.id, etsy_rows)
                results["etsy"] = etsy_rows
            except Exception as exc:
                st.error(f"Etsy/Firecrawl error: {exc}")

    if toggles.get("instagram"):
        with st.spinner("Fetching Instagram posts..."):
            try:
                ig_rows = fetch_instagram_rows(keyword)
                store_instagram(search.id, ig_rows)
                results["instagram"] = ig_rows
            except Exception as exc:
                st.error(f"Instagram error: {exc}")

    with get_session() as session:
        search.status = "completed"
        session.add(search)
        session.commit()

    return results


def main():
    st.title("Niche Research Studio")
    st.caption("Compare YouTube, Etsy, Instagram, and web signals for any niche.")
    key_banner()

    with st.form("search"):
        keyword = st.text_input("Keyword", placeholder="3d printed planter")
        c1, c2, c3, c4 = st.columns(4)
        use_youtube = c1.checkbox("YouTube", value=True)
        use_etsy = c2.checkbox("Etsy", value=True)
        use_instagram = c3.checkbox("Instagram", value=False)
        use_web = c4.checkbox("Web", value=True)
        submitted = st.form_submit_button("Run Research")

    tabs = st.tabs(
        [
            "Search",
            "YouTube Explorer",
            "Etsy Explorer",
            "Instagram Explorer",
            "Keyword Insights",
            "Search History",
        ]
    )

    if submitted and keyword:
        if len(keyword.strip()) < 3:
            st.error("Please enter a keyword with at least 3 characters.")
        else:
            toggles = {
                "youtube": use_youtube and bool(settings.youtube_api_key),
                "etsy": use_etsy and bool(settings.firecrawl_api_key),
                "instagram": use_instagram and bool(settings.instagram_token and settings.instagram_user_id),
            }
            st.session_state["last_keyword"] = keyword.strip()
            st.session_state["platforms"] = toggles
            st.session_state["results"] = run_search(keyword.strip(), toggles)

    results = st.session_state.get("results", {"youtube": [], "etsy": [], "instagram": []})
    keyword = st.session_state.get("last_keyword")
    platforms = st.session_state.get(
        "platforms",
        {"youtube": True, "etsy": True, "instagram": False},
    )

    with tabs[0]:
        if not keyword:
            st.info("Enter a keyword and click Run Research to begin.")
        else:
            summary = {
                "YouTube videos": len(results["youtube"]) if platforms.get("youtube") else 0,
                "Etsy listings": len(results["etsy"]) if platforms.get("etsy") else 0,
                "IG posts": len(results["instagram"]) if platforms.get("instagram") else 0,
            }
            stat_cards(summary)

    with tabs[1]:
        if keyword and platforms.get("youtube"):
            render_table("YouTube videos", results["youtube"])
        else:
            st.info("Enable YouTube and run a search.")

    with tabs[2]:
        if keyword and platforms.get("etsy"):
            render_table("Etsy listings", results["etsy"])
            price_histogram(results["etsy"])
        else:
            st.info("Enable Etsy and run a search.")

    with tabs[3]:
        if keyword and platforms.get("instagram"):
            render_table("Instagram posts", results["instagram"])
        else:
            st.info("Enable Instagram and run a search.")

    with tabs[4]:
        if keyword:
            platform_texts = {
                "youtube": [r.get("Title", "") for r in results["youtube"]],
                "etsy": [r.get("Title", "") for r in results["etsy"]],
                "instagram": [r.get("Caption", "") for r in results["instagram"]],
            }
            df = merge_platform_counts(platform_texts)
            st.subheader("Cross-platform keywords")
            st.dataframe(df)
            keyword_bar(df)
        else:
            st.info("Run a search to see keyword insights.")

    with tabs[5]:
        recent = list_recent_searches(limit=15)
        if not recent:
            st.info("No searches yet.")
        else:
            for search in recent:
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.write(f"{search.query}")
                col2.caption(f"{search.created_at.isoformat()}  |  {search.platforms}")
                if col3.button("Load", key=f"load_{search.id}"):
                    st.session_state["last_keyword"] = search.query
                    st.session_state["platforms"] = {p: True for p in search.platforms.split(",")}
                    st.session_state["results"] = load_results(search.id)
                    st.experimental_rerun()


if __name__ == "__main__":
    main()
