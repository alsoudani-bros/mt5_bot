# from __future__ import (absolute_import, division, print_function,
#                         unicode_literals)
# import datetime  # For datetime objects
# import os.path  # To manage paths
# import sys  # To find out the script name (in argv[0])
# # Import the backtrader platform
# import backtrader as bt

# if __name__ == '__main__':
#     # Create a cerebro entity
#     cerebro = bt.Cerebro()

#     # Datas are in a subfolder of the samples. Need to find where the script is
#     # because it could have been called from anywhere
#     modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
#     datapath = os.path.join(modpath, 'historical_data1.csv')

#     # Create a Data Feed
#     data = bt.feeds.GenericCSVData(
#         dataname=r"candles_data\us100\2022_2023_15min_us100.csv",

#         fromdate=datetime.datetime(2000, 1, 1),
#         todate=datetime.datetime(2000, 12, 31),

#         nullvalue=0.0,

#         dtformat=('%Y-%m-%d'),
#         tmformat=('%H:%M:%S'),

#         datetime=0,
#         time=1,
#         high=2,
#         low=3,
#         open=4,
#         close=5,
#         volume=6,
#         openinterest=-1
#     )

#     # Add the Data Feed to Cerebro
#     cerebro.adddata(data)

#     # Set our desired cash start
#     cerebro.broker.setcash(200000.0)

#     # Print out the starting conditions
#     print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

#     # Run over everything
#     cerebro.run()

#     # Print out the final result
#     print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


candles_start_range = candles_count - candles_count_on_each_side - 1
candles_end_range = candles_count_on_each_side


for x in range(candles_start_range, candles_end_range, -1):
    print(x)
