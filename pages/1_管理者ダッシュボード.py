import streamlit as st
from modules.supabase_client import fetch_logs
import pandas as pd
from io import BytesIO

st.title("管理者ダッシュボード")

# -----------------------------
# データ取得
# -----------------------------
ok, logs = fetch_logs()

if not ok:
    st.error(f"取得に失敗しました: {logs}")
    st.stop()

df = pd.DataFrame(logs)

# -----------------------------
# フィルタ UI
# -----------------------------
st.subheader("フィルタ")

# 日付フィルタ
dates = sorted(df["date"].unique(), reverse=True)
selected_date = st.selectbox("日付を選択", ["すべて"] + dates)

# 店舗フィルタ
stores = sorted(df["store"].unique())
selected_store = st.selectbox("店舗を選択", ["すべて"] + stores)

# -----------------------------
# フィルタ適用
# -----------------------------
df_filtered = df.copy()

if selected_date != "すべて":
    df_filtered = df_filtered[df_filtered["date"] == selected_date]

if selected_store != "すべて":
    df_filtered = df_filtered[df_filtered["store"] == selected_store]

# -----------------------------
# 表示
# -----------------------------
st.subheader("ログ一覧")
st.dataframe(df_filtered)

# -----------------------------
# Excel ダウンロード（.xlsx）
# -----------------------------
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="logs")
    return output.getvalue()

excel_data = to_excel(df_filtered)

st.download_button(
    label="Excel ダウンロード（.xlsx）",
    data=excel_data,
    file_name="logs.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
# -----------------------------
# ① 待機時間ランキング（店舗別）
# -----------------------------
st.subheader("待機時間ランキング（店舗別）")

if not df_filtered.empty:
    ranking = (
        df_filtered.groupby("store")["wait_minutes"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    ranking.columns = ["店舗", "待機時間合計（分）"]
    st.dataframe(ranking)
else:
    st.info("データがありません。")


# -----------------------------
# ② 店舗別 平均待機時間グラフ
# -----------------------------
st.subheader("店舗別 平均待機時間グラフ")

if not df_filtered.empty:
    avg_wait = (
        df_filtered.groupby("store")["wait_minutes"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    avg_wait.columns = ["店舗", "平均待機時間（分）"]

    st.bar_chart(avg_wait, x="店舗", y="平均待機時間（分）")
else:
    st.info("データがありません。")


# -----------------------------
# ③ 月次レポート自動生成
# -----------------------------
st.subheader("月次レポート（自動集計）")

# 日付を datetime に変換
df["date"] = pd.to_datetime(df["date"])

# 月列を追加
df["month"] = df["date"].dt.to_period("M").astype(str)

monthly = (
    df.groupby("month")["wait_minutes"]
    .agg(["count", "sum", "mean"])
    .reset_index()
)

monthly.columns = ["月", "件数", "待機時間合計（分）", "平均待機時間（分）"]

st.dataframe(monthly)

# 月次レポート Excel ダウンロード
def to_excel_monthly(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="monthly_report")
    return output.getvalue()

monthly_excel = to_excel_monthly(monthly)

st.download_button(
    label="月次レポートを Excel でダウンロード",
    data=monthly_excel,
    file_name="monthly_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
# -----------------------------
# 店舗ごとの詳細レポート
# -----------------------------
st.subheader("店舗ごとの詳細レポート")

if not df.empty:
    # 店舗ごとに集計
    store_report = (
        df.groupby("store")["wait_minutes"]
        .agg(["count", "sum", "mean", "max", "min"])
        .reset_index()
    )

    store_report.columns = [
        "店舗",
        "件数",
        "待機時間合計（分）",
        "平均待機時間（分）",
        "最大待機時間（分）",
        "最小待機時間（分）"
    ]

    st.dataframe(store_report)

    # Excel ダウンロード
    def to_excel_store(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="store_report")
        return output.getvalue()

    store_excel = to_excel_store(store_report)

    st.download_button(
        label="店舗別レポートを Excel でダウンロード",
        data=store_excel,
        file_name="store_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("データがありません。")
