import pyMeow as pm
import offsets
import numpy as np
from node import Node, int_from_buffer, float_from_buffer, linked_insert
import pydirectinput
import asyncio

import time
from champList import champNames
from stats import champStats
from skillshotlist import dontDraw

import threading

attackSpeedBase = 0.6
attackSpeedRatio = 0
attackWindupPercentage = 0.2
clickDelay = 0.07
rangeExtender = 100

dodgekey = "w"

ping = 0.050


width = 3440
height = 1440

# this fixes the latency issue with keypresses
pydirectinput.PAUSE = 0.005


class gameTimes:
    gameTime = 0
    canAttackTime = 0
    canMoveTime = 0


class dodgeClass:
    dodge = False
    pos = [0, 0]
    lastDodgeTime = 0


class drawItems:
    attackspeedText = 0
    debugText = ""
    debugTextMem = ""


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
print("here is base")
print(hex(mod['base']))
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
    print(view_proj_matrix.reshape(16))
    return view_proj_matrix.reshape(16)


def world_to_screen(view_proj_matrix, width, height, x, y, z, offscreen=False):
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

    # print(out_x, out_y)

    if offscreen:
        if -width <= out_x <= width*2 and -height <= out_y <= height*2:
            return out_x, out_y
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
            print("target pos " + str(pm.r_floats(proc, e + offsets.ObjPos, 3)))
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
        size = 3

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

                drawItems.debugText = str(pm.r_ints(
                    proc, obj + offsets.MissileSpellInfo, 20))
                drawItems.debugTextMem = str(hex(obj))

                print(str(hex(obj) + "  " + str(pm.r_ints16(proc,
                      obj + offsets.MissileSpellInfo, 10))))

                if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == 1063):
                    pm.draw_text("lux Q", 2500, 500 + 20*missleCount,
                                 20, pm.get_color("white"))
                    size = 10

                if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == 10972):
                    pm.draw_text("lux E", 2500, 500 + 20*missleCount,
                                 20, pm.get_color("white"))
                    size = 10
                if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == 26549):
                    pm.draw_text("lux W", 2500, 500 + 20*missleCount,
                                 20, pm.get_color("white"))

                if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == 32210):
                    pm.draw_text("Blitz Q", 2500, 500 + 20*missleCount,
                                 20, pm.get_color("white"))

                if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == -29353):
                    pm.draw_text("Draven Q", 2500, 500 + 20*missleCount,
                                 20, pm.get_color("white"))
                    continue
                if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == 2433):
                    pm.draw_text("Kaisa Q", 2500, 500 + 20*missleCount,
                                 20, pm.get_color("white"))
                    continue
                if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == 13001):
                    pm.draw_text("Ashe W", 2500, 500 + 20*missleCount,
                                 20, pm.get_color("white"))
                    continue
                if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == -14079):
                    # pm.draw_text("Zeri Q", 2500, 500 + 20*missleCount, 20, pm.get_color("white"))
                    continue
                if (pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16) == -4798):
                    pm.draw_text("Kalista e", 2500, 500 + 20*missleCount,
                                 20, pm.get_color("white"))
                    continue

                if (dontDraw(pm.r_int16(proc, obj + offsets.MissileSpellInfo + 16))):
                    continue

                localPlayerPos = pm.r_floats(proc, player + offsets.ObjPos, 3)
                localPlayerScreenPos = (world_to_screen(find_view_proj_matrix(
                    mod['base']), width, height, localPlayerPos[0], localPlayerPos[1], localPlayerPos[2] + 50))

                # me spell thin

                # if (missleStartPos[0] < (localPlayerPos[0] + 200)):
                #     if (missleStartPos[0] > (localPlayerPos[0] - 200)):
                #         if (missleStartPos[2] > (localPlayerPos[2] - 200)):
                #             if (missleStartPos[2] < (localPlayerPos[2] + 200)):
                #                 missleStartPosToScreen = (world_to_screen(find_view_proj_matrix(
                #                     mod['base']), width, height, missleStartPos[0], missleStartPos[1], missleStartPos[2]))
                #                 missleEndPosToScreen = (world_to_screen(find_view_proj_matrix(
                #                     mod['base']), width, height, missleEndPos[0], missleEndPos[1], missleEndPos[2]))

                #                 pm.draw_line(missleStartPosToScreen[0], missleStartPosToScreen[1],
                #                              missleEndPosToScreen[0], missleEndPosToScreen[1], pm.get_color("white"), 1)
                #                 pm.draw_circle(
                #                     missleStartPosToScreen[0], missleStartPosToScreen[1], 5, pm.get_color("purple"))
                #                 pm.draw_circle(
                #                     missleEndPosToScreen[0], missleEndPosToScreen[1], 5, pm.get_color("red"))
                #                 continue

                # print(pm.r_floats(proc, obj + offsets.MissileStartPos, 3))
                # print(pm.r_floats(proc, obj + offsets.MissileEndPos, 3))

                # print(pm.r_string(proc, info))

                ##
                # Draw the missle
                ##

                missleStartPosToScreen = (world_to_screen(find_view_proj_matrix(
                    mod['base']), width, height, missleStartPos[0], (missleStartPos[1]) + 50, missleStartPos[2], offscreen=True))
                missleEndPosToScreen = (world_to_screen(find_view_proj_matrix(
                    mod['base']), width, height, missleEndPos[0], (missleEndPos[1]) + 50, missleEndPos[2], offscreen=True))

                if missleStartPos[0] == None and missleStartPos[1] == None and missleEndPos[0] == None and missleEndPos[1] == None:
                    continue

                pm.draw_line(missleStartPosToScreen[0], missleStartPosToScreen[1],
                             missleEndPosToScreen[0], missleEndPosToScreen[1], pm.get_color("white"), size)
                pm.draw_circle(
                    missleStartPosToScreen[0], missleStartPosToScreen[1], 20, pm.get_color("blue"))
                pm.draw_circle(
                    missleEndPosToScreen[0], missleEndPosToScreen[1], 20, pm.get_color("red"))

                # print(localPlayerPos)

                # getting perpendicular
                vector = [0, 0]
                vector[0] = missleEndPos[0] - missleStartPos[0]
                vector[1] = missleEndPos[2] - missleStartPos[2]
                magnitude = (vector[0]**2 + vector[1]**2)**0.5
                unitLength = [0, 0]
                unitLength[0] = vector[0]/magnitude * 200
                unitLength[1] = vector[1]/magnitude * 200

                # my perpendicular distance test function
                # perpendicularLengthDataArray = np.array([missleStartPosToScreen[0], missleStartPosToScreen[1]],[missleEndPosToScreen[0], missleEndPosToScreen[1]], [localPlayerScreenPos[0], localPlayerScreenPos[1]])

                # pm.draw_line(localPlayerPos[0], localPlayerPos[2], localPlayerPos[0] - unitLength[2], localPlayerPos[2] + unitLength[0], 10 ,pm.get_color("purple"))

                # pm.draw_line(localPlayerPos[0], localPlayerPos[2], localPlayerPos[0] -
                #              100, localPlayerPos[2] + 100, pm.get_color("purple"), 10)

                playerToMissle = [missleEndPosToScreen[0] - localPlayerScreenPos[0],
                                  missleEndPosToScreen[1] - localPlayerScreenPos[1]]

                dodgeUp = [
                    (localPlayerScreenPos[0] + playerToMissle[0]) - (localPlayerScreenPos[0] + unitLength[1]), (localPlayerScreenPos[1] + playerToMissle[1]) - (localPlayerScreenPos[1] + unitLength[0])]
                dodgeDown = [
                    (localPlayerScreenPos[0] + playerToMissle[0]) - (localPlayerScreenPos[0] - unitLength[1]), (localPlayerScreenPos[1] + playerToMissle[1]) - (localPlayerScreenPos[1] - unitLength[0])]

                dodgeUpMagnitude = (dodgeUp[0]**2 + dodgeUp[1]**2)**0.5
                dodgeDownMagnitude = (dodgeDown[0]**2 + dodgeDown[1]**2)**0.5

                if dodgeUpMagnitude < 1000:
                    print("toofar")
                    # dodge lines
                    pm.draw_line(
                        localPlayerScreenPos[0], localPlayerScreenPos[1], localPlayerScreenPos[0] - unitLength[1], localPlayerScreenPos[1] - unitLength[0], pm.get_color("red"), 1)
                    pm.draw_line(
                        localPlayerScreenPos[0], localPlayerScreenPos[1], localPlayerScreenPos[0] + unitLength[1], localPlayerScreenPos[1] + unitLength[0], pm.get_color("blue"), 1)

                    # middle plyaer to missle end point
                    pm.draw_line(
                        localPlayerScreenPos[0], localPlayerScreenPos[1], localPlayerScreenPos[0] + playerToMissle[0], localPlayerScreenPos[1] + playerToMissle[1], pm.get_color("purple"), 1)

                    # player dodge points to misslew
                    pm.draw_line(
                        localPlayerScreenPos[0] + unitLength[1], localPlayerScreenPos[1] + unitLength[0], localPlayerScreenPos[0] + playerToMissle[0], localPlayerScreenPos[1] + playerToMissle[1], pm.get_color("green"), 2)
                    pm.draw_line(
                        localPlayerScreenPos[0] - unitLength[1], localPlayerScreenPos[1] - unitLength[0], localPlayerScreenPos[0] + playerToMissle[0], localPlayerScreenPos[1] + playerToMissle[1], pm.get_color("green"), 2)

                if (pm.key_pressed(0x53)):
                    # if the dodge radius is too far dont
                    if dodgeUpMagnitude > 400:
                        print("toofar")
                        continue
                    # if within range dodge initiate

                    dodgeClass.dodge = True
                    # choosing to dodge up or down
                    if dodgeUpMagnitude < dodgeDownMagnitude:
                        dodgeClass.pos = [int(
                            localPlayerScreenPos[0] - unitLength[1]), int(localPlayerScreenPos[1] - unitLength[0])]
                    else:
                        dodgeClass.pos = [int(
                            localPlayerScreenPos[0] + unitLength[1]), int(localPlayerScreenPos[1] + unitLength[0])]
                    #     pydirectinput.moveTo(int(
                    #         localPlayerScreenPos[0] - unitLength[1]), int(localPlayerScreenPos[1] - unitLength[0]))
                    # else:
                    #     pydirectinput.moveTo(int(
                    #         localPlayerScreenPos[0] + unitLength[1]), int(localPlayerScreenPos[1] + unitLength[0]))

            # print(pm.r_floats(proc, y + offsets.MissileEndPos, 3))
        except:
            pass
            # print("issue")


def getAttackTime():
    if champ == "zeri":

        return max([1/(attackSpeedBase + (attackSpeedRatio * (pm.r_float(proc, player + offsets.objBonusAtkSpeed)))), 1/1.5])
    if (attackSpeedRatio != 0):
        drawItems.attackspeedText = (attackSpeedBase + (attackSpeedRatio *
                                                        (pm.r_float(proc, player + offsets.objBonusAtkSpeed))))
        return 1/(attackSpeedBase + (attackSpeedRatio * (pm.r_float(proc, player + offsets.objBonusAtkSpeed))))

    drawItems.attackspeedText = (
        attackSpeedBase * (1 + (pm.r_float(proc, player + offsets.objBonusAtkSpeed))))
    return 1/(attackSpeedBase * (1 + (pm.r_float(proc, player + offsets.objBonusAtkSpeed))))


def attackCycle():

    # dodging
    if (dodgeClass.dodge and pm.key_pressed(0x04) == False and pm.key_pressed(0x53)):
        if (gameTimes.gameTime > dodgeClass.lastDodgeTime + 10):
            dodgeClass.dodge = False
            pydirectinput.moveTo(dodgeClass.pos[0], dodgeClass.pos[1])
            pydirectinput.keyDown(dodgekey)
            pydirectinput.keyUp(dodgekey)
            pydirectinput.keyDown("k")
            pydirectinput.keyUp("k")
            dodgeClass.lastDodgeTime = gameTimes.gameTime
            gameTimes.canMoveTime = gameTimes.gameTime + clickDelay
            return
        if (gameTimes.gameTime >= gameTimes.canMoveTime):
            dodgeClass.dodge = False
            pydirectinput.moveTo(dodgeClass.pos[0], dodgeClass.pos[1])
            pydirectinput.keyDown(dodgekey)
            pydirectinput.keyUp(dodgekey)
            pydirectinput.keyDown("k")
            pydirectinput.keyUp("k")
            dodgeClass.lastDodgeTime = gameTimes.gameTime
            gameTimes.canMoveTime = gameTimes.gameTime + clickDelay

        gameTimes.canMoveTime = gameTimes.gameTime + clickDelay

    if gameTimes.gameTime > gameTimes.canAttackTime and pm.key_pressed(0x06) and not pm.key_pressed(0x04):

        target = asyncio.run(getTarget())
        try:
            pm.draw_circle(int(target[0]),  int(
                target[1]), 100, pm.get_color("red"))
        except:
            print("fail")
        if target != "break" and target[0] != None:
            m = pm.mouse_position()
            pydirectinput.moveTo(int(target[0]), int(target[1]))

            # pydirectinput.keyDown("q")
            # pydirectinput.keyUp("q")
            pydirectinput.keyDown("j")
            pydirectinput.keyUp("j")

            if (pm.key_pressed(0x04)):
                return
            pydirectinput.moveTo(int(m['x']), int(m['y']))
            if (pm.key_pressed(0x04)):
                return
            pydirectinput.moveTo(int(m['x']), int(m['y']))

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

    # A button click => auto anything
    # wip make it get target lowest minion
    elif gameTimes.gameTime > gameTimes.canAttackTime and pm.key_pressed(0x41) and not pm.key_pressed(0x04):
        pydirectinput.keyDown("x")
        pydirectinput.keyUp("x")

        time.sleep(0.01)

        if (pm.key_pressed(0x04)):
            return
        gameTimes.canAttackTime = gameTimes.gameTime + ping + getAttackTime()
        gameTimes.canMoveTime = gameTimes.gameTime + \
            getAttackTime() * attackWindupPercentage
        return

    # walk
    elif gameTimes.gameTime > gameTimes.canMoveTime:
        pydirectinput.keyDown("k")
        pydirectinput.keyUp("k")

        gameTimes.canMoveTime = gameTimes.gameTime + clickDelay


def printsome():
    print("just a test function to print")


def drawshit():

    # pm.draw_text((str(drawItems.attackspeedText)),
    #              2500, 200, 20, pm.get_color("white"))

    # pm.draw_text((str(pm.r_floats(proc, player + offsets.ObjPos, 3))),
    #              3000, 400, 20, pm.get_color("white"))
    # pm.draw_text(drawItems.debugTextMem + "  " +
    #              drawItems.debugText, 500, 200, 20, pm.get_color("white"))
    pass
######
# MAIN START
#####


print(pm.r_floats(proc, player + offsets.ObjPos, 3))
champ = pm.r_string(proc, pm.r_int(proc, player + offsets.ObjName)).lower()
if (champ in champStats):
    attackSpeedBase = champStats[champ]["attackSpeedBase"]
    attackSpeedRatio = champStats[champ]["attackSpeedRatio"]
    attackWindupPercentage = champStats[champ]["attackWindupPercentage"]
    print("stats of " + champ)

# find objects
c = (find_object_pointers(root))

pm.overlay_init(fps=144)


eList = []
print("finding")
for obj in c:
    try:
        if (pm.r_int(proc, obj + offsets.ObjName)) is not None:
            n = pm.r_int(proc, obj + offsets.ObjName)
            if (pm.r_string(proc, n).lower() in champNames):
                if (pm.r_int(proc, obj + offsets.ObjTeam) != pm.r_int(proc, player + offsets.ObjTeam)):
                    eList.append(obj)
                    print("found enemy : " + pm.r_string(proc, n))
                else:
                    print("found team : " + pm.r_string(proc, n))

    except:
        pass

print("found " + str(len(eList)) + "/5")

while pm.overlay_loop():
    gameTimes.gameTime = pm.r_float(proc, mod['base'] + offsets.GameTime)
    if ((pm.key_pressed(0x06) or pm.key_pressed(0x41) or pm.key_pressed(0x53))) and gameTimes.gameTime > gameTimes.canMoveTime:
        attackThread = threading.Thread(target=attackCycle)
        attackThread.start()
        attackThread.join()

    pm.begin_drawing()
    pm.draw_fps(3000, 200)

    GetMissles()
    # ChampCastSpell()

    drawshit()

    try:
        if (pm.r_bool(proc, player + offsets.ObjCastSpell)):
            pass
            # print("spellcasting")
    except:
        # input poll when game ended?
        print("game Ended")
        break

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
