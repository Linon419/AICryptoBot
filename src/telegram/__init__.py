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


class TelegramBot:

    def __init__(self):
        self.bot = telebot.TeleBot(token=os.getenv("BOT_TOKEN"))
        self.subscription_manager = SubscriptionManager()
        self.monitor = None  # Will be initialized in run()

    def check(self, message: Message):
        users = [int(i) for i in os.getenv("BOT_ALLOW_USER").split(",")]
        groups = [int(i) for i in os.getenv("BOT_ALLOW_GROUP").split(",")]

        if message.from_user.id in users:
            return True
        if message.chat.id in groups:
            return True
        logging.warning("未授权用户")

    def send_message(self, message: str):
        self.bot.send_message(chat_id=os.getenv("CHAT_ID"), text=message)

    def __register_handlers(self):
        @self.bot.message_handler(commands=["start"])
        def start(message):
            self.bot.send_chat_action(message.chat.id, "typing")
            help_text = """欢迎使用 AICryptoBot！

命令列表：
/start - 显示此帮助信息
/query - 分析交易对（如 /query BTCUSDT）
/subscribe - 订阅交易对的EMA排列通知（如 /subscribe BTCUSDT）
/unsubscribe - 取消订阅（如 /unsubscribe BTCUSDT）
/list - 查看我的订阅列表

直接发送交易对（如BTCUSDT）也可以获取建议，多个交易对请用半角逗号隔开。"""
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

        @self.bot.message_handler(func=lambda message: self.check(message))
        def private_query(message: Message):
            user_input = message.text.split()[-1].strip()
            if "/query@" in user_input:
                self.bot.reply_to(message, "请提供交易对，如 `/query@burn_cryptobot btcusdt`", parse_mode="markdown")
                return

            pairs = user_input.split(",")
            for pair in pairs:
                self.bot.send_chat_action(message.chat.id, "typing")
                pair = pair.upper()
                logging.info("%s@%s分析交易：%s...", message.chat.id, message.from_user.id, pair)
                result = analyzer(pair)
                text = f"{result}\nhttps://www.binance.com/zh-CN/futures/{pair}\n\n开源：https://github.com/BennyThink/AICryptoBot"
                self.bot.reply_to(message, text, disable_web_page_preview=True)

    def run(self):
        self.__register_handlers()
        # Start EMA monitoring service
        self.monitor = EMAMonitor(bot_instance=self)
        self.monitor.start()
        logging.info("Starting Telegram bot with EMA monitoring enabled")
        self.bot.infinity_polling()
