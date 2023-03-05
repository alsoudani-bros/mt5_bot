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


# def print_message():
#     print("waiting still...")


# def call_me():
#     print("it worked")


# repeater.run(minutes={9, 10, 13, 14}, callback=call_me,
#              wait_callback=print_message)

# request connection status and parameters
# print(mt5.account_info().equity)
# get data on MetaTrader 5 version
# print(mt5.version())

# set time zone to UTC
# timezone = pytz.timezone("Etc/UTC")
# utc_from = datetime(2020, 1, 10, tzinfo=timezone)
# # get 10 EURUSD M15 bars starting from 01.10.2020 in UTC time zone
# rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_M15, utc_from, 10)

# pprint.pprint(rates)


def get_equity():
    equity = mt5.account_info().equity
    print(equity)
    return equity


def get_balance():
    balance = mt5.account_info().balance
    print(balance)
    return balance


def get_profit():
    profit = mt5.account_info().profit
    print(profit)
    return profit


def get_margin_free():
    margin_free = mt5.account_info().margin_free
    print(margin_free)
    return margin_free


def get_available_symbols():
    available_symbols = []
    symbols = mt5.symbols_get()
    for s in symbols:
        print(s.name, s.last)
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
    # for s in symbols:
    #     print(s.name)
    #     available_symbols.append(s.name)
    # return available_symbols


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


# long position:  money willing to lose per trade / (entry price - stop price) * contract size
# short position:  money willing to lose per trade / (stop price - entry price) * contract size
# get_equity()
# get_balance()
# get_profit()
# get_margin_free()
# check_connection()
# get_available_symbols()
get_symbol_info('XAUUSD')
get_symbol_info('US100.cash')
get_symbol_info('EURUSD')
get_symbol_info('AUDJPY')
