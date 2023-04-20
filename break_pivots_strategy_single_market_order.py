import handlers
import datetime

last_long_position_pivot_high = 0.0
last_long_position_ticket = 0
last_short_position_pivot_low = 0.0
last_short_position_ticket = 0
starting_balance = 0.0
last_report_time = datetime.datetime.now()
symbol= input("Enter the symbol you want to trade: ").strip()

def check_market(time_frame, risk_percent, risk_reward_ratio,start_trading_hour, start_trading_minute, end_trading_hour, end_trading_minute):
    global symbol
    global last_long_position_pivot_high
    global last_long_position_ticket
    global last_short_position_pivot_low
    global last_short_position_ticket
    global starting_balance
    global last_report_time
        
    if not handlers.is_weekend_break():
        trading_time = handlers.The_time_of(start_trading_hour,start_trading_minute,end_trading_hour,end_trading_minute, "Trading time")
        close_positions_time= handlers.The_time_of(13,0,14,0, "Close positions time")
        
        if close_positions_time:
            handlers.close_all_open_positions(symbol)
            
        if handlers.get_report(last_report_time, 60):
            last_report_time = datetime.datetime.now()
                
        if starting_balance == 0.0 or not trading_time: 
            starting_balance = handlers.get_balance()
            
            
        if trading_time:
            if not handlers.position_still_open(symbol, last_long_position_ticket):
                last_long_position_pivot_high = 0.0
                last_long_position_ticket = 0
            
            if not handlers.position_still_open(symbol, last_short_position_ticket):
                last_short_position_pivot_low = 0.0
                last_short_position_ticket = 0
                
            current_balance = handlers.get_balance()
            recent_pivot_high = handlers.get_pivot_highs(symbol, time_frame, 100, 2)[0]
            recent_pivot_low = handlers.get_pivot_lows(symbol, time_frame, 100, 2)[0]
            fast_recent_pivot_high = handlers.get_pivot_highs(symbol, time_frame, 100, 1)[0]
            fast_recent_pivot_low = handlers.get_pivot_lows(symbol, time_frame, 100, 1)[0]
            last_candle = handlers.get_candles_by_count(symbol, time_frame, 1)
            last_candle_open = last_candle['open'][0]
            last_candle_close = last_candle['close'][0]
            last_candle_high = last_candle['high'][0]
            last_candle_low = last_candle['low'][0]
            
            print(f"\n\n Report.............................. \n\n last candle open: {last_candle_open}\n last candle close: {last_candle_close}\n last candle high: {last_candle_high}\n last candle low: {last_candle_low} \n recent pivot high: {recent_pivot_high}\n recent pivot low: {recent_pivot_low}\n fast recent pivot high: {fast_recent_pivot_high}\n fast recent pivot low: {fast_recent_pivot_low}\n last long position pivot high: {last_long_position_pivot_high}\n last short position pivot low: {last_short_position_pivot_low}\n\n End of Report..............................\n\n")
            
            if not handlers.reached_max_loss(starting_balance, current_balance, 2):
                
                if last_candle_close > recent_pivot_high and last_candle_low <= recent_pivot_high and last_candle_close > last_candle_open and last_long_position_pivot_high != recent_pivot_high:
                    print("Start taking a long position")
                    stop_loss = fast_recent_pivot_low if fast_recent_pivot_low > recent_pivot_low else recent_pivot_low    
                    if handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent):
                        last_long_position_pivot_high = recent_pivot_high
                        last_long_position_ticket = handlers.get_most_recent_position(symbol).ticket
                
                elif last_candle_close < recent_pivot_low and last_candle_high >= recent_pivot_low and  last_candle_close < last_candle_open and last_short_position_pivot_low != recent_pivot_low:
                    print("start taking a short position")
                    stop_loss = fast_recent_pivot_high if fast_recent_pivot_high < recent_pivot_high else recent_pivot_high
                    if handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent):
                        last_short_position_pivot_low = recent_pivot_low
                        last_short_position_ticket = handlers.get_most_recent_position(symbol).ticket
                            
                else:
                    print("No conditions met and No position taken")
        