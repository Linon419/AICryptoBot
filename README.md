# AICryptoBot

> [!CAUTION]
> 本项目仅供学习交流使用。交易有风险，入市需谨慎。若因本项目产生任何损失，概不负责。

# 简介

通过调用加密货币交易所的API接口，获取不同时间周期的K线数据，并计算关键技术指标（如RSI、MACD等）。

结合先进的大语言模型（如 Pixtral、GPT、Claude 等）的强大分析能力，对币种未来的价格走势进行智能预测，为投资决策提供高效的辅助支持。

# 功能演示

## Telegram 机器人模式

![image](/assets/bot.png)

## 脚本模式

会自动用默认浏览器打开分析结果，你也可以在 `output` 目录下找到对应的文件手动查阅

![image](/assets/script.jpg)

## K线数据来源

币安合约

## 支持的LLM

更多模型支持中……

* OpenAI兼容的模型接口，包括 MistralAI、Grok 等

# 使用方式

由于 API 接口成本高昂，因此不提供公开可使用的bot。
> [!NOTE]
> 也许以后有需求会考虑做个网站或者试用bot，但是目前只能自行搭建环境使用。

需要自行配置，推荐使用 Docker 或者手动配置环境的方式。

# 使用 docker 运行

具体可用命令参考下一节

```shell
docker run ghcr.io/bennythink/src
```

# 手动配置环境

## 安装 Python

Python 3.8+，使用 [pdm](https://github.com/pdm-project/pdm)作为包管理器

安装pdm可以参考[官方文档](https://pdm-project.org/zh-cn/latest/)

或者也可以使用 pip 安装

```shell
pip install pdm==2.20.1
```

## 安装 ta-lib

需要安装 `ta-lib` 作为计算技术指标的依赖

### macOS

```shell
brew install ta-lib
```

### Linux

参考 `Dockerfile` 编译并安装 `ta-lib`

## Windows

根据文档安装 `ta-lib`，[参考文档](https://github.com/TA-Lib/ta-lib-python?tab=readme-ov-file#windows)
也可以使用[预编译的版本](https://github.com/cgohlke/talib-build/)

## 安装依赖

克隆本项目之后，切换到工作目录

```shell
git clone https://github.com/BennyThink/AICryptoBot
pdm install
```

## 配置环境变量

根据个人需求，阅读参考配置文件中的注释进行设置。

需要配置 LLM的接口，对于 GPT 接口，推荐使用 [「头顶冒火」的API](https://burn.hair/register?aff=lNgp️)

根据数据时间间隔的不同，每次调用会消耗不等的token数量，默认配置可能会消耗50-90K的 token，约 0.1-0.2 美元。

> [!IMPORTANT]  
> 请根据个人投资策略和需求，自行配置时间间隔，以便最大化节约成本。

```shell
cp .env.example aicryptbot/.env
```

# 使用

支持两种模式，第一种是以 Telegram bot 的形式运行，第二种是脚本方式，默认为脚本模式

```shell
# 脚本模式
python main.py --symbols=ETHUSDT,BTCUSDT
# 机器人模式，之后可以和机器人对话，发送交易对即可
python main.py --mode=bot
```

如果在 Docker 中运行，那么直接接配置好环境变量，然后运行即可

```shell
docker run --env-file .env ghcr.io/bennythink/src --symbols=ETHUSDT,BTCUSDT
docker run --env-file .env ghcr.io/bennythink/src --mode=bot
```

# 代码自动格式化

```shell
black --line-length 120 . && isort --profile black . 
```

# 参考链接

* 币安文档：[https://www.binance.com/zh-CN/binance-api](https://www.binance.com/zh-CN/binance-api)
* 头顶冒火🤯 GPT 接口站：[https://burn.hair/](https://burn.hair/register?aff=lNgp️)
* 头顶冒火🤯 Claude+Mistral+Grok+GPT模型：[https://api.burn.hair/](https://api.burn.hair)

# 赞赏

如果觉得这个项目对你有帮助，可以请我喝杯咖啡

* Stripe： https://buy.stripe.com/dR67vU4p13Ox73a6oq
* Buy Me a Coffee: https://www.buymeacoffee.com/bennythink
* Toncoin: `UQBkXRAUVoEF2AA7QejHpsr3JmBWhsIfQTLURxJ3txc_rVFI`
* USDT-TON: `UQBkXRAUVoEF2AA7QejHpsr3JmBWhsIfQTLURxJ3txc_rVFI`
* USDT-TRC20: `TL8kqCm9SwrV44qLaKvWbwrTtDN3sx5dVP`
* XLM: `GDGGEI35XJ7BQ6K3WLSVVFJA5JWGSIDVT4QAWAYHBG2Y3V3NLP76RC5U`
* TRX:`TF9peZjC2FYjU4xNMPg3uP4caYLJxtXeJS`
* ALGO: `Q3YIDNVGHNWYPPOWJE4K5UVTYGM33ADPNVRKXSTYGWAPAWADJSDZ34N6AA`

# License

MIT
 