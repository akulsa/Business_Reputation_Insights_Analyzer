import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import json

from config import SERPAPI_API_KEY
from data_fetcher import fetch_google_maps_reviews
from preprocess import preprocess_reviews
from analysis_pipeline import (
    add_sentiment,
    extract_themes,
    summarize_reviews,
    generate_recommendations,
    compute_basic_stats,
)

# ---------------------------------------------------------
# Page Setup
# ---------------------------------------------------------
st.set_page_config(page_title="Business Reputation & Insights Analyzer", layout="wide")

st.title("📊 Business Reputation & Insights Analyzer")
st.markdown("""
Analyze reviews of any business — or compare two businesses head-to-head.

Features:
- Sentiment breakdown  
- Themes extraction  
- AI summary  
- Recommendations  
- Competitor comparison  
- Rating & sentiment graphs  
""")


# ---------------------------------------------------------
# Session Initialization
# ---------------------------------------------------------
SESSION_KEYS = [
    "df_raw", "df_analyzed",
    "themes", "summary", "recs",
    "csv_uploaded_once",

    # competitor mode
    "df_A_raw", "df_B_raw",
    "A_processed", "B_processed",
    "A_themes", "B_themes",
    "A_summary", "B_summary",
    "A_recs", "B_recs",
    "compared"
]

for k in SESSION_KEYS:
    if k not in st.session_state:
        st.session_state[k] = None


def reset_single():
    for key in ["df_raw", "df_analyzed", "themes", "summary", "recs"]:
        st.session_state[key] = None


def reset_competitor():
    for key in ["df_A_raw", "df_B_raw", "A_processed", "B_processed",
                "A_themes", "B_themes", "A_summary", "B_summary",
                "A_recs", "B_recs", "compared"]:
        st.session_state[key] = None


# ---------------------------------------------------------
# SIDEBAR – Mode Selector
# ---------------------------------------------------------
st.sidebar.header("Choose Mode")

mode = st.sidebar.radio(
    "Select operation",
    ["Single Business Analysis", "Upload CSV", "Compare Two Businesses"]
)


# =========================================================
# MODE 1 — SINGLE BUSINESS ANALYSIS (existing)
# =========================================================
if mode == "Single Business Analysis":

    st.sidebar.subheader("Google Maps (SerpAPI)")

    place_id = st.sidebar.text_input("Place ID")
    serpapi_key = st.sidebar.text_input(
        "SerpAPI API Key (optional)",
        value=SERPAPI_API_KEY,
        type="password"
    )

    if st.sidebar.button("Fetch Reviews"):
        if not place_id:
            st.error("Please enter a place_id.")
        else:
            with st.spinner("Fetching reviews..."):
                try:
                    df = fetch_google_maps_reviews(place_id, serpapi_key or None)

                    if df.empty:
                        st.warning("No reviews found.")
                    else:
                        reset_single()
                        st.session_state["df_raw"] = df
                        st.session_state["csv_uploaded_once"] = None
                        st.success(f"Fetched {len(df)} reviews.")

                except Exception as e:
                    st.error(f"Error: {e}")

    df = st.session_state["df_raw"]

    if df is not None:
        st.subheader("📄 Raw Reviews")
        st.dataframe(df.head(20), use_container_width=True)

        # ================ STEP 1 ================
        step1 = st.expander("🔧 Step 1: Preprocess & Sentiment", expanded=True)
        with step1:
            if st.button("Run Analysis"):
                start = time.time()
                with st.spinner("Processing..."):
                    try:
                        df_proc = preprocess_reviews(df)
                        df_proc = add_sentiment(df_proc)
                        st.session_state["df_analyzed"] = df_proc
                        st.success("Analysis completed.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                st.write(f"⏱ {time.time() - start:.2f}s")

            df_analyzed = st.session_state["df_analyzed"]

            if df_analyzed is not None:
                stats = compute_basic_stats(df_analyzed)

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Reviews", stats["total_reviews"])
                col2.metric("Average Rating", f"{stats['avg_rating']:.2f}")
                col3.metric("Positive Reviews", stats["sentiment_counts"].get("positive", 0))

                # Sentiment distribution
                fig, ax = plt.subplots()
                pd.Series(stats["sentiment_counts"]).plot(kind="bar", ax=ax)
                ax.set_title("Sentiment Distribution")
                st.pyplot(fig)

                # Sentiment confidence
                fig2, ax2 = plt.subplots()
                df_analyzed["sentiment_score"].plot(kind="hist", bins=20, ax=ax2)
                ax2.set_title("Sentiment Confidence")
                st.pyplot(fig2)

                # Rating distribution
                if "rating" in df_analyzed.columns:
                    fig3, ax3 = plt.subplots()
                    df_analyzed["rating"].plot(kind="hist", bins=20, ax=ax3)
                    ax3.set_title("Rating Distribution")
                    st.pyplot(fig3)

        # ================ STEP 2 ================
        step2 = st.expander("💡 Step 2: Insights & Recommendations", expanded=True)
        with step2:
            if df_analyzed is None:
                st.warning("Complete Step 1 first.")
            else:
                if st.button("Generate Insights"):
                    start = time.time()
                    with st.spinner("Generating insights..."):
                        try:
                            themes = extract_themes(df_analyzed)
                            summary = summarize_reviews(df_analyzed)
                            recs = generate_recommendations(df_analyzed, themes)

                            st.session_state["themes"] = themes
                            st.session_state["summary"] = summary
                            st.session_state["recs"] = recs

                            st.success("Insights ready.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    st.write(f"⏱ {time.time() - start:.2f}s")

                themes = st.session_state["themes"]
                summary = st.session_state["summary"]
                recs = st.session_state["recs"]

                if themes:
                    st.subheader("🔍 Themes")
                    colA, colB = st.columns(2)
                    colA.write("Positive")
                    for t in themes.get("positive", []): colA.write("- " + t)
                    colB.write("Negative")
                    for t in themes.get("negative", []): colB.write("- " + t)

                if summary:
                    st.subheader("📝 Summary")
                    st.write(summary)

                if recs:
                    st.subheader("🧭 Recommendations")
                    st.write(recs)

                    from analysis_pipeline import _call_llm
                    prompt = f"""
Rate these recommendations for actionability (1–10).
Return JSON: {{ "score": number, "reason": "..." }}
{recs}
"""

                    try:
                        eva = json.loads(_call_llm(prompt))
                    except:
                        eva = {"score": "N/A", "reason": "Failed"}

                    st.metric("Actionability Score", eva["score"])
                    st.write(eva["reason"])

                    st.write("### Was this helpful?")
                    c1, c2 = st.columns(2)
                    if c1.button("👍 Yes"): st.success("Thanks!")
                    if c2.button("👎 No"): st.info("We'll improve.")



# =========================================================
# MODE 2 — CSV UPLOAD (unchanged)
# =========================================================
if mode == "Upload CSV":

    uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])

    if uploaded is not None and st.session_state["csv_uploaded_once"] is None:
        try:
            df_uploaded = pd.read_csv(
                uploaded,
                encoding="utf-8",
                engine="c",
                on_bad_lines="skip"
            )
            if "text" not in df_uploaded.columns:
                st.error("CSV must have a 'text' column.")
            else:
                reset_single()
                st.session_state["df_raw"] = df_uploaded
                st.session_state["csv_uploaded_once"] = True
                st.success(f"Loaded {len(df_uploaded)} rows.")
        except Exception as e:
            st.error(f"CSV error: {e}")

    df = st.session_state["df_raw"]

    if df is not None:
        st.subheader("📄 Uploaded CSV")
        st.dataframe(df.head(), use_container_width=True)
        st.info("Processing works same as Single Business Mode.")



# =========================================================
# MODE 3 — COMPARE TWO BUSINESSES (NEW)
# =========================================================
if mode == "Compare Two Businesses":

    st.sidebar.subheader("Business A")
    place_A = st.sidebar.text_input("Place ID (Business A)")

    st.sidebar.subheader("Business B")
    place_B = st.sidebar.text_input("Place ID (Business B)")

    serpapi_key = st.sidebar.text_input(
        "SerpAPI API Key (optional)",
        value=SERPAPI_API_KEY,
        type="password"
    )

    if st.sidebar.button("Fetch Both"):
        if not place_A or not place_B:
            st.error("Enter both Place IDs.")
        else:
            reset_competitor()
            with st.spinner("Fetching Business A..."):
                st.session_state["df_A_raw"] = fetch_google_maps_reviews(place_A, serpapi_key or None)

            with st.spinner("Fetching Business B..."):
                st.session_state["df_B_raw"] = fetch_google_maps_reviews(place_B, serpapi_key or None)

            st.success("Fetched both businesses!")

    dfA = st.session_state["df_A_raw"]
    dfB = st.session_state["df_B_raw"]

    # STOP if missing
    if dfA is None or dfB is None:
        st.info("Enter both IDs and fetch.")
        st.stop()

    # Display raw
    st.subheader("📄 Business A – Raw Reviews")
    st.dataframe(dfA.head(10), use_container_width=True)

    st.subheader("📄 Business B – Raw Reviews")
    st.dataframe(dfB.head(10), use_container_width=True)

    # -----------------------------
    # Step 1 — process both
    # -----------------------------
    if st.button("Run Step 1 for Both"):
        with st.spinner("Processing both businesses..."):
            try:
                A = preprocess_reviews(dfA)
                A = add_sentiment(A)

                B = preprocess_reviews(dfB)
                B = add_sentiment(B)

                st.session_state["A_processed"] = A
                st.session_state["B_processed"] = B

                st.success("Sentiment completed for both.")
            except Exception as e:
                st.error(f"Error: {e}")

    A = st.session_state["A_processed"]
    B = st.session_state["B_processed"]

    if A is not None and B is not None:
        st.subheader("📊 Sentiment Comparison")

        col1, col2 = st.columns(2)

        statsA = compute_basic_stats(A)
        statsB = compute_basic_stats(B)

        with col1:
            st.markdown("### Business A")
            st.metric("Reviews", statsA["total_reviews"])
            st.metric("Avg Rating", f"{statsA['avg_rating']:.2f}")

            figA, axA = plt.subplots()
            pd.Series(statsA["sentiment_counts"]).plot(kind="bar", ax=axA)
            axA.set_title("Sentiment")
            st.pyplot(figA)

        with col2:
            st.markdown("### Business B")
            st.metric("Reviews", statsB["total_reviews"])
            st.metric("Avg Rating", f"{statsB['avg_rating']:.2f}")

            figB, axB = plt.subplots()
            pd.Series(statsB["sentiment_counts"]).plot(kind="bar", ax=axB)
            axB.set_title("Sentiment")
            st.pyplot(figB)

    # -----------------------------
    # Step 2 — insights both
    # -----------------------------
    if A is not None and B is not None:
        if st.button("Generate Combined Insights"):
            with st.spinner("Generating insights for both businesses..."):
                try:
                    st.session_state["A_themes"] = extract_themes(A)
                    st.session_state["B_themes"] = extract_themes(B)

                    st.session_state["A_summary"] = summarize_reviews(A)
                    st.session_state["B_summary"] = summarize_reviews(B)

                    st.session_state["A_recs"] = generate_recommendations(A, st.session_state["A_themes"])
                    st.session_state["B_recs"] = generate_recommendations(B, st.session_state["B_themes"])

                    st.session_state["compared"] = True

                    st.success("Comparison Insights Ready!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state["compared"]:
        st.subheader("🔍 Themes Comparison")

        A_t = st.session_state["A_themes"]
        B_t = st.session_state["B_themes"]

        colA, colB = st.columns(2)
        colA.write("### Business A – Themes")
        colA.write("- Positive:")
        for t in A_t.get("positive", []): colA.write("• " + t)
        colA.write("- Negative:")
        for t in A_t.get("negative", []): colA.write("• " + t)

        colB.write("### Business B – Themes")
        colB.write("- Positive:")
        for t in B_t.get("positive", []): colB.write("• " + t)
        colB.write("- Negative:")
        for t in B_t.get("negative", []): colB.write("• " + t)

        st.subheader("📝 Summaries")
        st.write("### Business A Summary")
        st.write(st.session_state["A_summary"])

        st.write("### Business B Summary")
        st.write(st.session_state["B_summary"])

        st.subheader("🧭 Recommendations Comparison")
        st.write("### Business A Recommendations")
        st.write(st.session_state["A_recs"])

        st.write("### Business B Recommendations")
        st.write(st.session_state["B_recs"])

        # Gemini competitor insight
        from analysis_pipeline import _call_llm

        compare_prompt = f"""
Compare these two businesses based on:
- sentiment
- themes
- ratings
- strengths
- weaknesses
- improvement opportunities

Business A Summary:
{st.session_state['A_summary']}

Business B Summary:
{st.session_state['B_summary']}

Return a clear comparison and say **which business performs better overall and why**.
"""

        st.subheader("🏆 Gemini Competitor Insight")
        try:
            insight = _call_llm(compare_prompt)
            st.write(insight)
        except:
            st.error("Failed to generate competitor insight.")



            

