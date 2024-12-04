#!/usr/bin/env python3
# coding: utf-8

import logging
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
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = Path(__file__).parent.parent.joinpath("output")
    output.mkdir(exist_ok=True)

    env = Environment(loader=FileSystemLoader(cur_dir))
    template = env.get_template("template.html")
    html = template.render(now=now, table=table)
    html_path = output.joinpath(f"analysis_{now}.html")
    html_path.write_text(html)
    webbrowser.open(html_path.absolute().as_uri(), new=0, autoraise=True)


def analyzer(symbols: list | str) -> str:
    gpt = GPT()
    data = []
    if isinstance(symbols, str):
        symbols = [symbols]

    for symbol in symbols:
        symbol = symbol.upper()
        d1m = BinanceAPI(symbol, "1m", count=30).get_all_indicators()  # 最近30分钟（细节）
        d5m = BinanceAPI(symbol, "5m", count=40).get_all_indicators()  # 最近3小时20分钟（短线波动）
        d15m = BinanceAPI(symbol, "15m", count=30).get_all_indicators()  # 最近7.5小时（日内趋势）
        d1h = BinanceAPI(symbol, "1h", count=25).get_all_indicators()  # 最近25小时（日内到短期趋势）
        d2h = BinanceAPI(symbol, "2h", count=15).get_all_indicators()  # 最近1.25天（中期波动）
        d4h = BinanceAPI(symbol, "4h", count=10).get_all_indicators()  # 最近1.66天（背景趋势）
        d8h = BinanceAPI(symbol, "8h", count=8).get_all_indicators()  # 最近2.66天（中期背景趋势）
        d12h = BinanceAPI(symbol, "12h", count=6).get_all_indicators()  # 最近3天（长期背景趋势）
        d1d = BinanceAPI(symbol, "1d", count=5).get_all_indicators()  # 最近5天（日线趋势背景）

        indicators = {
            "1m": d1m,
            "5m": d5m,
            "15m": d15m,
            "1h": d1h,
            "2h": d2h,
            "4h": d4h,
            "8h": d8h,
            "12h": d12h,
            "1d": d1d,
        }

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
