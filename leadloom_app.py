# leadloom_app.py

import streamlit as st
import pandas as pd
import time
import os
import io
from datetime import datetime
import base64

# Page config
st.set_page_config(
    page_title="LeadLoom – AI-Powered B2B Lead Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    .stButton > button {
        background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border: none;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(78, 205, 196, 0.3);
    }
    .api-status {
        padding: 1rem;
        border-radius: 8px;
        font-weight: 500;
        text-align: center;
        margin: 1rem 0;
    }
    .api-success { background: #d1fae5; color: #065f46; border: 1px solid #10b981; }
    .api-error { background: #fee2e2; color: #991b1b; border: 1px solid #ef4444; }
</style>
""", unsafe_allow_html=True)

# Load API key
def get_openai_client():
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None, "API key not configured"

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        client.models.list()
        return client, "Connected successfully"
    except ImportError:
        return None, "Install OpenAI SDK: pip install openai"
    except Exception as e:
        return None, f"Connection failed: {str(e)}"

# Score class helper
def get_score_class(score):
    try:
        score = int(''.join(filter(str.isdigit, str(score)))[:3])
        if score >= 80:
            return "✅ High"
        elif score >= 60:
            return "⚠️ Medium"
        else:
            return "❌ Low"
    except:
        return "N/A"

# AI generation function
def generate_lead_analysis(client, company, industry, url, offer, icp_keywords, size, tone, length, cta):
    if not client:
        return "OpenAI API not available"

    prompt = f"""
    You are a B2B sales strategist. Analyze the lead and write copy.

    CLIENT:
    - Product: {offer}
    - ICP: {icp_keywords}
    - Size: {size}

    LEAD:
    - Company: {company}
    - Industry: {industry}
    - URL: {url}

    Write:
    1. Score (0-100)
    2. Reason for score
    3. 3 common pain points
    4. Two email drafts in {tone} tone and {length} length
    {'Include CTA.' if cta else 'No strong CTA.'}

    Format:
    SCORE:
    REASONING:
    PAIN POINTS:
    EMAIL 1:
    EMAIL 2:
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Parse output
def parse_output(text):
    result = {"score": "N/A", "reasoning": "", "pain_points": "", "email1": "", "email2": ""}
    lines = text.split("\n")
    section = None
    for line in lines:
        if line.startswith("SCORE:"):
            result["score"] = line[6:].strip()
        elif line.startswith("REASONING:"):
            section = "reasoning"
        elif line.startswith("PAIN POINTS:"):
            section = "pain_points"
        elif line.startswith("EMAIL 1:"):
            section = "email1"
        elif line.startswith("EMAIL 2:"):
            section = "email2"
        elif section:
            result[section] += line + "\n"
    return result

# OpenAI setup
client, api_status = get_openai_client()

st.title("🚀 LeadLoom")
st.subheader("AI-Powered B2B Lead Intelligence & Outreach")

if client:
    st.markdown(f'<div class="api-status api-success">✅ {api_status}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="api-status api-error">❌ {api_status}<br>Add OPENAI_API_KEY to .streamlit/secrets.toml</div>', unsafe_allow_html=True)

# Sidebar setup
with st.sidebar:
    st.header("🎯 ICP Configuration")
    offer = st.text_input("Your Product/Service", "CRM for SMBs")
    icp_keywords = st.text_input("ICP Keywords", "SaaS, startup, HubSpot")
    size = st.selectbox("Target Company Size", ["Startup", "Small", "Mid", "Enterprise", "Any"])
    st.header("✉️ Email Settings")
    tone = st.selectbox("Email Tone", ["Professional", "Friendly", "Direct"])
    length = st.selectbox("Email Length", ["Short", "Medium", "Long"])
    cta = st.checkbox("Include CTA", True)

# Upload file
st.markdown("### 📤 Upload Your Leads (CSV)")
file = st.file_uploader("CSV must include Company Name, Industry, Website or LinkedIn URL", type=["csv"])

if file:
    df = pd.read_csv(file)
    if "Company Name" not in df.columns or "Industry" not in df.columns:
        st.error("Required columns missing: Company Name, Industry")
    else:
        st.success(f"Loaded {len(df)} leads")
        st.dataframe(df.head())

        # Analyze top 3
        st.markdown("### 🔍 AI Lead Analysis (Top 3)")
        for idx, row in df.head(3).iterrows():
            with st.spinner(f"Analyzing {row['Company Name']}..."):
                analysis = generate_lead_analysis(
                    client,
                    row["Company Name"],
                    row["Industry"],
                    row.get("Website", row.get("LinkedIn URL", "")),
                    offer, icp_keywords, size, tone, length, cta
                )
            result = parse_output(analysis)

            st.markdown(f"#### 🏢 {row['Company Name']} – Score: {result['score']} ({get_score_class(result['score'])})")
            st.write("**Reasoning:**", result["reasoning"])
            st.write("**Pain Points:**", result["pain_points"])
            st.write("**Email 1**")
            st.code(result["email1"])
            st.write("**Email 2**")
            st.code(result["email2"])
            time.sleep(1)
else:
    st.info("Upload a CSV file to begin.")
