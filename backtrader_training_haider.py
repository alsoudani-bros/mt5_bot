from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds
from datetime import datetime, timedelta
import backtrader.analyzers as btanalyzers

import datetime
import warnings

import matplotlib
matplotlib.use('Qt5Agg')  # or 'TkAgg'

# if __name__ == '__main__':
#     # Create a cerebro entity
#     cerebro = bt.Cerebro()

#     # Create a Data Feed
#     data = bt.feeds.GenericCSVData(
#         dataname=r"candles_data\us100\test.csv",

#         fromdate=datetime.datetime(2022, 1, 3),
#         todate=datetime.datetime(2022, 12, 30),

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
#         # openinterest=-1
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
def backtest(algorithm):
    os.system("cls")
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000)
    data = btfeeds.YahooFinanceCSVData(
        dataname=r"candles_data\us100\test_2022_2023_15min_us100.csv")
    cerebro.adddata(data)
    cerebro.addstrategy(algorithm)
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='mysharpe')
    thestrarts=cerebro.run()
    thestrarts = thestrarts[0]
    # cerebro.plot()
    print(thestrarts.analyzers.mysharpe.get_analysis())
    # print(max.drawdown.get_analysis())
    
class SmaCross(bt.Strategy):
    def __init__(self):
        sma1 = bt.ind.SMA(period=5)
        sma2 = bt.ind.SMA(period=20)
        self.crossover = bt.ind.CrossOver(sma1, sma2)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.order = self.order_target_percent(target=1)
                self.log('BUY CREATE, %.2f' % self.datas[0].close[0])

        elif self.crossover < 0:
            self.order = self.order_target_percent(target=0)
            self.log('SELL CREATE, %.2f' % self.datas[0].close[0])
            
backtest(SmaCross)
