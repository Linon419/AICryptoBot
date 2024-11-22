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
