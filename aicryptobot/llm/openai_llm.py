#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - openai_llm.py

import json
import logging
import os

from openai import OpenAI

from llm import LLM
from llm.definition import TradingAction


class GPT(LLM):
    def __init__(self):
        base_url, api_key, model = os.getenv("OPENAI_BASE_URL"), os.getenv("OPENAI_API_KEY"), os.getenv("OPENAI_MODEL")
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def send(self, indicators: list, current: str) -> TradingAction:
        logging.info("发送数据给 OpenAI %s", self.model)
        messages = [{"role": "system", "content": self.system_prompt}]
        for indicator in indicators:
            messages.append({"role": "system", "content": indicator})
        if current:
            logging.info("已有持仓，添加额外信息中...")
            messages.append({"role": "user", "content": f"My current holdings: {current}"})
        completion = self.client.chat.completions.create(model="gpt-4o", temperature=0.1, messages=messages)
        return json.loads(completion.choices[0].message.content)
