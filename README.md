---
title: Business Reputation & Insights Analyzer
emoji: 📊
colorFrom: purple
colorTo: indigo
sdk: streamlit
sdk_version: "1.36.0"
app_file: app.py
pinned: false
---

# 📘 Business Reputation & Insights Analyzer
### AI-powered Google Maps Review Analysis & Two-Business Competitor Comparison

## 🚀 Live Demo

Try the live application here:

👉 **https://huggingface.co/spaces/shovidhyan/Business_Reputation_Insights_Analyzer**


This project analyzes customer reviews from **Google Maps** or **CSV datasets** using advanced AI techniques:

- Sentiment classification  
- Topic extraction  
- AI-generated summaries  
- Actionable recommendations  
- Competitor comparison  
- Visual insight dashboards  

Built using **Streamlit**, **Google Gemini**, **HuggingFace Transformers**, and **SerpAPI**.

---

## 🚀 Features

### ✔ Single Business Analysis
- Fetch reviews using **SerpAPI + Google Maps Place ID**
- Text preprocessing & sentiment scoring
- Sentiment distribution chart
- Sentiment confidence histogram
- Rating distribution
- Key positive & negative themes
- AI summary of customer experience
- AI-generated business improvement recommendations
- LLM-based actionability score

---

### ✔ CSV Review Analysis
Upload a CSV with at least a `text` column:



text, rating, author, date




Runs the entire analysis pipeline on your dataset.

---

### ✔ Two-Business Competitor Comparison (NEW)
Compare **Business A vs Business B**:

- Sentiment comparison  
- Rating comparison  
- Themes comparison  
- Side-by-side summaries  
- Recommendation comparison  
- **Gemini-powered competitive insight**  
  > "Which business performs better overall and why?"

Perfect for business benchmarking, marketing analysis, and consulting use-cases.

---

### ✔ Quality & Evaluation Metrics
- Processing time tracking  
- Sentiment confidence graph  
- LLM Actionability score  
- User feedback buttons  
- Organized expanders for clean UI  

---

## 🧱 Tech Stack

| Layer | Tools |
|-------|--------|
| Frontend UI | Streamlit |
| LLM | Google Gemini (models/gemini-2.5-flash) |
| Sentiment Model | HuggingFace Transformers |
| Data Source | SerpAPI (Google Maps Reviews) |
| Preprocessing | Pandas |
| Visualization | Matplotlib |
| Deployment | HuggingFace Spaces |

---

## 📂 Project Structure

```text
project/
│
├── 📄 app.py                 # Main Streamlit Application entry point
├── 🤖 analysis_pipeline.py   # Core LLM logic (Prompt engineering & API calls)
├── 🧹 preprocess.py          # Text cleaning, tokenization, and normalization
├── 🌐 data_fetcher.py        # Integration with SerpAPI to scrape Google Maps reviews
├── 🔐 config.py              # Environment variable management & API Key loading
├── 📦 requirements.txt       # List of all Python dependencies
└── 📘 README.md              # Project documentation

```

# ▶️ Usage Guide

## 👉 Mode 1: Single Business Analysis
1. Select **Single Business Analysis**
2. Enter a **Google Maps place_id**
3. Click **Fetch Reviews**
4. Run **Step 1** (Preprocessing & Sentiment)
5. Run **Step 2** (Insights & Recommendations)

### 📌 You will get:
- Sentiment graphs  
- Rating graphs  
- Key themes  
- AI-generated summary  
- AI-generated recommendations  
- Actionability score  

---

## 👉 Mode 2: Upload CSV
1. Select **Upload CSV**
2. Upload a dataset containing at least a `text` column
3. Run **Step 1** and **Step 2** normally

---

## 👉 Mode 3: Compare Two Businesses
1. Select **Compare Two Businesses**
2. Enter **Place ID A**
3. Enter **Place ID B**
4. Click **Fetch Both**
5. Run **Step 1 for Both**
6. Click **Generate Combined Insights**

### 📌 Outputs include:
- A/B sentiment comparison  
- A/B rating comparison  
- A/B themes comparison  
- A/B summary comparison  
- A/B recommendation comparison  
- LLM-powered competitor analysis  

---

# 🎯 Requirement Coverage

| Requirement | Status |
|------------|--------|
| Sentiment Classification | ✔ Implemented |
| Topic Extraction | ✔ Implemented |
| Summaries | ✔ Implemented |
| Recommendations | ✔ Implemented |
| Competitor Comparison | ✔ Fully Implemented |
| Evaluation Metrics | ✔ Processing time, sentiment confidence, actionability |
| Langflow-style chaining | ✔ Implemented via modular pipeline |



---

## 🔧 Setup Instructions


# 1️⃣ Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

# 2️⃣ Install project dependencies
```bash
pip install -r requirements.txt
```

# 3️⃣ Create environment variables file (.env)
```bash
echo "SERPAPI_API_KEY=your_serpapi_api_key" > .env
echo "GEMINI_API_KEY=your_gemini_key" >> .env
echo "GEMINI_MODEL=models/gemini-2.5-flash" >> .env
```
# 4️⃣ Run the Streamlit application
```bash
streamlit run app.py
```



