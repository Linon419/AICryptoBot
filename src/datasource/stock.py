#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - stock.py


import datetime
import json
import logging
import os

import dateparser
import pandas as pd
import talib
import yfinance

from datasource import DataSource


class StockAPI(DataSource):
    def __init__(self, symbol: str = None, interval: str = "15m", count=50):
        self.df = pd.DataFrame()
        self.__symbol = symbol
        self.__interval = interval
        self.__count = count
        if symbol is not None:
            self._candlestick()

    def _candlestick(self):
        # Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        end = datetime.datetime.now()
        # calculate start date by interval and count
        delta = end - dateparser.parse(self.__interval)
        start = end - (delta * self.__count)
        self.df = yfinance.download(self.__symbol, interval=self.__interval, start=start, end=end)
        self.df.columns = self.df.columns.droplevel(1)
        self.df.rename(
            columns={"Close": "close", "High": "high", "Low": "low", "Open": "open", "Volume": "volume"},
            inplace=True,
        )

    def get_all_indicators(self) -> str:
        logging.debug("获取 %s %s的技术指标中....", self.__symbol, self.__interval)
        self._boll()
        self._rsi()
        self._macd()
        self._volume()
        self._ma()
        return self.df.to_string()

    def __str__(self):
        return "yahoo finance"
