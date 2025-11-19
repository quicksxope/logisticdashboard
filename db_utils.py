import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def run_query(query, params=None, fetch=True):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params or [])
    result = None
    if fetch:
        result = cur.fetchall()
    else:
        conn.commit()
    cur.close()
    conn.close()
    return result
