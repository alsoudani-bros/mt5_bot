import handlers
import datetime

last_position_pivot_high = 0.0
last_long_position_ticket = 0
last_position_pivot_low = 0.0
last_short_position_ticket = 0
last_position_direction = "direction"
starting_balance = 0.0
last_report_time = datetime.datetime.now()
symbol= input("Enter the symbol you want to trade: ").strip()


def check_market(time_frame, risk_percent, risk_reward_ratio,start_break_hour, start_break_minute, end_break_hour, end_break_minute):
    global symbol
    global last_position_pivot_high
    global last_long_position_ticket
    global last_position_pivot_low
    global last_short_position_ticket
    global last_position_direction
    global starting_balance
    global last_report_time
    
        
    if not handlers.is_weekend_break():
        break_time = handlers.The_time_of(start_break_hour,start_break_minute,end_break_hour,end_break_minute, "Break time")
        
        if handlers.get_report(last_report_time, 60):
            last_report_time = datetime.datetime.now()
                
        if starting_balance == 0.0 or break_time: 
            starting_balance = handlers.get_balance()
            
            
        if not break_time:
            current_balance = handlers.get_balance()
            recent_pivot_high = handlers.get_pivot_highs(symbol, time_frame, 100, 2)[0]
            recent_pivot_low = handlers.get_pivot_lows(symbol, time_frame, 100, 2)[0]
            last_candle = handlers.get_candles_by_count(symbol, time_frame, 1)
            last_candle_open = last_candle['open'][0]
            last_candle_close = last_candle['close'][0]
            last_candle_high = last_candle['high'][0]
            last_candle_low = last_candle['low'][0]
            
            print(f"last candle open: {last_candle_open} and close: {last_candle_close}")
            
            if not handlers.reached_max_loss(starting_balance, current_balance, 2):
                
                there_is_long_position_has_same_pivot_high = last_position_pivot_high == recent_pivot_high and handlers.position_still_open(symbol, last_long_position_ticket) and last_position_direction == "long"
                there_is_long_position_has_same_pivot_low = last_position_pivot_low == recent_pivot_low and handlers.position_still_open(symbol, last_long_position_ticket) and last_position_direction == "long"
                there_is_short_position_has_same_pivot_high = last_position_pivot_high == recent_pivot_high and handlers.position_still_open(symbol, last_short_position_ticket) and last_position_direction == "short"
                there_is_short_position_has_same_pivot_low = last_position_pivot_low == recent_pivot_low and handlers.position_still_open(symbol, last_short_position_ticket) and last_position_direction == "short"
                if last_candle_close > recent_pivot_high and last_candle_low <= recent_pivot_high and last_candle_close > last_candle_open and not there_is_long_position_has_same_pivot_high and not there_is_long_position_has_same_pivot_low:
                    print("Start taking a long position")
                    stop_loss = recent_pivot_low
                    if handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent):
                        last_position_pivot_high = recent_pivot_high
                        last_position_pivot_low = recent_pivot_low
                        last_position_direction = "long"
                        last_long_position_ticket = handlers.get_most_recent_position(symbol).ticket
                
                elif last_candle_close < recent_pivot_low and last_candle_high >= recent_pivot_low and  last_candle_close < last_candle_open and not there_is_short_position_has_same_pivot_high and not there_is_short_position_has_same_pivot_low:
                    print("start taking a short position")
                    stop_loss = recent_pivot_high
                    if handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent):
                        last_position_pivot_high = recent_pivot_high
                        last_position_pivot_low = recent_pivot_low
                        last_position_direction = "short"
                        last_short_position_ticket = handlers.get_most_recent_position(symbol).ticket
                            
                else:
                    print("No conditions met and No position taken")
        