#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - openai_llm.py

import json
import logging
import os
import time

from openai import AzureOpenAI, OpenAI

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

    def send(self, symbol: str, indicators: list, current: str) -> TradingAction:
        logging.info("发送数据给 %s %s", self.client, self.model)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Token to analyze: {symbol}"},
        ]
        for indicator in indicators:
            messages.append({"role": "user", "content": indicator})
        if current:
            logging.info("已有持仓，添加额外信息中...")
            messages.append({"role": "user", "content": f"My current holdings: {current}"})
        completion = self.client.chat.completions.create(model=self.model, temperature=0.1, messages=messages)
        return json.loads(completion.choices[0].message.content)
