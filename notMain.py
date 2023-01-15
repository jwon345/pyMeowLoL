import pyautogui
import keyboard
import time
import pydirectinput

xOffset = 800
yOffset = 300

xPlayerOffset = 100
yPlayerOffset = 150

mouseSpeed = 0.001


def findAndMove():
    location = pyautogui.locateCenterOnScreen(
        "enemyIconLvl1.png", region=(xOffset, yOffset, 1000, 1000), grayscale=True, confidence=0.91)
    print(location)

    try:
        originalPos = pyautogui.position()
        pydirectinput.moveTo(location[0] + xPlayerOffset,
                             location[1] + yPlayerOffset, mouseSpeed)
        pydirectinput.mouseDown()
        pydirectinput.mouseUp()
        pydirectinput.moveTo(originalPos[0], originalPos[1], mouseSpeed)
        # pyautogui.moveto(location[0], location[1], 10)
    except:
        print('move issue')


while True:  # making a loop
    time.sleep(0.02)
    if keyboard.is_pressed('a'):  # if key 'q' is pressed
        findAndMove()
