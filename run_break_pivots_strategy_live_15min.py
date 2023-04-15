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
                time_frame="15min",
                risk_percent=0.25,
                risk_reward_ratio=1.1,
                start_break_hour=13,
                start_break_minute=30,
                end_break_hour=17,
                end_break_minute=0)
                
handlers.run(
    minutes={15, 30, 45, 0},
    callback=check_market_callback,
    wait_callback=still_alive)
