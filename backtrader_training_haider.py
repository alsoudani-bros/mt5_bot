from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
# Import the backtrader platform
import backtrader as bt

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=r"candles_data\us100\test.csv",

        fromdate=datetime.datetime(2022, 1, 3),
        todate=datetime.datetime(2022, 12, 30),

        nullvalue=0.0,

        dtformat=('%Y-%m-%d %H:%M'),
        tmformat=('%H:%M'),

        datetime=0,
        time=1,
        high=2,
        low=3,
        open=4,
        close=5,
        volume=6,
        # openinterest=-1
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(200000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
