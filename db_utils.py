import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ==========================================================
# 1) KONEKSI DATABASE
# ==========================================================
def get_connection():
    """Create a PostgreSQL connection using DATABASE_URL."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn


# ==========================================================
# 2) RUN QUERY (SELECT)
# ==========================================================
def run_query(query, params=None):
    """Run SELECT and return list of dict rows."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params)
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
    except Exception as e:
        raise e


# ==========================================================
# 3) RUN EXEC (INSERT / UPDATE / DELETE)
# ==========================================================
def run_exec(query, params=None):
    """Execute INSERT / UPDATE / DELETE."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        raise e
