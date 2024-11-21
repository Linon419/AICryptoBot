#!/usr/bin/env python3
# coding: utf-8


from abc import ABC, abstractmethod


class CEX(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def __macd(self):
        pass

    @abstractmethod
    def __rsi(self):
        pass

    @abstractmethod
    def __boll(self):
        pass

    @abstractmethod
    def __volume(self):
        pass

    @abstractmethod
    def __kdj(self):
        pass

    @abstractmethod
    def __candlestick(self):
        pass

    @abstractmethod
    def __ma(self):
        pass

    def __str__(self):
        raise NotImplementedError
