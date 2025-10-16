#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - ema_detector.py

import logging
import os
from typing import Dict, Optional

from datasource.binance_api import BinanceAPI
from datasource.stock import StockAPI


class EMAAlignmentType:
    """EMA alignment types"""

    BULLISH = "bullish"  # Perfect bullish alignment: 21 > 55 > 100 > 200 and price > 21
    BEARISH = "bearish"  # Perfect bearish alignment: 21 < 55 < 100 < 200 and price < 21
    MIXED = "mixed"  # Mixed or no clear alignment


class EMADetector:
    """Detect EMA alignment patterns"""

    def __init__(self):
        self.interval = os.getenv("MONITOR_INTERVAL", "1h")  # Default to 1h

    def detect_alignment(self, symbol: str) -> Optional[Dict]:
        """
        Detect EMA alignment for a given symbol

        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)

        Returns:
            Dict with alignment info or None if error:
            {
                'symbol': str,
                'alignment': str (bullish/bearish/mixed),
                'price': float,
                'ema21': float,
                'ema55': float,
                'ema100': float,
                'ema200': float,
                'interval': str
            }
        """
        try:
            # Get data source based on symbol type
            if symbol.endswith("USDT"):
                data_source = BinanceAPI(symbol, self.interval, count=10)
            else:
                data_source = StockAPI(symbol, self.interval, count=10)

            # Calculate indicators
            data_source._boll()
            data_source._rsi()
            data_source._macd()
            data_source._volume()
            data_source._ma()

            # Get the latest values
            df = data_source.df
            if df.empty:
                logging.warning("No data available for %s", symbol)
                return None

            latest = df.iloc[-1]

            # Extract values
            price = float(latest["close"])
            ema21 = float(latest["ema21"])
            ema55 = float(latest["ema55"])
            ema100 = float(latest["ema100"])
            ema200 = float(latest["ema200"])

            # Detect alignment
            alignment = self._check_alignment(price, ema21, ema55, ema100, ema200)

            result = {
                "symbol": symbol,
                "alignment": alignment,
                "price": round(price, 2),
                "ema21": round(ema21, 2),
                "ema55": round(ema55, 2),
                "ema100": round(ema100, 2),
                "ema200": round(ema200, 2),
                "interval": self.interval,
            }

            logging.debug("EMA alignment for %s: %s", symbol, alignment)
            return result

        except Exception as e:
            logging.error("Failed to detect EMA alignment for %s: %s", symbol, e)
            return None

    def _check_alignment(
        self, price: float, ema21: float, ema55: float, ema100: float, ema200: float
    ) -> str:
        """
        Check if EMAs are in perfect bullish or bearish alignment

        Perfect bullish: 21 > 55 > 100 > 200 and price > 21
        Perfect bearish: 21 < 55 < 100 < 200 and price < 21
        """
        # Check perfect bullish alignment
        if price > ema21 and ema21 > ema55 and ema55 > ema100 and ema100 > ema200:
            return EMAAlignmentType.BULLISH

        # Check perfect bearish alignment
        if price < ema21 and ema21 < ema55 and ema55 < ema100 and ema100 < ema200:
            return EMAAlignmentType.BEARISH

        # Mixed or unclear alignment
        return EMAAlignmentType.MIXED

    def format_notification(self, alignment_info: Dict) -> str:
        """
        Format alignment info into a notification message

        Args:
            alignment_info: Dict returned by detect_alignment()

        Returns:
            Formatted message string
        """
        symbol = alignment_info["symbol"]
        alignment = alignment_info["alignment"]
        price = alignment_info["price"]
        ema21 = alignment_info["ema21"]
        ema55 = alignment_info["ema55"]
        ema100 = alignment_info["ema100"]
        ema200 = alignment_info["ema200"]
        interval = alignment_info["interval"]

        if alignment == EMAAlignmentType.BULLISH:
            emoji = "🟢"
            alignment_text = "完美多头排列"
            description = "价格强势上涨，建议关注做多机会"
        elif alignment == EMAAlignmentType.BEARISH:
            emoji = "🔴"
            alignment_text = "完美空头排列"
            description = "价格强势下跌，建议关注做空机会"
        else:
            emoji = "⚪️"
            alignment_text = "震荡行情"
            description = "EMA排列混乱，建议观望"

        message = f"""{emoji} EMA排列通知

交易对: {symbol}
周期: {interval}
状态: {alignment_text}

当前价格: {price}
EMA21: {ema21}
EMA55: {ema55}
EMA100: {ema100}
EMA200: {ema200}

💡 {description}

查看详情: https://www.binance.com/zh-CN/futures/{symbol}"""

        return message
