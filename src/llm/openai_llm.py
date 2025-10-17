#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - openai_llm.py

import json
import logging
import os

from openai import AzureOpenAI, OpenAI
from partial_json_parser import Allow, loads
from tenacity import after, retry, stop_after_attempt, wait_random_exponential

from llm import LLM
from llm.definition import TradingAction


class GPT(LLM):
    def __init__(self):
        prefix, provider = "", os.getenv("OPENAI_PROVIDER", "OpenAI")
        if provider == "Azure":
            prefix = "AZURE_"
        base_url, api_key, model = (
            os.getenv(f"{prefix}OPENAI_BASE_URL"),
            os.getenv(f"{prefix}OPENAI_API_KEY"),
            os.getenv(f"{prefix}OPENAI_MODEL"),
        )

        if provider == "Azure":
            logging.info("使用 Azure OpenAI API")
            self.client = AzureOpenAI(api_key=api_key, api_version="2024-10-01-preview", azure_endpoint=base_url)
        else:
            logging.info("使用 OpenAI API")
            self.client = OpenAI(base_url=base_url, api_key=api_key)

        self.model = model

    @retry(
        wait=wait_random_exponential(min=1, max=30),
        stop=stop_after_attempt(3),
        after=after.after_log(logging.getLogger(__name__), logging.WARNING),
    )
    def __create(self, messages) -> dict:
        # 请求失败，或者没有返回正确的格式
        completion = self.client.chat.completions.create(model=self.model, temperature=0.1, messages=messages)
        content = completion.choices[0].message.content.replace("\n", "")
        return loads(content, Allow.ALL)

    def send(self, symbol: str, indicators: dict) -> TradingAction:
        logging.info("发送数据给 %s %s，分析%s", self.client, self.model, symbol)

        if symbol.endswith("USDT"):
            messages = [
                {"role": "system", "content": self.crypto_system_prompt},
                {"role": "user", "content": f"Token: {symbol}"},
            ]
        else:
            messages = [
                {"role": "system", "content": self.stock_system_prompt},
                {"role": "user", "content": f"stock: {symbol}"},
            ]
        for name, value in indicators.items():
            messages.append({"role": "user", "content": f"interval: {name}, data: {value}"})

        # Debug: log total message size
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        logging.debug("Total prompt size: %d characters, %d messages", total_chars, len(messages))

        try:
            return self.__create(messages)
        except Exception as e:
            logging.error("%s: OpenAI API 请求失败: %s", symbol, e)
            return {
                "action": "N/A",
                "detail": "",
                "take_profit": {"usdt": 0, "percentage": 0},
                "stop_loss": {"usdt": 0, "percentage": 0},
            }
