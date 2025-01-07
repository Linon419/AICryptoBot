#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - tradingview.py

import json
import logging
import os

import pandas as pd
import talib

from datasource import DataSource


class TradingViewAPI(DataSource):
    def __init__(self, *args, **kwargs):
        pass

    def _macd(self):
        pass

    def _rsi(self):
        pass

    def _boll(self):
        pass

    def _volume(self):
        pass

    def _candlestick(self):
        pass

    def _ma(self):
        pass

    def get_all_indicators(self) -> str:
        pass
