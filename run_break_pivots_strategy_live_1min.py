from dotenv import dotenv_values
import handlers
import break_pivots_strategy_single_market_order
config = dotenv_values(".env")


login = config.get("MT_LOGIN")
password = config.get("MT_PASSWORD")
server="FTMO-Demo"

handlers.establish_MT5_connection(login, server, password)

def still_alive():
    pass
    
def check_market_callback():
    break_pivots_strategy_single_market_order.check_market(
                time_frame="1min",
                risk_percent=0.05,
                risk_reward_ratio=1.1)
                
handlers.run_every_minute(
    callback=check_market_callback,
    wait_callback=still_alive)
