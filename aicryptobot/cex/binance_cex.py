#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - binance_cex.py

import os

from binance.spot import Spot

from cex import CEX


class Binance(CEX):

    def __init__(self):
        api_key, api_secret = os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET")
        self.spot = Spot(api_key, api_secret)

    def macd(self):
        pass

    def rsi(self):
        pass

    def boll(self):
        pass

    def volume(self):
        pass

    def kdj(self):
        pass

    def candlestick(self):
        # K线数据：开盘价、收盘价、最高价、最低价（最好包含多个时间段）
        pass

    def spot(self):
        pass

    def futures(self):
        pass

    def __str__(self):
        return "binance"
