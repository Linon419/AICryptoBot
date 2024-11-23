#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - __init__.py.py

import os

import telebot


class TelegramBot:
    def __init__(self):
        self.bot = telebot.TeleBot(token=os.getenv("BOT_TOKEN"))

    def send(self, message: str):
        self.bot.send_message(chat_id=os.getenv("CHAT_ID"), text=message)

    def handlers(self):
        @self.bot.message_handler(commands=["start"])
        def start(message):
            self.bot.reply_to(message, "欢迎来到 AICryptoBot!发送交易对（如BTCUSDT）获取交易建议")

        @self.bot.message_handler(chat_id=[260260121, 381599695, 521804980])
        def query_crypto(message):
            self.bot.reply_to()

    def run(self):
        self.bot.polling(non_stop=True)
