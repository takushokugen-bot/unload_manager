import streamlit as st
from datetime import datetime
from modules.master_loader import (
    load_master,
    get_prefectures,
    get_cities,
    get_stores,
    get_store_info
)
from modules.supabase_client import insert_log, fetch_logs

# -----------------------------
# ページタイトル
# -----------------------------
st.title("荷卸し管理アプリ（Excelマスタ版）")

# -----------------------------
# Excel マスタ読み込み
# -----------------------------
try:
    df_master = load_master()
except Exception as e:
    st.error(f"マスタの読み込みに失敗しました: {e}")
    st.stop()

# -----------------------------
# ドライバー入力UI
# -----------------------------
st.header("ドライバー入力")

# 県
pref = st.selectbox("県を選択", [""] + get_prefectures(df_master))

# 市区町村
if pref:
    city = st.selectbox("市区町村を選択", [""] + get_cities(df_master, pref))
else:
    city = ""

# 店舗名
if city:
    store = st.selectbox("店舗名を選択", [""] + get_stores(df_master, pref, city))
else:
    store = ""

# 店舗情報表示
if store:
    info = get_store_info(df_master, pref, city, store)
    st.subheader("店舗情報")
    st.write(f"住所：{info['住所']}")
    st.write(f"荷卸し開始時刻（制約）：{info['荷卸し開始時刻']}")
    st.write(f"荷卸し終了時刻（制約）：{info['荷卸し終了時刻']}")
    st.write(f"制約メモ：{info['制約メモ']}")

    # -----------------------------
    # 作業時間入力
    # -----------------------------
    st.subheader("作業時間入力")

    arrival = st.time_input("到着時刻")
    start = st.time_input("荷卸し開始時刻")
    finish = st.time_input("荷卸し終了時刻")

    # -----------------------------
    # 待機時間ロジック
    # -----------------------------
    def calc_wait(arrival_t, start_t, limit_start_t):
        arrival_dt = datetime.combine(datetime.today(), arrival_t)
        start_dt = datetime.combine(datetime.today(), start_t)
        limit_dt = datetime.combine(datetime.today(), limit_start_t)

        effective_base = max(arrival_dt, limit_dt)
        wait = (start_dt - effective_base).total_seconds() / 60
        return max(0, int(wait))

    # 制約開始時刻を time 型に変換
    limit_start = info["荷卸し開始時刻"]
    if isinstance(limit_start, str):
        limit_start = datetime.strptime(limit_start, "%H:%M").time()

    wait_minutes = calc_wait(arrival, start, limit_start)

    st.write(f"**待機時間（制約考慮）：{wait_minutes} 分**")

    # -----------------------------
    # Supabase 保存処理
    # -----------------------------
    if st.button("記録する"):
        log_data = {
            "date": datetime.today().date().isoformat(),
            "prefecture": pref,
            "city": city,
            "store": store,
            "arrival": arrival.strftime("%H:%M"),
            "start": start.strftime("%H:%M"),
            "finish": finish.strftime("%H:%M"),
            "wait_minutes": wait_minutes,
        }

        ok, res = insert_log(log_data)

        if ok:
            st.success("Supabase に保存しました！")
        else:
            st.error(f"保存に失敗しました: {res}")

# -----------------------------
# 保存済みログ一覧（常に表示）
# -----------------------------
st.header("保存済みログ一覧")

ok, logs = fetch_logs()

if ok:
    if logs:
        for row in logs:
            st.markdown("---")
            st.write(f"日付：{row['date']}")
            st.write(f"県：{row['prefecture']}")
            st.write(f"市区町村：{row['city']}")
            st.write(f"店舗：{row['store']}")
            st.write(f"到着：{row['arrival']}")
            st.write(f"開始：{row['start']}")
            st.write(f"終了：{row['finish']}")
            st.write(f"待機時間：{row['wait_minutes']} 分")
    else:
        st.info("まだログがありません。")
else:
    st.error(f"取得に失敗しました: {logs}")
