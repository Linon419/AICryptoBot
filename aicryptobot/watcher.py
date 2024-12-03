#!/usr/bin/env python3
# coding: utf-8

import logging
import os
import random
import time
from hashlib import sha1

import redis
import requests
import telebot
from bs4 import BeautifulSoup
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()


class Updater:
    def __init__(self):
        self.url = "https://www.binance.com/zh-CN/square/profile/Ultra-short-contract-trader"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        }
        self.redis = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
        self.bot = telebot.TeleBot(token=os.getenv("BOT_TOKEN"))

    def __get_latest_post(self):
        logging.info("Fetching latest post...")
        response = requests.get(self.url, headers=self.headers)
        content = response.text
        soup = BeautifulSoup(content, "html.parser")
        latest = soup.find(
            "div",
            class_="FeedBuzzBaseView_FeedBuzzBaseViewRootBox__1fzEU FeedBuzzBaseViewRootBox feed-card is-card css-15owl46",
        )

        return latest.text

    @staticmethod
    def __calculate_hash(content: str):
        return sha1(content.encode()).hexdigest()

    def __has_update(self):
        latest = self.__get_latest_post()
        latest_hash = self.__calculate_hash(str(latest))
        self.redis.ping()

        if self.redis.get("latest_hash") != latest_hash:
            self.redis.set("latest_hash", latest_hash)
            return latest
        return False

    def send_notification(self):
        jitter = random.uniform(0, 10)
        time.sleep(jitter)
        if content := self.__has_update():
            logging.info("New post found!")
            self.bot.send_message(260260121, content)
            print(content)
        else:
            logging.warning("No new post found.")


if __name__ == "__main__":
    updater = Updater()
    updater.send_notification()
