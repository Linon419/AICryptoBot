#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - openai_llm.py

import os

from openai import OpenAI

from llm import LLM


class GPT(LLM):
    def __init__(self):
        base_url, api_key, model = os.getenv("OPENAI_BASE_URL"), os.getenv("OPENAI_API_KEY"), os.getenv("OPENAI_MODEL")
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def send(self):
        pass

    def set_system_prompt(self):
        pass
