#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - types.py

from typing import TypedDict


class TakeProfit(TypedDict):
    usdt: float
    percentage: float


class StopLoss(TypedDict):
    usdt: float
    percentage: float


class TradingAction(TypedDict):
    action: str
    detail: str
    take_profit: TakeProfit
    stop_loss: StopLoss
