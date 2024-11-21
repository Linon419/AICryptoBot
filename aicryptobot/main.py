#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - main.py
import logging

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
from aicryptobot.llm.openai_llm import GPT

from aicryptobot.cex.binance_api import BinanceAPI

if __name__ == "__main__":
    b = BinanceAPI("XLMUSDT", "1m")
    data1m = b.get_all_indicators()
    b = BinanceAPI("XLMUSDT", "5m")
    data5m = b.get_all_indicators()
    gpt = GPT()
    gpt.send(data1m, data5m)

    # b = Binance("BTCUSDT", "1h")
    # b.kdj()
