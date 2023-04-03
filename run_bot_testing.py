from dotenv import dotenv_values
import handlers
import main
config = dotenv_values(".env")

login = config.get("MT_LOGIN")
password = config.get("MT_PASSWORD")
# server = "MetaQuotes-Demo"
server="FTMO-Demo"



handlers.establish_MT5_connection(login, server, password)



def still_alive():
    pass

def check_market_callback():
    break_end_hour = 17
    break_end_minute = 0
    risk_reward_ratio = 3
    if symbol != "US100.cash":
        break_end_hour = 17
        break_end_minute = 0
        risk_reward_ratio = 1
    main.check_market(symbol=symbol,
                time_frame="15min",
                stage_one_risk_percent=0.1,
                stage_two_risk_percent=0.2,
                stages_cut_profit_percent=2.5,
                risk_reward_ratio=risk_reward_ratio,
                starting_balance_for_the_week=198000,
                break_start_hour=13,
                break_start_minute=30,
                break_end_hour=break_end_hour,
                break_end_minute=break_end_minute,
                max_positions_open_at_once_per_direction=10)
    



symbol= input("Enter the symbol you want to trade: ").strip()
print(symbol)
handlers.run(
    minutes={15, 30, 45, 0},
    callback=check_market_callback,
    wait_callback=still_alive)
