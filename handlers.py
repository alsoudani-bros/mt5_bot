import random
import pprint
import pytz
import datetime
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import dotenv_values
from pandas.plotting import register_matplotlib_converters
from scipy.signal import argrelextrema
import numpy as np
from time import sleep
import winsound
from threading import Thread
from pushbullet import PushBullet
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
register_matplotlib_converters()
config = dotenv_values(".env")


def send_push_notification(header, body):
    try:
        push_bullet_access_token = config.get("PUSH_BULLET_ACCESS_TOKEN")
        pb = PushBullet(push_bullet_access_token)
        pb.push_note(header, body)
        print("push notification sent")
    except Exception as e:
        print("push notification failed")
        print(e)

def establish_MT5_connection(login, server, password):
    now= datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    if mt5.initialize(login=int(login), server=server, password=password):
        print("Successfully connected.........")
        push_notification_header=f"Connected to MT5"
        push_notification_body=f"Successfully connected to MT5 {now}"
        send_push_notification(push_notification_header, push_notification_body)
    else:
        print("Connection failed............")
        push_notification_header=f"Connection Failure to MT5"
        push_notification_body=f"Failed to connect to MT5 {now}"
        send_push_notification(push_notification_header, push_notification_body)
        print("will try to establish connection again in 5 seconds")
        sleep(5)
        establish_MT5_connection(login, server, password)

def run(wait_callback, callback, **kwargs):
    now= datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    minutes = kwargs.get("minutes", {0})
    hours = kwargs.get("hours")
    while True:
        try:
            if (datetime.datetime.now().second == 2 and (datetime.datetime.now().minute in minutes and (hours is None or datetime.datetime.now().hour in hours))):
                print(f"\n\n Checking market time {datetime.datetime.now()}\n...........................................\n")
                callback()
                sleep(1)
            else:
                # print(datetime.datetime.now())
                wait_callback()
                sleep(.5)
        except Exception as e:
            print(f"some issue in the process happened at {now}")
            print(e)
            send_push_notification("Issues In the bot", f"Some issue in the process happened at {now}")
            sleep(1)
            # next line to troubleshoot errors
            # callback()

def run_every_minute(wait_callback, callback):
    now= datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    while True:
        try:
            if (datetime.datetime.now().second == 1 ):
                print(f"\n\n Checking market time {datetime.datetime.now()}\n...........................................\n")
                callback()
                sleep(1)
            else:
                # print(datetime.datetime.now())
                wait_callback()
                sleep(.5)
        except Exception as e:
            print(f"some issue in the process happened at {now}")
            print(e)
            send_push_notification("Issues In the bot", f"Some issue in the process happened at {now}")
            sleep(1)
            # next line to troubleshoot errors
            # callback()

def The_time_of(period_start_hour, period_start_minute, period_end_hour, period_end_minute, message):
    now = datetime.datetime.now()
    start_time = now.replace(
        hour=period_start_hour, minute=period_start_minute)
    end_time = now.replace(hour=period_end_hour,
                           minute=period_end_minute)
    # current_time = now.strftime("%H:%M:%S")
    # print(current_time)
    if now >= start_time and now <= end_time:
        print(f"{message}")
        return True
    else:
        # print("Trading time")
        return False

def news_release_or_weekend(symbol, month, day, hour, minute, reason):
    now = datetime.datetime.now()
    news_release_time = now.replace(
        month=month, day=day, hour=hour, minute=minute)
    before_news_release = news_release_time - datetime.timedelta(minutes=5)
    after_news_release = news_release_time + datetime.timedelta(minutes=5)
    if now >= before_news_release and now <= after_news_release:
        print(f"Avoid news release time for {symbol}")
        send_push_notification(f"Stop the bot news release soon for {symbol}", f"{reason}")
        return True
    else:
        print(
            f"the remaining time for the {reason} on the symbol: {symbol} is {before_news_release - now}")
        return False

def get_pivot_highs(symbol, time_frame, candles_count, candles_count_on_each_side):
    pivot_highs = []
    candles = get_candles_by_count(symbol, time_frame, candles_count)
    ticks_frame = pd.DataFrame(candles)
    ticks_frame['max'] = ticks_frame.iloc[argrelextrema(
        ticks_frame['close'].values, np.greater, order=candles_count_on_each_side)[0]]['close']
    for pivot in ticks_frame['max']:
        if pivot > 0:
            pivot_highs.append(pivot)
    return pivot_highs

def get_pivot_lows(symbol, time_frame, candles_count, candles_count_on_each_side):
    pivot_lows = []
    candles = get_candles_by_count(symbol, time_frame, candles_count)
    ticks_frame = pd.DataFrame(candles)
    ticks_frame['min'] = ticks_frame.iloc[argrelextrema(
        ticks_frame['close'].values, np.less, order=candles_count_on_each_side)[0]]['close']
    for pivot in ticks_frame['min']:
        if pivot > 0:
            pivot_lows.append(pivot)
    return pivot_lows

def get_candles_by_count(symbol, time_frame, candles_count):
    time_frame = time_frame.strip()
    match time_frame:
        case "1min":
            selected_time_frame = mt5.TIMEFRAME_M1
        case "5min":
            selected_time_frame = mt5.TIMEFRAME_M5
        case "15min":
            selected_time_frame = mt5.TIMEFRAME_M15
        case "30min":
            selected_time_frame = mt5.TIMEFRAME_M30
        case "1hour":
            selected_time_frame = mt5.TIMEFRAME_H1
    rates = mt5.copy_rates_from_pos(symbol, selected_time_frame, 1, candles_count)
    rates = np.flip(rates)
    ticks_frame = pd.DataFrame(rates)
    # print(
    #     f"The last {len(rates)} candles received for the symbol {symbol} in the {time_frame} time frame:")
    # print(ticks_frame)
    return ticks_frame

def get_candles_by_date(symbol, time_frame, from_date, to_date, save_to="last_saved_candles.csv"):
    time_frame = time_frame.strip()
    match time_frame:
        case "1min":
            selected_time_frame = mt5.TIMEFRAME_M1
        case "5min":
            selected_time_frame = mt5.TIMEFRAME_M5
        case "15min":
            selected_time_frame = mt5.TIMEFRAME_M15
        case "30min":
            selected_time_frame = mt5.TIMEFRAME_M30
        case "1hour":
            selected_time_frame = mt5.TIMEFRAME_H1
    dates_hash = {}
    for index, date in enumerate(from_date.split(",")):
        match index:
            case 0:
                dates_hash["from_year"] = int(date.strip())
            case 1:
                dates_hash["from_month"] = int(date.strip())
            case 2:
                dates_hash["from_day"] = int(date.strip())
    for index, date in enumerate(to_date.split(",")):
        match index:
            case 0:
                dates_hash["to_year"] = int(date.strip())
            case 1:
                dates_hash["to_month"] = int(date.strip())
            case 2:
                dates_hash["to_day"] = int(date.strip())
    timezone = pytz.timezone("Etc/UTC")
    utc_from = datetime(
        dates_hash["from_year"], dates_hash["from_month"], dates_hash["from_day"], tzinfo=timezone)
    utc_to = datetime(dates_hash["to_year"], dates_hash["to_month"],
                      dates_hash["to_day"], tzinfo=timezone)
    rates = mt5.copy_rates_range(symbol, selected_time_frame, utc_from, utc_to)
    print(
        f"The total received candles from {from_date} to {to_date} are {len(rates)}")
    rates = pd.DataFrame(rates)
    rates["time"] = pd.to_datetime(rates["time"], unit="s")
    rates.rename(columns={"time":"Date","open": "Open", "high": "High", "low": "Low",
                       "close": "Close", "real_volume": "Volume"}, inplace=True)
    del rates['spread']
    del rates['tick_volume']
    rates = rates[['Date', 'Open', 'High', 'Low', 'Close', 'Close', 'Volume']]
    rates.to_csv(save_to, index=False)
    return rates

def get_balance():
    now= datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    balance = mt5.account_info().balance
    print(f"Current Balance is: {balance}$")
    # send_push_notification(f"The Balance as of {now}",f"The current balance is {balance}$")
    return balance

def get_available_symbols():
    available_symbols = []
    symbols = mt5.symbols_get()
    print("The available symbols are")
    for s in symbols:
        print(s.name)
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

def close_open_position(symbol, ticket_number):
    now= datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    result = mt5.Close(symbol, ticket=ticket_number)
    if result:
        ring('SystemAsterisk')
        print(
            f"Successfully closed the position with ticket number: {ticket_number} on the symbol: {symbol} time of closing: {now}")
        # push_notification_header=f"Close Open Position on {symbol}"
        # push_notification_body=f"Successfully closed the position with ticket number: {ticket_number} on the symbol: {symbol} time of closing: {now}"
        # send_push_notification(push_notification_header, push_notification_body)
    else:
        ring('SystemHand')
        print(
            f"Failed to close the position with ticket number: {ticket_number} on the symbol: {symbol} failed to close at: {now}")
        push_notification_header=f"Failed To Close Open Position on {symbol}"
        push_notification_body=f"Failed to close the position with ticket number: {ticket_number} on the symbol: {symbol} failed to close at: {now}"
        send_push_notification(push_notification_header, push_notification_body)

def close_all_open_positions(symbol):
    total_closed_positions = 0
    now= datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    positions = mt5.positions_get(symbol=symbol)
    if len(positions) > 0:
        for position in positions:
            close_open_position(symbol, position.ticket)
            total_closed_positions += 1
        print(f"All open positions are closed on the symbol: {symbol} time of closing: {now}")
        push_notification_header=f"All open positions closed on {symbol}"
        push_notification_body=f"All open positions are closed on the symbol: {symbol} time of closing: {now}"
        send_push_notification(push_notification_header, push_notification_body)
        return total_closed_positions
    else:
        print(f"No open positions to close for the symbol: {symbol} time of checking: {now}")
        push_notification_header=f"No Open Positions to close on {symbol}"
        push_notification_body=f"No open positions to close for the symbol: {symbol} time of checking: {now}"
        send_push_notification(push_notification_header, push_notification_body)
        return total_closed_positions

def close_open_order(ticket_number):
    now= datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": ticket_number
    }
    result = mt5.order_send(request)
    if result.retcode == 10009:
        ring('SystemAsterisk')
        print(f"{result.comment}\nPending Order number: {result.order} got removed \nTime Of Execution: {now}")
        push_notification_header=f"Close Pending Order"
        push_notification_body=f"{result.comment}\nPending Order number: {result.order} got removed \nTime Of Execution: {now}"
        send_push_notification(push_notification_header, push_notification_body)
    else:
        ring('SystemHand')
        print(
            f"There was an error sending the request\nThe error code: {result.retcode}\nThe request was:\n{request}\nTime Of Request: {now}")
        push_notification_header=f"Failed To Close Pending Order"
        push_notification_body=f"There was an error sending the request\nThe error code: {result.retcode}\nThe request was:\n{request}\nTime Of Request: {now}"
        send_push_notification(push_notification_header, push_notification_body)

def close_all_open_orders(symbol):
    total_closed_orders = 0
    now= datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    print(f"Start closing all open orders for the symbol: {symbol}")
    orders = mt5.orders_get(symbol=symbol)
    if len(orders) > 0:
        for order in orders:
            close_open_order(order.ticket)
            total_closed_orders += 1
        print(f"All open orders are closed on the symbol: {symbol} time of closing: {now}")
        push_notification_header=f"All open orders closed on {symbol}"
        push_notification_body=f"All open orders are closed on the symbol: {symbol} time of closing: {now}"
        send_push_notification(push_notification_header, push_notification_body)
        return total_closed_orders
    else:
        print(f"No open orders to close for the symbol: {symbol} time of checking: {now}")
        push_notification_header=f"No Open Orders to close on {symbol}"
        push_notification_body=f"No open orders to close for the symbol: {symbol} time of checking: {now}"
        send_push_notification(push_notification_header, push_notification_body)
        return total_closed_orders
        
def manage_pending_orders_depends_on_pivots(symbol, recent_pivot_high, recent_pivot_low):
    total_closed_orders = 0
    pending_orders = mt5.orders_get(symbol=symbol)
    if len(pending_orders) > 0:
        for order in pending_orders:
            if order.type == 2 and order.price_open < recent_pivot_low:
                close_open_order(order.ticket)
                total_closed_orders += 1
            elif order.type == 3 and order.price_open > recent_pivot_high:
                close_open_order(order.ticket)
                total_closed_orders += 1
            else:
                print(f"There are {len(pending_orders)} pending orders for the symbol {symbol} and they are still valid")
        return total_closed_orders
    else:
        print(f"No available open pending orders for the symbol: {symbol}")
        return total_closed_orders

def number_of_current_open_positions(symbol, direction):
    positions = mt5.positions_get(symbol=symbol)
    count = 0
    if len(positions) > 0:
        if direction == 'long':
            for position in positions:
                if position.type == 0:
                    count += 1
        elif direction =='short':
            for position in positions:
                if position.type == 1:
                    count += 1
    return count
        
def send_market_order(symbol, direction, stop_loss_price, risk_reward_ratio, risk_percent):
    now= datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    random_id = random.randint(100000000, 999999999)
    money_to_risk = get_balance() * risk_percent/100
    deviation = 100
    if direction == "long":
        market_price = mt5.symbol_info_tick(symbol).ask
        distance_from_stop_loss = abs(market_price - stop_loss_price)
        distance_from_take_profit = distance_from_stop_loss * risk_reward_ratio
        if symbol == "US100.cash":
            lot_size = round(money_to_risk/distance_from_stop_loss, 2)
        elif symbol == "XAUUSD":
            lot_size = round(money_to_risk/(distance_from_stop_loss * 100), 2)
        elif symbol == "GBPJPY":
            lot_size = round(money_to_risk * 0.132 /
                            (distance_from_stop_loss * 100), 2)
        elif symbol == "EURUSD":
            lot_size = round(money_to_risk * 0.1 /
                            (distance_from_stop_loss * 10000), 2)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": market_price,
            "sl": stop_loss_price,
            "tp": round(market_price + distance_from_take_profit, 2),
            "deviation": deviation,
            "magic": random_id,
            "comment": "python script open position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }
    elif direction == "short":
        market_price = mt5.symbol_info_tick(symbol).bid
        distance_from_stop_loss = abs(market_price - stop_loss_price)
        distance_from_take_profit = distance_from_stop_loss * risk_reward_ratio
        if symbol == "US100.cash":
            lot_size = round(money_to_risk/distance_from_stop_loss, 2)
        elif symbol == "XAUUSD":
            lot_size = round(money_to_risk/(distance_from_stop_loss * 100), 2)
        elif symbol == "GBPJPY":
            lot_size = round(money_to_risk * 0.132 /
                            (distance_from_stop_loss * 100), 2)
        elif symbol == "EURUSD":
            lot_size = round(money_to_risk * 0.1 /
                            (distance_from_stop_loss * 10000), 2)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL,
            "price": market_price,
            "sl": stop_loss_price,
            "tp": round(market_price - distance_from_take_profit, 2),
            "deviation": deviation,
            "magic": random_id,
            "comment": "python script open position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }

    result = mt5.order_send(request)
    if result.retcode == 10009:
        ring('SystemAsterisk')
        print(f"{result.comment}\nOrder number: {result.order}\nSymbol: {symbol}\nVolume: {result.volume}\nEntry Price: {result.price}\nTime Of Excution: {now}")
        # push_notification_header = f"Market order placed {symbol} {direction}"
        # push_notification_body = f"{result.comment}\nOrder number: {result.order}\nSymbol: {symbol}\nVolume: {result.volume}\nEntry Price: {result.price}\nTime Of Excution: {now}"
        # send_push_notification(push_notification_header, push_notification_body)
        return True
    else:
        ring('SystemHand')
        print(
            f"There was an error sending the request\nThe error code: {result.retcode}\nThe request was:\n{request}\nTime Of Request: {now}")
        push_notification_header = f"Failed to place Market order {symbol} {direction}"
        push_notification_body = f"There was an error sending the request\nThe error code: {result.retcode}\nThe request was:\n{request}\nTime Of Request: {now}"
        send_push_notification(push_notification_header, push_notification_body)
        return False

def position_still_open(symbol, ticket):
    open_positions = mt5.positions_get(symbol=symbol)
    if len(open_positions) > 0:
        for position in open_positions:
            if position.ticket == ticket:
                return True
    else:
        return False

def get_most_recent_position(symbol):
    open_positions = mt5.positions_get(symbol=symbol)
    if len(open_positions) > 0:
        most_recent_position = open_positions[-1]
        return most_recent_position
    else:
        return None

def send_limit_order(symbol, direction, entry_price, stop_loss_price, risk_reward_ratio, risk_percent):
    now= datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    random_id = random.randint(100000000, 999999999)
    money_to_risk = get_balance() * risk_percent/100
    distance_from_stop_loss = abs(entry_price - stop_loss_price)
    distance_from_take_profit = distance_from_stop_loss * risk_reward_ratio
    if symbol == "US100.cash":
        lot_size = round(money_to_risk/distance_from_stop_loss, 2)
    elif symbol == "XAUUSD":
        lot_size = round(money_to_risk/(distance_from_stop_loss * 100), 2)
    elif symbol == "GBPJPY":
        lot_size = round(money_to_risk * 0.132 /
                         (distance_from_stop_loss * 100), 2)
    elif symbol == "EURUSD":
        lot_size = round(money_to_risk * 0.1 /
                         (distance_from_stop_loss * 10000), 2)
    deviation = 100
    if direction == "long":
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "price": entry_price,
            "sl": stop_loss_price,
            "tp": round(entry_price + distance_from_take_profit, 2),
            "deviation": deviation,
            "magic": random_id,
            "comment": "python script open ",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }
    elif direction == "short":
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL_LIMIT,
            "price": entry_price,
            "sl": stop_loss_price,
            "tp": round(entry_price - distance_from_take_profit, 2),
            "deviation": deviation,
            "magic": random_id,
            "comment": "python script open position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }
    result = mt5.order_send(request)
    if result.retcode == 10009:
        ring('SystemAsterisk')
        print(f"{result.comment}\nOrder number: {result.order}\nSymbol: {symbol}\nVolume: {result.volume}\nEntry Price: {entry_price}\nTime Of Execution: {now}")
        # push_notification_header = f"Limit order placed {symbol} {direction}"
        # push_notification_body = f"{result.comment}\nOrder number: {result.order}\nSymbol: {symbol}\nVolume: {result.volume}\nEntry Price: {entry_price}\nTime Of Execution: {now}"
        # send_push_notification(push_notification_header, push_notification_body)
        return True
    else:
        ring('SystemHand')
        print(
            f"There was an error sending the request\nThe error code: {result.retcode}\nThe request was:\n{request}\nTime Of Request: {now}")
        push_notification_header = f"Failed to place Limit order {symbol} {direction}"
        push_notification_body = f"There was an error sending the request\nThe error code: {result.retcode}\nThe request was:\n{request}\nTime Of Request: {now}"
        send_push_notification(push_notification_header, push_notification_body)
        return False

def reached_max_loss(starting_balance, current_balance, max_loss_percentage):
    now= datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    max_loss = starting_balance * max_loss_percentage/100
    if starting_balance - current_balance > max_loss:
        print(f"Reached max loss of {starting_balance - current_balance}$ which is more than {max_loss}$")
        push_notification_header = f"Account reached max loss"
        push_notification_body = f"Reached max loss of {starting_balance - current_balance}$ which is more than {max_loss}$ {now}"
        send_push_notification(push_notification_header, push_notification_body)
        return True
    else:
        return False

def ring(track_name):
    soundProcess = Thread(target=winsound.PlaySound, args=[
        track_name, winsound.SND_ALIAS])
    soundProcess.start()

def is_weekend_break():
    is_friday = datetime.datetime.now().strftime('%A') == "Friday"
    is_saturday = datetime.datetime.now().strftime('%A') == "Saturday"
    is_sunday = datetime.datetime.now().strftime('%A') == "Sunday"
    if is_saturday:
        print("It is Saturday No trading today")
        return True
    elif is_friday:
        friday_break_hours = [14,15,16,17,18,19,20,21,22,23]
        is_break = False
        for hour in friday_break_hours:
            if datetime.datetime.now().hour == hour:
                is_break = True
                break
        if is_break:
            print("It is Friday break hours No trading today")
            return True
        else:
            return False
    elif is_sunday:
        sunday_break_hours = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        is_break= False
        for hour in sunday_break_hours:
            if datetime.datetime.now().hour == hour:
                is_break = True
                break
        if is_break:
            print("It is Sunday break hours No trading today")
            return True
        else:
            return False
    else:
        return False
    
def get_report(last_checked_time, minutes):
    time_now = datetime.datetime.now()
    time_since_last_report = (time_now - last_checked_time).total_seconds() / 60
    ping = mt5.terminal_info().ping_last/1000
    account_info= mt5.account_info()
    if time_since_last_report >= minutes:
        send_push_notification(f"{minutes} minutes Report...",f"Report time: {time_now.strftime('%d/%m/%Y %H:%M')}\n Last ping: {ping} ms\n Account name: {account_info.name}\n Last balance: {account_info.balance}$")
        return True
    else:
        return False

# testing..........................................................................
# activate next line to run the script and turn it off when you are done
# login = config.get("CHALLANGE_MT_LOGIN")
# password = config.get("CHALLANGE_MT_PASSWORD")
# server="FTMO-Server"

# login = config.get("MT_LOGIN")
# password = config.get("MT_PASSWORD")
# server="FTMO-Demo"
# # server = "MetaQuotes-Demo"
# establish_MT5_connection(login, server, password)

# print(break_period(0, 0, 1, 0))
# positions = mt5.positions_get(symbol="US100.cash")
# for position in positions:
#     print(position.type == 1)
# print(positions)
# x= get_most_recent_position("US100.cash").ticket
# print(position_still_open("US100.cash", x))
# print(reached_max_loss(191000, 189000, 1))
# x = manage_pending_orders_depends_on_pivots("US100.cash", 13100, 13000)
# x +=1
# print(x)
# # close_all_open_orders("US100.cash")
# close_all_open_positions("US100.cash")

# ring('SystemAsterisk')
# ring('SystemExclamation')
# ring('SystemExit')
# ring('SystemHand')
# ring('SystemQuestion')

# def wait_func():
#     print("Waiting for hope...")


# def the_main_func():
#     print("The main function")


# repeater.run(
#     minutes={15, 30, 45, 0},
#     callback=the_main_func,
#     wait_callback=wait_func)
# long position:  money willing to lose per trade / (entry price - stop price) * contract size
# short position:  money willing to lose per trade / (stop price - entry price) * contract size
# get_account_name()
# get_equity()
# get_balance()
# get_profit()
# get_margin_free()
# check_connection()
# get_available_symbols()
# get_symbol_info('US100.cash')
# send_order(symbol, direction, type, entry_price, stop_loss_price, risk_reward_ratio, risk_percent)
# get_open_positions()
# close_open_position("XAUUSD", 50390019819)
# get_open_orders()
# close_open_order(50389969290)
# open_positions = mt5.positions_get()
# print(f"Total open positions: {open_positions}")
# send_market_order("US100.cash", "short", 13033.00, 1, 0.01)
# send_limit_order("US100.cash", "long", 12200.00, 12150.00, 1.9, 0.1)
# get_candles_by_date("US100.cash", "15min", "2022,1,1", "2023,1,1", r"candles_data\us100\test_2022_2023_15min_us100.csv")
# print(get_candles_by_count("US100.cash", "15min", 5)['spread'])
# print(get_pivot_highs("US100.cash", "15min", 100, 2)[0])
# print(get_pivot_lows("US100.cash", "15min", 100, 2)[0])

# within_the_period(5, 0, 13, 0)
# send_push_notification("test", "test body")

# print(get_candles_by_count("US100.cash", "1min", 1))

# def something():
#     pass

# def doit():
#     get_candles_by_count(symbol=symbol, time_frame="15min", candles_count=1)
#     print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))

# symbol = input("input symbol >> ")
# run(something, doit, minutes={35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59})



# symbol = "EURUSD"
# lot = 0.1
# point = mt5.symbol_info(symbol).point
# price = mt5.symbol_info_tick(symbol).ask
# deviation = 20
# request = {
#     "action": mt5.TRADE_ACTION_DEAL,
#     "symbol": symbol,
#     "volume": lot,
#     "type": mt5.ORDER_TYPE_BUY,
#     "price": price,
#     "sl": price - 100 * point,
#     "tp": price + 100 * point,
#     "deviation": deviation,
#     "magic": 234000,
#     "comment": "python script open",
#     "type_time": mt5.ORDER_TIME_GTC,
#     "type_filling": mt5.ORDER_FILLING_FOK,
# }

# # send a trading request
# print(request)
# result = mt5.order_send(request)
# print(result)
# data = "Hello World"
# price_excution = "long at 1234.56"

# Send the data by passing the main title
# and text to be send


# Put a success message after sending
# the notification
# put_success("Message sent successfully...")

    
# is_weekend_break()

# x = datetime.datetime.now()- datetime.timedelta(hours=1)
# print(x)
# get_report(x, 30)