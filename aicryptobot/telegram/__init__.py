#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - __init__.py.py
import logging
import os

import telebot
from telebot.types import Message

from engine import analyzer


class TelegramBot:

    def __init__(self):
        self.bot = telebot.TeleBot(token=os.getenv("BOT_TOKEN"))

    def check(self, message: Message):
        users = [260260121, 381599695, 521804980, 91024550, 716648345]
        groups = [-1001886218691]

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
            self.bot.reply_to(message, "发送交易对（如BTCUSDT）获取建议，多个交易对请用半角逗号隔开。")

        @self.bot.message_handler(commands=["/query"])
        def group_query(message: Message):
            self.private_query(message)

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
                gh = "https://github.com/BennyThink/AICryptoBot"
                text = f"{result}\nhttps://www.binance.com/zh-CN/futures/{pair}\n\n欢迎加入贡献：{gh}"
                self.bot.reply_to(message, text, disable_web_page_preview=True)

    def run(self):
        self.__register_handlers()
        self.bot.infinity_polling()
