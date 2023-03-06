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
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

config = dotenv_values(".env")

login = config.get("MT_LOGIN")
password = config.get("MT_PASSWORD")

# connect to MetaTrader 5
if not mt5.initialize(login=int(login), server="MetaQuotes-Demo", password=password):
    print("initialize() failed")
    mt5.shutdown()


# def print_message():
#     print("waiting still...")


# def call_me():
#     print("it worked")


# repeater.run(
#     minutes={46, 47, 48, 49}, 
#     callback=call_me,
#     wait_callback=print_message
# )

# request connection status and parameters
print(mt5.account_info().equity)
# get data on MetaTrader 5 version
# print(mt5.version())

# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
utc_from = datetime(2020, 1, 10, tzinfo=timezone)
# get 10 EURUSD H4 bars starting from 01.10.2020 in UTC time zone
rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M15, 0, 200)

pprint.pprint(rates)


#PLOT
# create DataFrame out of the obtained data
ticks_frame = pd.DataFrame(rates)
# convert time in seconds into the datetime format
ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')
# display ticks on the chart
n = 2

ticks_frame['min'] = ticks_frame.iloc[argrelextrema(ticks_frame['close'].values, np.less_equal, order=n)[0]]['close']
ticks_frame['max'] = ticks_frame.iloc[argrelextrema(ticks_frame['close'].values, np.greater_equal, order=n)[0]]['close']

plt.scatter(ticks_frame['time'], ticks_frame['min'], c='r')
plt.scatter(ticks_frame['time'], ticks_frame['max'], c='g')
plt.plot(ticks_frame['time'], ticks_frame['close'], 'b-', label='close')
 
# display the legends
plt.legend(loc='upper left')
 
# add the header
plt.title('EURUSD bars')
 
# display the chart
plt.show()
