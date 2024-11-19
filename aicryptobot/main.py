#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - main.py
import logging

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from cex.binance_cex import Binance

if __name__ == "__main__":
    b = Binance()
    print(b)
