import re
import pandas as pd
from transformers import pipeline
from sqlalchemy import create_engine, text
import streamlit as st

# 1. Load Hugging Face model
@st.cache_resource
def load_model():
    return pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-wikiSQL")

nl2sql = load_model()

# 2. Neon Postgres connection (replace with your actual Neon URL)
DATABASE_URL = "postgresql://<user>:<password>@<host>/<dbname>?sslmode=require"
engine = create_engine(DATABASE_URL)

# ----------------- Helpers -----------------
def natural_to_sql(question):
    prompt = "translate to SQL: " + question
    result = nl2sql(prompt, max_new_tokens=128, do_sample=False)
    return result[0]['generated_text']

def clean_sql(query: str) -> str:
    query = query.replace("table", "users")

    synonyms = {
        "User": "name",
        "Users": "users",
        "Signed": "signup_date",
        "Sign": "signup_date"
    }
    for wrong, right in synonyms.items():
        query = re.sub(rf"\b{wrong}\b", right, query, flags=re.IGNORECASE)

    # Expand "SELECT name" into full details
    query = re.sub(r"SELECT\s+name", "SELECT *", query, flags=re.IGNORECASE)

    # Handle "on/at/equals/is" → "="
    query = re.sub(r"\b(on|at|equals|is)\b", "=", query, flags=re.IGNORECASE)

    # Fix dates → 'YYYY-MM-DD'
    if re.search(r"\d{4}-\d{2}-\d{2}", query) and not "'" in query:
        query = re.sub(r"(\d{4}-\d{2}-\d{2})", r"'\1'", query)

    return query

def run_query(sql_query):
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        rows = result.fetchall()
        columns = result.keys()
        return pd.DataFrame(rows, columns=columns)

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="AI-Powered SQL Helper", page_icon="YB", layout="centered")

st.title(" AI-Powered SQL Helper")
st.markdown(" ### Built with **Neon (Postgres)** + **Hugging Face Transformers**")

question = st.text_input(
    "💬 Ask your question in natural language:",
    placeholder="Write your question e.g., Show me all the details of users"
)

if st.button("🚀 Run Query"):
    with st.spinner("Generating SQL and fetching results..."):
        raw_sql = natural_to_sql(question)
        st.subheader("🔹 Generated SQL (raw)")
        st.code(raw_sql, language="sql")

        fixed_sql = clean_sql(raw_sql)
        st.subheader("🔹 Cleaned SQL")
        st.code(fixed_sql, language="sql")

        try:
            df = run_query(fixed_sql)
            if not df.empty:
                st.subheader("📊 Query Results")
                st.dataframe(df, use_container_width=True)  # responsive
            else:
                st.warning("⚠️ No results found.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

st.markdown("---")
st.caption("Made with ❤️ **Yaaseen Basit** using Streamlit, Neon, and Hugging Face")
