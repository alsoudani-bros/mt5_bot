import datetime
import winsound
import time
from threading import Thread


def timer(offset_sec):
    current_time = datetime.datetime.now()
    while True:
        if current_time.second == offset_sec:
            break
        current_time = datetime.datetime.now()

    while True:
        soundProcess = Thread(target=winsound.PlaySound, args=[
                              'SystemQuestion', winsound.SND_ALIAS])
        soundProcess.start()
        time.sleep(300)


timer(50)
