"""
白酒行业财务指标计算
基于财务分析中常用的三项指标，对三家公司 2015—2024 年年报进行横向对比：
    净利率   = 归母净利润 / 营业总收入
    营收增速 = (本期营收 - 上期营收) / 上期营收     （LAG 窗口函数）
    ROE      = 归母净利润 / 平均归母股东权益          （期初与期末均值）

输出：数据/指标汇总.csv
"""

import os
import sqlite3

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "数据", "finance.db")
OUT_PATH = os.path.join(BASE, "数据", "指标汇总.csv")

STOCKS = ["贵州茅台", "五粮液", "泸州老窖"]
START, END = "20150101", "20241231"

PROFIT_SQL = """
SELECT CAST(报告日 AS TEXT) AS 年份,
       ROUND(营业总收入 / 100000000.0, 2) AS 营收_亿元,
       ROUND(归属于母公司所有者的净利润 / 100000000.0, 2) AS 归母净利润_亿元,
       ROUND(归属于母公司所有者的净利润 * 100.0 / 营业总收入, 2) AS 净利率,
       ROUND((营业总收入 - LAG(营业总收入) OVER (ORDER BY 报告日)) * 100.0
             / LAG(营业总收入) OVER (ORDER BY 报告日), 2) AS 营收增速
FROM {table}
WHERE CAST(报告日 AS TEXT) LIKE '%1231'
ORDER BY 报告日
"""

ROE_SQL = """
WITH bs AS (
    SELECT CAST(报告日 AS TEXT) AS 年份,
           CAST(归属于母公司股东权益合计 AS REAL) AS 权益
    FROM {bs_table}
    WHERE CAST(报告日 AS TEXT) LIKE '%1231'
),
pl AS (
    SELECT CAST(报告日 AS TEXT) AS 年份,
           CAST(归属于母公司所有者的净利润 AS REAL) AS 净利润
    FROM {pl_table}
    WHERE CAST(报告日 AS TEXT) LIKE '%1231'
)
SELECT p.年份,
       ROUND(p.净利润 * 100.0
             / ((b.权益 + LAG(b.权益) OVER (ORDER BY b.年份)) / 2), 2) AS ROE
FROM pl p
JOIN bs b ON p.年份 = b.年份
ORDER BY p.年份
"""


def main():
    conn = sqlite3.connect(DB_PATH)
    frames = []

    for name in STOCKS:
        profit = pd.read_sql(PROFIT_SQL.format(table=f"{name}_利润表"), conn)
        roe = pd.read_sql(
            ROE_SQL.format(bs_table=f"{name}_资产负债表", pl_table=f"{name}_利润表"), conn
        )
        df = profit.merge(roe, on="年份", how="left")
        df["公司"] = name
        df = df[(df["年份"] >= START) & (df["年份"] <= END)]
        frames.append(df)
        print(f"{name}：{len(df)} 个年度观测值")

    conn.close()

    result = pd.concat(frames, ignore_index=True)
    result = result[["公司", "年份", "营收_亿元", "归母净利润_亿元", "净利率", "营收增速", "ROE"]]
    result.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print("指标汇总已导出：", OUT_PATH)


if __name__ == "__main__":
    main()
