#!/usr/bin/env python3
# coding: utf-8


from abc import ABC, abstractmethod


class CEX(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def _macd(self):
        pass

    @abstractmethod
    def _rsi(self):
        pass

    @abstractmethod
    def _boll(self):
        pass

    @abstractmethod
    def _volume(self):
        pass

    @abstractmethod
    def _kdj(self):
        pass

    @abstractmethod
    def _candlestick(self):
        pass

    @abstractmethod
    def _ma(self):
        pass

    def __str__(self):
        raise NotImplementedError
