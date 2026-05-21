from supabase import create_client
import streamlit as st

# secrets.toml に設定済みのキーを読み込む
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_log(data: dict):
    """ドライバー入力ログを Supabase に保存"""
    try:
        response = supabase.table("logs").insert(data).execute()
        return True, response
    except Exception as e:
        return False, str(e)

def fetch_logs():
    """保存済みログを取得（新しい順）"""
    try:
        data = supabase.table("logs").select("*").order("date", desc=True).execute()
        return True, data.data
    except Exception as e:
        return False, str(e)
