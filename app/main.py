import streamlit as st

from app.analysis.keywords import merge_platform_counts, normalize_text
from app.config import get_settings
from app.storage.db import init_db
from app.ui.components import keyword_bar, price_histogram, render_table, stat_cards


st.set_page_config(page_title="Niche Research", layout="wide")

settings = get_settings()
init_db()


def _placeholder_data(keyword: str):
    # Placeholder data so the UI renders before APIs are wired.
    youtube_rows = [
        {
            "Title": f"{keyword} ideas",
            "Channel": "Maker Hub",
            "Views": 125000,
            "Published": "2024-02-10",
            "Tags": ["3d print", "planter", "diy"],
            "Link": "https://youtube.com/watch?v=demo1",
        }
    ]
    etsy_rows = [
        {
            "Title": f"{keyword} planter",
            "Price": 24.99,
            "Rating": 4.8,
            "#Reviews": 320,
            "Tags": ["planter", "succulent", "modern"],
            "URL": "https://etsy.com/listing/demo",
        }
    ]
    ig_rows = [
        {
            "Caption": f"Check out this {keyword} design",
            "Likes": 2100,
            "Comments": 120,
            "Hashtags": ["#3dprinted", "#planter"],
            "Link": "https://instagram.com/p/demo",
        }
    ]
    web_rows = [
        {"title": f"Top 10 {keyword}", "url": "https://blog.example.com/demo", "snippet": "roundup post"}
    ]
    return youtube_rows, etsy_rows, ig_rows, web_rows


def main():
    st.title("Niche Research Studio")
    st.caption("Compare YouTube, Etsy, Instagram, and web signals for any niche.")

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
        st.session_state["last_keyword"] = keyword
        st.session_state["platforms"] = {
            "youtube": use_youtube,
            "etsy": use_etsy,
            "instagram": use_instagram,
            "web": use_web,
        }

    keyword = st.session_state.get("last_keyword")
    platforms = st.session_state.get(
        "platforms",
        {"youtube": True, "etsy": True, "instagram": False, "web": True},
    )

    with tabs[0]:
        if not keyword:
            st.info("Enter a keyword and click Run Research to begin.")
        else:
            yt_rows, etsy_rows, ig_rows, web_rows = _placeholder_data(keyword)
            summary = {
                "YouTube videos": len(yt_rows) if platforms.get("youtube") else 0,
                "Etsy listings": len(etsy_rows) if platforms.get("etsy") else 0,
                "IG posts": len(ig_rows) if platforms.get("instagram") else 0,
                "Web results": len(web_rows) if platforms.get("web") else 0,
            }
            stat_cards(summary)

    with tabs[1]:
        if keyword and platforms.get("youtube"):
            yt_rows, _, _, _ = _placeholder_data(keyword)
            render_table("YouTube videos", yt_rows)
        else:
            st.info("Enable YouTube and run a search.")

    with tabs[2]:
        if keyword and platforms.get("etsy"):
            _, etsy_rows, _, _ = _placeholder_data(keyword)
            render_table("Etsy listings", etsy_rows)
            price_histogram(etsy_rows)
        else:
            st.info("Enable Etsy and run a search.")

    with tabs[3]:
        if keyword and platforms.get("instagram"):
            _, _, ig_rows, _ = _placeholder_data(keyword)
            render_table("Instagram posts", ig_rows)
        else:
            st.info("Enable Instagram and run a search.")

    with tabs[4]:
        if keyword:
            yt_rows, etsy_rows, ig_rows, web_rows = _placeholder_data(keyword)
            platform_texts = {
                "youtube": [r.get("Title", "") for r in yt_rows],
                "etsy": [r.get("Title", "") for r in etsy_rows],
                "instagram": [r.get("Caption", "") for r in ig_rows],
                "web": [r.get("title", "") for r in web_rows],
            }
            df = merge_platform_counts(platform_texts)
            st.subheader("Cross-platform keywords")
            st.dataframe(df)
            keyword_bar(df)
        else:
            st.info("Run a search to see keyword insights.")

    with tabs[5]:
        st.info("Search history will appear here once caching is wired.")


if __name__ == "__main__":
    main()
