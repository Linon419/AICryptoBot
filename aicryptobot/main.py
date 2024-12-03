#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - main.py

import argparse
import logging
import os

from dotenv import load_dotenv

load_dotenv()  # do not put these two after importing custom packages
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from engine import analyzer
from telegram import TelegramBot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose the mode and provide symbols.")
    parser.add_argument("--mode", choices=["script", "bot"], default="script", help="`script` or `bot`")
    parser.add_argument("--symbols", type=str, help="Comma-separated list of symbols, e.g., BTCUSDT,TRXUSDT.")
    args = parser.parse_args()

    if args.mode == "script":
        default_symbols = ["LTCUSDT"]
        symbols = args.symbols.split(",") if args.symbols else default_symbols
        analyzer(symbols)
    elif args.mode == "bot":
        logging.info("Running as bot...")
        bot = TelegramBot()
        bot.run()
