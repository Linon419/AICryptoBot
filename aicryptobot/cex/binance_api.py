#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - binance_cex.py

import os

from binance.spot import Spot
from binance.um_futures import UMFutures
from cex import CEX

import random

import pandas as pd
import talib

import logging


class BinanceAPI(CEX):

    def __init__(self, symbol: str, interval: str):
        api_key, api_secret = os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET")
        self.__um_client = UMFutures()
        self.df = pd.DataFrame()
        self.__symbol = symbol
        self.__interval = interval
        self._candlestick()

    def _candlestick(self):
        # K线数据：开盘价、收盘价、最高价、最低价（最好包含多个时间段）
        candles = self.__um_client.klines(symbol=self.__symbol, interval=self.__interval, limit=200)
        columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "transaction_value",
            "transaction_count",
            "active_buy_volume",
            "active_buy_value",
            "ignore",
        ]

        self.df = pd.DataFrame(candles, columns=columns)
        numeric_columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "transaction_value",
            "transaction_count",
            "active_buy_volume",
            "active_buy_value",
        ]
        self.df[numeric_columns] = self.df[numeric_columns].apply(pd.to_numeric)
        self.df["open_time"] = pd.to_datetime(self.df["open_time"], unit="ms")
        self.df["close_time"] = pd.to_datetime(self.df["close_time"], unit="ms")

    def _boll(self):
        # 默认参数是时间周期 20，标准差系数 2
        upperband, middleband, lowerband = talib.BBANDS(self.df["close"], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        self.df["upperband"] = upperband
        self.df["middleband"] = middleband
        self.df["lowerband"] = lowerband

    def _rsi(self):
        rsi6 = talib.RSI(self.df["close"], timeperiod=6)
        rsi12 = talib.RSI(self.df["close"], timeperiod=12)
        rsi24 = talib.RSI(self.df["close"], timeperiod=24)
        self.df["rsi6"] = rsi6
        self.df["rsi12"] = rsi12
        self.df["rsi24"] = rsi24

    def _macd(self):
        dif, dea, macd = talib.MACD(self.df["close"], fastperiod=12, slowperiod=26, signalperiod=9)
        self.df["dif"] = dif
        self.df["dea"] = dea
        self.df["macd"] = macd

    def _volume(self):
        pass
        # 似乎不是很重要
        # vol = self.df["volume"]
        # ma5 = self.df["volume"].rolling(window=5).mean()
        # ma10 = self.df["volume"].rolling(window=10).mean()
        # self.df["vol-ma5"] = ma5
        # self.df["vol-ma10"] = ma10

    def _ma(self):
        # sma7 = talib.SMA(self.df["close"], timeperiod=7)
        # sma25 = talib.SMA(self.df["close"], timeperiod=25)
        # sma99 = talib.SMA(self.df["close"], timeperiod=99)

        ema7 = talib.EMA(self.df["close"], timeperiod=7)
        ema25 = talib.EMA(self.df["close"], timeperiod=25)
        ema99 = talib.EMA(self.df["close"], timeperiod=99)

        # self.df["sma7"] = sma7
        # self.df["sma25"] = sma25
        # self.df["sma99"] = sma99

        self.df["ema7"] = ema7
        self.df["ema25"] = ema25
        self.df["ema99"] = ema99

    def get_all_indicators(self):
        logging.info("Gathering %s indicators....", self.__interval)
        self._boll()
        self._rsi()
        self._macd()
        self._volume()
        self._ma()
        self.df.drop(columns=["ignore", "close_time"], inplace=True)
        self.df.dropna(inplace=True)

        return self.df.to_json(orient="records", date_format="iso")

    def __str__(self):
        return "binance"
