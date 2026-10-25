"""
白酒行业财务对比可视化
读取 数据/指标汇总.csv，输出三张对比图到 图表/：
    图1 净利率对比（折线）
    图2 营收增速对比（折线，含零轴参考线）
    图3 ROE 对比（分组柱状）
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE, "数据", "指标汇总.csv")
FIG_DIR = os.path.join(BASE, "图表")

COLORS = {"贵州茅台": "#C8102E", "五粮液": "#1F6FB2", "泸州老窖": "#E0A526"}
SIZE_LINE = (9, 4.3)
SIZE_BAR = (10, 4.6)

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 110


def series(df, company, col):
    d = df[df["公司"] == company].copy()
    d["年"] = d["年份"].astype(str).str[:4].astype(int)
    return d.set_index("年")[col]


def plot_lines(df, col, title, ylabel, filename):
    plt.figure(figsize=SIZE_LINE)
    for company, color in COLORS.items():
        s = series(df, company, col)
        plt.plot(s.index, s.values, marker="o", linewidth=2, label=company, color=color)
    plt.title(title, fontsize=14)
    plt.xlabel("年份")
    plt.ylabel(ylabel)
    plt.grid(alpha=0.3, linestyle="--")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=150)
    plt.close()


def plot_roe_bars(df):
    years = sorted(series(df, "贵州茅台", "ROE").index)
    x = np.arange(len(years))
    width = 0.26

    plt.figure(figsize=SIZE_BAR)
    for i, (company, color) in enumerate(COLORS.items()):
        s = series(df, company, "ROE").reindex(years)
        plt.bar(x + (i - 1) * width, s.values, width=width, label=company, color=color)
    plt.xticks(x, years)
    plt.title("三家白酒企业 ROE 对比（2015-2024）", fontsize=14)
    plt.xlabel("年份")
    plt.ylabel("ROE（%）")
    plt.grid(alpha=0.3, axis="y", linestyle="--")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "图3_ROE对比.png"), dpi=150)
    plt.close()


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

    plot_lines(df, "净利率", "三家白酒企业净利率对比（2015-2024）", "净利率（%）", "图1_净利率对比.png")
    plot_lines(df, "营收增速", "三家白酒企业营收增速对比（2015-2024）", "营收增速（%）", "图2_营收增速对比.png")
    plot_roe_bars(df)
    print("三张图表已输出到：", FIG_DIR)


if __name__ == "__main__":
    main()
