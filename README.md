# LeadLoom AI Agent (Zentara)

## Overview
LeadLoom is an AI-powered tool that lets you upload a CSV of business leads and instantly:
- Score them based on ICP fit
- Explain why each lead is a good/bad match
- Generate 2 cold email drafts per lead

## How to Use
1. Install requirements:
   ```
   pip install -r requirements.txt
   ```

2. Add your OpenAI API key in `.streamlit/secrets.toml`:
   ```
   [default]
   OPENAI_API_KEY = "your-key-here"
   ```

3. Run the app:
   ```
   streamlit run leadloom_app.py
   ```

4. Upload a CSV and get instant lead analysis and emails.

## Built With
- GPT-4o
- Streamlit
- Pandas
