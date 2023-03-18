import sys
sys.path.append("./live_tools")
import ccxt
import ta
import pandas as pd
from utilities.perp_bitget import PerpBitget
from utilities.custom_indicators import get_n_columns
from utilities.var import ValueAtRisk
from datetime import datetime
import time
import json
import copy

now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("--- Start Execution Time :", current_time, "---")

f = open(
    "./live_tools/secret.json",
)
secret = json.load(f)
f.close()

account_to_select = "bitget_exemple"
production = True
timeframe = "1h"
type = ["long", "short"]
leverage = 1
max_var = 1
max_side_exposition = 1

params_coin = {
    "BTC/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 2.25,
        "long_ma_window": 500
    },
    "AAVE/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "APE/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "APT/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "AVAX/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "AXS/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "C98/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "CRV/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "DOGE/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "DOT/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "DYDX/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "ETH/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "FIL/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "FTM/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "BNB/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "GALA/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "GMT/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "GRT/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "KNC/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "KSM/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 2.25,
        "long_ma_window": 500
    },
    "LRC/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "MANA/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "MASK/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "MATIC/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "NEAR/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "ONE/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "OP/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 2.25,
        "long_ma_window": 500
    },
    "SAND/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "SHIB/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "SOL/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "STG/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "WAVES/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 2.25,
        "long_ma_window": 500
    },
    "YFI/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "WOO/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 1,
        "long_ma_window": 500
    },
    "EGLD/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 2.25,
        "long_ma_window": 500
    },
    "ETC/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 2.25,
        "long_ma_window": 500
    },
    "JASMY/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 2.25,
        "long_ma_window": 500
    },
    "ROSE/USDT:USDT": {
        "wallet_exposure": 0.05,
        "bb_window": 100,
        "bb_std": 2.25,
        "long_ma_window": 500
    },
}

def open_long(row):
    if (
        row['n1_close'] < row['n1_higher_band'] 
        and (row['close'] > row['higher_band']) 
        and (row['close'] > row['long_ma'])
    ):
        return True
    else:
        return False

def close_long(row):
    if (row['close'] < row['ma_band']):
        return True
    else:
        return False

def open_short(row):
    if (
        row['n1_close'] > row['n1_lower_band'] 
        and (row['close'] < row['lower_band']) 
        and (row['close'] < row['long_ma'])        
    ):
        return True
    else:
        return False

def close_short(row):
    if (row['close'] > row['ma_band']):
        return True
    else:
        return False

print(f"--- Bollinger Trend on {len(params_coin)} tokens {timeframe} Leverage x{leverage} ---")

bitget = PerpBitget(
    apiKey=secret[account_to_select]["apiKey"],
    secret=secret[account_to_select]["secret"],
    password=secret[account_to_select]["password"],
)

# Get data
df_list = {}
for pair in params_coin:
    temp_data = bitget.get_more_last_historical_async(pair, timeframe, 1000)
    if len(temp_data) == 990:
        df_list[pair] = temp_data
    else:
        print(f"Pair {pair} not loaded, length: {len(temp_data)}")
print("Data OHLCV loaded 100%")

for pair in df_list:
    df = df_list[pair]
    params = params_coin[pair]
    bol_band = ta.volatility.BollingerBands(close=df["close"], window=params["bb_window"], window_dev=params["bb_std"])
    df["lower_band"] = bol_band.bollinger_lband()
    df["higher_band"] = bol_band.bollinger_hband()
    df["ma_band"] = bol_band.bollinger_mavg()

    df['long_ma'] = ta.trend.sma_indicator(close=df['close'], window=params["long_ma_window"])
    
    df["n1_close"] = df["close"].shift(1)
    df["n1_lower_band"] = df["lower_band"].shift(1)
    df["n1_higher_band"] = df["higher_band"].shift(1)

    df['iloc'] = range(len(df))

print("Indicators loaded 100%")

var = ValueAtRisk(df_list=df_list.copy())
var.update_cov(current_date=df_list["BTC/USDT:USDT"].index[-1], occurance_data=989)
print("Value At Risk loaded 100%")

usd_balance = float(bitget.get_usdt_equity())
print("USD balance :", round(usd_balance, 2), "$")

positions_data = bitget.get_open_position()
position_list = [
    {"pair": d["symbol"], "side": d["side"], "size": float(d["contracts"]) * float(d["contractSize"]), "market_price":d["info"]["marketPrice"], "usd_size": float(d["contracts"]) * float(d["contractSize"]) * float(d["info"]["marketPrice"]), "open_price": d["entryPrice"]}
    for d in positions_data if d["symbol"] in df_list]

positions = {}
for pos in position_list:
    positions[pos["pair"]] = {"side": pos["side"], "size": pos["size"], "market_price": pos["market_price"], "usd_size": pos["usd_size"], "open_price": pos["open_price"]}

print(f"{len(positions)} active positions ({list(positions.keys())})")

# Check for closing positions...
positions_to_delete = []
for pair in positions:
    row = df_list[pair].iloc[-2]
    last_price = float(df_list[pair].iloc[-1]["close"])
    position = positions[pair]

    if position["side"] == "long" and close_long(row):
        close_long_market_price = last_price
        close_long_quantity = float(
            bitget.convert_amount_to_precision(pair, position["size"])
        )
        exchange_close_long_quantity = close_long_quantity * close_long_market_price
        print(
            f"Place Close Long Market Order: {close_long_quantity} {pair[:-5]} at the price of {close_long_market_price}$ ~{round(exchange_close_long_quantity, 2)}$"
        )
        if production:
            bitget.place_market_order(pair, "sell", close_long_quantity, reduce=True)
            positions_to_delete.append(pair)

    elif position["side"] == "short" and close_short(row):
        close_short_market_price = last_price
        close_short_quantity = float(
            bitget.convert_amount_to_precision(pair, position["size"])
        )
        exchange_close_short_quantity = close_short_quantity * close_short_market_price
        print(
            f"Place Close Short Market Order: {close_short_quantity} {pair[:-5]} at the price of {close_short_market_price}$ ~{round(exchange_close_short_quantity, 2)}$"
        )
        if production:
            bitget.place_market_order(pair, "buy", close_short_quantity, reduce=True)
            positions_to_delete.append(pair)

for pair in positions_to_delete:
    del positions[pair]

# Check current VaR risk
positions_exposition = {}
long_exposition = 0
short_exposition = 0
for pair in df_list:
    positions_exposition[pair] = {"long":0, "short":0}

positions_data = bitget.get_open_position()
for pos in positions_data:
    if pos["symbol"] in df_list and pos["side"] == "long":
       pct_exposition = (float(pos["contracts"]) * float(pos["contractSize"]) * float(pos["info"]["marketPrice"])) / usd_balance
       positions_exposition[pos["symbol"]]["long"] += pct_exposition
       long_exposition += pct_exposition
    elif pos["symbol"] in df_list and pos["side"] == "short":
       pct_exposition = (float(pos["contracts"]) * float(pos["contractSize"]) * float(pos["info"]["marketPrice"])) / usd_balance
       positions_exposition[pos["symbol"]]["short"] += pct_exposition
       short_exposition += pct_exposition

current_var = var.get_var(positions=positions_exposition)
print(f"Current VaR rsik 1 period: - {round(current_var, 2)}%, LONG exposition {round(long_exposition * 100, 2)}%, SHORT exposition {round(short_exposition * 100, 2)}%")

for pair in df_list:
    if pair not in positions:
        try:
            row = df_list[pair].iloc[-2]
            last_price = float(df_list[pair].iloc[-1]["close"])
            pct_sizing = params_coin[pair]["wallet_exposure"]
            if open_long(row) and "long" in type:
                long_market_price = float(last_price)
                long_quantity_in_usd = usd_balance * pct_sizing * leverage
                temp_positions = copy.deepcopy(positions_exposition)
                temp_positions[pair]["long"] += (long_quantity_in_usd / usd_balance)
                temp_long_exposition = long_exposition + (long_quantity_in_usd / usd_balance)
                temp_var = var.get_var(positions=temp_positions)
                if temp_var > max_var or temp_long_exposition > max_side_exposition:
                    print(f"Blocked open LONG on {pair}, because next VaR: - {round(current_var, 2)}%")
                else:
                    long_quantity = float(bitget.convert_amount_to_precision(pair, float(
                        bitget.convert_amount_to_precision(pair, long_quantity_in_usd / long_market_price)
                    )))
                    exchange_long_quantity = long_quantity * long_market_price
                    print(
                        f"Place Open Long Market Order: {long_quantity} {pair[:-5]} at the price of {long_market_price}$ ~{round(exchange_long_quantity, 2)}$"
                    )
                    if production:
                        bitget.place_market_order(pair, "buy", long_quantity, reduce=False)
                        positions_exposition[pair]["long"] += (long_quantity_in_usd / usd_balance)
                        long_exposition += (long_quantity_in_usd / usd_balance)

            elif open_short(row) and "short" in type:
                short_market_price = float(last_price)
                short_quantity_in_usd = usd_balance * pct_sizing * leverage
                temp_positions = copy.deepcopy(positions_exposition)
                temp_positions[pair]["short"] += (short_quantity_in_usd / usd_balance)
                temp_short_exposition = short_exposition + (short_quantity_in_usd / usd_balance)
                temp_var = var.get_var(positions=temp_positions)
                if temp_var > max_var or temp_short_exposition > max_side_exposition:
                    print(f"Blocked open SHORT on {pair}, because next VaR: - {round(current_var, 2)}%")
                else:
                    short_quantity = float(bitget.convert_amount_to_precision(pair, float(
                        bitget.convert_amount_to_precision(pair, short_quantity_in_usd / short_market_price)
                    )))
                    exchange_short_quantity = short_quantity * short_market_price
                    print(
                        f"Place Open Short Market Order: {short_quantity} {pair[:-5]} at the price of {short_market_price}$ ~{round(exchange_short_quantity, 2)}$"
                    )
                    if production:
                        bitget.place_market_order(pair, "sell", short_quantity, reduce=False)
                        positions_exposition[pair]["short"] += (short_quantity_in_usd / usd_balance)
                        short_exposition += (short_quantity_in_usd / usd_balance)
              
        except Exception as e:
            print(f"Error on {pair} ({e}), skip {pair}")        


now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("--- End Execution Time :", current_time, "---")

