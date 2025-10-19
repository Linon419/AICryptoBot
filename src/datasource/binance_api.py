#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - binance_cex.py


import logging
import os

import pandas as pd
from binance.um_futures import UMFutures

from datasource import DataSource


class BinanceAPI(DataSource):

    def __init__(self, symbol: str = None, interval: str = "15m", count=50):
        api_key, api_secret = (os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))
        self.__um_client = UMFutures(key=api_key, secret=api_secret)
        self.df = pd.DataFrame()
        self.__symbol = symbol
        self.__interval = interval
        self.__count = count
        if symbol is not None:
            self._candlestick()

    def _candlestick(self):
        # K线数据：开盘价、收盘价、最高价、最低价（最好包含多个时间段）
        # EMA200 needs at least 200 candles, so we fetch 200 + count to ensure enough data
        limit = max(200 + self.__count, 300)  # At least 300 candles to ensure EMA200 can be calculated
        logging.debug("Fetching %s klines for %s, interval=%s, limit=%d", self.__symbol, self.__symbol, self.__interval, limit)
        candles = self.__um_client.klines(symbol=self.__symbol, interval=self.__interval, limit=limit)
        logging.debug("Got %d candles for %s", len(candles) if candles else 0, self.__symbol)
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

    def get_all_indicators(self) -> str:
        logging.debug("获取 %s %s的技术指标中....", self.__symbol, self.__interval)
        logging.debug("DataFrame shape before indicators: %s", self.df.shape)
        self._boll()
        self._rsi()
        self._macd()
        self._volume()
        self._ma()
        self.df.drop(columns=["ignore", "close_time", "transaction_value", "transaction_count"], inplace=True)
        self.df.dropna(inplace=True)
        logging.info("DataFrame shape after dropna for %s %s: %s", self.__symbol, self.__interval, self.df.shape)

        # Only keep the last 'count' rows to avoid sending too much data to LLM
        if len(self.df) > self.__count:
            self.df = self.df.tail(self.__count)
            logging.debug("Trimmed DataFrame to last %d rows for %s %s", self.__count, self.__symbol, self.__interval)

        # 转换数据格式 rsi保留整数，macd boll ema active_buy_value 保留两位小数
        self.df["rsi6"] = self.df["rsi6"].astype(int)
        self.df["rsi12"] = self.df["rsi12"].astype(int)
        self.df["rsi24"] = self.df["rsi24"].astype(int)
        self.df["dif"] = self.df["dif"].round(2)
        self.df["dea"] = self.df["dea"].round(2)
        self.df["macd"] = self.df["macd"].round(2)
        self.df["upperband"] = self.df["upperband"].round(2)
        self.df["middleband"] = self.df["middleband"].round(2)
        self.df["lowerband"] = self.df["lowerband"].round(2)
        self.df["ema21"] = self.df["ema21"].round(2)
        self.df["ema55"] = self.df["ema55"].round(2)
        self.df["ema100"] = self.df["ema100"].round(2)
        self.df["ema200"] = self.df["ema200"].round(2)
        self.df["active_buy_value"] = self.df["active_buy_value"].round(2)

        # 价格数据（OHLCV）也保留两位小数，确保数据精度一致
        self.df["open"] = self.df["open"].round(2)
        self.df["high"] = self.df["high"].round(2)
        self.df["low"] = self.df["low"].round(2)
        self.df["close"] = self.df["close"].round(2)
        self.df["volume"] = self.df["volume"].round(2)
        self.df["active_buy_volume"] = self.df["active_buy_volume"].round(2)

        # 秒级时间戳
        return self.df.to_json(orient="records", date_format="epoch", date_unit="s")

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
