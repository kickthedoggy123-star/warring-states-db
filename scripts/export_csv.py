import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

SOURCE_XLSX = BASE_DIR / "source" / "戰國史料_西元年分類表.xlsx"

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

events = pd.read_excel(SOURCE_XLSX, sheet_name="事件明細")
years = pd.read_excel(SOURCE_XLSX, sheet_name="年份總表")

events.to_csv(DATA_DIR / "events.csv", index=False, encoding="utf-8-sig")
years.to_csv(DATA_DIR / "years.csv", index=False, encoding="utf-8-sig")

print("完成！")
print("已產生 data/events.csv")
print("已產生 data/years.csv")