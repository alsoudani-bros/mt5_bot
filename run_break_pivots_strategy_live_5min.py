from dotenv import dotenv_values
import handlers
import break_pivots_strategy_single_market_order
config = dotenv_values(".env")


login = config.get("CHALLANGE_MT_LOGIN")
password = config.get("CHALLANGE_MT_PASSWORD")
server="FTMO-Server"

handlers.establish_MT5_connection(login, server, password)

def still_alive():
    pass
    
def check_market_callback():
    break_pivots_strategy_single_market_order.check_market(
                time_frame="5min",
                risk_percent=0.1,
                risk_reward_ratio=7,
                max_gap_size=100,
                max_breaking_candle_size=100,
                start_trading_hour=6,
                start_trading_minute=0,
                end_trading_hour=9,
                end_trading_minute=0)
                
handlers.run(
    minutes={0,5,10,15,20,25,30,35,40,45,50,55},
    callback=check_market_callback,
    wait_callback=still_alive)
