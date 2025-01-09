#!/usr/bin/env python3
# coding: utf-8


from abc import ABC, abstractmethod

import pandas as pd
import talib


class DataSource(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        self.df = pd.DataFrame()

    def _macd(self):
        dif, dea, macd = talib.MACD(self.df["close"], fastperiod=12, slowperiod=26, signalperiod=9)
        self.df["dif"] = dif
        self.df["dea"] = dea
        self.df["macd"] = macd

    def _rsi(self):
        rsi6 = talib.RSI(self.df["close"], timeperiod=6)
        rsi12 = talib.RSI(self.df["close"], timeperiod=12)
        rsi24 = talib.RSI(self.df["close"], timeperiod=24)
        self.df["rsi6"] = rsi6
        self.df["rsi12"] = rsi12
        self.df["rsi24"] = rsi24

    def _boll(self):
        # 默认参数是时间周期 20，标准差系数 2
        upperband, middleband, lowerband = talib.BBANDS(self.df["close"], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        self.df["upperband"] = upperband
        self.df["middleband"] = middleband
        self.df["lowerband"] = lowerband

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

    @abstractmethod
    def _candlestick(self):
        pass

    def __str__(self):
        raise NotImplementedError
