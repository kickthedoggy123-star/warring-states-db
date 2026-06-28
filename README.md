# 戰國史料資料庫 Warring States Chronology Database

本資料庫整理戰國時期編年史料，以西元前年份為主索引，將同一年發生的事件集中整理。

## 資料來源

目前資料來源：

- 《戰國史料編年輯證》
- OCR / Word / Excel 整理稿

## 資料結構

```text
warring-states-db/
├── source/
│   └── 戰國史料_西元年分類表.xlsx
├── scripts/
│   └── build_database.py
├── data/
│   ├── events.csv
│   └── years.csv
└── database/
    └── warring_states.db