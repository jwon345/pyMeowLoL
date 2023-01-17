import pyMeow as pm
import subprocess
import sys
import time
import offsets
from node import Node, int_from_buffer, linked_insert


def find_object_pointers(base, max_count=800):
    # Given a memory interface will iterate through objects in memory
    # returns object addresses
    object_pointers = pm.r_uint(proc, base + offsets.ObjectManager)
    root_node = Node(pm.r_uint(proc, object_pointers +
                     offsets.ObjectMapRoot), None)
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
            data = pm.r_bytes(current_node.address, 0x18)
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

player = pm.r_uint(proc, mod['base'] + 0x3163080)
om = pm.r_uint(proc, mod['base'] + offsets.ObjectManager)
root = pm.r_uint(proc, om + offsets.ObjectMapRoot)
# pointers = find_object_pointers(mod['base'])

# print(pointers)

input()

while True:

    # print(pm.r_float(proc, mod['base'] + offsets.GameTime))
    # print(pm.r_floats(proc, player + 0x1DC, 2))  # position?
    # print(pm.r_float(proc, player + 0x132C))  # as
    # print(pm.r_float(proc, player + 0x13A4))  # attack range

    # print(pm.r_float(proc, player + offsets.ObjHealth))
    # print(pm.r_float(proc, player + offsets.ObjHealth))
    print(pm.r_string(proc, player + offsets.ObjName))

    try:
        print(pm.r_uint(proc, root + offsets.ObjectMapNodeNetId))
        print(pm.r_string(proc, pm.r_uint(proc, root +
              offsets.ObjectMapNodeObject) + offsets.ObjName))
    except:
        print("issue")

    root = pm.r_uint(proc, root + 0x8)

    # print(pm.r_string(proc, om + (1506535 * 0x18) + offsets.ObjName))
    # print(pm.r_float(proc, om + (1506535 * 0x18) + offsets.ObjHealth))
    # print(pm.r_string(proc, om + (1833941 * 0x18) + offsets.ObjName))
    # print(pm.r_float(proc, om + (1833941 * 0x18) + offsets.ObjHealth))

    print("nope")

    # print(pm.r_bytes(proc, mod['base'] + 0x3163080 + 0x12D4, 4))
    print("\n")
    time.sleep(1)
