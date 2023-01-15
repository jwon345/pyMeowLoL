import time
import pyMeow as pm
import keyboard


xSearchBase = 1050
ySearchBase = 50

xSearchSize = 1350
ySearchSize = 1300

# xSearchBase = 1175
# ySearchBase = 100

# xSearchSize = 1100
# ySearchSize = 1100

xPlayerOffset = 100
yPlayerOffset = 150

# screen settings

screenX = 3440
screenY = 1440

textBase = 3000


def overlay():

    attackSpeed = 1

    counter = 0

    pm.overlay_init()

    while pm.overlay_loop():

        time.sleep(0.05)
        pm.begin_drawing()

        pm.draw_fps(textBase, 100)
        pm.draw_text("attack Speed-" + str(attackSpeed),
                     textBase, 130, 20, pm.get_color("red"))

        pm.gui_window_box(textBase, 300, 100, 100, "chagne")
        pm.gui_slider(100, 100, 100, 100, "sdf", "asdf", 0, 0, 1)

        # hitbox
        pm.draw_rectangle_lines(xSearchBase, ySearchBase, xSearchSize,
                                ySearchSize, pm.get_color("white"), 1)

        pm.end_drawing()

        if keyboard.is_pressed(";"):
            print(attackSpeed, flush=True)

        if keyboard.is_pressed(","):
            counter = 0
            attackSpeed -= 0.05
            attackSpeed = round(attackSpeed, 2)
            print(attackSpeed, flush=True)

        if keyboard.is_pressed("."):
            counter = 0
            attackSpeed += 0.05
            attackSpeed = round(attackSpeed, 2)
            print(attackSpeed, flush=True)

        # if pm.key_pressed(190):
        #     counter += 1
        #     if counter > 15:
        #         counter = 0
        #         attackSpeed += 0.05
        #         attackSpeed = round(attackSpeed, 2)
        #         print(attackSpeed, flush=True)


overlay()
