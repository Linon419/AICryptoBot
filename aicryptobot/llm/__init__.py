#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - __init__.py.py


from abc import ABC, abstractmethod


class LLM(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def set_system_prompt(self):
        pass

    @abstractmethod
    def send(self):
        pass
