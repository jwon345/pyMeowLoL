import pyMeow as pm
import subprocess
import sys
import time
import offsets
import numpy as np
from node import Node, int_from_buffer, float_from_buffer, linked_insert
import keyboard
import pydirectinput
import asyncio

import threading


eName = ["Kassadin", "Brand", "Jhin", "Jax",
         "Kindred", "PracticeTool_TargetDummy"]

attackSpeedBase = 0.6
attackWindupPercentage = 0.18
clickDelay = 0.07
rangeExtender = 25

ping = 0.020


width = 3440
height = 1440

# this fixes the latency issue with keypresses
pydirectinput.PAUSE = 0.005


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
        print("loop")
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


print(pm.enum_processes())

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


def getAttackTime():
    return 1/(attackSpeedBase * (1 + (pm.r_float(proc, player + offsets.objBonusAtkSpeed))))


# find objects
c = (find_object_pointers(root))

while True:

    # print(pm.r_float(proc, mod['base'] + offsets.GameTime))
    # print(pm.r_floats(proc, player + 0x1DC, 2))  # position?
    # print(pm.r_float(proc, player + 0x132C))  # as
    # print(pm.r_float(proc, player + 0x13A4))  # attack range

    # print(pm.r_float(proc, player + offsets.ObjHealth))
    # print(pm.r_float(proc, player + offsets.ObjHealth))
    # print(pm.r_string(proc, player + offsets.ObjName))

    # print(pm.r_int(proc, root))

    # print(pm.r_int(proc, pm.r_int(proc, root)))

    # print(find_view_proj_matrix(mod['base']))

    # time.sleep(5)

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

    gameTime = 0
    canAttackTime = 0
    canMoveTime = 0

    while True:

        time.sleep(0.02)

        gameTime = pm.r_float(proc, mod['base'] + offsets.GameTime)
        if keyboard.is_pressed("a"):
            if gameTime > canAttackTime and not pm.key_pressed(0x04):
                print("attack")
                target = asyncio.run(getTarget())
                if target != "break" and target[0] != None:
                    m = pm.mouse_position()
                    # pm.mouse_move(
                    #     int(((target[0]) - m['x'])*2),
                    #     int(((target[1]) - m['y'])*-2))
                    pydirectinput.moveTo(int(target[0]), int(target[1]))

                    pydirectinput.keyDown("j")
                    pydirectinput.keyUp("j")

                    time.sleep(0.01)
                    if (pm.key_pressed(0x04)):
                        break
                    pydirectinput.moveTo(int(m['x']), int(m['y']))
                    if (pm.key_pressed(0x04)):
                        break
                    pydirectinput.moveTo(int(m['x']), int(m['y']))
                    if (pm.key_pressed(0x04)):
                        break
                    pydirectinput.moveTo(int(m['x']), int(m['y']))
                    # pm.mouse_move(
                    #     int((m['x']-(target[0]))*2),
                    #     int((m['y']-(target[1]))*-2)
                    # )

                    # make sure mouse moves back
                    # if pm.mouse_position

                    canAttackTime = gameTime + ping + getAttackTime()
                    canMoveTime = gameTime + getAttackTime() * attackWindupPercentage
                # walk
                elif gameTime > canMoveTime:

                    pydirectinput.keyDown("k")
                    pydirectinput.keyUp("k")
                    canMoveTime = gameTime + clickDelay

            # walk
            elif gameTime > canMoveTime:
                pydirectinput.keyDown("k")
                pydirectinput.keyUp("k")

                canMoveTime = gameTime + clickDelay

        # for e in eList:
        #     # is visible
        #     if (pm.r_bool(proc, e + offsets.ObjVisibility) == False):
        #         continue

        #     # is in range
        #     targetPos = pm.r_floats(proc, e + offsets.ObjPos, 3)
        #     MePos = pm.r_floats(proc, player + offsets.ObjPos, 3)

        #     resX = targetPos[0]-MePos[0]
        #     resZ = targetPos[1]-MePos[1]
        #     resY = targetPos[2]-MePos[2]
        #     res = pm.vec3(resX, resY, resZ)
        #     # print(res)
        #     if pm.vec3_mag(res) < pm.r_float(proc, player + offsets.objAtkRange):
        #         print(pm.r_float(proc, player + offsets.objAtkRange))
        #     else:
        #         continue
        #     # set if lowest

        #     print(pm.r_string(proc, e + offsets.ObjPlayerName))
        #     # print(pm.r_floats(proc, e + offsets.ObjPos, 3))
        #     # print(pm.r_bool(proc, e + offsets.ObjVisibility))
        #     pos = (pm.r_floats(proc, e + offsets.ObjPos, 3))
        #     print(world_to_screen(find_view_proj_matrix(
        #         mod['base']), width, height, pos[0], pos[1], pos[2]))
        #     mouseMov = (world_to_screen(find_view_proj_matrix(
        #         mod['base']), width, height, pos[0], pos[1], pos[2]))
        #     print('\n')

        # print('\n\n\n\n\njjjjjjjjjjjjj')
