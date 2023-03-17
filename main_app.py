import pprint
import pytz
import datetime
import MetaTrader5 as mt5
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import argrelextrema
import numpy as np
from dotenv import dotenv_values
import repeater
import handlers
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
config = dotenv_values(".env")

login = config.get("MT_LOGIN")
password = config.get("MT_PASSWORD")
handlers.establish_MT5_connection(login, password)

symbol = "XAUUSD"
time_frame = "15min"
last_long_position_pivot_high = 0
last_short_position_pivot_low = 0


def check_market():

    global last_short_position_pivot_low
    global last_long_position_pivot_high

    starting_balance_for_the_day = 100000
    current_balance = handlers.get_balance()
    account_change_percent = (
        current_balance - starting_balance_for_the_day)/starting_balance_for_the_day

    first_risk_percent = 3
    second_risk_percent = 5

    recent_pivot_high = handlers.get_recent_pivot_high(
        symbol, time_frame, 20, 2)
    recent_pivot_low = handlers.get_recent_pivot_low(symbol, time_frame, 20, 2)
    last_candle = handlers.get_candles_by_count(symbol, time_frame, 1)[0]
    if handlers.within_the_period(0, 0, 23, 59) and account_change_percent > - 0.04:
        if last_candle[4] > recent_pivot_high:
            if last_long_position_pivot_high == recent_pivot_high:
                print("Pass previously taken a long position at this pivot high")
            else:
                print("take a long position")
                stop_loss = recent_pivot_low
                handlers.send_market_order(
                    symbol, "long", stop_loss, 1.9, 0.1)
                entry_price = recent_pivot_high
                handlers.send_limit_order(
                    symbol, "long", entry_price, stop_loss, 1.9, 0.1)
                last_long_position_pivot_high = recent_pivot_high
        elif last_candle[4] < recent_pivot_low:
            if last_short_position_pivot_low == recent_pivot_low:
                print("Pass previously taken a short position at this pivot low")
            else:
                print("take a short position")
                stop_loss = recent_pivot_high
                handlers.send_market_order(
                    symbol, "short", stop_loss, 1.9, 0.0005)
                entry_price = recent_pivot_low
                handlers.send_limit_order(
                    symbol, "short", entry_price, stop_loss, 1.9, 0.0005)
                last_short_position_pivot_low = recent_pivot_low
        else:
            print("no conditions met and no position taken")
    else:
        print("The time now is out side the time limits for trading.......")


def still_alive():
    pass


handlers.run(
    minutes={15, 30, 45, 0},
    callback=check_market,
    wait_callback=still_alive)
