#!/usr/bin/env python3
# coding: utf-8

import logging
import os
import webbrowser
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from cex.binance_api import BinanceAPI
from llm.openai_llm import GPT


def show(df: pd.DataFrame):
    print(df.to_string())
    table = df.to_html(index=False)

    cur_dir = Path(__file__).parent
    now = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    output = Path(__file__).parent.parent.joinpath("output")
    output.mkdir(exist_ok=True)

    env = Environment(loader=FileSystemLoader(cur_dir))
    template = env.get_template("template.html")
    html = template.render(now=now, table=table)
    html_path = output.joinpath(f"analysis_{now}.html")
    html_path.write_text(html, encoding="u8")
    webbrowser.open(html_path.absolute().as_uri(), new=0, autoraise=True)


def analyzer(symbols: list | str) -> str:
    gpt = GPT()
    data = []
    if isinstance(symbols, str):
        symbols = [symbols]

    for symbol in symbols:
        symbol = symbol.upper()

        intervals = os.getenv("BINANCE_INTERVAL", "1m=30,5m=40,15m=30,1h=25,2h=15,4h=10,8h=8,12h=6,1d=5")
        # 1m=30 最近30分钟（细节）   5m=40 最近3小时20分钟（短线波动）   15m=30 最近7.5小时（日内趋势）
        # 1h=25 最近25小时（日内到短期趋势）   2h=15 最近1.25天（中期波动）   4h=10 最近1.66天（背景趋势）
        # 8h=8 最近2.66天（中期背景趋势）   12h=6 最近3天（长期背景趋势）   1d=5 最近5天（日线趋势背景）
        indicators = {}
        for item in intervals.split(","):
            interval, count = item.split("=")
            indicators[interval] = BinanceAPI(symbol, interval, count=int(count)).get_all_indicators()

        logging.info("采集数据密度：%s", indicators.keys())
        recommendation = gpt.send(symbol, indicators)
        action, detail = recommendation["action"], recommendation["detail"]

        if action == "long":
            logging.info("GPT 推荐做多 %s，详情：%s", symbol, detail)
            # account.new_order("BUY", usdt)
        elif action == "short":
            logging.info("GPT 推荐做空 %s，详情：%s", symbol, detail)
            # account.new_order("SELL", usdt)
        elif action == "hold":
            logging.info("GPT 推荐持有 %s，详情：%s", symbol, detail)
        elif action == "close":
            logging.warning("[TODO]GPT 推荐平仓 %s，详情：%s", symbol, detail)
        else:
            logging.error("无法识别的操作：%s", action)

        item = {"symbol": symbol}
        item.update(recommendation)
        data.append(item)

    df = pd.DataFrame(data)
    show(df)
    return df.to_string()
