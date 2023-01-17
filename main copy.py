import pyMeow as pm
import pyautogui
import time
import pydirectinput
import subprocess
import sys

xSearchBase = 1050
ySearchBase = 50

xSearchSize = 1350
ySearchSize = 1300

# xSearchBase = 1175
# ySearchBase = 100

# xSearchSize = 1100
# ySearchSize = 1100

xPlayerOffset = 115
yPlayerOffset = 150

# screen settings

screenX = 3440
screenY = 1440

textBase = 3000


mouseSpeed = 0.001

confidence = 0.5

gameTime = 0



attackSpeed = 0.7
attackWindPercentage = 0.38

Orbwalk = False
orbCounter = 0

stateMachine = 0

# this fixes the latency issue with keypresses
pydirectinput.PAUSE = 0.02

# allows it to run
# PYDEVD_DISABLE_FILE_VALIDATION = 1
# proc = subprocess.Popen([sys.executable, 'overlay.py'])
proc = subprocess.Popen([sys.executable, 'overlay.py'], stdout=subprocess.PIPE)


def findAndMove2():
    location = pyautogui.locateCenterOnScreen(
        "enemyIconLvl1.png", region=(xSearchBase, ySearchBase, xSearchSize, ySearchSize), confidence=confidence)
    print(location)

    m = pm.mouse_position()

    try:
        print(int(location.x-m['x']))
        print(int(location.y-m['y']))
        pm.mouse_move(
            int(((location.x + 50) - m['x'])*2),
            int(((location.y + 150)-m['y'])*-2))

        pydirectinput.keyDown("j")
        pydirectinput.keyUp("j")

        pm.mouse_move(
            int((m['x']-(location.x + 50))*2),
            int((m['y']-(location.y + 150))*-2)
        )

        print("\a")

        time.sleep((1/attackSpeed) * attackWindPercentage)
        # print("windup : " + str((1/attackSpeed) * attackWindPercentage))

        # interval = (((1/attackSpeed) * (1-(attackWindPercentage*2)))/10)

        pydirectinput.keyDown("k")
        pydirectinput.keyUp("k")

        # print("next : " + str((1/attackSpeed) * (1-(attackWindPercentage*2))))

        time.sleep((1/attackSpeed) * (1-(attackWindPercentage*2)))


    except:
        print("issues")


def findAndMove():
    location = pyautogui.locateCenterOnScreen(
        "enemyIconLvl1.png", region=(xSearchBase, ySearchBase, xSearchSize, ySearchSize), confidence=confidence)
    print(location)

    # show where they are
    # try:
    #     pm.begin_drawing()
    #     pm.draw_rectangle(location.x, location.y, 100,
    #                       100, pm.get_color("pink"))
    #     pm.end_drawing()
    # except:
    #     print(1)

    m = pm.mouse_position()
    print(m)

    # try:
    #     print(int(location.x-m['x']))
    #     print(int(location.y-m['y']))
    #     pm.mouse_move(
    #         int((screenX/2) + ((location.x + 50) - m['x'])*2),
    #         int((screenY/2) + ((location.y + 150)-m['y'])*-2))

    #     pydirectinput.keyDown("j")
    #     pydirectinput.keyUp("j")

    #     pm.mouse_move(
    #         int((screenX/2) + (m['x']-(location.x + 50))*2),
    #         int((screenY/2) + (m['y']-(location.y + 150))*-2)
    #     )

    # except:
    #     print("issues")

    try:
        print(int(location.x-m['x']))
        print(int(location.y-m['y']))
        pm.mouse_move(
            int(((location.x + 50) - m['x'])*2),
            int(((location.y + 150)-m['y'])*-2))

        pydirectinput.keyDown("j")
        pydirectinput.keyUp("j")

        pm.mouse_move(
            int((m['x']-(location.x + 50))*2),
            int((m['y']-(location.y + 150))*-2)
        )

    except:
        print("issues")


while True:
    time.sleep(0.05)

    

    if pm.key_pressed(65):
        print("with as" + str(attackSpeed))
        findAndMove()
    if (pm.key_pressed(90)):
        findAndMove2()

    if (pm.key_pressed(88)):
        print("pressed x")

    if (pm.key_pressed(190) or pm.key_pressed(188)):
        time.sleep(0.005)
        result = proc.stdout.readline().decode().replace("\n", "").replace("\r", "")
        try:
            print("attack set " + str(result))
            attackSpeed = float(result)
        except:
            print("failed... got" + str(result))
