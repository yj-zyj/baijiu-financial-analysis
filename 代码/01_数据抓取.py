"""
白酒行业财务数据抓取
从新浪财经公开财报接口获取三家上市公司 利润表 / 资产负债表，写入本地 SQLite 数据库。

数据源：akshare（stock_financial_report_sina）
输出：数据/finance.db
"""

import os
import time
import sqlite3

import akshare as ak

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "数据", "finance.db")

STOCKS = {
    "sh600519": "贵州茅台",
    "sz000858": "五粮液",
    "sz000568": "泸州老窖",
}
REPORTS = ["利润表", "资产负债表"]


def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    for code, name in STOCKS.items():
        for report in REPORTS:
            df = ak.stock_financial_report_sina(stock=code, symbol=report)
            table = f"{name}_{report}"
            df.to_sql(table, conn, if_exists="replace", index=False)
            print(f"{table} 入库完成：{df.shape[0]} 行 × {df.shape[1]} 列")
            time.sleep(2)  # 控制请求频率，避免接口限流

    conn.close()
    print("全部入库完成：", DB_PATH)


if __name__ == "__main__":
    main()
