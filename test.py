from ctypes import *
import time


while True:
    windll.user32.BlockInput(True)
    print("blocking")
    time.sleep(2)
    windll.user32.BlockInput(False)
    print("enable")
    time.sleep(2)
