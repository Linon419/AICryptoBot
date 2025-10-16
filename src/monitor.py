#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - monitor.py

import logging
import os
import time
from threading import Thread
from typing import Dict, Set

from ema_detector import EMAAlignmentType, EMADetector
from subscription_manager import SubscriptionManager


class EMAMonitor:
    """Monitor EMA alignments and send notifications"""

    def __init__(self, bot_instance=None):
        """
        Initialize the monitor

        Args:
            bot_instance: TelegramBot instance for sending notifications
        """
        self.bot = bot_instance
        self.subscription_manager = SubscriptionManager()
        self.detector = EMADetector()
        self.check_interval = int(os.getenv("MONITOR_CHECK_INTERVAL", "3600"))  # Default 1 hour
        self.running = False
        self.thread = None
        # Track last alignment state to avoid duplicate notifications
        self.last_alignment: Dict[str, str] = {}

    def start(self):
        """Start the monitoring service in a background thread"""
        if self.running:
            logging.warning("Monitor is already running")
            return

        self.running = True
        self.thread = Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logging.info(
            "EMA monitor started, checking every %d seconds (%d minutes)",
            self.check_interval,
            self.check_interval // 60,
        )

    def stop(self):
        """Stop the monitoring service"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logging.info("EMA monitor stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_all_subscriptions()
            except Exception as e:
                logging.error("Error in monitor loop: %s", e)

            # Sleep for the configured interval
            time.sleep(self.check_interval)

    def _check_all_subscriptions(self):
        """Check all subscribed symbols for EMA alignments"""
        all_symbols = self.subscription_manager.get_all_symbols()

        if not all_symbols:
            logging.debug("No symbols to monitor")
            return

        logging.info("Checking EMA alignments for %d symbols", len(all_symbols))

        for symbol in all_symbols:
            try:
                self._check_symbol(symbol)
            except Exception as e:
                logging.error("Error checking symbol %s: %s", symbol, e)

    def _check_symbol(self, symbol: str):
        """
        Check a single symbol for EMA alignment and notify subscribers if needed

        Args:
            symbol: Trading pair symbol
        """
        # Detect alignment
        alignment_info = self.detector.detect_alignment(symbol)

        if not alignment_info:
            logging.warning("Failed to get alignment info for %s", symbol)
            return

        alignment = alignment_info["alignment"]

        # Check if alignment has changed and is bullish or bearish
        last_alignment = self.last_alignment.get(symbol)
        is_new_alignment = last_alignment != alignment

        # Only notify if:
        # 1. Alignment is bullish or bearish (not mixed)
        # 2. Alignment has changed from previous check
        if alignment in [EMAAlignmentType.BULLISH, EMAAlignmentType.BEARISH] and is_new_alignment:
            self._notify_subscribers(symbol, alignment_info)

        # Update last alignment state
        self.last_alignment[symbol] = alignment

    def _notify_subscribers(self, symbol: str, alignment_info: Dict):
        """
        Send notification to all subscribers of a symbol

        Args:
            symbol: Trading pair symbol
            alignment_info: Alignment information dict
        """
        if not self.bot:
            logging.warning("No bot instance available for notifications")
            return

        subscribers = self.subscription_manager.get_subscribers(symbol)

        if not subscribers:
            logging.debug("No subscribers for %s", symbol)
            return

        message = self.detector.format_notification(alignment_info)

        logging.info(
            "Sending %s alignment notification for %s to %d subscribers",
            alignment_info["alignment"],
            symbol,
            len(subscribers),
        )

        for user_id in subscribers:
            try:
                self.bot.bot.send_message(chat_id=user_id, text=message, disable_web_page_preview=True)
                logging.debug("Sent notification to user %s", user_id)
            except Exception as e:
                logging.error("Failed to send notification to user %s: %s", user_id, e)

    def check_now(self, symbol: str) -> Dict:
        """
        Manually check a symbol's EMA alignment (for testing or on-demand checks)

        Args:
            symbol: Trading pair symbol

        Returns:
            Alignment info dict
        """
        return self.detector.detect_alignment(symbol)
