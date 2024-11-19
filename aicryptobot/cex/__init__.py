#!/usr/bin/env python3
# coding: utf-8


from abc import ABC, abstractmethod


class CEX(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def macd(self):
        pass

    @abstractmethod
    def rsi(self):
        pass

    @abstractmethod
    def boll(self):
        pass

    @abstractmethod
    def volume(self):
        pass

    @abstractmethod
    def kdj(self):
        pass

    @abstractmethod
    def candlestick(self):
        # K线数据：开盘价、收盘价、最高价、最低价（最好包含多个时间段）
        pass

    @abstractmethod
    def spot(self):
        # 现货
        pass

    @abstractmethod
    def futures(self):
        # U本位合约
        pass

    def __str__(self):
        raise NotImplementedError
