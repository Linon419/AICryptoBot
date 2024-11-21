#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - openai_llm.py

import os

from openai import OpenAI
import logging
import json
from llm import LLM


class GPT(LLM):
    def __init__(self):
        base_url, api_key, model = os.getenv("OPENAI_BASE_URL"), os.getenv("OPENAI_API_KEY"), os.getenv("OPENAI_MODEL")
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def send(self, data_1m, data_5m):
        logging.info("Sending data to OpenAI...")
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": data_1m,
                },
                {
                    "role": "user",
                    "content": data_5m,
                },
            ],
        )

        content = completion.choices[0].message.content
        print(content)
