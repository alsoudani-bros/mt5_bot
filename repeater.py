from datetime import datetime, timedelta
from time import sleep


def run(wait_callback, callback, **kwargs):
    minutes = kwargs.get("minutes", {0})
    hours = kwargs.get("hours")

    while True:
        if (datetime.now().second == 0 and (datetime.now().minute in minutes and (hours is None or datetime.now().hour in hours))):
            print(datetime.now())
            callback()
            sleep(1)
        else:
            print(datetime.now())
            wait_callback()
            sleep(.5)

