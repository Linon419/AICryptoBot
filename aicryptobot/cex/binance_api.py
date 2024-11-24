#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - binance_cex.py

import json
import logging
import os

import pandas as pd
import talib
from binance.um_futures import UMFutures

from cex import CEX

if os.getenv("ENV", "dev") != "dev":
    logging.warning("⚠️⚠️⚠️生产环境⚠️⚠️⚠️️")


class BinanceAPI(CEX):

    def __init__(self, symbol: str = None, interval: str = "15m"):
        suffix = ""
        if os.getenv("ENV", "dev") == "dev":
            suffix = "_TEST"
        api_key, api_secret, base_url = (
            os.getenv(f"BINANCE_API_KEY{suffix}"),
            os.getenv(f"BINANCE_API_SECRET{suffix}"),
            os.getenv(f"BINANCE_BASE_URL{suffix}"),
        )
        self.__um_client = UMFutures(key=api_key, secret=api_secret, base_url=base_url)
        self.df = pd.DataFrame()
        self.__symbol = symbol
        self.__interval = interval
        if symbol is not None:
            self._candlestick()

    def _candlestick(self):
        # K线数据：开盘价、收盘价、最高价、最低价（最好包含多个时间段）
        candles = self.__um_client.klines(symbol=self.__symbol, interval=self.__interval, limit=150)
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

    def get_all_indicators(self) -> str:
        logging.debug("获取 %s %s的技术指标中....", self.__symbol, self.__interval)
        self._boll()
        self._rsi()
        self._macd()
        self._volume()
        self._ma()
        self.df.drop(columns=["ignore", "close_time", "transaction_value", "transaction_count", "ema99"], inplace=True)
        self.df.dropna(inplace=True)

        return self.df.to_json(orient="records", date_format="iso")

    def __str__(self):
        return "binance"

    def get_usdt_balance(self):
        assets = self.__um_client.balance()
        for asset in assets:
            if asset["asset"] == "USDT":
                return asset

    def new_order(self, side, usdt, leverage=5):
        price = self.get_price()
        # 需要处理一下精度问题
        quantity = round(usdt / price, 3)
        logging.info("%s：%s，数量：%s", self.__symbol, "做空" if side == "SELL" else "做多", quantity)
        self.__um_client.change_leverage(symbol=self.__symbol, leverage=leverage)
        self.__um_client.new_order(symbol=self.__symbol, side=side, quantity=quantity, type="MARKET")

    def get_holdings(self) -> list:
        data = self.__um_client.get_position_risk(symbol=self.__symbol)
        return data

    def close_holdings(self, quantity=None):
        position = self.get_holdings()
        position_amount = float(position[0]["positionAmt"])
        if quantity is None:
            quantity = abs(position_amount)
        # positionAmt>0 做多，positionAmt<0 做空
        if position_amount > 0:
            logging.info("做多平仓，数量：%s", quantity)
            self.__um_client.new_order(symbol=self.__symbol, side="SELL", closePosition=True, type="MARKET")
        else:
            logging.info("做空平仓，数量：%s", quantity)
            self.__um_client.new_order(symbol=self.__symbol, side="BUY", closePosition=True, type="MARKET")

    def get_price(self) -> float:
        # 1 个币的价格，单位 USDT
        return float(self.__um_client.ticker_price(symbol=self.__symbol)["price"])
