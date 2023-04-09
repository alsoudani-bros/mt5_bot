import handlers

symbol= input("Enter the symbol you want to trade: ").strip()
last_21_EMA = float(input('Last 21 EMA: '))
last_50_EMA = float(input('Last 50 EMA: '))
last_long_position_ticket= 0
last_short_position_ticket = 0


def check_market(time_frame, risk_percent, risk_reward_ratio, starting_balance_for_the_week):

    
    trading_time = handlers.The_time_of(6,0,9,0,"Trading time")
    global symbol
    global last_21_EMA
    global last_50_EMA
    global last_long_position_ticket
    global last_short_position_ticket
    
    if trading_time:
        current_balance = handlers.get_balance()
        
        pivot_high_1 = handlers.get_pivot_highs(symbol, time_frame, 100, 2)[0]
        pivot_high_2 = handlers.get_pivot_highs(symbol, time_frame, 100, 2)[1]
        pivot_low_1 = handlers.get_pivot_lows(symbol, time_frame, 100, 2)[0]
        pivot_low_2 = handlers.get_pivot_lows(symbol, time_frame, 100, 2)[1]
        lower_highs = pivot_high_1 < pivot_high_2
        higher_lows = pivot_low_1 > pivot_low_2
        
        candles = handlers.get_candles_by_count(symbol, time_frame, 5)
        last_candle_open = candles['open'][0]
        last_candle_close = candles['close'][0]
        last_candle_high = candles['high'][0]
        last_candle_low = candles['low'][0]
        # second_candle_close = candles['close'][1]
        # third_candle_close = candles['close'][2]
        # fourth_candle_close = candles['close'][3]
        # fifth_candle_close = candles['close'][4]
        
        last_21_EMA = (2/(21+1)) * (last_candle_close - last_21_EMA) + (last_21_EMA)
        last_50_EMA = (2/(50+1)) * (last_candle_close - last_50_EMA) + (last_50_EMA)
        there_is_open_long_position = handlers.position_still_open(symbol, last_long_position_ticket)
        there_is_open_short_position = handlers.position_still_open(symbol, last_short_position_ticket)
        # past_candles_close_above_21_EMA = second_candle_close > last_21_EMA and third_candle_close > last_21_EMA and fourth_candle_close > last_21_EMA and fifth_candle_close > last_21_EMA
        # past_candles_close_below_21_EMA = second_candle_close < last_21_EMA and third_candle_close < last_21_EMA and fourth_candle_close < last_21_EMA and fifth_candle_close < last_21_EMA
        print(f"last candle open: {last_candle_open} and close: {last_candle_close} and high: {last_candle_high} and low: {last_candle_low} and last 21 EMA: {last_21_EMA} and last 50 EMA: {last_50_EMA} ")
        
        if (there_is_open_short_position and last_candle_close > last_21_EMA) or (there_is_open_long_position and last_candle_close < last_21_EMA):
            handlers.close_all_open_positions(symbol)
        
        stop_loss = last_50_EMA
        if not handlers.reached_max_loss(starting_balance_for_the_week, current_balance, 4.5):
        
            if last_21_EMA > last_50_EMA and last_candle_low < last_21_EMA and last_candle_close > last_50_EMA and last_candle_close > last_21_EMA and last_candle_close > last_candle_open and not there_is_open_long_position and higher_lows:
                print("Taking a long position")
                handlers.ring('SystemHand')
                handlers.send_market_order(symbol, "long", stop_loss, risk_reward_ratio, risk_percent)
                last_long_position_ticket = handlers.get_most_recent_position(symbol).ticket
            
            elif last_21_EMA < last_50_EMA and last_candle_high > last_21_EMA and last_candle_close < last_50_EMA and last_candle_close < last_21_EMA and last_candle_close < last_candle_open and not there_is_open_short_position and lower_highs:
                print("Taking a short position")
                handlers.ring('SystemHand')
                handlers.send_market_order(symbol, "short", stop_loss, risk_reward_ratio, risk_percent)
                last_short_position_ticket = handlers.get_most_recent_position(symbol).ticket
        else:
            handlers.close_all_open_positions(symbol)
    else:
        print("out side of trading time")