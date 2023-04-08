from dotenv import dotenv_values
import handlers
import break_pivots_strategy_single_market_order
config = dotenv_values(".env")

login = config.get("MT_LOGIN")
password = config.get("MT_PASSWORD")
# server = "MetaQuotes-Demo"
server="FTMO-Demo"



handlers.establish_MT5_connection(login, server, password)



def still_alive():
    pass

def check_market_callback():
    break_pivots_strategy_single_market_order.check_market(symbol=symbol,
                time_frame="15min",
                risk_percent=0.25,
                risk_reward_ratio=2,
                starting_balance_for_the_week=200000)
    



symbol= input("Enter the symbol you want to trade: ").strip()
print(symbol)
handlers.run(
    minutes={15, 30, 45, 0},
    callback=check_market_callback,
    wait_callback=still_alive)
