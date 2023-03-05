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

login = config.get("MT_LOGIN")
password = config.get("MT_PASSWORD")

# connect to MetaTrader 5
if not mt5.initialize(login=int(login), server="MetaQuotes-Demo", password=password):
    print("initialize() failed")
    mt5.shutdown()


def print_message():
    print("waiting still...")


def call_me():
    print("it worked")


repeater.run(minutes={9, 10, 13, 14}, callback=call_me,
             wait_callback=print_message)

# request connection status and parameters
# print(mt5.account_info().equity)
# get data on MetaTrader 5 version
# print(mt5.version())

# set time zone to UTC
# timezone = pytz.timezone("Etc/UTC")
# utc_from = datetime(2020, 1, 10, tzinfo=timezone)
# # get 10 EURUSD H4 bars starting from 01.10.2020 in UTC time zone
# rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_M15, utc_from, 10)

# pprint.pprint(rates)
