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
import winsound
from threading import Thread
register_matplotlib_converters()
config = dotenv_values(".env")

# login = config.get("MT_LOGIN")
# password = config.get("MT_PASSWORD")
# server = "MetaQuotes-Demo"

login = config.get("CHALLANGE_MT_LOGIN")
password = config.get("CHALLANGE_MT_PASSWORD")
server="FTMO-Server"

handlers.establish_MT5_connection(
    login, server, password)

last_long_position_pivot_high = 0
last_short_position_pivot_low = 0


def check_market(symbol, time_frame, stage_one_risk_percent, stage_two_risk_percent, stages_cut_profit_percent, risk_reward_ratio, starting_balance_for_the_week, max_percent_drop_for_the_day, break_start_hour, break_start_minute, break_end_hour, break_end_minute):

    global last_short_position_pivot_low
    global last_long_position_pivot_high

    current_balance = handlers.get_balance()
    net_profit = current_balance - starting_balance_for_the_week
    account_change_percent = round(net_profit/starting_balance_for_the_week, 2)

    if account_change_percent < stages_cut_profit_percent:
        risk_percent = stage_one_risk_percent
        print(f"will use {stage_one_risk_percent} risk because account net change percent is {account_change_percent} which is less than {stages_cut_profit_percent} cut point")
    else:
        risk_percent = stage_two_risk_percent
        print(f"will use {stage_two_risk_percent} risk because account net change percent is {account_change_percent} which is more than {stages_cut_profit_percent} cut point")

    recent_pivot_high = handlers.get_recent_pivot_high(
        symbol, time_frame, 20, 2)
    recent_pivot_low = handlers.get_recent_pivot_low(symbol, time_frame, 20, 2)

    last_candle = handlers.get_candles_by_count(symbol, time_frame, 1)[0]
    last_candle_open = last_candle[1]
    last_candle_close = last_candle[4]

    if not handlers.break_period(break_start_hour, break_start_minute, break_end_hour, break_end_minute):
        if account_change_percent > - max_percent_drop_for_the_day/100:
            if last_candle_close > recent_pivot_high and last_candle_open <= recent_pivot_high:
                if last_long_position_pivot_high == recent_pivot_high:
                    handlers.ring('SystemHand')
                    print("Pass previously taken a long position at this pivot high")
                else:
                    print("take a long position")
                    stop_loss = recent_pivot_low
                    handlers.send_market_order(
                        symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                    entry_price = recent_pivot_high
                    handlers.send_limit_order(
                        symbol, "long", entry_price, stop_loss, risk_reward_ratio, risk_percent)
                    last_long_position_pivot_high = recent_pivot_high
            elif last_candle_close < recent_pivot_low and last_candle_open >= recent_pivot_low:
                if last_short_position_pivot_low == recent_pivot_low:
                    handlers.ring('SystemHand')
                    print("Pass previously taken a short position at this pivot low")
                else:
                    print("take a short position")
                    stop_loss = recent_pivot_high
                    handlers.send_market_order(
                        symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                    entry_price = recent_pivot_low
                    handlers.send_limit_order(
                        symbol, "short", entry_price, stop_loss, risk_reward_ratio, risk_percent)
                    last_short_position_pivot_low = recent_pivot_low
            else:
                print("no conditions met and no position taken")
        else:
            print(
                f"The today's account profit percent is {account_change_percent} which is below the {-max_percent_drop_for_the_day/100} limit")

        manage_pending_orders(symbol, recent_pivot_high, recent_pivot_low)

        handlers.get_open_positions()
    else:
        print("The Break time now no trading.......")


def manage_pending_orders(symbol, recent_pivot_high, recent_pivot_low):
    pending_orders = handlers.get_open_orders()
    available_open_orders = mt5.orders_total()
    if available_open_orders > 0:
        for order in pending_orders:
            if order.symbol == symbol and order.type == 2 and order.price_open < recent_pivot_low:
                handlers.close_open_order(order.ticket)
            elif order.symbol == symbol and order.type == 3 and order.price_open > recent_pivot_high:
                handlers.close_open_order(order.ticket)
            else:
                print("No Change on the pending orders and they are still valid")
    else:
        print("No available open pending orders")


def still_alive():
    pass


def check_market_callback():
    check_market(symbol="US100.cash",
                 time_frame="15min",
                 stage_one_risk_percent=0.25,
                 stage_two_risk_percent=0.5,
                 stages_cut_profit_percent=2.5,
                 risk_reward_ratio=1.9,
                 starting_balance_for_the_week=196000,
                 max_percent_drop_for_the_day=4,
                 break_start_hour=13,
                 break_start_minute=30,
                 break_end_hour=23,
                 break_end_minute=59)


handlers.run(
    minutes={15, 30, 45, 0},
    callback=check_market_callback,
    wait_callback=still_alive)
