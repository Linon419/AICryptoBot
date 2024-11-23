#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - __init__.py.py

import os

import telebot

from engine import analyzer


class TelegramBot:
    def __init__(self):
        self.bot = telebot.TeleBot(token=os.getenv("BOT_TOKEN"))

    def send_message(self, message: str):
        self.bot.send_message(chat_id=os.getenv("CHAT_ID"), text=message)

    def __register_handlers(self):
        @self.bot.message_handler(commands=["start"])
        def start(message):
            self.bot.reply_to(
                message, "欢迎来到 AICryptoBot!发送交易对（如BTCUSDT）获取交易建议，多个交易对请用半角逗号隔开。"
            )

        @self.bot.message_handler(chat_id=[260260121, 381599695, 521804980])
        def query_crypto(message):
            pairs = message.text.split(",")
            for pair in pairs:
                self.bot.reply_to(message, analyzer(pair))

    def run(self):
        self.__register_handlers()
        self.bot.polling(non_stop=True)
