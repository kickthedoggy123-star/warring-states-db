import sqlite3
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

EVENTS_CSV = BASE_DIR / "data" / "events.csv"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DB_PATH = DATABASE_DIR / "warring_states.db"


COLUMN_MAP = {
    "西元前年": "year_label",
    "年份數字": "bce_year",
    "紀年標題": "reign_title",
    "同年序號": "event_order",
    "資料類型": "data_type",
    "國家": "states",
    "人物": "people",
    "事件詞": "keywords",
    "原文內容": "event_text",
}


def main():
    if not EVENTS_CSV.exists():
        raise FileNotFoundError(f"找不到檔案：{EVENTS_CSV}")

    if DB_PATH.exists():
        DB_PATH.unlink()

    events = pd.read_csv(EVENTS_CSV, encoding="utf-8-sig")

    events.columns = (
        events.columns
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    events = events.rename(columns=COLUMN_MAP)

    required_columns = [
        "year_label",
        "bce_year",
        "reign_title",
        "event_order",
        "data_type",
        "states",
        "people",
        "keywords",
        "event_text",
    ]

    missing = [col for col in required_columns if col not in events.columns]

    if missing:
        print("目前讀到的欄位：")
        print(events.columns.tolist())
        raise ValueError(f"缺少欄位：{missing}")

    events["bce_year"] = pd.to_numeric(events["bce_year"], errors="coerce")
    events["event_order"] = pd.to_numeric(events["event_order"], errors="coerce")

    events = events[required_columns].copy()

    events.insert(0, "event_id", range(1, len(events) + 1))

    conn = sqlite3.connect(DB_PATH)

    events.to_sql("events", conn, if_exists="replace", index=False)

    conn.execute("CREATE INDEX idx_events_bce_year ON events(bce_year)")
    conn.execute("CREATE INDEX idx_events_year_label ON events(year_label)")
    conn.execute("CREATE INDEX idx_events_states ON events(states)")
    conn.execute("CREATE INDEX idx_events_people ON events(people)")
    conn.execute("CREATE INDEX idx_events_keywords ON events(keywords)")

    conn.commit()
    conn.close()

    print("完成！")
    print(f"已建立資料庫：{DB_PATH}")
    print(f"共匯入 {len(events)} 筆事件資料")


if __name__ == "__main__":
    main()