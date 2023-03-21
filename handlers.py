import random
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
from scipy.signal import argrelextrema
import numpy as np
from time import sleep
import winsound
from threading import Thread
register_matplotlib_converters()

config = dotenv_values(".env")

# login = config.get("CHALLANGE_MT_LOGIN")
# password = config.get("CHALLANGE_MT_PASSWORD")
# server="FTMO-Server"
login = config.get("MT_LOGIN")
password = config.get("MT_PASSWORD")
server = "MetaQuotes-Demo"


def establish_MT5_connection(login, server, password):
    if not mt5.initialize(login=int(login), server=server, password=password):
        print("Connection failed............")
        mt5.shutdown()
    else:
        print("Successfully connected.........")


# establish_MT5_connection(login, server, password)


def shutdown_MT5_connection():
    mt5.shutdown()
    print(f"You are now disconnected.......")


def run(wait_callback, callback, **kwargs):
    minutes = kwargs.get("minutes", {0})
    hours = kwargs.get("hours")

    while True:
        try:
            if (datetime.now().second == 10 and (datetime.now().minute in minutes and (hours is None or datetime.now().hour in hours))):
                print(datetime.now())
                callback()
                sleep(1)
            else:
                # print(datetime.now())
                wait_callback()
                sleep(.5)
        except Exception as e:
            print(f"some issue in the process happened at {datetime.now()}")
            print('Failed market checking ' + str(e))
            sleep(1)


def break_period(period_start_hour, period_start_minute, period_end_hour, period_end_minute):
    now = datetime.now()
    start_time = now.replace(
        hour=period_start_hour, minute=period_start_minute)
    end_time = now.replace(hour=period_end_hour,
                           minute=period_end_minute)
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    if now >= start_time and now <= end_time:
        print("Break period")
        return True
    else:
        print("Not a break period")
        return False


def news_release(symbol, month, day, hour, minute, news_type):
    now = datetime.now()
    news_release_time = now.replace(
        month=month, day=day, hour=hour, minute=minute)
    before_news_release = news_release_time - datetime.timedelta(minutes=5)
    after_news_release = news_release_time + datetime.timedelta(minutes=5)
    if now >= before_news_release and now <= after_news_release:
        print(f"avoid new release time for {symbol}")
        return True
    else:
        print(
            f"the remaining time for the {news_type} on the symbol: {symbol} is {before_news_release - now}")
        return False


def get_recent_pivot_high(symbol, time_frame, candles_count, candles_count_on_each_side):
    candles = get_candles_by_count(symbol, time_frame, candles_count)
    ticks_frame = pd.DataFrame(candles)
    ticks_frame['max'] = ticks_frame.iloc[argrelextrema(
        ticks_frame['close'].values, np.greater, order=candles_count_on_each_side)[0]]['close']
    candles_start_range = candles_count - candles_count_on_each_side - 1
    candles_end_range = candles_count_on_each_side

    for candle_index_under_evaluation in range(candles_start_range, candles_end_range, -1):
        if ticks_frame['max'][candle_index_under_evaluation] > 0:
            print(
                f"The most recent pivot high is {ticks_frame['max'][candle_index_under_evaluation]}")
            return ticks_frame['max'][candle_index_under_evaluation]


def get_recent_pivot_low(symbol, time_frame, candles_count, candles_count_on_each_side):
    candles = get_candles_by_count(symbol, time_frame, candles_count)
    ticks_frame = pd.DataFrame(candles)
    ticks_frame['min'] = ticks_frame.iloc[argrelextrema(
        ticks_frame['close'].values, np.less, order=candles_count_on_each_side)[0]]['close']
    candles_start_range = candles_count - candles_count_on_each_side - 1
    candles_end_range = candles_count_on_each_side

    for candle_index_under_evaluation in range(candles_start_range, candles_end_range, -1):
        if ticks_frame['min'][candle_index_under_evaluation] > 0:
            print(
                f"The most recent pivot low is {ticks_frame['min'][candle_index_under_evaluation]}")
            return ticks_frame['min'][candle_index_under_evaluation]


def get_candles_by_count(symbol, time_frame, candles_count):
    time_frame = time_frame.strip()
    match time_frame:
        case "5min":
            selected_time_frame = mt5.TIMEFRAME_M5
        case "15min":
            selected_time_frame = mt5.TIMEFRAME_M15
        case "30min":
            selected_time_frame = mt5.TIMEFRAME_M30
        case "1hour":
            selected_time_frame = mt5.TIMEFRAME_H1
    rates = mt5.copy_rates_from_pos(
        symbol, selected_time_frame, 1, candles_count)
    # print(
    #     f"The last {len(rates)} candles received for the symbol {symbol} in the {time_frame} time frame:")
    # print(rates)
    return rates


def get_candles_by_date(symbol, time_frame, from_date, to_date, save_to="last_saved_candles.csv"):
    time_frame = time_frame.strip()
    match time_frame:
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
    # print(
    #     f"The total received candles from {from_date} to {to_date} are {len(rates)}")
    rates = pd.DataFrame(rates)
    rates["time"] = pd.to_datetime(rates["time"], unit="s")
    rates.to_csv(save_to)
    return rates


def get_equity():
    equity = mt5.account_info().equity
    print(f"Current equity is: {equity}$")
    return equity


def get_balance():
    balance = mt5.account_info().balance
    print(f"Current Balance is: {balance}$")
    return balance


def get_account_name():
    name = mt5.account_info().name
    print(f" The name of the current connected account is: {name}")
    return name


def get_profit():
    profit = mt5.account_info().profit
    print(f"Total profits are: {profit}$")
    return profit


def get_margin_free():
    margin_free = mt5.account_info().margin_free
    print(f"The available margin for trading is: {margin_free}$")
    return margin_free


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


def get_open_positions():
    positions_total = mt5.positions_total()
    positions = mt5.positions_get()
    print(f"Total open positions: {positions_total} positions")
    for position in positions:
        print(f"Position Ticket: {position.ticket}\nPosition time: {position.time}\nPosition magic: {position.magic}\nPosition symbol: {position.symbol}\nPosition Volume: {position.volume}\nPosition entry price: {position.price_open}\nPosition stop loss price: {position.sl}\nPosition take profit price: {position.tp}")
    return positions


def close_open_position(symbol, ticket_number):
    result = mt5.Close(symbol, ticket=ticket_number)
    if result:
        ring('SystemAsterisk')
        print(
            f"Successfully closed the position with ticket number: {ticket_number} on the symbol: {symbol}")
    else:
        ring('SystemHand')
        print(
            f"Failed to close the position with ticket number: {ticket_number} on the symbol: {symbol}")


def get_open_orders():
    orders_total = mt5.orders_total()
    orders = mt5.orders_get()
    print(orders)
    print(f"Total open orders: {orders_total} orders")
    for order in orders:
        if order.type == 2:
            print(f"Order Ticket: {order.ticket}\nOrder time: {order.time_setup}\nOrder magic: {order.magic}\nOrder symbol: {order.symbol}\nDirection: Long\nOrder Volume: {order.volume_current}\nOrder entry price: {order.price_open}\nOrder stop loss price: {order.sl}\nOrder take profit price: {order.tp}")
        elif order.type == 3:
            print(f"Order Ticket: {order.ticket}\nOrder time: {order.time_setup}\nOrder magic: {order.magic}\nOrder symbol: {order.symbol}\nDirection: Short\nOrder Volume: {order.volume_current}\nOrder entry price: {order.price_open}\nOrder stop loss price: {order.sl}\nOrder take profit price: {order.tp}")
        else:
            print(f"Order Ticket: {order.ticket}\nOrder time: {order.time_setup}\nOrder magic: {order.magic}\nOrder symbol: {order.symbol}\nDirection: not coded yet\nOrder Volume: {order.volume_current}\nOrder entry price: {order.price_open}\nOrder stop loss price: {order.sl}\nOrder take profit price: {order.tp}")
    return orders


def close_open_order(ticket_number):
    request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": ticket_number
    }
    result = mt5.order_send(request)
    now = datetime.now()
    if result.retcode == 10009:
        ring('SystemAsterisk')
        print(f"{result.comment}\nPending Order number: {result.order} got removed \nTime Of Excution: {now}")

    else:
        ring('SystemHand')
        print(
            f"There was an error sending the request\nThe error code: {result.retcode}\nThe request was:\n{request}\nTime Of Request: {now}")


def check_connection():
    account_info = mt5.terminal_info()
    status = account_info.connected
    internet_connection = account_info.ping_last/1000
    number_of_available_symbols = mt5.symbols_total()
    if status:
        print(
            f'You have established connection with the Metatrader5 terminal \nThe Ping is {round(internet_connection)} ms \nThe total available symbols for trading are {number_of_available_symbols}')
        return status, internet_connection
    else:
        ring('SystemHand')
        print("No connection with the Metatrader5 terminal")
        return status


def send_market_order(symbol, direction, stop_loss_price, risk_reward_ratio, risk_percent):
    market_price = mt5.symbol_info_tick(symbol).ask
    random_id = random.randint(100000000, 999999999)
    money_to_risk = get_balance() * risk_percent/100
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
    deviation = 100
    if direction == "long":
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(symbol).ask,
            "sl": stop_loss_price,
            "tp": round(market_price + distance_from_take_profit, 2),
            "deviation": deviation,
            "magic": random_id,
            "comment": "python script open position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }
    elif direction == "short":
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(symbol).bid,
            "sl": stop_loss_price,
            "tp": round(market_price - distance_from_take_profit, 2),
            "deviation": deviation,
            "magic": random_id,
            "comment": "python script open position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }

    result = mt5.order_send(request)
    now = datetime.now()
    if result.retcode == 10009:
        ring('SystemAsterisk')
        print(f"{result.comment}\nOrder number: {result.order}\nSymbol: {symbol}\nVolume: {result.volume}\nEntry Price: {result.price}\nTime Of Excution: {now}")
    else:
        ring('SystemHand')
        print(
            f"There was an error sending the request\nThe error code: {result.retcode}\nThe request was:\n{request}\nTime Of Request: {now}")


def send_limit_order(symbol, direction, entry_price, stop_loss_price, risk_reward_ratio, risk_percent):
    random_id = random.randint(100000000, 999999999)
    money_to_risk = get_balance() * risk_percent/100
    distance_from_stop_loss = abs(entry_price - stop_loss_price)
    distance_from_take_profit = distance_from_stop_loss * risk_reward_ratio
    if symbol == "US100.cash":
        lot_size = round(money_to_risk/distance_from_stop_loss, 2)
    elif symbol == "XAUUSD":
        lot_size = round(money_to_risk/(distance_from_stop_loss * 100), 2)
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
    now = datetime.now()
    if result.retcode == 10009:
        ring('SystemAsterisk')
        print(f"{result.comment}\nOrder number: {result.order}\nSymbol: {symbol}\nVolume: {result.volume}\nEntry Price: {result.price}\nTime Of Excution: {now}")
    else:
        ring('SystemHand')
        print(
            f"There was an error sending the request\nThe error code: {result.retcode}\nThe request was:\n{request}\nTime Of Request: {now}")


def ring(track_name):
    soundProcess = Thread(target=winsound.PlaySound, args=[
        track_name, winsound.SND_ALIAS])
    soundProcess.start()


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
# send_market_order("XAUUSD", "long", 1919.00, 1.9, 0.1)
# send_limit_order("US100.cash", "long", 12200.00, 12150.00, 1.9, 0.1)
# get_candles_by_date("US100.cash", "15min", "2022,1,1",
#                     "2023,1,1", r"candles_data\us100\2022_2023_15min_us100.csv")
# get_candles_by_count("XAUUSD", "15min", 1)
# get_recent_pivot_high("US100.cash", "15min", 20, 2)
# get_recent_pivot_low("US100.cash", "15min", 20, 2)
# within_the_period(5, 0, 13, 0)

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
