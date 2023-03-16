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

login = config.get("CHALLANGE_MT_LOGIN")
password = config.get("CHALLANGE_MT_PASSWORD")
handlers.establish_MT5_connection(login, password)

symbol = "US100.cash"
time_frame = "15min"


def check_market():
    recent_pivot_high = handlers.get_recent_pivot_high(
        symbol, time_frame, 20, 2)
    recent_pivot_low = handlers.get_recent_pivot_low(symbol, time_frame, 20, 2)
    last_candle = handlers.get_candles_by_count(symbol, time_frame, 1)[0]
    if last_candle[4] > recent_pivot_high:
        print("take long position")
    elif last_candle[4] < recent_pivot_low:
        print("take short position")
    else:
        print("no position taken")


check_market()
