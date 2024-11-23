#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - main.py

import logging

from dotenv import load_dotenv

load_dotenv()

from engine import analyzer

load_dotenv()  # do not put these two after importing custom packages
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


if __name__ == "__main__":
    tokens = ["ADAUSDT"]
    analyzer(tokens)
