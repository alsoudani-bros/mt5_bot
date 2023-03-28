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
from time import sleep
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
last_long_position_pivot_high_ticket = 0
last_short_position_pivot_low = 0
last_short_position_pivot_low_ticket = 0

def check_market(symbol, time_frame, stage_one_risk_percent, stage_two_risk_percent, stages_cut_profit_percent, risk_reward_ratio, starting_balance_for_the_week, break_start_hour, break_start_minute, break_end_hour, break_end_minute, max_positions_open_at_once):

    global last_long_position_pivot_high
    global last_long_position_pivot_high_ticket
    global last_short_position_pivot_low
    global last_short_position_pivot_low_ticket

    current_balance = handlers.get_balance()
    net_profit = current_balance - starting_balance_for_the_week
    account_change_percent = round((net_profit/starting_balance_for_the_week)*100, 2)

    if account_change_percent < stages_cut_profit_percent:
        risk_percent = stage_one_risk_percent
        print(f"will use {stage_one_risk_percent} risk because account net change percent is {account_change_percent} which is less than {stages_cut_profit_percent} cut point")
    else:
        risk_percent = stage_two_risk_percent
        print(f"will use {stage_two_risk_percent} risk because account net change percent is {account_change_percent} which is more than {stages_cut_profit_percent} cut point")

    recent_pivot_high = handlers.get_recent_pivot_high(symbol, time_frame, 100, 2)
    while not isinstance(recent_pivot_high, float):
        now= datetime.now().strftime("%d/%m/%Y %H:%M")
        print(f"Trying to get the recent pivot high for the {symbol} at {now}")
        recent_pivot_high = handlers.get_recent_pivot_high(symbol, time_frame, 100, 2)
        sleep(5)
        
    recent_pivot_low = handlers.get_recent_pivot_low(symbol, time_frame, 100, 2)
    while not isinstance(recent_pivot_low, float):
        now= datetime.now().strftime("%d/%m/%Y %H:%M")
        print(f"Trying to get the recent pivot low for the {symbol} at {now}")
        recent_pivot_low = handlers.get_recent_pivot_low(symbol, time_frame, 100, 2)
        sleep(5)
    distance_between_pivot_high_low = abs(recent_pivot_high - recent_pivot_low)
    last_candle = handlers.get_candles_by_count(symbol, time_frame, 1)
    last_candle_open = last_candle['open'][0]
    last_candle_close = last_candle['close'][0]
    
    if not handlers.break_period(break_start_hour, break_start_minute, break_end_hour, break_end_minute):
        if not handlers.reached_max_loss(starting_balance_for_the_week, current_balance, 4.5):
            if last_candle_close > recent_pivot_high and last_candle_open <= recent_pivot_high:
                if last_long_position_pivot_high == recent_pivot_high and handlers.position_still_open(symbol, last_long_position_pivot_high_ticket):
                    handlers.ring('SystemHand')
                    handlers.send_push_notification("Avoid position taking", f"Will not take another position at this pivot high because we already have a position open at this pivot high and the ticket number is {last_long_position_pivot_high_ticket}")
                    print(f"Will not take another position at this pivot high because we already have a position open at this pivot high and the ticket number is {last_long_position_pivot_high_ticket}")
                else:
                    if handlers.number_of_current_open_positions(symbol,"long") >= max_positions_open_at_once:
                        print(f"Will not take another position we have {max_positions_open_at_once} or more current long positions open for the {symbol}")
                        handlers.send_push_notification("Avoid position taking", f"Will not take another position we have {max_positions_open_at_once} or more current long positions open for the {symbol}")
                    else:
                        distance_between_pivot_high_last_candle_close = abs(recent_pivot_high - last_candle_close)
                        print("Taking a long position")
                        stop_loss = recent_pivot_low
                        if distance_between_pivot_high_last_candle_close > distance_between_pivot_high_low:
                            # next line is a market order which made to detect the price action with current pivot high and how will react accordingly with stop loss that is why it has very small size 0.01
                            handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, 0.01)
                            entry_price = recent_pivot_high + distance_between_pivot_high_low
                            if not handlers.send_limit_order(symbol, "long", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                                handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                            entry_price = recent_pivot_high
                            if not handlers.send_limit_order(symbol, "long", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                                handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                        else:
                            handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                            entry_price = recent_pivot_high
                            if not handlers.send_limit_order(symbol, "long", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                                handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                        last_long_position_pivot_high = recent_pivot_high
                        last_long_position_pivot_high_ticket = handlers.get_most_recent_position(symbol).ticket
            elif last_candle_close < recent_pivot_low and last_candle_open >= recent_pivot_low:
                if last_short_position_pivot_low == recent_pivot_low and handlers.position_still_open(symbol, last_short_position_pivot_low_ticket):
                    handlers.ring('SystemHand')
                    print(f"Will not take another position at this pivot low because we already have a position open at this pivot low and the ticket number is {last_short_position_pivot_low_ticket}")
                    handlers.send_push_notification("Avoid position taking", f"Will not take another position at this pivot low because we already have a position open at this pivot low and the ticket number is {last_short_position_pivot_low_ticket}")
                else:
                    if handlers.number_of_current_open_positions(symbol,"short") >= max_positions_open_at_once:
                        print(f"Will not take another position we have {max_positions_open_at_once} or more current short positions open for the {symbol}")
                        handlers.send_push_notification("Avoid position taking", f"Will not take another position we have {max_positions_open_at_once} or more current short positions open for the {symbol}")
                    else:
                        distance_between_pivot_low_last_candle_close = abs(recent_pivot_low - last_candle_close)
                        print("Taking a short position")
                        stop_loss = recent_pivot_high
                        if distance_between_pivot_low_last_candle_close > distance_between_pivot_high_low:
                            # next line is a market order which made to detect the price action with current pivot low and how will react accordingly with stop loss that is why it has very small size 0.01
                            handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, 0.01)
                            entry_price = recent_pivot_low - distance_between_pivot_high_low
                            if not handlers.send_limit_order(symbol, "short", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                                handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                            entry_price = recent_pivot_low
                            if not handlers.send_limit_order(symbol, "short", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                                handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                        else:
                            handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                            entry_price = recent_pivot_low
                            if not handlers.send_limit_order(symbol, "short", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                                handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                        last_short_position_pivot_low = recent_pivot_low
                        last_short_position_pivot_low_ticket = handlers.get_most_recent_position(symbol).ticket
            else:
                print("No conditions met and No position taken")
        else:
            handlers.close_all_open_orders(symbol)
            handlers.close_all_open_positions(symbol)

    handlers.manage_pending_orders_depends_on_pivots(symbol, recent_pivot_high, recent_pivot_low)

def still_alive():
    pass

def check_market_callback():
    check_market(symbol=symbol,
                time_frame="15min",
                stage_one_risk_percent=0.1,
                stage_two_risk_percent=0.2,
                stages_cut_profit_percent=2.5,
                risk_reward_ratio=2,
                starting_balance_for_the_week=193000,
                break_start_hour=13,
                break_start_minute=30,
                break_end_hour=17,
                break_end_minute=30,
                max_positions_open_at_once=4)


symbol= input("Enter the symbol you want to trade: ").strip()
print(symbol)
handlers.run(
    minutes={15, 30, 45, 0},
    callback=check_market_callback,
    wait_callback=still_alive)
