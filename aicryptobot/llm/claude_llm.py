#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - claude_llm.py

import os

import anthropic

from llm import LLM


class Claude(LLM):
    def __init__(self):
        base_url, api_key, model = os.getenv("CLAUDE_BASE_URL"), os.getenv("CLAUDE_API_KEY"), os.getenv("CLAUDE_MODEL")
        self.client = anthropic.Anthropic(base_url=base_url, api_key=api_key)
        self.model = model

    def send(self):
        pass

    def set_system_prompt(self):
        pass
