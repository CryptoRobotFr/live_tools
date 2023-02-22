import sys

sys.path.append("./live_tools")
import ccxt
import ta
import pandas as pd
from utilities.spot_binance import SpotBinance
from utilities.custom_indicators import SuperTrend
from datetime import datetime
import time
import json
import requests
f = open(
    "./live_tools/secret.json",
)
secret = json.load(f)
f.close()

timeframe = "1h"
account_to_select = "binance_exemple"

params_coin = {
    "BTCUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 20,
        "long_ema_window": 400
    },
    "ETHUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 5,
        "long_ema_window": 400
    },
    "ADAUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 35,
        "long_ema_window": 400
    },
    "XRPUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 30,
        "long_ema_window": 400
    },
    "BNBUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 30,
        "long_ema_window": 400
    },
    "LINKUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 15,
        "long_ema_window": 400
    },
    "LTCUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 25,
        "long_ema_window": 400
    },
    "SOLUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 40,
        "long_ema_window": 400
    },
    "AVAXUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 35,
        "long_ema_window": 400
    },
    "DOTUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 40,
        "long_ema_window": 400
    },
    "MATICUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 5,
        "long_ema_window": 400
    },
    "NEARUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 5,
        "long_ema_window": 400
    },
    "EGLDUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 5,
        "long_ema_window": 400
    },
    "FTMUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 15,
        "long_ema_window": 400
    },
    "ETCUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 5,
        "long_ema_window": 400
    },
    "EOSUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 35,
        "long_ema_window": 400
    },
    "FILUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 35,
        "long_ema_window": 400
    },
    "SANDUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 20,
        "long_ema_window": 400
    },
    "AXSUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 10,
        "long_ema_window": 400
    },
    "LRCUSDT": {
        "wallet_exposure": 0.05,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 45,
        "long_ema_window": 400
    }
}

binance = SpotBinance(
    apiKey=secret[account_to_select]["apiKey"],
    secret=secret[account_to_select]["secret"],
)

now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("Execution Time :", current_time)

open_order = []

df_list = {}
pair_list = params_coin.keys()
symbol_list = [pair.replace("USDT", "") for pair in pair_list]
print(symbol_list)
for pair in params_coin:
    params = params_coin[pair]
    df = binance.get_last_historical(pair, timeframe, 1000)

    # -- Populate indicators --
    super_trend = SuperTrend(
        df["high"],
        df["low"],
        df["close"],
        params["st_short_atr_window"],
        params["st_short_atr_multiplier"],
    )

    df["super_trend_direction"] = super_trend.super_trend_direction()
    df["ema_short"] = ta.trend.ema_indicator(
        close=df["close"], window=params["short_ema_window"]
    )
    df["ema_long"] = ta.trend.ema_indicator(
        close=df["close"], window=params["long_ema_window"]
    )

    df_list[pair] = df
    
all_balance = binance.get_all_balance()
symbol_balance = {}
usdt_balance = all_balance["USDT"]
usdt_all_balance = usdt_balance
for k in all_balance:
    if k in symbol_list:
        if all_balance[k] > binance.get_min_order_amount(k+"USDT"):
            symbol_balance[k] = binance.convert_amount_to_precision(k+"USDT", all_balance[k])
            usdt_all_balance = usdt_all_balance + symbol_balance[k] * df_list[k+"USDT"].iloc[-1]["close"]
        else:
            symbol_balance[k] = 0
print("symbol_balance", symbol_balance)
print("usdt_all_balance", usdt_all_balance)

for symbol in params_coin:
    try:
        binance.cancel_all_orders(symbol)
    except:
        pass
    
for symbol in symbol_balance:
    pair = symbol + "USDT"
    row = df_list[pair].iloc[-2]
    if symbol_balance[symbol] == 0:
        if row["super_trend_direction"] == True and row["ema_short"] > row["ema_long"]:
            buy_limit_price = binance.convert_price_to_precision(pair, row["ema_short"])
            buy_quantity_in_usd = usdt_all_balance * params_coin[pair]["wallet_exposure"]
            buy_quantity = binance.convert_amount_to_precision(pair, (buy_quantity_in_usd / buy_limit_price))
            print(f"Buy limit on {pair} of {buy_quantity} at the price of {buy_limit_price}$")
            try:
                binance.place_limit_order(pair, "Buy", buy_quantity, buy_limit_price)
            except Exception as e:
                print(f"    Error: {e}")
    elif symbol_balance[symbol] > 0:
        if row["super_trend_direction"] == False or row["ema_short"] < row["ema_long"]:
            sell_limit_price = binance.convert_price_to_precision(pair, row["ema_short"])
            sell_quantity = binance.convert_amount_to_precision(pair, symbol_balance[symbol])
            print(f"Sell limit on {pair} of {sell_quantity} at the price of {sell_limit_price}$")
            try:
                binance.place_limit_order(pair, "Sell", sell_quantity, sell_limit_price)
            except Exception as e:
                print(f"    Error: {e}")

            
