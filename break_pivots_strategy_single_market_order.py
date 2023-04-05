import datetime
from time import sleep
import handlers

last_position_pivot_high = 0
last_long_position_ticket = 0
last_position_pivot_low = 0
last_short_position_ticket = 0
last_position_direction = "direction"
# closed_orders_since_last_run = 0

# def check_market(symbol, time_frame, stage_one_risk_percent, stage_two_risk_percent, stages_cut_profit_percent, risk_reward_ratio, starting_balance_for_the_week, break_start_hour, break_start_minute, break_end_hour, break_end_minute, max_positions_open_at_once_per_direction):
def check_market(symbol, time_frame, stage_one_risk_percent, stage_two_risk_percent, stages_cut_profit_percent, risk_reward_ratio, starting_balance_for_the_week):

    global last_position_pivot_high
    global last_long_position_ticket
    global last_position_pivot_low
    global last_short_position_ticket
    global last_position_direction
    # global closed_orders_since_last_run
    
    newyork_break = handlers.break_period(10,0,23,59)
    london_break2 = handlers.break_period(3,0,5,30)
    london_break1 = handlers.break_period(0,0,1,0)
    close_all_positions_break = handlers.break_period(13,0,14,0)

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
    # distance_between_pivot_high_low = abs(recent_pivot_high - recent_pivot_low)
    last_candle = handlers.get_candles_by_count(symbol, time_frame, 1)
    last_candle_open = last_candle['open'][0]
    last_candle_close = last_candle['close'][0]
    print(f"last candle open: {last_candle_open} and close: {last_candle_close}")
    
    if not london_break1 and not london_break2 and not newyork_break:
        if not handlers.reached_max_loss(starting_balance_for_the_week, current_balance, 4.5):
            if last_candle_close > recent_pivot_high and last_candle_open <= recent_pivot_high:
                previous_long_position_at_same_pivot_high = last_position_pivot_high == recent_pivot_high and handlers.position_still_open(symbol, last_long_position_ticket) and last_position_direction == "long"
                previous_long_position_has_same_pivot_low = last_position_pivot_low == recent_pivot_low and handlers.position_still_open(symbol, last_long_position_ticket) and last_position_direction == "long"
                if previous_long_position_at_same_pivot_high or previous_long_position_has_same_pivot_low:
                    handlers.ring('SystemHand')
                    handlers.send_push_notification("Avoid position taking", f"Will not take another position at this pivot high because we already have a position open at this pivot high and the ticket number is {last_long_position_ticket}")
                    print(f"Will not take another position at this pivot high because we already have a position open at this pivot high and the ticket number is {last_long_position_ticket}")
                else:
                    print("Taking a long position")
                    stop_loss = recent_pivot_low
                    handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                    # if handlers.number_of_current_open_positions(symbol,"long") >= max_positions_open_at_once_per_direction:
                    #     print(f"Will not take another position we have {max_positions_open_at_once_per_direction} or more current long positions open for the {symbol}")
                    #     handlers.send_push_notification("Avoid position taking", f"Will not take another position we have {max_positions_open_at_once_per_direction} or more current long positions open for the {symbol}")
                    # else:
                    #     # distance_between_pivot_high_last_candle_close = abs(recent_pivot_high - last_candle_close)
                    #     print("Taking a long position")
                    #     # stop_loss = recent_pivot_low
                        # if distance_between_pivot_high_last_candle_close > distance_between_pivot_high_low:
                            # next line is a market order which made to detect the price action with current pivot high and how will react accordingly with stop loss that is why it has very small size 0.01
                            # handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, 0.01)
                            # entry_price = recent_pivot_high + distance_between_pivot_high_low
                            # if not handlers.send_limit_order(symbol, "long", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                            #     handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                            # entry_price = recent_pivot_high
                            # if not handlers.send_limit_order(symbol, "long", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                            #     handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                        # else:
                        #     handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                            # entry_price = recent_pivot_high
                            # if not handlers.send_limit_order(symbol, "long", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                            #     handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                        
                    last_position_pivot_high = recent_pivot_high
                    last_position_pivot_low = recent_pivot_low
                    last_position_direction = "long"
                    last_long_position_ticket = handlers.get_most_recent_position(symbol).ticket
            
            elif last_candle_close < recent_pivot_low and last_candle_open >= recent_pivot_low:
                previous_short_position_has_same_pivot_high = last_position_pivot_high == recent_pivot_high and handlers.position_still_open(symbol, last_short_position_ticket) and last_position_direction == "short"
                previous_short_position_at_same_pivot_low = last_position_pivot_low == recent_pivot_low and handlers.position_still_open(symbol, last_short_position_ticket) and last_position_direction == "short"
                if previous_short_position_has_same_pivot_high or previous_short_position_at_same_pivot_low:
                    handlers.ring('SystemHand')
                    print(f"Will not take another position at this pivot low because we already have a position open at this pivot low and the ticket number is {last_short_position_ticket}")
                    handlers.send_push_notification("Avoid position taking", f"Will not take another position at this pivot low because we already have a position open at this pivot low and the ticket number is {last_short_position_ticket}")
                else:
                    print("Taking a short position")
                    stop_loss = recent_pivot_high
                    handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                    # if handlers.number_of_current_open_positions(symbol,"short") >= max_positions_open_at_once_per_direction:
                    #     print(f"Will not take another position we have {max_positions_open_at_once_per_direction} or more current short positions open for the {symbol}")
                    #     handlers.send_push_notification("Avoid position taking", f"Will not take another position we have {max_positions_open_at_once_per_direction} or more current short positions open for the {symbol}")
                    # else:
                        # distance_between_pivot_low_last_candle_close = abs(recent_pivot_low - last_candle_close)
                        # print("Taking a short position")
                        # stop_loss = recent_pivot_high
                        # if distance_between_pivot_low_last_candle_close > distance_between_pivot_high_low:
                            # next line is a market order which made to detect the price action with current pivot low and how will react accordingly with stop loss that is why it has very small size 0.01
                            # handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, 0.01)
                            # entry_price = recent_pivot_low - distance_between_pivot_high_low
                            # if not handlers.send_limit_order(symbol, "short", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                            #     handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                            # entry_price = recent_pivot_low
                            # if not handlers.send_limit_order(symbol, "short", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                            #     handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                        # else:
                        #     handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                            # entry_price = recent_pivot_low
                            # if not handlers.send_limit_order(symbol, "short", entry_price, stop_loss, risk_reward_ratio, risk_percent):
                            #     handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                        
                    last_position_pivot_high = recent_pivot_high
                    last_position_pivot_low = recent_pivot_low
                    last_position_direction = "short"
                    last_short_position_ticket = handlers.get_most_recent_position(symbol).ticket
                        
            else:
                print("No conditions met and No position taken")
        else:
            # handlers.close_all_open_orders(symbol)
            handlers.close_all_open_positions(symbol)
    if close_all_positions_break:
        handlers.close_all_open_positions(symbol)

    # closed_orders_since_last_run += handlers.manage_pending_orders_depends_on_pivots(symbol, recent_pivot_high, recent_pivot_low)
    # print(f"Closed orders since last run: {closed_orders_since_last_run}")
    # handlers.send_push_notification("Total Closed Orders", f"Total closed orders since last run are: {closed_orders_since_last_run} orders")