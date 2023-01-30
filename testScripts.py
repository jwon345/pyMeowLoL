import pyMeow as pm
import offsets
import numpy as np
from node import Node, int_from_buffer, float_from_buffer, linked_insert
import keyboard
import pydirectinput
import asyncio

import threading


eName = ["Nami", "TwistedFate", "Jhin", "Amumu",
         "Shen", "PracticeTool_TargetDummy"]

attackSpeedBase = 0.679
attackSpeedRatio = 0
attackWindupPercentage = 0.16
clickDelay = 0.07
rangeExtender = 100

ping = 0.020


width = 3440
height = 1440

# this fixes the latency issue with keypresses
pydirectinput.PAUSE = 0.005


class gameTimes:
    gameTime = 0
    canAttackTime = 0
    canMoveTime = 0


def find_object_pointers(base, max_count=800):
    # Given a memory interface will iterate through objects in memory
    # returns object addresses
    object_pointers = pm.r_int(proc, base + offsets.ObjectManager)
    root_node = Node(root, None)
    addresses_seen = set()
    current_node = root_node
    pointers = set()
    count = 0
    while current_node is not None and count < max_count:
        if current_node.address in addresses_seen:
            current_node = current_node.next
            continue
        addresses_seen.add(current_node.address)
        try:
            data = pm.r_bytes(proc, current_node.address, 0x18)
            count += 1
        except:
            pass
        else:
            for i in range(3):
                child_address = int_from_buffer(data, i * 4)
                if child_address in addresses_seen:
                    continue
                linked_insert(current_node, child_address)
            net_id = int_from_buffer(data, offsets.ObjectMapNodeNetId)
            if net_id - 0x40000000 <= 0x100000:
                # help reduce redundant objects
                pointers.add(int_from_buffer(
                    data, offsets.ObjectMapNodeObject))
        current_node = current_node.next
    return pointers


proc = pm.open_process(processName="League of Legends.exe")

# print(pm.get_module(proc)) 0x201804485A0,


mod = (pm.get_module(proc, "League of Legends.exe"))

print(mod['base'])
print("\n")

rollingOffset = 0
visitedObjects = 0

player = pm.r_int(proc, mod['base'] + offsets.LocalPlayer)
om = pm.r_int(proc, mod['base'] + offsets.ObjectManager)
root = pm.r_int(proc, om + offsets.ObjectMapRoot)
# pointers = find_object_pointers(mod['base'])


# print(pointers)
def list_to_matrix(floats):
    m = np.array(floats)
    return m.reshape(4, 4)


def find_view_proj_matrix(base):
    data = pm.r_bytes(proc, base + offsets.Renderer, 0x8)
    width = int_from_buffer(data, offsets.RendererWidth)
    height = int_from_buffer(data, offsets.RendererHeight)

    data = pm.r_bytes(proc, base + offsets.ViewProjMatrices, 128)
    view_matrix = list_to_matrix(
        [float_from_buffer(data, i * 4) for i in range(16)])
    proj_matrix = list_to_matrix(
        [float_from_buffer(data, 64 + (i * 4)) for i in range(16)])
    view_proj_matrix = np.matmul(view_matrix, proj_matrix)
    return view_proj_matrix.reshape(16)


def world_to_screen(view_proj_matrix, width, height, x, y, z):
    # pasted / translated world to screen math
    clip_coords_x = x * \
        view_proj_matrix[0] + y * view_proj_matrix[4] + \
        z * view_proj_matrix[8] + view_proj_matrix[12]
    clip_coords_y = x * \
        view_proj_matrix[1] + y * view_proj_matrix[5] + \
        z * view_proj_matrix[9] + view_proj_matrix[13]
    clip_coords_w = x * \
        view_proj_matrix[3] + y * view_proj_matrix[7] + \
        z * view_proj_matrix[11] + view_proj_matrix[15]

    if clip_coords_w < 1.:
        clip_coords_w = 1.

    M_x = clip_coords_x / clip_coords_w
    M_y = clip_coords_y / clip_coords_w

    out_x = (width / 2. * M_x) + (M_x + width / 2.)
    out_y = -(height / 2. * M_y) + (M_y + height / 2.)

    if 0 <= out_x <= width and 0 <= out_y <= height:
        return out_x, out_y

    return None, None


async def getTarget():

    lowest = 99999

    for e in eList:
        # is visible
        if (pm.r_bool(proc, e + offsets.ObjVisibility) == False):
            continue

        # is in range
        targetPos = pm.r_floats(proc, e + offsets.ObjPos, 3)
        MePos = pm.r_floats(proc, player + offsets.ObjPos, 3)

        resX = targetPos[0]-MePos[0]
        resZ = targetPos[1]-MePos[1]
        resY = targetPos[2]-MePos[2]
        res = pm.vec3(resX, resY, resZ)
        # print(res)
        if pm.vec3_mag(res) < pm.r_float(proc, player + offsets.objAtkRange) + rangeExtender:
            print(pm.r_float(proc, player + offsets.objAtkRange))
        else:
            continue

        # set if lowest
        if pm.r_float(proc, e + offsets.ObjHealth) < lowest and pm.r_float(proc, e + offsets.ObjHealth) != 0:
            lowest = pm.r_float(proc, e + offsets.ObjHealth)
            pos = (pm.r_floats(proc, e + offsets.ObjPos, 3))

    if lowest != 99999:
        try:
            print("target is " + pm.r_string(proc, e + offsets.ObjPlayerName))
        except:
            print("name cant print")

        return (world_to_screen(find_view_proj_matrix(
            mod['base']), width, height, pos[0], pos[1], pos[2]))
    else:
        return "break"


def ChampCastSpell():

    if (pm.r_bool(proc, player + offsets.ObjCastSpell)):
        a = pm.r_int(proc, player + offsets.ObjSpellBook)
        # n = pm.r_bytes(proc, a, 30)
        n = pm.r_float(proc, a + 0x24)
        print(n)

    #


def GetMissles():
    objectList = find_object_pointers(root)
    missleCount = 0
    b = [0, 0]
    for obj in objectList:
        try:
            missleStartPos = (pm.r_floats(
                proc, obj + offsets.MissileStartPos, 3))
            missleEndPos = (pm.r_floats(proc, obj + offsets.MissileEndPos, 3))

            # if missle startpos within the map and is not an auto attack
            if (missleStartPos[0] > 1 and missleStartPos[0] < 20000
                and missleEndPos[0] > 1 and missleEndPos[0] < 20000
                    and (pm.r_int(proc, obj + offsets.MissileSpellInfo + 0x4) in [0, 1, 2, 3])
                ):

                missleCount += 1

                # pm.draw_text(str(hex(obj) + "  " + str(pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16))), 2500, 200 + 20*missleCount,
                #              20, pm.get_color("white"))

                # if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == 1063):
                #     pm.draw_text("lux Q", 2500, 500 + 20*missleCount,
                #                  20, pm.get_color("white"))
                # if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == 10972):
                #     pm.draw_text("lux E", 2500, 500 + 20*missleCount,
                #                  20, pm.get_color("white"))
                # if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == 26549):
                #     pm.draw_text("lux W", 2500, 500 + 20*missleCount,
                #                  20, pm.get_color("white"))
                # if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == -29353):
                #     pm.draw_text("Draven Q", 2500, 500 + 20*missleCount,
                #                  20, pm.get_color("white"))
                #     continue

                localPlayerPos = pm.r_floats(proc, player + offsets.ObjPos, 3)
                if (missleStartPos[0] < (localPlayerPos[0] + 200)):
                    if (missleStartPos[0] > (localPlayerPos[0] - 200)):
                        if (missleStartPos[2] > (localPlayerPos[2] - 200)):
                            if (missleStartPos[2] < (localPlayerPos[2] + 200)):
                                missleStartPosToScreen = (world_to_screen(find_view_proj_matrix(
                                    mod['base']), width, height, missleStartPos[0], missleStartPos[1], missleStartPos[2]))
                                missleEndPosToScreen = (world_to_screen(find_view_proj_matrix(
                                    mod['base']), width, height, missleEndPos[0], missleEndPos[1], missleEndPos[2]))

                                pm.draw_line(missleStartPosToScreen[0], missleStartPosToScreen[1],
                                             missleEndPosToScreen[0], missleEndPosToScreen[1], pm.get_color("white"), 1)
                                pm.draw_circle(
                                    missleStartPosToScreen[0], missleStartPosToScreen[1], 5, pm.get_color("purple"))
                                pm.draw_circle(
                                    missleEndPosToScreen[0], missleEndPosToScreen[1], 5, pm.get_color("red"))
                                continue

                # print(pm.r_floats(proc, obj + offsets.MissileStartPos, 3))
                # print(pm.r_floats(proc, obj + offsets.MissileEndPos, 3))

                # print(pm.r_string(proc, info))

                missleStartPosToScreen = (world_to_screen(find_view_proj_matrix(
                    mod['base']), width, height, missleStartPos[0], missleStartPos[1], missleStartPos[2]))
                missleEndPosToScreen = (world_to_screen(find_view_proj_matrix(
                    mod['base']), width, height, missleEndPos[0], missleEndPos[1], missleEndPos[2]))

                pm.draw_line(missleStartPosToScreen[0], missleStartPosToScreen[1],
                             missleEndPosToScreen[0], missleEndPosToScreen[1], pm.get_color("white"), 8)
                pm.draw_circle(
                    missleStartPosToScreen[0], missleStartPosToScreen[1], 20, pm.get_color("blue"))
                pm.draw_circle(
                    missleEndPosToScreen[0], missleEndPosToScreen[1], 20, pm.get_color("red"))

            # print(pm.r_floats(proc, y + offsets.MissileEndPos, 3))
        except:

            pass
            # print("issue")


def getAttackTime():
    if (attackSpeedRatio != 0):
        return 1/(attackSpeedBase + (attackSpeedRatio * (pm.r_float(proc, player + offsets.objBonusAtkSpeed))))

    return 1/(attackSpeedBase * (1 + (pm.r_float(proc, player + offsets.objBonusAtkSpeed))))


def attackCycle():
    if gameTimes.gameTime > gameTimes.canAttackTime and not pm.key_pressed(0x04):
        print("attack")
        target = asyncio.run(getTarget())
        try:
            pm.draw_circle(int(target[0]),  int(
                target[1]), 100, pm.get_color("red"))
        except:
            print("fail")
        if target != "break" and target[0] != None:
            m = pm.mouse_position()
            # pm.mouse_move(
            #     int(((target[0]) - m['x'])*2),
            #     int(((target[1]) - m['y'])*-2))
            pydirectinput.moveTo(int(target[0]), int(target[1]))

            pydirectinput.keyDown("j")
            pydirectinput.keyUp("j")

            if (pm.key_pressed(0x04)):
                return
            pydirectinput.moveTo(int(m['x']), int(m['y']))
            if (pm.key_pressed(0x04)):
                return
            pydirectinput.moveTo(int(m['x']), int(m['y']))
            if (pm.key_pressed(0x04)):
                return
            pydirectinput.moveTo(int(m['x']), int(m['y']))
            # pm.mouse_move(
            #     int((m['x']-(target[0]))*2),
            #     int((m['y']-(target[1]))*-2)
            # )

            # make sure mouse moves back
            # if pm.mouse_position

            gameTimes.canAttackTime = gameTimes.gameTime + ping + getAttackTime()
            gameTimes.canMoveTime = gameTimes.gameTime + \
                getAttackTime() * attackWindupPercentage
        # walk
        elif gameTimes.gameTime > gameTimes.canMoveTime:

            pydirectinput.keyDown("k")
            pydirectinput.keyUp("k")
            gameTimes.canMoveTime = gameTimes.gameTime + clickDelay

    # walk
    elif gameTimes.gameTime > gameTimes.canMoveTime:
        pydirectinput.keyDown("k")
        pydirectinput.keyUp("k")

        gameTimes.canMoveTime = gameTimes.gameTime + clickDelay


def printsome():
    print("just a test function to print")


# find objects
c = (find_object_pointers(root))

pm.overlay_init(fps=144)

while True:

    eList = []
    print("finding")
    for obj in c:
        try:
            if (pm.r_int(proc, obj + offsets.ObjName)) is not None:
                n = pm.r_int(proc, obj + offsets.ObjName)
                if (pm.r_string(proc, n) in eName):
                    eList.append(obj)
                    print("found : " + pm.r_string(proc, n))
        except:
            pass

    print("done")

    while pm.overlay_loop():
        gameTimes.gameTime = pm.r_float(proc, mod['base'] + offsets.GameTime)
        if (pm.key_pressed(0x06)) and gameTimes.gameTime > gameTimes.canMoveTime:
            attackThread = threading.Thread(target=attackCycle)
            attackThread.start()
            attackThread.join()

        pm.begin_drawing()
        pm.draw_fps(3000, 200)

        GetMissles()
        # ChampCastSpell()

        try:
            if (pm.r_bool(proc, player + offsets.ObjCastSpell)):
                pass
                # print("spellcasting")
        except:
            print("game Ended")
            input()

            # MePos = pm.r_floats(proc, player + offsets.ObjPos, 3)
            # attackRadius = pm.r_float(proc, player + offsets.objAtkRange)
            # MeScreenPos = (world_to_screen(find_view_proj_matrix(
            #     mod['base']), width, height, MePos[0], MePos[1], MePos[2]))
            # try:
            #     pm.draw_ellipse_lines(int(MeScreenPos[0]), int(
            #         MeScreenPos[1])+50, attackRadius, attackRadius * 0.8, pm.get_color("white"))
            # except:
            #     print("offscreen")

        pm.end_drawing()
