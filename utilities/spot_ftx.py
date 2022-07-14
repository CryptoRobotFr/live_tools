import ccxt
import pandas as pd
import time

class SpotFtx():
    def __init__(self, apiKey=None, secret=None, subAccountName=None):
        ftxAuthObject = {
            "apiKey": apiKey,
            "secret": secret,
            'headers': {
                'FTX-SUBACCOUNT': subAccountName
            }
        }
        if ftxAuthObject['secret'] == None:
            self._auth = False
            self._session = ccxt.ftx()
        else:
            self._auth = True
            self._session = ccxt.ftx(ftxAuthObject)
        self.market = self._session.load_markets()

    def authentication_required(fn):
        """Annotation for methods that require auth."""
        def wrapped(self, *args, **kwargs):
            if not self._auth:
                print("You must be authenticated to use this method", fn)
                exit()
            else:
                return fn(self, *args, **kwargs)
        return wrapped

    def get_historical_since(self, symbol, timeframe, startDate):
        try:
            tempData = self._session.fetch_ohlcv(symbol, timeframe, int(
                time.time()*1000)-1209600000, limit=1000)
            dtemp = pd.DataFrame(tempData)
            timeInter = int(dtemp.iloc[-1][0] - dtemp.iloc[-2][0])
        except:
            return None

        finished = False
        start = False
        allDf = []
        startDate = self._session.parse8601(startDate)
        while(start == False):
            try:
                tempData = self._session.fetch_ohlcv(
                    symbol, timeframe, startDate, limit=1000)
                dtemp = pd.DataFrame(tempData)
                timeInter = int(dtemp.iloc[-1][0] - dtemp.iloc[-2][0])
                nextTime = int(dtemp.iloc[-1][0] + timeInter)
                allDf.append(dtemp)
                start = True
            except:
                startDate = startDate + 1209600000*2

        if dtemp.shape[0] < 1:
            finished = True
        while(finished == False):
            try:
                tempData = self._session.fetch_ohlcv(
                    symbol, timeframe, nextTime, limit=1000)
                dtemp = pd.DataFrame(tempData)
                nextTime = int(dtemp.iloc[-1][0] + timeInter)
                allDf.append(dtemp)
                # print(dtemp.iloc[-1][0])
                if dtemp.shape[0] < 1:
                    finished = True
            except:
                finished = True
        result = pd.concat(allDf, ignore_index=True, sort=False)
        result = result.rename(
            columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
        result = result.set_index(result['timestamp'])
        result.index = pd.to_datetime(result.index, unit='ms')
        del result['timestamp']
        return result

    def get_last_historical(self, symbol, timeframe, limit):
        result = pd.DataFrame(data=self._session.fetch_ohlcv(
            symbol, timeframe, None, limit=limit))
        result = result.rename(
            columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
        result = result.set_index(result['timestamp'])
        result.index = pd.to_datetime(result.index, unit='ms')
        del result['timestamp']
        return result

    def get_bid_ask_price(self, symbol):
        try:
            ticker = self._session.fetchTicker(symbol)
        except BaseException as err:
            print("An error occured", err)
            exit()
        return {"bid":ticker["bid"],"ask":ticker["ask"]}

    def get_min_order_amount(self, symbol):
        return self._session.markets_by_id[symbol]["info"]["minProvideSize"]

    def convert_amount_to_precision(self, symbol, amount):
        return self._session.amount_to_precision(symbol, amount)

    def convert_price_to_precision(self, symbol, price):
        return self._session.price_to_precision(symbol, price)

    @authentication_required
    def get_all_balance(self):
        try:
            allBalance = self._session.fetchBalance()
        except BaseException as err:
            print("An error occured", err)
            exit()
        return allBalance['total']

    @authentication_required
    def get_all_balance_in_usd(self):
        try:
            allBalance = {}
            allBalance = self._session.fetchBalance()
            allBalance = allBalance['total']
            return_balance = {}
            for coin in allBalance.copy():
                try:
                    if allBalance[coin] > 0:
                        if coin != "USD":
                            return_balance[coin] = float(allBalance[coin]) * float(self.market[coin+'/USD']['info']['last'])
                        else:
                            return_balance[coin] = float(allBalance[coin])
                except:
                    pass
                    print("Cannot get price of",coin+'/USD')
        except BaseException as err:
            print("An error occured", err)
            exit()
        return return_balance

    @authentication_required
    def get_balance_of_one_coin(self, coin):
        try:
            allBalance = self._session.fetchBalance()
        except BaseException as err:
            print("An error occured", err)
            exit()
        try:
            return allBalance['total'][coin]
        except:
            return 0

    @authentication_required
    def get_detail_balance_of_one_coin(self, coin):
        try:
            allBalance = self._session.fetchBalance()
        except BaseException as err:
            print("An error occured", err)
            exit()
        try:
            return allBalance[coin]
        except:
            return 0

    @authentication_required
    def place_market_order(self, symbol, side, amount):
        try:
            return self._session.createOrder(
                symbol, 
                'market', 
                side, 
                self.convert_amount_to_precision(symbol, amount),
                None
            )
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def place_limit_order(self, symbol, side, amount, price):
        try:
            return self._session.createOrder(
                symbol, 
                'limit', 
                side, 
                self.convert_amount_to_precision(symbol, amount), 
                self.convert_price_to_precision(symbol, price)
                )
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def place_market_stop_loss(self, symbol, amount, price):
        params = {
        'stopPrice': self.convert_price_to_precision(symbol, price),  # your stop price
        }
        try:
            return self._session.createOrder(
                symbol, 
                'stop', 
                'sell', 
                self.convert_amount_to_precision(symbol, amount), 
                None,
                params
                )
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def cancel_all_open_order(self, symbol):
        try:
            return self._session.cancel_all_orders(symbol)
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def cancel_order_by_id(self, id):
        try:
            return self._session.cancel_order(id)
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def get_open_order(self):
        try:
            return self._session.fetchOpenOrders()
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def get_open_stop_order(self):
        params = {
            'type':'stop'
        }
        try:
            return self._session.fetchOpenOrders(None,None,None,params)
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def get_my_trades(self, symbol=None, since=None, limit=1):
        try:
            return self._session.fetch_my_trades(symbol, since, limit)
        except BaseException as err:
            print("An error occured", err)
            exit()
