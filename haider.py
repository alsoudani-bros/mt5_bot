import random
import pprint
import pytz
import datetime
import MetaTrader5 as mt5
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import dotenv_values
import repeater
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

config = dotenv_values(".env")

# login = config.get("MT_LOGIN")
# password = config.get("MT_PASSWORD")
login = config.get("CHALLANGE_MT_LOGIN")
password = config.get("CHALLANGE_MT_PASSWORD")

# connect to MetaTrader 5
# if not mt5.initialize(login=int(login), server="MetaQuotes-Demo", password=password):
#     print("initialize() failed")
#     mt5.shutdown()
if not mt5.initialize(login=int(login), server="FTMO-Server", password=password):
    print("initialize() failed")
    mt5.shutdown()


def get_equity():
    equity = mt5.account_info().equity
    print(f"Current equity is: {equity}$")
    return equity


def get_balance():
    balance = mt5.account_info().balance
    print(f"Current Balance is: {balance}$")
    return balance


def get_account_name():
    name = mt5.account_info().name
    print(f" The name of the current connected account is: {name}")
    return name


def get_profit():
    profit = mt5.account_info().profit
    print(f"Total profits are: {profit}$")
    return profit


def get_margin_free():
    margin_free = mt5.account_info().margin_free
    print(f"The available margin for trading is: {margin_free}$")
    return margin_free


def get_available_symbols():
    available_symbols = []
    symbols = mt5.symbols_get()
    print("The available symbols are")
    for s in symbols:
        print(s.name)
        available_symbols.append(s.name)
    return available_symbols


def get_symbol_info(symbol):
    # symbol = symbol.upper()
    symbol_info = mt5.symbol_info(symbol)
    name = symbol_info.name
    spread = symbol_info.spread
    pip_size = symbol_info.trade_tick_size * 10
    contract_size = symbol_info.trade_contract_size
    tick_value = symbol_info.trade_tick_value
    print(tick_value)
    print(
        f"Name: {name}\nSpread: {spread}\nPip Size: {pip_size}\nContract Size: {contract_size}")
    return name, spread, pip_size, contract_size


def get_open_positions():
    positions_total = mt5.positions_total()
    positions = mt5.positions_get()
    print(f"Total open positions: {positions_total} positions")
    for position in positions:
        print(f"Position Ticket: {position.ticket}\nPosition time: {position.time}\nPosition magic: {position.magic}\nPosition symbol: {position.symbol}\nPosition Volume: {position.volume}\nPosition entry price: {position.price_open}\nPosition stop loss price: {position.sl}\nPosition take profit price: {position.tp}")
    return positions


def get_open_orders():
    orders_total = mt5.orders_total()
    orders = mt5.orders_get()
    print(f"Total open orders: {orders_total} orders")
    for order in orders:
        print(f"Order Ticket: {order.ticket}\nOrder time: {order.time_setup}\nOrder magic: {order.magic}\nOrder symbol: {order.symbol}\nOrder Volume: {order.volume_current}\nOrder entry price: {order.price_open}\nOrder stop loss price: {order.sl}\nOrder take profit price: {order.tp}")
    return orders


def check_connection():
    account_info = mt5.terminal_info()
    status = account_info.connected
    internet_connection = account_info.ping_last/1000
    number_of_available_symbols = mt5.symbols_total()
    if status:
        print(
            f'You have established connection with the Metatrader5 terminal \nThe Ping is {round(internet_connection)} ms \nThe total available symbols for trading are {number_of_available_symbols}')
        return status, internet_connection
    else:
        print("No connection with the Metatrader5 terminal")
        return status


def send_market_order(symbol, direction, stop_loss_price, risk_reward_ratio, risk_percent):
    market_price = mt5.symbol_info_tick(symbol).ask
    random_id = random.randint(100000000, 999999999)
    money_to_risk = get_balance() * risk_percent/100
    distance_from_stop_loss = abs(market_price - stop_loss_price)
    distance_from_take_profit = distance_from_stop_loss * risk_reward_ratio
    if symbol == "US100.cash":
        lot_size = round(money_to_risk/distance_from_stop_loss, 2)
    elif symbol == "AUXUSD":
        lot_size = round(money_to_risk/(distance_from_stop_loss * 100), 2)
    deviation = 100
    if direction == "long":
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(symbol).ask,
            "sl": stop_loss_price,
            "tp": round(market_price + distance_from_take_profit, 2),
            "deviation": deviation,
            "magic": random_id,
            "comment": "python script open position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }
    elif direction == "short":
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(symbol).bid,
            "sl": stop_loss_price,
            "tp": round(market_price - distance_from_take_profit, 2),
            "deviation": deviation,
            "magic": random_id,
            "comment": "python script open position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }

    result = mt5.order_send(request)
    if result.retcode == 10009:
        now = datetime.now()
        print(f"{result.comment}\nOrder number: {result.order}\nSymbol: {symbol}\nVolume: {result.volume}\nEntry Price: {result.price}\nTime Of Excution: {now}")
    else:
        print(
            f"There was an error sending the request\nThe error code: {result.retcode}\nThe request was:\n{request}\nTime Of Request: {now}")


def send_limit_order(symbol, direction, entry_price, stop_loss_price, risk_reward_ratio, risk_percent):
    random_id = random.randint(100000000, 999999999)
    money_to_risk = get_balance() * risk_percent/100
    distance_from_stop_loss = abs(entry_price - stop_loss_price)
    distance_from_take_profit = distance_from_stop_loss * risk_reward_ratio
    if symbol == "US100.cash":
        lot_size = round(money_to_risk/distance_from_stop_loss, 2)
    elif symbol == "AUXUSD":
        lot_size = round(money_to_risk/(distance_from_stop_loss * 100), 2)
    deviation = 100
    if direction == "long":
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "price": entry_price,
            "sl": stop_loss_price,
            "tp": round(entry_price + distance_from_take_profit, 2),
            "deviation": deviation,
            "magic": random_id,
            "comment": "python script open ",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }
    elif direction == "short":
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL_LIMIT,
            "price": entry_price,
            "sl": stop_loss_price,
            "tp": round(entry_price - distance_from_take_profit, 2),
            "deviation": deviation,
            "magic": random_id,
            "comment": "python script open position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }
    result = mt5.order_send(request)
    if result.retcode == 10009:
        now = datetime.now()
        print(f"{result.comment}\nOrder number: {result.order}\nSymbol: {symbol}\nVolume: {result.volume}\nEntry Price: {result.price}\nTime Of Excution: {now}")
    else:
        print(
            f"There was an error sending the request\nThe error code: {result.retcode}\nThe request was:\n{request}\nTime Of Request: {now}")


# long position:  money willing to lose per trade / (entry price - stop price) * contract size
# short position:  money willing to lose per trade / (stop price - entry price) * contract size
# get_account_name()
# get_equity()
# get_balance()
# get_profit()
# get_margin_free()
# check_connection()
# get_available_symbols()
# get_symbol_info('US100.cash')
# send_order(symbol, direction, type, entry_price, stop_loss_price, risk_reward_ratio, risk_percent)
# get_open_positions()
# get_open_orders()
# open_positions = mt5.positions_get()
# print(f"Total open positions: {open_positions}")
# send_market_order("US100.cash", "short", 12345.00, 1.9, 0.1)
# send_limit_order("US100.cash", "long", 12200.00, 12150.00, 1.9, 0.1)


# symbol = "EURUSD"
# lot = 0.1
# point = mt5.symbol_info(symbol).point
# price = mt5.symbol_info_tick(symbol).ask
# deviation = 20
# request = {
#     "action": mt5.TRADE_ACTION_DEAL,
#     "symbol": symbol,
#     "volume": lot,
#     "type": mt5.ORDER_TYPE_BUY,
#     "price": price,
#     "sl": price - 100 * point,
#     "tp": price + 100 * point,
#     "deviation": deviation,
#     "magic": 234000,
#     "comment": "python script open",
#     "type_time": mt5.ORDER_TIME_GTC,
#     "type_filling": mt5.ORDER_FILLING_FOK,
# }

# # send a trading request
# print(request)
# result = mt5.order_send(request)
# print(result)
