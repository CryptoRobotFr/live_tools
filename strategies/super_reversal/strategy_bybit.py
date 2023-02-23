import sys

sys.path.append("./live_tools")
import ccxt
import ta
import pandas as pd
from utilities.spot_bybit import SpotBybit
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
account_to_select = "bybit_exemple"

params_coin = {
    "ETHUSDT": {
        "wallet_exposure": 50,
        "st_short_atr_window": 7,
        "st_short_atr_multiplier": 4,
        "short_ema_window": 49,
        "long_ema_window": 250
    },
    "BCHUSDT": {
        "wallet_exposure": 25,
        "st_short_atr_window": 17,
        "st_short_atr_multiplier": 25,
        "short_ema_window": 46,
        "long_ema_window": 380
    },
    "YFIUSDT": {
        "wallet_exposure": 25,
        "st_short_atr_window": 18,
        "st_short_atr_multiplier": 4,
        "short_ema_window": 49,
        "long_ema_window": 240
    },
}

bybit = SpotBybit(
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
    df = bybit.get_last_historical(pair, timeframe, 1000)

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
all_balance = bybit.get_all_balance()
print(all_balance)
symbol_balance = {}
usdt_balance = all_balance["USDT"]
usdt_all_balance = usdt_balance
for k in all_balance:
    if k in symbol_list:
        if all_balance[k] > bybit.get_min_order_amount(k+"USDT"):
            symbol_balance[k] = bybit.convert_amount_to_precision(k+"USDT", all_balance[k])
            usdt_all_balance = usdt_all_balance + symbol_balance[k] * df_list[k+"USDT"].iloc[-1]["close"]
        else:
            symbol_balance[k] = 0
            
for k in symbol_list:
    if k not in all_balance:
        symbol_balance[k] = 0
print("symbol_balance", symbol_balance)
print("usdt_all_balance", usdt_all_balance)

for symbol in params_coin:
    try:
        bybit.cancel_all_orders(symbol)
    except:
        pass
    
for symbol in symbol_balance:
    pair = symbol + "USDT"
    print(pair)
    row = df_list[pair].iloc[-1]
    if symbol_balance[symbol] == 0:
        if row["super_trend_direction"] == True and row["ema_short"] > row["ema_long"]:
            buy_limit_price = bybit.convert_price_to_precision(pair, row["ema_short"])
            buy_quantity_in_usd = usdt_all_balance * params_coin[pair]["wallet_exposure"]
            buy_quantity = bybit.convert_amount_to_precision(pair, (buy_quantity_in_usd / buy_limit_price))
            print(f"Buy limit on {pair} of {buy_quantity} at the price of {buy_limit_price}$")
            try:
                bybit.place_limit_order(pair, "Buy", buy_quantity, buy_limit_price)
            except Exception as e:
                print(f"    Error: {e}")
    elif symbol_balance[symbol] > 0:
        if row["super_trend_direction"] == False or row["ema_short"] < row["ema_long"]:
            sell_limit_price = bybit.convert_price_to_precision(pair, row["ema_short"])
            sell_quantity = bybit.convert_amount_to_precision(pair, symbol_balance[symbol])
            print(f"Sell limit on {pair} of {sell_quantity} at the price of {sell_limit_price}$")
            try:
                bybit.place_limit_order(pair, "Sell", sell_quantity, sell_limit_price)
            except Exception as e:
                print(f"    Error: {e}")

            
