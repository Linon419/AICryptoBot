#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - binance_cex.py
import os

import okx.Account as Account
import okx.Funding as Funding
import okx.Trade as Trade

from cex import CEX


class OKX(CEX):
    # fund 资金账户 trade 交易账户
    FUNDING = 6
    TRADING = 18

    def __init__(self):
        api_key, api_secret, passphrase = (
            os.getenv("OKX_API_KEY"),
            os.getenv("OKX_API_SECRET"),
            os.getenv("OKX_PASSPHRASE"),
        )

        params = dict(
            api_key=api_key,
            api_secret_key=api_secret,
            passphrase=passphrase,
            use_server_time=False,
            flag="0",
            debug=False,
        )

        self.account = Account.AccountAPI(**params)
        self.funding = Funding.FundingAPI(**params)
        self.trade = Trade.TradeAPI(**params)

    def __macd(self):
        pass

    def __rsi(self):
        pass

    def __boll(self):
        pass

    def __volume(self):
        pass

    def __kdj(self):
        pass

    def __candlestick(self):
        # K线数据：开盘价、收盘价、最高价、最低价（最好包含多个时间段）
        pass

    def spot(self):
        pass

    def futures(self):
        pass

    def __str__(self):
        return "okx"
