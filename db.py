from sqlalchemy import create_engine, text
import pandas as pd

# Neon Postgres connection
DATABASE_URL = "postgresql://<user>:<password>@<host>/<dbname>?sslmode=require"

engine = create_engine(DATABASE_URL)

def run_query(sql_query):
    """Fetch data using SQL"""
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        rows = result.fetchall()
        columns = result.keys()
        return pd.DataFrame(rows, columns=columns)

def execute_sql(sql_query, params=None):
    """Execute Insert, Update, Delete queries safely"""
    with engine.connect() as conn:
        conn.execute(text(sql_query), params or {})
        conn.commit()
