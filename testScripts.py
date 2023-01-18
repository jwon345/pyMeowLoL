import pyMeow as pm
import subprocess
import sys
import time
import offsets
import numpy as np
from node import Node, int_from_buffer, float_from_buffer, linked_insert

eName = ["L/ucian", "Brand", "Caitlyn", "Malphite",
         "Kayle", "PracticeTool_TargetDummy"]


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

    width = 3440
    height = 1440

    eList = []
    print("finding")
    for obj in c:
        try:

            if (pm.r_int(proc, obj + offsets.ObjName)) is not None:
                n = pm.r_int(proc, obj + offsets.ObjName)
                if (pm.r_string(proc, n) in eName):
                    eList.append(obj)
                    print("good")

            # eList.append(obj)

            # if (pm.r_string(proc, obj + offsets.ObjPlayerName)) == "Target Dummy":

            #     print(pm.r_string(proc, obj + offsets.ObjName))
            #     print(pm.r_string(proc, pm.r_int(proc, obj + offsets.ObjName)))
            #     time.sleep(10)

            # if (pm.r_string(proc, obj + offsets.ObjPlayerName) == "Jax Bot"):
            #     while True:
            #         time.sleep(1)
            #         # print(pm.r_floats(proc, player + 0x1DC, 3))  # position?

            #         print(pm.r_string(proc, obj + offsets.ObjPlayerName))
            #         print(pm.r_string(proc, obj + offsets.ObjName))
            #         n = pm.r_int(proc, obj + offsets.ObjName)
            #         print(n)
            #         name = (pm.r_string(proc, n))
            #         if name == "Jax":
            #             print("yes")
            #         print("\n")

            #         pos = (pm.r_floats(proc, player + 0x1DC, 3))  # playerPos?2
            #         print(world_to_screen(find_view_proj_matrix(
            #             mod['base']), width, height, pos[0], pos[1], pos[2]))

        except:
            pass
            # print("pass")

            # print(pm.r_floats(proc, obj + offsets.ObjPos, 2))
            # print(bytes.decode(pm.r_string(proc, obj + offsets.ObjName)))
    # print(pm.r_string(proc, om + (1506535 * 0x18) + offsets.ObjName))
    # print(pm.r_float(proc, om + (1506535 * 0x18) + offsets.ObjHealth))
    # print(pm.r_string(proc, om + (1833941 * 0x18) + offsets.ObjName))
    # print(pm.r_float(proc, om + (1833941 * 0x18) + offsets.ObjHealth))

    print("done")

    while True:
        for e in eList:


            #is visible

            #is in range

            #set if lowest

            


            print(pm.r_string(proc, e + offsets.ObjPlayerName))
            pos = (pm.r_floats(proc, e + offsets.ObjPos, 3))
            print(pm.r_floats(proc, e + offsets.ObjPos, 3))
            print(pm.r_bool(proc, e + offsets.ObjVisibility))
            print(world_to_screen(find_view_proj_matrix(
                mod['base']), width, height, pos[0], pos[1], pos[2]))
            print('\n')
            time.sleep(0.5)

    print("nope")

    # print(pm.r_bytes(proc, mod['base'] + 0x3163080 + 0x12D4, 4))
    print("\n")
    time.sleep(1)
