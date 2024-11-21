#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - main.py

import json
import logging

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
from cex.binance_api import BinanceAPI
from llm.openai_llm import GPT


def engine(symbol):
    indicators = [
        # BinanceAPI(symbol, "5m").get_all_indicators(),
        BinanceAPI(symbol, "15m").get_all_indicators(),
        BinanceAPI(symbol, "30m").get_all_indicators(),
        BinanceAPI(symbol, "1h").get_all_indicators(),
    ]
    gpt = GPT()

    account = BinanceAPI(symbol, "1m")
    h = account.get_holdings()
    recommendation = gpt.send(indicators, None if len(h) == 0 else json.dumps(h))

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
        return


if __name__ == "__main__":
    # engine("XLMUSDT")
    # engine("TONUSDT")
    # engine("BTCUSDT")
    # engine("DOGEUSDT")
    engine("PNUTUSDT")
    engine("OPUSDT")
