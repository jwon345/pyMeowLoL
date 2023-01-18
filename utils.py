import pyMeow as pm
import offsets
from node import Node, int_from_buffer, float_from_buffer, linked_insert
import numpy as np


def find_object_pointers(proc, base, max_count=800):
    # Given a memory interface will iterate through objects in memory
    # returns object addresses
    object_pointers = pm.r_int(proc, base + offsets.ObjectManager)
    root_node = Node(object_pointers, None)
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

def find_view_proj_matrix(proc, base):
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