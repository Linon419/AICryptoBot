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


class BinanceAPI(CEX):

    def __init__(self, symbol: str, interval: str):
        api_key, api_secret = os.getenv("BINANCE_API_KEY"), os.getenv(
            "BINANCE_API_SECRET"
        )
        self.__um_client = UMFutures()
        self.df = pd.DataFrame()
        self.__symbol = symbol
        self.__interval = interval
        self.__candlestick()

    def __candlestick(self):
        # K线数据：开盘价、收盘价、最高价、最低价（最好包含多个时间段）
        candles = self.__um_client.klines(
            symbol=self.__symbol, interval=self.__interval, limit=1000
        )
        columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "taker_buy_volume",
            "taker_buy_quote_volume",
            "ignore",
        ]

        self.df = pd.DataFrame(candles, columns=columns)
        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_volume",
            "taker_buy_volume",
            "taker_buy_quote_volume",
        ]
        self.df[numeric_columns] = self.df[numeric_columns].apply(pd.to_numeric)
        self.df["open_time"] = pd.to_datetime(self.df["open_time"], unit="ms")
        self.df["close_time"] = pd.to_datetime(self.df["close_time"], unit="ms")

    def __boll(self):
        # 默认参数是时间周期 20，标准差系数 2
        upperband, middleband, lowerband = talib.BBANDS(
            self.df["close"], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
        )
        self.df["upperband"] = upperband
        self.df["middleband"] = middleband
        self.df["lowerband"] = lowerband
        important_columns = self.df[
            ["open_time", "upperband", "middleband", "lowerband"]
        ]
        print(important_columns.tail(1))

    def __rsi(self):
        rsi6 = talib.RSI(self.df["close"], timeperiod=6)
        rsi12 = talib.RSI(self.df["close"], timeperiod=12)
        rsi24 = talib.RSI(self.df["close"], timeperiod=24)
        print(rsi6.tail(1).iloc[0], rsi12.tail(1).iloc[0], rsi24.tail(1).iloc[0])

    def __macd(self):
        dif, dea, macd = talib.MACD(
            self.df["close"], fastperiod=12, slowperiod=26, signalperiod=9
        )
        print(dif.tail(1).iloc[0], dea.tail(1).iloc[0], macd.tail(1).iloc[0])

    def __volume(self):
        vol = self.df["volume"]
        ma5 = self.df["volume"].rolling(window=5).mean()
        ma10 = self.df["volume"].rolling(window=10).mean()
        print(vol.tail(1).iloc[0], ma5.tail(1).iloc[0], ma10.tail(1).iloc[0])

    def __kdj(self):
        # 不准所以最好别用！
        k, d = talib.STOCH(
            self.df["high"],
            self.df["low"],
            self.df["close"],
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0,
        )

        # 计算 J 值
        j = 3 * k - 2 * d

        print(k.tail(1).iloc[0], d.tail(1).iloc[0], j.tail(1).iloc[0])

    def __ma(self):
        sma7 = talib.SMA(self.df["close"], timeperiod=7)
        sma25 = talib.SMA(self.df["close"], timeperiod=25)
        sma99 = talib.SMA(self.df["close"], timeperiod=99)

        ema7 = talib.EMA(self.df["close"], timeperiod=7)
        ema25 = talib.EMA(self.df["close"], timeperiod=25)
        ema99 = talib.EMA(self.df["close"], timeperiod=99)

        print(sma7.tail(1).iloc[0], sma25.tail(1).iloc[0], sma99.tail(1).iloc[0])
        print(ema7.tail(1).iloc[0], ema25.tail(1).iloc[0], ema99.tail(1).iloc[0])

    def get_all_indicators():
        pass

    def __str__(self):
        return "binance"
