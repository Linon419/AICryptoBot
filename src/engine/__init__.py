#!/usr/bin/env python3
# coding: utf-8

import logging
import os
import webbrowser
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from datasource.binance_api import BinanceAPI
from datasource.stock import StockAPI
from llm.openai_llm import GPT


def show(df: pd.DataFrame):
    print(df.to_string())
    table = df.to_html(index=False)

    cur_dir = Path(__file__).parent
    now = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    output = Path(__file__).parent.parent.joinpath("output")
    output.mkdir(exist_ok=True)

    env = Environment(loader=FileSystemLoader(cur_dir))
    template = env.get_template("template.html")
    html = template.render(now=now, table=table)
    html_path = output.joinpath(f"analysis_{now}.html")
    html_path.write_text(html, encoding="u8")
    webbrowser.open(html_path.absolute().as_uri(), new=0, autoraise=True)


def get_indicators(symbol, interval, count):
    if symbol.endswith("USDT"):
        return BinanceAPI(symbol, interval, count=int(count)).get_all_indicators()
    else:
        return StockAPI(symbol, interval, count=int(count)).get_all_indicators()


def format_recommendation(recommendation: dict) -> str:
    """格式化单个交易建议为美观的文本输出"""
    symbol = recommendation.get("symbol", "N/A")
    action = recommendation.get("action", "N/A")
    detail = recommendation.get("detail", "")
    take_profit = recommendation.get("take_profit", {})
    stop_loss = recommendation.get("stop_loss", {})

    # 确定动作图标和文本
    action_emoji = {
        "long": "🟢",
        "short": "🔴",
        "hold": "🟡",
        "close": "⚫"
    }
    action_text = {
        "long": "做多 (LONG)",
        "short": "做空 (SHORT)",
        "hold": "观望 (HOLD)",
        "close": "平仓 (CLOSE)"
    }

    emoji = action_emoji.get(action.lower(), "⚪")
    action_label = action_text.get(action.lower(), action.upper())

    # 判断是加密货币还是股票，决定使用的货币单位
    is_crypto = symbol.endswith("USDT")
    currency_key = "usdt" if is_crypto else "usd"
    currency_label = "USDT" if is_crypto else "USD"

    # 获取价格数据（优先使用正确的key，如果不存在则尝试另一个）
    # 处理 None 值，转换为 0
    tp_price = take_profit.get(currency_key, take_profit.get("usdt", take_profit.get("usd", 0)))
    tp_price = tp_price if tp_price is not None else 0
    tp_pct = take_profit.get("percentage", 0)
    tp_pct = tp_pct if tp_pct is not None else 0
    sl_price = stop_loss.get(currency_key, stop_loss.get("usdt", stop_loss.get("usd", 0)))
    sl_price = sl_price if sl_price is not None else 0
    sl_pct = stop_loss.get("percentage", 0)
    sl_pct = sl_pct if sl_pct is not None else 0

    # 构建格式化输出
    output = f"""
━━━━━━━━━━━━━━━━━━━━
{emoji} {symbol} - {action_label}
━━━━━━━━━━━━━━━━━━━━

📊 市场分析：
{detail}

━━━━━━━━━━━━━━━━━━━━
💰 交易参数：

🎯 止盈目标 (Take Profit)
   • 价格: ${tp_price:,.2f} {currency_label}
   • 涨幅: {tp_pct:+.2f}%

🛡️ 止损位置 (Stop Loss)
   • 价格: ${sl_price:,.2f} {currency_label}
   • 跌幅: {sl_pct:+.2f}%
━━━━━━━━━━━━━━━━━━━━
"""
    return output.strip()


def analyzer(symbols: list | str) -> str:
    gpt = GPT()
    data = []
    formatted_outputs = []

    if isinstance(symbols, str):
        symbols = [symbols]

    for symbol in symbols:
        symbol = symbol.upper()
        # 多周期分析：1d=10日线大趋势，4h=20趋势背景，1h=30核心周期，15m=40短期确认，5m=50精确入场
        if symbol.endswith("USDT"):
            interval = os.getenv("BINANCE_INTERVAL", "1d=10,4h=20,1h=30,15m=40,5m=50")
        else:
            interval = os.getenv("STOCK_INTERVAL", "1d=50,5d=40,1wk=30,1mo=20")

        indicators = {}
        for item in interval.split(","):
            interval, count = item.split("=")
            indicators[interval] = get_indicators(symbol, interval, count)

        logging.info("采集数据密度：%s", indicators.keys())
        recommendation = gpt.send(symbol, indicators)
        action, detail = recommendation["action"], recommendation["detail"]

        if action == "long":
            logging.info("GPT 推荐做多 %s，详情：%s", symbol, detail)
            # account.new_order("BUY", usdt)
        elif action == "short":
            logging.info("GPT 推荐做空 %s，详情：%s", symbol, detail)
            # account.new_order("SELL", usdt)
        elif action == "hold":
            logging.info("GPT 推荐持有 %s，详情：%s", symbol, detail)
        elif action == "close":
            logging.warning("[TODO]GPT 推荐平仓 %s，详情：%s", symbol, detail)
        else:
            logging.error("无法识别的操作：%s", action)

        item = {"symbol": symbol}
        item.update(recommendation)
        data.append(item)

        # 添加格式化输出
        formatted_outputs.append(format_recommendation(item))

    df = pd.DataFrame(data)
    show(df)

    # 返回格式化的文本，多个交易对用双换行分隔
    return "\n\n".join(formatted_outputs)
