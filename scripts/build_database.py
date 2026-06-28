from pathlib import Path
import sqlite3
import pandas as pd


# =========================
# 1. 路徑設定
# =========================

BASE_DIR = Path(__file__).resolve().parents[1]

SOURCE_XLSX = BASE_DIR / "source" / "戰國史料_西元年分類表.xlsx"

DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"

EVENTS_CSV = DATA_DIR / "events.csv"
YEARS_CSV = DATA_DIR / "years.csv"
DB_PATH = DATABASE_DIR / "warring_states.db"


# =========================
# 2. 工具函式
# =========================

def ensure_dirs():
    """
    確保 data/ 和 database/ 資料夾存在。
    """
    DATA_DIR.mkdir(exist_ok=True)
    DATABASE_DIR.mkdir(exist_ok=True)


def read_excel_safely(path: Path):
    """
    讀取 Excel，並檢查是否存在。
    """
    if not path.exists():
        raise FileNotFoundError(
            f"找不到檔案：{path}\n"
            "請確認 Excel 已放在 source/ 資料夾內。"
        )

    return pd.ExcelFile(path)


def find_sheet(excel_file, possible_names):
    """
    從 Excel 中尋找可能的工作表名稱。
    例如：事件明細、事件總表、年份總表。
    """
    for name in possible_names:
        if name in excel_file.sheet_names:
            return name

    raise ValueError(
        "找不到指定工作表。\n"
        f"目前 Excel 內有這些工作表：{excel_file.sheet_names}\n"
        f"程式期待其中之一：{possible_names}"
    )


def clean_text(value):
    """
    清理文字欄位。
    """
    if pd.isna(value):
        return ""

    text = str(value).strip()
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text


def normalize_events(df):
    """
    將事件表整理成固定欄位。
    你的 Excel 若欄位名稱略有不同，也盡量自動對應。
    """

    column_map = {}

    for col in df.columns:
        c = str(col).strip()

        if c in ["西元前年", "年份", "year_label"]:
            column_map[col] = "year_label"

        elif c in ["西元年數字", "年份數字", "bce_year"]:
            column_map[col] = "bce_year"

        elif c in ["周王紀年", "周紀年", "zhou_reign"]:
            column_map[col] = "zhou_reign"

        elif c in ["事件序號", "序號", "event_order"]:
            column_map[col] = "event_order"

        elif c in ["事件內容", "事件", "原文", "event_text"]:
            column_map[col] = "event_text"

        elif c in ["人物", "people"]:
            column_map[col] = "people"

        elif c in ["國家", "state", "states"]:
            column_map[col] = "states"

        elif c in ["事件詞", "關鍵詞", "keywords"]:
            column_map[col] = "keywords"

        elif c in ["頁次", "頁碼", "page"]:
            column_map[col] = "source_page"

        elif c in ["備註", "note"]:
            column_map[col] = "note"

    df = df.rename(columns=column_map)

    required = ["year_label", "event_text"]

    for col in required:
        if col not in df.columns:
            raise ValueError(
                f"事件表缺少必要欄位：{col}\n"
                f"目前欄位為：{list(df.columns)}"
            )

    # 如果沒有 bce_year，就從「前468」這種文字中抽數字
    if "bce_year" not in df.columns:
        df["bce_year"] = (
            df["year_label"]
            .astype(str)
            .str.extract(r"(\d+)")
            .astype(float)
        )

    # 如果沒有事件序號，自動生成
    if "event_order" not in df.columns:
        df["event_order"] = df.groupby("year_label").cumcount() + 1

    for optional_col in [
        "zhou_reign", "people", "states", "keywords", "source_page", "note"
    ]:
        if optional_col not in df.columns:
            df[optional_col] = ""

    df = df[
        [
            "bce_year",
            "year_label",
            "zhou_reign",
            "event_order",
            "states",
            "people",
            "keywords",
            "event_text",
            "source_page",
            "note",
        ]
    ].copy()

    df["event_id"] = range(1, len(df) + 1)

    # 清理文字
    for col in [
        "year_label", "zhou_reign", "states", "people",
        "keywords", "event_text", "source_page", "note"
    ]:
        df[col] = df[col].apply(clean_text)

    df["bce_year"] = pd.to_numeric(df["bce_year"], errors="coerce").astype("Int64")
    df["event_order"] = pd.to_numeric(df["event_order"], errors="coerce").fillna(0).astype(int)

    # 排序：前468 → 前467 → 前466，所以 bce_year 要由大到小
    df = df.sort_values(
        by=["bce_year", "event_order"],
        ascending=[False, True]
    )

    df = df[
        [
            "event_id",
            "bce_year",
            "year_label",
            "zhou_reign",
            "event_order",
            "states",
            "people",
            "keywords",
            "event_text",
            "source_page",
            "note",
        ]
    ]

    return df


def build_years_table(events_df):
    """
    由事件表自動生成年份表。
    每一年一列。
    """
    years_df = (
        events_df
        .groupby(["bce_year", "year_label"], dropna=False)
        .agg(
            zhou_reign=("zhou_reign", "first"),
            event_count=("event_id", "count")
        )
        .reset_index()
    )

    years_df = years_df.sort_values(
        by="bce_year",
        ascending=False
    )

    years_df["year_id"] = range(1, len(years_df) + 1)

    years_df = years_df[
        [
            "year_id",
            "bce_year",
            "year_label",
            "zhou_reign",
            "event_count",
        ]
    ]

    return years_df


def save_csv(events_df, years_df):
    """
    輸出 CSV。
    utf-8-sig 可避免 Excel 開啟中文亂碼。
    """
    events_df.to_csv(EVENTS_CSV, index=False, encoding="utf-8-sig")
    years_df.to_csv(YEARS_CSV, index=False, encoding="utf-8-sig")


def save_sqlite(events_df, years_df):
    """
    輸出 SQLite 資料庫。
    """
    conn = sqlite3.connect(DB_PATH)

    events_df.to_sql("events", conn, if_exists="replace", index=False)
    years_df.to_sql("years", conn, if_exists="replace", index=False)

    # 建立索引，加速查詢
    conn.execute("CREATE INDEX IF NOT EXISTS idx_events_bce_year ON events(bce_year)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_events_people ON events(people)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_events_states ON events(states)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_events_keywords ON events(keywords)")

    conn.commit()
    conn.close()


def main():
    ensure_dirs()

    excel_file = read_excel_safely(SOURCE_XLSX)

    event_sheet = find_sheet(
        excel_file,
        ["事件明細", "事件總表", "Sheet1"]
    )

    events_raw = pd.read_excel(SOURCE_XLSX, sheet_name=event_sheet)

    events_df = normalize_events(events_raw)
    years_df = build_years_table(events_df)

    save_csv(events_df, years_df)
    save_sqlite(events_df, years_df)

    print("完成！")
    print(f"事件數量：{len(events_df)}")
    print(f"年份數量：{len(years_df)}")
    print(f"已輸出：{EVENTS_CSV}")
    print(f"已輸出：{YEARS_CSV}")
    print(f"已輸出：{DB_PATH}")


if __name__ == "__main__":
    main()