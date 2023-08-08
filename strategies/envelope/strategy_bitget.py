import sys
sys.path.append("./live_tools")
import ccxt
import ta
from utilities.perp_bitget import PerpBitget
import pandas as pd
import json

account_to_select = "bitget_exemple"
production = True

pair = "BTC/USDT:USDT"
leverage = 1
type=["long", "short"]
base_window = 5
envelopes = [0.07, 0.10, 0.12]
src="close"

f = open(
    "./live_tools/secret.json",
)
secret = json.load(f)
f.close()


bitget = PerpBitget(
    apiKey=secret[account_to_select]["apiKey"],
    secret=secret[account_to_select]["secret"],
    password=secret[account_to_select]["password"],
)

candles = bitget.get_last_historical(pair, "1h", 100)
df = pd.DataFrame(candles)

high_envelopes = [round(1/(1-e)-1, 3) for e in envelopes]
if src == "close":
    src = df["close"]
elif src == "ohlc4":
    src = (df["close"] + df["high"] + df["low"] + df["open"]) / 4

df['ma_base'] = ta.trend.sma_indicator(close=df['close'], window=base_window).shift(1)
for i in range(1, len(envelopes) + 1):
    df[f'ma_high_{i}'] = df['ma_base'] * (1 + high_envelopes[i-1])
    df[f'ma_low_{i}'] = df['ma_base'] * (1 - envelopes[i-1])

balance = float(bitget.get_usdt_equity())
balance = balance * leverage
print(f"Balance: {round(balance, 2)} $", )

buy_orders = []
sell_orders = []
orders = bitget.get_open_order(pair)
oder_ids_to_cancel = []
for order in orders:
    oder_ids_to_cancel.append(order["id"])
    if order["side"] == "buy" and order["info"]["reduceOnly"] == False:
        buy_orders.append(order)
    elif order["side"] == "sell" and order["info"]["reduceOnly"] == False:
        sell_orders.append(order)

if len(oder_ids_to_cancel) > 0:
    bitget.cancel_order_ids(ids=oder_ids_to_cancel, symbol=pair)

positions = bitget.get_open_position(pair)
for position in positions:
    if position["side"] == "long":
        print(f"Place close long limit order of {position['contracts'] * position['contractSize']} {pair} {round(df.iloc[-1]['ma_base'], 2)} $")
        bitget.place_limit_order(
            symbol=pair,
            side="sell",
            amount=position["contracts"] * position["contractSize"],
            price=(df.iloc[-1]['ma_base']),
            reduce=True,
        )
    elif position["side"] == "short":
        print(f"Place close short limit order of {position['contracts'] * position['contractSize']} {pair} {round(df.iloc[-1]['ma_base'], 2)} $")
        bitget.place_limit_order(
            symbol=pair,
            side="buy",
            amount=position["contracts"] * position["contractSize"],
            price=df.iloc[-1]["ma_base"],
            reduce=True,
        )

positions = bitget.get_open_position(pair)
# orders
if len(positions) > 0:
    first_buy_envelope = len(envelopes) - len(buy_orders)
    for i in range(first_buy_envelope, len(envelopes)):
        price = df.iloc[-2][f"ma_low_{i+1}"]
        amount = (balance / len(envelopes)) / price
        print(f"Place buy order (envelope {i+1}) of {amount} {pair} at price {round(price, 2)} $")
        bitget.place_limit_order(
            symbol=pair,
            side="buy",
            amount=amount,
            price=price,
            reduce=False,
        )

    first_sell_envelope = len(envelopes) - len(sell_orders)
    for i in range(first_sell_envelope, len(envelopes)):
        price = df.iloc[-2][f"ma_high_{i+1}"]
        amount = (balance / len(envelopes)) / price
        print(f"Place sell order (envelope {i+1}) of {amount} {pair} at price {round(price, 2)} $")
        bitget.place_limit_order(
            symbol=pair,
            side="sell",
            amount=amount,
            price=price,
            reduce=False,
        )

else:
    for i in range(len(envelopes)):
        price = df.iloc[-2][f"ma_high_{i+1}"]
        amount = (balance / len(envelopes)) / price
        print(f"Place sell order (envelope {i+1}) of {amount} {pair} at price {round(price, 2)} $")
        bitget.place_limit_order(
            symbol=pair,
            side="sell",
            amount=amount,
            price=price,
            reduce=False,
        )

    for i in range(len(envelopes)):
        price = df.iloc[-2][f"ma_low_{i+1}"]
        amount = (balance / len(envelopes)) / price
        print(f"Place buy order (envelope {i+1}) of {amount} {pair} at price {round(price, 2)} $")
        bitget.place_limit_order(
            symbol=pair,
            side="buy",
            amount=amount,
            price=price,
            reduce=False,
        )