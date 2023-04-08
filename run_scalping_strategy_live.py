from dotenv import dotenv_values
import handlers
import scalping_strategy
config = dotenv_values(".env")

login = config.get("CHALLANGE_MT_LOGIN")
password = config.get("CHALLANGE_MT_PASSWORD")
server="FTMO-Server"

handlers.establish_MT5_connection(login, server, password)

def still_alive():
    pass

def check_market_callback():
    scalping_strategy.check_market(
                time_frame="1min",
                risk_percent=0.25,
                risk_reward_ratio=1,
                starting_balance_for_the_week=200000)

handlers.run_every_minute(
    callback=check_market_callback,
    wait_callback=still_alive)