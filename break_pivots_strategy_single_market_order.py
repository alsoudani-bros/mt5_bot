import handlers

last_position_pivot_high = 0
last_long_position_ticket = 0
last_position_pivot_low = 0
last_short_position_ticket = 0
last_position_direction = "direction"
symbol= input("Enter the symbol you want to trade: ").strip()
def check_market(time_frame, risk_percent, risk_reward_ratio, starting_balance_for_the_week):
    global symbol
    global last_position_pivot_high
    global last_long_position_ticket
    global last_position_pivot_low
    global last_short_position_ticket
    global last_position_direction
    
    Trading_time = handlers.The_time_of(1,0,13,0, "Trading time")
    
    if Trading_time:
        current_balance = handlers.get_balance()
        recent_pivot_high = handlers.get_pivot_highs(symbol, time_frame, 100, 2)[0]
        recent_pivot_low = handlers.get_pivot_lows(symbol, time_frame, 100, 2)[0]
        last_candle = handlers.get_candles_by_count(symbol, time_frame, 1)
        last_candle_open = last_candle['open'][0]
        last_candle_close = last_candle['close'][0]
        print(f"last candle open: {last_candle_open} and close: {last_candle_close}")
        
        if not handlers.reached_max_loss(starting_balance_for_the_week, current_balance, 4.5):
            
            if last_candle_close > recent_pivot_high and last_candle_open <= recent_pivot_high:
                previous_long_position_at_same_pivot_high = last_position_pivot_high == recent_pivot_high and handlers.position_still_open(symbol, last_long_position_ticket) and last_position_direction == "long"
                previous_long_position_has_same_pivot_low = last_position_pivot_low == recent_pivot_low and handlers.position_still_open(symbol, last_long_position_ticket) and last_position_direction == "long"
            
                if previous_long_position_at_same_pivot_high or previous_long_position_has_same_pivot_low:
                    handlers.ring('SystemHand')
                    # handlers.send_push_notification("Avoid position taking", f"Will not take another position at this pivot high because we already have a position open at this pivot high and the ticket number is {last_long_position_ticket}")
                    print(f"Will not take another position at this pivot high because we already have a position open at this pivot high and the ticket number is {last_long_position_ticket}")
                else:
                    print("Taking a long position")
                    stop_loss = recent_pivot_low
                    handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                    last_position_pivot_high = recent_pivot_high
                    last_position_pivot_low = recent_pivot_low
                    last_position_direction = "long"
                    last_long_position_ticket = handlers.get_most_recent_position(symbol).ticket
            
            elif last_candle_close < recent_pivot_low and last_candle_open >= recent_pivot_low:
                previous_short_position_has_same_pivot_high = last_position_pivot_high == recent_pivot_high and handlers.position_still_open(symbol, last_short_position_ticket) and last_position_direction == "short"
                previous_short_position_at_same_pivot_low = last_position_pivot_low == recent_pivot_low and handlers.position_still_open(symbol, last_short_position_ticket) and last_position_direction == "short"
            
                if previous_short_position_has_same_pivot_high or previous_short_position_at_same_pivot_low:
                    handlers.ring('SystemHand')
                    # print(f"Will not take another position at this pivot low because we already have a position open at this pivot low and the ticket number is {last_short_position_ticket}")
                    handlers.send_push_notification("Avoid position taking", f"Will not take another position at this pivot low because we already have a position open at this pivot low and the ticket number is {last_short_position_ticket}")
                else:
                    print("Taking a short position")
                    stop_loss = recent_pivot_high
                    handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                    last_position_pivot_high = recent_pivot_high
                    last_position_pivot_low = recent_pivot_low
                    last_position_direction = "short"
                    last_short_position_ticket = handlers.get_most_recent_position(symbol).ticket
                        
            else:
                print("No conditions met and No position taken")
    else:
        handlers.close_all_open_positions(symbol)