#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - constant.py

# 数据来源 https://www.binance.com/zh-CN/markets/overview
# Array.from(document.querySelectorAll('.subtitle3.text-t-primary')).map(v=>v.innerText)
all_tokens = {
    "Solana": ["PNUT", "BONK", "WIF", "RENDER", "BOME", "JTO", "ACT", "JUP", "IO", "W", "FIDA", "GMT", "TNSR"],
    "RWA": ["AVAX", "OM", "ICP", "MKR", "POLYX", "PENDLE", "SNX", "LUMIA", "HIFI", "DUSK", "LTO"],
    "meme": ["DOGE", "PEPE", "SHIB", "WIF", "FLOKI", "NEIRO", "DOGS", "TURBO", "MEME", "1000SATS"],
    "payments": ["BTC", "XRP", "BCH", "LTC", "ACH", "UTK", "COTI", "PUNDIX", "XNO"],
    "ai": ["MDT", "NMR", "RLC", "NFP", "PHA", "IQ", "POND", "AI", "IO", "TAO", "ACT", "FET", "WLD"],
    "l1l2": ["ETH", "SOL", "ADA", "BNB", "SUI", "TON", "SEI", "FTM", "EOS", "STRK", "STX", "OM", "TAO"],
    "metaverse": ["FLOKI", "SAND", "MANA", "AXS", "ILV", "VANRY", "MAGIC", "SLP", "BURGER", "ALICE", "MBOX"],
    "lauhchpool": [
        "SUI",
        "ETHFI",
        "ENA",
        "TON",
        "SEI",
        "IO",
        "NOT",
        "DOGS",
        "MEME",
        "BANANA",
        "ALT",
        "HMSTR",
        "PIXEL",
        "OMNI",
        "ACE",
        "REZ",
    ],
    "game": [
        "FLOKI",
        "GALA",
        "NOT",
        "SAND",
        "XAI",
        "MANA",
        "CATI",
        "IMX",
        "HMSTR",
        "YGG",
        "PIXEL",
        "ACE",
        "PORTAL",
        "ILV",
        "BEAMX",
        "ENJ",
    ],
    "defi": [
        "UNI",
        "ETHFI",
        "ENA",
        "RUNE",
        "AAVE",
        "CRV",
        "JTO",
        "JUP",
        "LDO",
        "EIGEN",
        "INJ",
        "RAY",
        "ACA",
        "LUNA",
    ],
    "storage": ["FIL", "STX", "AR", "BTTC", "SC", "STORJ", "HOT", "RIF"],
    "polkadot": ["AKRO", "ATA", "LIT", "PHA", "GLMR", "KSM", "ASTR", "ACA", "DOT"],
}


today_tokens = [
    # 跌幅最大的
    "GRASSUSDT",
    "GOATUSDT",
    "PNUTUSDT",
    "NEIROUSDT",
    "ACTUSDT",
    "TROYUSDT",
    # 涨幅最大的
    "XRPUSDT",
    "XLMUSDT",
    "ADAUSDT",
    "ALGOUSDT",
    "AVAXUSDT",
    "IOTAUSDT",
    "CRVUSDT",
    # 交易量最大的
    "BTCUSDT",
    "ETHUSDT",
    "DOGEUSDT",
    "SOLUSDT",
    "1000PEPEUSDT",
    "LTCUSDT",
    # 个人关注的
    "TONUSDT",
    "SUIUSDT",
    "TRXUSDT",
    "1000SHIBUSDT",
    "OPUSDT",
]
