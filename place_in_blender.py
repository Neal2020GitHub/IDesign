import bpy
import mathutils
import json
import math
import os

object_name = 'Cube'
object_to_delete = bpy.data.objects.get(object_name)

# Check if the object exists before trying to delete it
if object_to_delete is not None:
    bpy.data.objects.remove(object_to_delete, do_unlink=True)

def import_glb(file_path, object_name):
    bpy.ops.import_scene.gltf(filepath=file_path)
    imported_object = bpy.context.view_layer.objects.active
    if imported_object is not None:
        imported_object.name = object_name

def create_room(width, depth, height):
    # Create floor
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))

    # Extrude to create walls
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, height)})
    # bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Scale the walls to the desired dimensions
    bpy.ops.transform.resize(value=(width, depth, 1))

    bpy.context.active_object.location.x += width / 2
    bpy.context.active_object.location.y += depth / 2

def find_glb_files(directory):
    glb_files = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".glb"):
                key = file.split(".")[0]
                if key not in glb_files:
                    glb_files[key] = os.path.join(root, file)
    return glb_files

def get_highest_parent_objects():
    highest_parent_objects = []

    for obj in bpy.data.objects:
        # Check if the object has no parent
        if obj.parent is None:
            highest_parent_objects.append(obj)
    return highest_parent_objects

def delete_empty_objects():
    # Iterate through all objects in the scene
    for obj in bpy.context.scene.objects:
        # Check if the object is empty (has no geometry)
        print(obj.name, obj.type)
        if obj.type == 'EMPTY':
            bpy.context.view_layer.objects.active = obj
            bpy.data.objects.remove(obj)

def select_meshes_under_empty(empty_object_name):
    # Get the empty object
    empty_object = bpy.data.objects.get(empty_object_name)
    print(empty_object is not None)
    if empty_object is not None and empty_object.type == 'EMPTY':
        # Iterate through the children of the empty object
        for child in empty_object.children:
            # Check if the child is a mesh
            if child.type == 'MESH':
                # Select the mesh
                child.select_set(True)
                bpy.context.view_layer.objects.active = child
            else:
                select_meshes_under_empty(child.name)

def rescale_object(obj, scale):
    # Ensure the object has a mesh data
    if obj.type == 'MESH':
        bbox_dimensions = obj.dimensions
        scale_factors = (
                         scale["length"] / bbox_dimensions.x, 
                         scale["width"] / bbox_dimensions.y, 
                         scale["height"] / bbox_dimensions.z
                        )
        obj.scale = scale_factors


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--output_dir", type=str, required=True)
args = parser.parse_args()
output_dir = args.output_dir


objects_in_room = {}
file_path = output_dir + "/scene_graph.json"
with open(file_path, 'r') as file:
    data = json.load(file)
    for item in data:
        if item["new_object_id"] not in ["south_wall", "north_wall", "east_wall", "west_wall", "middle of the room", "ceiling"]:
            objects_in_room[item["new_object_id"]] = item

# import ipdb; ipdb.set_trace()
directory_path = os.path.join(output_dir, "Assets")
glb_file_paths = find_glb_files(directory_path)

for item_id, object_in_room in objects_in_room.items():
    # glb_file_path = os.path.join(directory_path, glb_file_paths[item_id])
    glb_file_path = glb_file_paths[item_id]
    import_glb(glb_file_path, item_id)

parents = get_highest_parent_objects()
empty_parents = [parent for parent in parents if parent.type == "EMPTY"]
print(empty_parents)

for empty_parent in empty_parents:
    bpy.ops.object.select_all(action='DESELECT')
    select_meshes_under_empty(empty_parent.name)
    
    bpy.ops.object.join()
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
    joined_object = bpy.context.view_layer.objects.active
    if joined_object is not None:
        joined_object.name = empty_parent.name + "-joined"

bpy.context.view_layer.objects.active = None

MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']
for OBJS in MSH_OBJS:
    bpy.context.view_layer.objects.active = OBJS
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    OBJS.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.objects.active = OBJS
    OBJS.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']
for OBJS in MSH_OBJS:
    item = objects_in_room[OBJS.name.split("-")[0]]
    object_position = (item["position"]["x"], item["position"]["y"], item["position"]["z"])  # X, Y, and Z coordinates
    object_rotation_z = (item["rotation"]["z_angle"] / 180.0) * math.pi + math.pi # Rotation angles in radians around the X, Y, and Z axes
    
    bpy.ops.object.select_all(action='DESELECT')
    OBJS.select_set(True)
    OBJS.location = object_position
    bpy.ops.transform.rotate(value=object_rotation_z,  orient_axis='Z')
    rescale_object(OBJS, item["size_in_meters"])

bpy.ops.object.select_all(action='DESELECT')
delete_empty_objects()

# TODO: Generate the room with the room shape
create_room(6.0, 6.0, 2.5)  # 4.0, 4.0, 2.5




# 渲染 top_down_view.png
# TODO: Change the room shape
room_width, room_depth, room_height = 6.0, 6.0, 2.5  # 4.0, 4.0, 2.5

# 计算房间中心点
center_x = room_width / 2.0
center_y = room_depth / 2.0
center_z = room_height

# 创建光源（如果不存在）
if "TopDownLight" not in bpy.data.objects:
    bpy.ops.object.light_add(type='AREA', location=(center_x, center_y, center_z-0.1))
    light = bpy.context.object
    light.data.energy = 800  # 亮度，根据房间大小调整
    light.data.size = 5       # 面积，越大光越柔和
    light.name = "TopDownLight"

# 创建相机（如果不存在）
if "TopDownCamera" not in bpy.data.objects:
    bpy.ops.object.camera_add(location=(center_x, center_y, center_z-0.1))
    camera = bpy.context.object
    camera.name = "TopDownCamera"
else:
    camera = bpy.data.objects["TopDownCamera"]
    camera.location = (center_x, center_y, center_z-0.1)

# 旋转相机朝下
camera.rotation_euler = (0, 0, math.radians(-90))

# FOV
camera.data.lens = 5

# 设置相机为活动相机
bpy.context.scene.camera = camera

# 设置渲染输出路径
bpy.context.scene.render.filepath = os.path.join(output_dir, "top_down_view.png")

# 渲染保存
bpy.ops.render.render(write_still=True)



# 渲染 corner_view.png
# 相机目标点 = 房间中心
target = (center_x, center_y, center_z / 2.0)  # 取房间中间偏下的位置

# TODO: 相机位置 = 房间一个角落
# corner_camera_location = (0.3, 0.3, center_z / 2.0)
corner_camera_location = (room_width-0.3, room_depth-0.3, center_z / 2.0)

# 创建相机（如果不存在）
if "CornerCamera" not in bpy.data.objects:
    bpy.ops.object.camera_add(location=corner_camera_location)
    corner_camera = bpy.context.object
    corner_camera.name = "CornerCamera"
else:
    corner_camera = bpy.data.objects["CornerCamera"]
    corner_camera.location = corner_camera_location

# 让相机朝向房间中心
direction = (
    target[0] - corner_camera.location.x,
    target[1] - corner_camera.location.y,
    target[2] - corner_camera.location.z,
)
rot_quat = mathutils.Vector(direction).to_track_quat('-Z', 'Y')
corner_camera.rotation_euler = rot_quat.to_euler()

# 设置相机参数
corner_camera.data.lens = 10  # 增加焦距，避免画面太广
bpy.context.scene.camera = corner_camera

# 设置渲染输出路径
bpy.context.scene.render.filepath = os.path.join(output_dir, "corner_view.png")

# 渲染保存
bpy.ops.render.render(write_still=True)



# 保存一下，在blender里查看
# bpy.ops.wm.save_as_mainfile(filepath=output_dir + "/scene.blend")
