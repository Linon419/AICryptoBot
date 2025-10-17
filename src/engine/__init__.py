#!/usr/bin/env python3
# coding: utf-8

import logging
import os
import webbrowser
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from datasource.binance_api import BinanceAPI
from datasource.stock import StockAPI
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


def get_indicators(symbol, interval, count):
    if symbol.endswith("USDT"):
        return BinanceAPI(symbol, interval, count=int(count)).get_all_indicators()
    else:
        return StockAPI(symbol, interval, count=int(count)).get_all_indicators()


def analyzer(symbols: list | str) -> str:
    gpt = GPT()
    data = []
    if isinstance(symbols, str):
        symbols = [symbols]

    for symbol in symbols:
        symbol = symbol.upper()
        # 5m=50 最近4小时（精确入场）   15m=40 最近10小时（短期趋势）   1h=30 最近1.25天（核心周期）
        # 4h=20 最近3天（趋势背景）   1d=10 最近10天（大趋势方向）
        if symbol.endswith("USDT"):
            interval = os.getenv("BINANCE_INTERVAL", "5m=50,15m=40,1h=30,4h=20,1d=10")
        else:
            interval = os.getenv("STOCK_INTERVAL", "1d=50,5d=40,1wk=30,1mo=20")

        indicators = {}
        for item in interval.split(","):
            interval, count = item.split("=")
            indicators[interval] = get_indicators(symbol, interval, count)

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
