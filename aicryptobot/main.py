#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - main.py

import json
import logging
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

load_dotenv()  # do not put these two after importing custom packages
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from cex.binance_api import BinanceAPI
from llm.openai_llm import GPT


def show(df: pd.DataFrame):
    print(df.to_string())
    table = df.to_html(index=False)

    cur_dir = Path(__file__).parent
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    p = Path(__file__).parent.joinpath("output", f"analysis_{now}.html")

    env = Environment(loader=FileSystemLoader(cur_dir))
    template = env.get_template("template.html")
    full_html = template.render(now=now, table=table)

    with open(p, "w", encoding="utf-8") as file:
        file.write(full_html)


def engine(symbols: list | str):
    gpt = GPT()
    data = []
    if isinstance(symbols, str):
        symbols = [symbols]

    for symbol in symbols:
        d15 = BinanceAPI(symbol, "15m").get_all_indicators()  # 约最近15m*50=12.5小时的数据
        d30 = BinanceAPI(symbol, "30m").get_all_indicators()  # 约最近30m*50=25小时的数据
        d1h = BinanceAPI(symbol, "1h").get_all_indicators()  # 约最近1h*50=50小时的数据
        indicators = [d15, d30, d1h]

        account = BinanceAPI()
        recommendation = gpt.send(symbol, indicators, account.get_holdings())
        time.sleep(15)

        action = recommendation["action"]
        detail = recommendation["detail"]
        take_profit = recommendation["take_profit"]
        stop_loss = recommendation["stop_loss"]
        usdt = 300

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


if __name__ == "__main__":
    tokens = [
        "GRASSUSDT",
        "PNUTUSDT",
        "TROYUSDT",
        "XRPUSDT",
        "CRVUSDT",
        "DOGEUSDT",
        "SOLUSDT",
        "1000PEPEUSDT",
        "LTCUSDT",
        "XLMUSDT",
        "ALGOUSDT",
        "IOTAUSDT",
        "TONUSDT",
        "SUIUSDT",
        "TRXUSDT",
        "1000SHIBUSDT",
        "OPUSDT",
    ]

    engine(tokens)
