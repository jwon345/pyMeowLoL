import pyMeow as pm
import subprocess
import sys
import time


proc = pm.open_process(processName=pm.get_process_name(36584))

print(pm.get_process_name(36584))
# print(pm.get_module(proc)) 0x201804485A0,


print(pm.enum_processes())

mod = (pm.get_module(proc, "League of Legends.exe"))

print(mod['base'])

while True:
    player = pm.r_int(proc, mod['base'] + 0x3163080)

    print(pm.r_floats(proc, player + 0x1DC, 2))
    print(pm.r_float(proc, player + 0x132C))  # as
    print(pm.r_int(proc, player + 0x13A4))  # attack range

    # print(pm.r_bytes(proc, mod['base'] + 0x3163080 + 0x12D4, 4))
    print("\n")
    time.sleep(1)
