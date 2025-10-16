#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - subscription_manager.py

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Set


class SubscriptionManager:
    """Manage user subscriptions for EMA alignment monitoring"""

    def __init__(self, data_file: str = None):
        if data_file is None:
            data_file = os.getenv("SUBSCRIPTION_FILE", "subscriptions.json")
        self.data_file = Path(data_file)
        self.subscriptions: Dict[int, Set[str]] = {}
        self._load()

    def _load(self):
        """Load subscriptions from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Convert lists to sets for efficient operations
                    self.subscriptions = {int(user_id): set(symbols) for user_id, symbols in data.items()}
                logging.info("Loaded %d user subscriptions", len(self.subscriptions))
            except Exception as e:
                logging.error("Failed to load subscriptions: %s", e)
                self.subscriptions = {}
        else:
            logging.info("No subscription file found, starting fresh")
            self.subscriptions = {}

    def _save(self):
        """Save subscriptions to file"""
        try:
            # Convert sets to lists for JSON serialization
            data = {str(user_id): list(symbols) for user_id, symbols in self.subscriptions.items()}
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.debug("Saved subscriptions to %s", self.data_file)
        except Exception as e:
            logging.error("Failed to save subscriptions: %s", e)

    def subscribe(self, user_id: int, symbol: str) -> bool:
        """
        Subscribe a user to a symbol

        Args:
            user_id: Telegram user/chat ID
            symbol: Trading pair symbol (e.g., BTCUSDT)

        Returns:
            True if newly subscribed, False if already subscribed
        """
        symbol = symbol.upper().strip()
        if user_id not in self.subscriptions:
            self.subscriptions[user_id] = set()

        if symbol in self.subscriptions[user_id]:
            return False

        self.subscriptions[user_id].add(symbol)
        self._save()
        logging.info("User %s subscribed to %s", user_id, symbol)
        return True

    def unsubscribe(self, user_id: int, symbol: str) -> bool:
        """
        Unsubscribe a user from a symbol

        Args:
            user_id: Telegram user/chat ID
            symbol: Trading pair symbol (e.g., BTCUSDT)

        Returns:
            True if unsubscribed, False if not subscribed
        """
        symbol = symbol.upper().strip()
        if user_id not in self.subscriptions or symbol not in self.subscriptions[user_id]:
            return False

        self.subscriptions[user_id].remove(symbol)
        if not self.subscriptions[user_id]:
            del self.subscriptions[user_id]
        self._save()
        logging.info("User %s unsubscribed from %s", user_id, symbol)
        return True

    def get_subscriptions(self, user_id: int) -> List[str]:
        """
        Get all subscriptions for a user

        Args:
            user_id: Telegram user/chat ID

        Returns:
            List of subscribed symbols
        """
        return sorted(list(self.subscriptions.get(user_id, set())))

    def get_all_symbols(self) -> Set[str]:
        """
        Get all unique symbols being monitored across all users

        Returns:
            Set of all subscribed symbols
        """
        all_symbols = set()
        for symbols in self.subscriptions.values():
            all_symbols.update(symbols)
        return all_symbols

    def get_subscribers(self, symbol: str) -> List[int]:
        """
        Get all users subscribed to a specific symbol

        Args:
            symbol: Trading pair symbol

        Returns:
            List of user IDs subscribed to the symbol
        """
        symbol = symbol.upper().strip()
        subscribers = []
        for user_id, symbols in self.subscriptions.items():
            if symbol in symbols:
                subscribers.append(user_id)
        return subscribers

    def clear_user(self, user_id: int) -> int:
        """
        Clear all subscriptions for a user

        Args:
            user_id: Telegram user/chat ID

        Returns:
            Number of subscriptions cleared
        """
        if user_id in self.subscriptions:
            count = len(self.subscriptions[user_id])
            del self.subscriptions[user_id]
            self._save()
            logging.info("Cleared %d subscriptions for user %s", count, user_id)
            return count
        return 0
