import bpy
import os
import json
import mathutils
import zipfile
import tempfile
import shutil
import re
import math

watermark = "# Created using MC Animaker by Priqnot\n\n"

def sanitize_name(name_str):
    if not name_str: return "unnamed"
    sanitized = name_str.lower()
    sanitized = re.sub(r'[^a-z0-9_.-]', '_', sanitized)
    return sanitized

def get_obj_state_at_frame(context, obj, frame, props):
    original_frame = context.scene.frame_current
    context.scene.frame_set(int(frame))
    state_tuple = (
        obj.matrix_world.copy(),
        obj.mc_props.solidify,
        obj.mc_props.block_light_level,
        obj.mc_props.sky_light_level
    )
    context.scene.frame_set(original_frame)
    return state_tuple

def get_morphed_matrix(matrix, new_scale_vector):
    loc, rot, original_scale = matrix.decompose()
    new_scale_matrix = mathutils.Matrix.Scale(new_scale_vector.x, 4, (1,0,0)) @ \
                        mathutils.Matrix.Scale(new_scale_vector.y, 4, (0,1,0)) @ \
                        mathutils.Matrix.Scale(new_scale_vector.z, 4, (0,0,1))
    return mathutils.Matrix.Translation(loc) @ rot.to_matrix().to_4x4() @ new_scale_matrix

def get_final_minecraft_matrix(world_matrix, props):
    loc, rot_quat, scale = world_matrix.decompose()
    loc.x *= -1.0
    eul = rot_quat.to_euler('XYZ')
    eul.y *= -1.0
    eul.z *= -1.0
    rot_quat = eul.to_quaternion()
    
    if not props.invert_normals_on_export:
        scale.x *= -1.0

    T = mathutils.Matrix.Translation(loc)
    R = rot_quat.to_matrix().to_4x4()
    
    S = mathutils.Matrix.Diagonal((scale.x, scale.z, scale.y, 1.0))

    pitch_fix = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')
    yaw_fix = mathutils.Matrix.Rotation(math.radians(180.0), 4, 'Z')
    base_correction_rotation = yaw_fix @ pitch_fix
    R = R @ base_correction_rotation

    offset = mathutils.Vector((0.5, 0.5, 0.5))
    T_offset_pos = mathutils.Matrix.Translation(offset)
    T_offset_neg = mathutils.Matrix.Translation(-offset)
    pivot_transform = T @ T_offset_pos @ R @ S @ T_offset_neg

    coord_conversion_matrix = mathutils.Matrix(((1, 0, 0, 0),
                                                (0, 0, 1, 0),
                                                (0, 1, 0, 0),
                                                (0, 0, 0, 1)))
    
    final_matrix = coord_conversion_matrix @ pivot_transform
    return final_matrix

def format_matrix(matrix):
    return ",".join([f"{val:.5f}f" for row in matrix for val in row])

def are_matrices_close(m1, m2, tolerance=0.0001):
    if not m1 or not m2: return False
    for i in range(4):
        for j in range(4):
            if abs(m1[i][j] - m2[i][j]) > tolerance:
                return False
    return True

def are_states_equal(s1, s2, tolerance=0.0001):
    m1, solidify1, block_light1, sky_light1 = s1
    m2, solidify2, block_light2, sky_light2 = s2
    
    if solidify1 != solidify2 or block_light1 != block_light2 or sky_light1 != sky_light2:
        return False
        
    return are_matrices_close(m1, m2, tolerance)

def reset_cube_uv_map(obj):
    if not obj or obj.type != 'MESH': return
    original_mode = obj.mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(scale_to_bounds=True)
    bpy.ops.object.mode_set(mode=original_mode)

class ResourcePackHelper:
    @staticmethod
    def get_file_content(rp_path, file_path_in_rp):
        if not rp_path or not os.path.exists(rp_path): return None
        try:
            if zipfile.is_zipfile(rp_path):
                with zipfile.ZipFile(rp_path, 'r') as z:
                    with z.open(file_path_in_rp) as f: return f.read().decode('utf-8')
            else:
                full_path = os.path.join(rp_path, file_path_in_rp)
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f: return f.read()
        except (KeyError, FileNotFoundError): return None

    @staticmethod
    def get_image_from_rp(rp_path, texture_path_in_rp, temp_dir):
        if not rp_path or not os.path.exists(rp_path): return None
        try:
            image_filename = os.path.basename(texture_path_in_rp)
            temp_image_path = os.path.join(temp_dir, image_filename)
            if zipfile.is_zipfile(rp_path):
                with zipfile.ZipFile(rp_path, 'r') as z:
                    with z.open(texture_path_in_rp) as source, open(temp_image_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    return temp_image_path
            else:
                full_path = os.path.join(rp_path, texture_path_in_rp)
                if os.path.exists(full_path):
                    shutil.copy(full_path, temp_image_path)
                    return temp_image_path
        except (KeyError, FileNotFoundError): return None

    def resolve_model_textures(self, rp_path, model_id):
        if ':' not in model_id: model_id = f"minecraft:{model_id}"
        namespace, model_name = model_id.split(':', 1)
        model_path = f"assets/{namespace}/models/{model_name}.json"
        model_content = self.get_file_content(rp_path, model_path)
        if not model_content: return {}
        try: model_json = json.loads(model_content)
        except json.JSONDecodeError: return {}
        textures = {}
        if 'parent' in model_json:
            textures.update(self.resolve_model_textures(rp_path, model_json['parent']))
        if 'textures' in model_json:
            textures.update(model_json['textures'])
        return textures

    def find_textures_for_block(self, rp_path, block_id):
        if ':' not in block_id: block_id = f"minecraft:{block_id}"
        namespace, block_name = block_id.split(':', 1)
        base_block_name = block_name.split('[')[0]
        blockstate_path = f"assets/{namespace}/blockstates/{base_block_name}.json"
        bs_content = self.get_file_content(rp_path, blockstate_path)
        if not bs_content: return None, f"Blockstate not found for {base_block_name}. Using fallback."
        try: bs_json = json.loads(bs_content)
        except json.JSONDecodeError: return None, f"Invalid blockstate for {base_block_name}. Using fallback."
        model_id = None
        if 'variants' in bs_json:
            variants = bs_json['variants']
            first_key = next(iter(variants)); model_info = variants[first_key]
            if isinstance(model_info, list): model_info = model_info[0]
            model_id = model_info.get('model')
        if not model_id: return None, "Could not determine model. Using fallback."
        resolved_textures = self.resolve_model_textures(rp_path, model_id)
        final_textures = {}
        for key, value in resolved_textures.items():
            while value.startswith('#'): value = resolved_textures.get(value[1:], value)
            final_textures[key] = value
        return final_textures, "Success"