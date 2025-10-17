#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - __init__.py.py
import logging
import os

import telebot
from telebot.types import Message

from engine import analyzer
from monitor import EMAMonitor
from subscription_manager import SubscriptionManager


def parse_user_input(text: str) -> tuple[str, list]:
    """
    解析用户输入，支持加密货币和股票查询

    Examples:
        "BTC" -> ("crypto", ["BTCUSDT"])
        "/crypto BTC ETH" -> ("crypto", ["BTCUSDT", "ETHUSDT"])
        "/stock AAPL" -> ("stock", ["AAPL"])

    Args:
        text: 用户输入的文本

    Returns:
        (mode, symbols) - mode为"crypto"或"stock"，symbols为交易对列表
    """
    text = text.strip()

    # 检查是否有命令前缀
    if text.startswith("/crypto"):
        mode = "crypto"
        symbols_str = text.replace("/crypto", "", 1).strip()
    elif text.startswith("/stock"):
        mode = "stock"
        symbols_str = text.replace("/stock", "", 1).strip()
    else:
        # 默认为加密货币
        mode = "crypto"
        symbols_str = text

    # 解析交易对（支持逗号或空格分隔）
    symbols = []
    for s in symbols_str.replace(",", " ").split():
        s = s.strip().upper()
        if s:
            # 如果是加密货币模式且没有USDT后缀，自动添加
            if mode == "crypto" and not s.endswith("USDT"):
                symbols.append(f"{s}USDT")
            else:
                symbols.append(s)

    return mode, symbols


class TelegramBot:

    def __init__(self):
        self.bot = telebot.TeleBot(token=os.getenv("BOT_TOKEN"))
        self.subscription_manager = SubscriptionManager()
        self.monitor = None  # Will be initialized in run()

    def check(self, message: Message):
        users_str = os.getenv("BOT_ALLOW_USER", "")
        groups_str = os.getenv("BOT_ALLOW_GROUP", "")

        users = [int(i.strip()) for i in users_str.split(",") if i.strip()]
        groups = [int(i.strip()) for i in groups_str.split(",") if i.strip()]

        if message.from_user.id in users:
            return True
        if message.chat.id in groups:
            return True
        logging.warning("未授权用户 %s", message.from_user.id)

    def send_message(self, message: str):
        self.bot.send_message(chat_id=os.getenv("CHAT_ID"), text=message)

    def __register_handlers(self):
        @self.bot.message_handler(commands=["start"])
        def start(message):
            self.bot.send_chat_action(message.chat.id, "typing")
            help_text = """欢迎使用 AICryptoBot！

📊 查询命令：
• 直接发送 BTC → 自动分析 BTCUSDT
• 多个币种：BTC ETH SOL
• /crypto BTC → 明确查询加密货币
• /stock AAPL → 查询股票

🔔 订阅命令：
/subscribe BTCUSDT - 订阅EMA排列通知
/unsubscribe BTCUSDT - 取消订阅
/list - 查看订阅列表

💡 提示：默认查询加密货币，股票请使用 /stock 命令"""
            self.bot.reply_to(message, help_text)

        @self.bot.message_handler(commands=["subscribe"])
        def subscribe_handler(message: Message):
            if not self.check(message):
                return

            parts = message.text.split()
            if len(parts) < 2:
                self.bot.reply_to(message, "请提供交易对，如 /subscribe BTCUSDT")
                return

            symbol = parts[1].upper().strip()
            if self.subscription_manager.subscribe(message.chat.id, symbol):
                self.bot.reply_to(
                    message,
                    f"✅ 已订阅 {symbol} 的EMA排列通知\n\n当检测到完美多头或空头排列时会自动通知你。",
                )
            else:
                self.bot.reply_to(message, f"你已经订阅了 {symbol}")

        @self.bot.message_handler(commands=["unsubscribe"])
        def unsubscribe_handler(message: Message):
            if not self.check(message):
                return

            parts = message.text.split()
            if len(parts) < 2:
                self.bot.reply_to(message, "请提供交易对，如 /unsubscribe BTCUSDT")
                return

            symbol = parts[1].upper().strip()
            if self.subscription_manager.unsubscribe(message.chat.id, symbol):
                self.bot.reply_to(message, f"✅ 已取消订阅 {symbol}")
            else:
                self.bot.reply_to(message, f"你没有订阅 {symbol}")

        @self.bot.message_handler(commands=["list"])
        def list_handler(message: Message):
            if not self.check(message):
                return

            subscriptions = self.subscription_manager.get_subscriptions(message.chat.id)
            if subscriptions:
                symbols_text = "\n".join([f"• {symbol}" for symbol in subscriptions])
                self.bot.reply_to(message, f"📋 你的订阅列表：\n\n{symbols_text}")
            else:
                self.bot.reply_to(message, "你还没有订阅任何交易对\n\n使用 /subscribe BTCUSDT 来订阅")

        @self.bot.message_handler(commands=["/query"])
        def group_query(message: Message):
            private_query(message)

        @self.bot.message_handler(commands=["crypto"])
        def crypto_handler(message: Message):
            if not self.check(message):
                return

            parts = message.text.split(maxsplit=1)
            if len(parts) < 2:
                self.bot.reply_to(message, "请提供币种，如 /crypto BTC ETH")
                return

            mode, symbols = parse_user_input(message.text)
            query_symbols(message, symbols, mode)

        @self.bot.message_handler(commands=["stock"])
        def stock_handler(message: Message):
            if not self.check(message):
                return

            parts = message.text.split(maxsplit=1)
            if len(parts) < 2:
                self.bot.reply_to(message, "请提供股票代码，如 /stock AAPL MSFT")
                return

            mode, symbols = parse_user_input(message.text)
            query_symbols(message, symbols, mode)

        @self.bot.message_handler(func=lambda message: self.check(message))
        def private_query(message: Message):
            user_input = message.text.strip()

            # 解析用户输入
            mode, symbols = parse_user_input(user_input)

            if not symbols:
                self.bot.reply_to(message, "请提供交易对，例如：\n• BTC\n• BTC ETH\n• /stock AAPL")
                return

            query_symbols(message, symbols, mode)

        def query_symbols(message: Message, symbols: list, mode: str):
            """查询多个交易对的分析结果"""
            for symbol in symbols:
                self.bot.send_chat_action(message.chat.id, "typing")
                logging.info("%s@%s分析交易：%s (mode=%s)",
                           message.chat.id, message.from_user.id, symbol, mode)
                result = analyzer(symbol)

                text = f"{result}"
                self.bot.reply_to(message, text, disable_web_page_preview=True)

    def run(self):
        self.__register_handlers()
        # Start EMA monitoring service
        self.monitor = EMAMonitor(bot_instance=self)
        self.monitor.start()
        logging.info("Starting Telegram bot with EMA monitoring enabled")
        self.bot.infinity_polling()
