import pandas as pd

def load_master(path="data/unload_master.xlsx"):
    """
    Excel マスタを読み込み、必要な列が揃っているかチェックして返す。
    """
    df = pd.read_excel(path)

    required_cols = ["県", "市区町村", "店舗名", "住所", "荷卸し開始時刻", "荷卸し終了時刻", "制約メモ"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"マスタに必要な列がありません: {col}")

    return df


def get_prefectures(df):
    """県の一覧を返す"""
    return sorted(df["県"].unique())


def get_cities(df, prefecture):
    """県を指定して市区町村一覧を返す"""
    return sorted(df[df["県"] == prefecture]["市区町村"].unique())


def get_stores(df, prefecture, city):
    """県・市区町村を指定して店舗一覧を返す"""
    return sorted(df[(df["県"] == prefecture) & (df["市区町村"] == city)]["店舗名"].unique())


def get_store_info(df, prefecture, city, store_name):
    """店舗名を指定して住所・制約を返す"""
    row = df[
        (df["県"] == prefecture) &
        (df["市区町村"] == city) &
        (df["店舗名"] == store_name)
    ].iloc[0]

    return {
        "住所": row["住所"],
        "荷卸し開始時刻": row["荷卸し開始時刻"],
        "荷卸し終了時刻": row["荷卸し終了時刻"],
        "制約メモ": row["制約メモ"]
    }
