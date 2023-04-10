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
                risk_percent=0.25,
                risk_reward_ratio=4.5)
                
handlers.run(
    minutes={0,5,10,15,20,25,30,35,40,45,50,55},
    callback=check_market_callback,
    wait_callback=still_alive)
