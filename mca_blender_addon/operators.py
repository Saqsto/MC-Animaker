import bpy
import os
import json
import tempfile

from bpy.types import Operator
from bpy.props import StringProperty
from . import utils
from . import generator

class MC_OT_KeyframeProperty(Operator):
    bl_idname = "mc.keyframe_property"; bl_label = "Apply and Keyframe on Selected"
    bl_description = "Apply the active object's value and insert a keyframe for this property on all selected compatible objects"
    bl_options = {'REGISTER', 'UNDO'}

    property_name: StringProperty()

    def execute(self, context):
        if not self.property_name: self.report({'WARNING'}, "No property specified."); return {'CANCELLED'}
        active_obj = context.active_object
        if not active_obj or not hasattr(active_obj, 'mc_props'): self.report({'WARNING'}, "Active object has no MC Animaker properties."); return {'CANCELLED'}
        try:
            active_value = getattr(active_obj.mc_props, self.property_name)
        except AttributeError:
            self.report({'WARNING'}, f"Property '{self.property_name}' not found on active object."); return {'CANCELLED'}

        for obj in context.selected_objects:
            if hasattr(obj, 'mc_props'):
                try:
                    setattr(obj.mc_props, self.property_name, active_value)
                    obj.keyframe_insert(data_path=f'mc_props.{self.property_name}')
                except TypeError:
                    self.report({'WARNING'}, f"Property '{self.property_name}' on object '{obj.name}' cannot be keyframed.")
        return {'FINISHED'}

class MC_OT_AddCommand(Operator):
    bl_idname = "mc.add_command"; bl_label = "Add Command"; bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        obj = context.active_object
        if obj and obj.mc_props.object_type == 'ENTITY': obj.mc_props.custom_commands.add()
        return {'FINISHED'}

class MC_OT_RemoveCommand(Operator):
    bl_idname = "mc.remove_command"; bl_label = "Remove Command"; bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        obj = context.active_object
        if obj and obj.mc_props.object_type == 'ENTITY':
            index = obj.mc_props.active_command_index
            if index >= 0 and index < len(obj.mc_props.custom_commands):
                obj.mc_props.custom_commands.remove(index)
                obj.mc_props.active_command_index = min(max(0, index - 1), len(obj.mc_props.custom_commands) - 1)
        return {'FINISHED'}

class MC_OT_AddBlock(Operator):
    bl_idname = "mc.add_block"; bl_label = "Add Block"; bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.mc_scene_props; block_id = props.add_block_id.strip()
        if not block_id: self.report({'WARNING'}, "Block ID cannot be empty."); return {'CANCELLED'}
        full_block_id = block_id if ':' in block_id else f"minecraft:{block_id}"; short_id = full_block_id.split(':')[-1]
        bpy.ops.mesh.primitive_cube_add(size=1.0, enter_editmode=False, align='WORLD', location=context.scene.cursor.location)
        obj = context.active_object; obj.name = f"MC_Block_{short_id}"; obj.mc_props.object_type = 'BLOCK'; obj.mc_props.block_id = full_block_id
        if props.resource_pack_path: bpy.ops.mc.apply_textures()
        else: utils.reset_cube_uv_map(obj)
        return {'FINISHED'}

class MC_OT_AddEntity(Operator):
    bl_idname = "mc.add_entity"; bl_label = "Add Entity"; bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.mc_scene_props; entity_id = props.add_entity_id.strip()
        if not entity_id: self.report({'WARNING'}, "Entity ID cannot be empty."); return {'CANCELLED'}
        full_entity_id = entity_id if ':' in entity_id else f"minecraft:{entity_id}"; short_id = full_entity_id.split(':')[-1]
        bpy.ops.object.empty_add(type='CUBE', align='WORLD', location=context.scene.cursor.location)
        obj = context.active_object; obj.name = f"MC_Entity_{short_id}"; obj.mc_props.object_type = 'ENTITY'; obj.mc_props.entity_id = full_entity_id
        obj.mc_props.sid = utils.sanitize_name(obj.name)
        return {'FINISHED'}

class MC_OT_ApplyTextures(Operator):
    bl_idname = "mc.apply_textures"; bl_label = "Apply Textures from Resource Pack"; bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Find and apply textures to all selected blocks from the specified Resource Pack"
    
    @classmethod
    def poll(cls, context):
        return any(obj.type == 'MESH' and hasattr(obj, 'mc_props') and obj.mc_props.object_type == 'BLOCK' for obj in context.selected_objects)

    def execute(self, context):
        selected_blocks = [obj for obj in context.selected_objects if obj.type == 'MESH' and hasattr(obj, 'mc_props') and obj.mc_props.object_type == 'BLOCK']
        
        if not selected_blocks:
            self.report({'WARNING'}, "No valid blocks selected.")
            return {'CANCELLED'}

        for obj in selected_blocks:
            self.apply_textures_to_object(context, obj)
            
        self.report({'INFO'}, f"Textures applied to {len(selected_blocks)} object(s).")
        return {'FINISHED'}

    def apply_textures_to_object(self, context, obj):
        props = context.scene.mc_scene_props
        rp_path = props.resource_pack_path
        if not rp_path:
            self.report({'WARNING'}, "No Resource Pack selected.")
            return
        
        utils.reset_cube_uv_map(obj)
        helper = utils.ResourcePackHelper()
        block_id = obj.mc_props.block_id
        texture_map, message = helper.find_textures_for_block(rp_path, block_id)
        
        if not texture_map:
            self.report({'WARNING'}, f"({obj.name}) {message}")
            namespace, block_name = (block_id.split(':', 1) if ':' in block_id else ('minecraft', block_id))
            texture_map = {'all': f'minecraft:block/{block_name.split("[")[0]}'}
            
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                self.create_and_apply_materials(context, obj, texture_map, rp_path, temp_dir)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to apply texture to '{obj.name}': {e}")

    def create_and_apply_materials(self, context, obj, texture_map, rp_path, temp_dir):
        helper = utils.ResourcePackHelper()
        obj.data.materials.clear()

        if 'end' in texture_map and 'top' not in texture_map:
            texture_map['top'] = texture_map['end']
            texture_map['bottom'] = texture_map['end']
        
        fallback_tex = texture_map.get('all', texture_map.get('side', texture_map.get('particle')))
        
        tex_paths = {
            'top': texture_map.get('top', fallback_tex),
            'bottom': texture_map.get('bottom', texture_map.get('top', fallback_tex)),
            'front': texture_map.get('front', texture_map.get('side', fallback_tex)),
            'back': texture_map.get('back', texture_map.get('side', fallback_tex)),
            'east': texture_map.get('east', texture_map.get('side', fallback_tex)),
            'west': texture_map.get('west', texture_map.get('side', fallback_tex)),
        }
        tex_paths['side'] = texture_map.get('side', fallback_tex)
        
        unique_texture_paths = {p for p in tex_paths.values() if p}
        created_materials = {}

        for path_key in unique_texture_paths:
            full_path = path_key if ':' in path_key else f"minecraft:{path_key}"
            namespace, path = full_path.split(':', 1)
            image_path_in_rp = f"assets/{namespace}/textures/{path}.png"
            image_filepath = helper.get_image_from_rp(rp_path, image_path_in_rp, temp_dir)
            if not image_filepath: continue
            
            img = bpy.data.images.load(image_filepath, check_existing=True); img.pack()
            mat_name = os.path.basename(path); mat = bpy.data.materials.new(name=mat_name); mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get('Principled BSDF')
            
            if bsdf:
                base_pos_x, base_pos_y = bsdf.location
            else:
                base_pos_x, base_pos_y = 0, 0

            tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            tex_image_node.location = (base_pos_x - 300, base_pos_y)
            
            mapping_node = mat.node_tree.nodes.new('ShaderNodeMapping')
            mapping_node.location = (base_pos_x - 550, base_pos_y)

            tex_coord_node = mat.node_tree.nodes.new('ShaderNodeTexCoord')
            tex_coord_node.location = (base_pos_x - 800, base_pos_y)
            
            tex_image_node.image = img
            tex_image_node.interpolation = 'Closest'

            img_width = img.size[0]
            img_height = img.size[1]

            if img_height > 0:
                scale_y = img_width / img_height
                mapping_node.inputs['Scale'].default_value[1] = scale_y
                mapping_node.inputs['Location'].default_value[1] = 1.0 - scale_y
            
            mat.node_tree.links.new(mapping_node.inputs['Vector'], tex_coord_node.outputs['UV'])
            mat.node_tree.links.new(tex_image_node.inputs['Vector'], mapping_node.outputs['Vector'])
            
            mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image_node.outputs['Color'])
            mat.node_tree.links.new(bsdf.inputs['Alpha'], tex_image_node.outputs['Alpha'])
            mat.blend_method = 'CLIP'
            obj.data.materials.append(mat)
            created_materials[path_key] = mat

        if not created_materials: raise Exception(f"No PNG textures found for definitions in {texture_map}")

        for face in obj.data.polygons:
            center = face.center; key = ''
            if abs(center.z) > 0.49: key = 'top' if center.z > 0 else 'bottom'
            elif abs(center.y) > 0.49: key = 'front' if center.y < 0 else 'back'
            elif abs(center.x) > 0.49: key = 'east' if center.x > 0 else 'west'
            if key:
                texture_name = tex_paths.get(key)
                material = created_materials.get(texture_name)
                if material:
                    mat_index = obj.data.materials.find(material.name)
                    if mat_index != -1: face.material_index = mat_index

class MC_OT_GenerateDatapack(Operator):
    bl_idname = "mc.generate_datapack"; bl_label = "Generate Datapack"; bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.mc_scene_props
        if props.export_type == 'ANIMATION':
            self.execute_animation(context)
        elif props.export_type == 'MODEL':
            self.execute_model(context)
        return {'FINISHED'}

    def execute_animation(self, context):
        props = context.scene.mc_scene_props; scene = context.scene; wm = context.window_manager
        if not props.datapack_output_path or not props.folder_name or not props.scene_name:
            self.report({'ERROR'}, "Please set the Output Path, Folder Name, and Scene Name."); return
        
        version_details = generator.VERSION_MAP.get(props.minecraft_version, generator.VERSION_MAP['1.21'])
        pack_format = version_details['pack_format']; function_folder_name = version_details['function_folder']
        ns = utils.sanitize_name(props.namespace); scene_name = utils.sanitize_name(props.scene_name)
        datapack_root = os.path.join(props.datapack_output_path, props.folder_name)
        base_path = os.path.join(datapack_root, "data", ns, function_folder_name)
        scenes_path = os.path.join(base_path, "animations", "scenes", scene_name)
        for path in [scenes_path, os.path.join(scenes_path, "keyframes", "blocks"), os.path.join(scenes_path, "keyframes", "entity", "commands"), os.path.join(base_path, "animations", "_main", scene_name)]:
            os.makedirs(path, exist_ok=True)
        
        pack_mcmeta = {"pack": {"pack_format": pack_format, "description": f"Animation '{props.scene_name}' generated by MC Animaker"}}
        with open(os.path.join(datapack_root, "pack.mcmeta"), 'w', encoding='utf-8') as f: json.dump(pack_mcmeta, f, indent=4)
        
        all_objects = [obj for obj in bpy.data.objects if hasattr(obj, 'mc_props') and obj.mc_props.object_type != 'NONE']
        if not all_objects: self.report({'WARNING'}, "No MC Animaker objects found to animate."); return
        
        start_frame = scene.frame_start if not props.use_custom_frame_range else props.start_frame
        end_frame = scene.frame_end if not props.use_custom_frame_range else props.end_frame
        
        context.window.cursor_set('WAIT'); wm.mca_progress = 0.0; wm.mca_progress_text = "Caching Animation Data..."
        animation_cache = {obj.name: {} for obj in all_objects}
        original_frame = scene.frame_current; total_frames = end_frame - start_frame + 1
        
        try:
            for i, frame in enumerate(range(start_frame, end_frame + 1)):
                scene.frame_set(frame)
                for obj in all_objects:
                    state_tuple = (obj.matrix_world.copy(), obj.mc_props.solidify, obj.mc_props.block_light_level, obj.mc_props.sky_light_level)
                    animation_cache[obj.name][frame] = state_tuple
                wm.mca_progress = (i + 1) / total_frames * 100.0
        finally:
            scene.frame_set(original_frame); wm.mca_progress = 0.0; wm.mca_progress_text = ""; context.window.cursor_set('DEFAULT')

        self.report({'INFO'}, "Cache created. Generating files...")
        
        main_path = os.path.join(base_path, "animations", "_main", scene_name)
        
        block_kfs = {}; entity_kfs = {}
        if props.export_blocks:
            block_kfs = generator.get_optimized_keyframes(props, all_objects, 'BLOCK', animation_cache, utils.are_states_equal, start_frame, end_frame)
        if props.export_entities:
            entity_objects = [obj for obj in all_objects if obj.mc_props.object_type == 'ENTITY']
            if entity_objects:
                entity_kfs = {f: {} for f in range(start_frame, end_frame + 1)}
                for frame in entity_kfs.keys():
                    frame_data = {}
                    for local_index, obj in enumerate(entity_objects):
                         frame_data[local_index] = (obj, animation_cache[obj.name][frame])
                    entity_kfs[frame] = frame_data
        
        generator.generate_main_functions(props, main_path, scene_name, ns, all_objects, start_frame, block_kfs, entity_kfs)
        generator.generate_create_commands(props, main_path, scene_name, all_objects, start_frame, animation_cache)

        sid_map = {}; used_sids = set()
        for obj in all_objects:
            if obj.mc_props.object_type == 'ENTITY' and obj.mc_props.use_custom_commands and obj.mc_props.sid:
                base_sid = utils.sanitize_name(obj.mc_props.sid); final_sid = base_sid; count = 1
                while final_sid in used_sids: final_sid = f"{base_sid}_{count}"; count += 1
                used_sids.add(final_sid); sid_map[obj] = final_sid
        
        kf_base_path = os.path.join(scenes_path, "keyframes")
        generator.generate_custom_command_files(props, os.path.join(kf_base_path, "entity", "commands"), scene_name, ns, all_objects, sid_map)
        if props.export_blocks and block_kfs:
            generator.generate_keyframes(props, os.path.join(kf_base_path, "blocks"), scene_name, ns, all_objects, 'BLOCK', generator.format_block_command, block_kfs, start_frame, end_frame, animation_cache, sid_map)
        if props.export_entities and entity_kfs:
            generator.generate_keyframes(props, os.path.join(kf_base_path, "entity"), scene_name, ns, all_objects, 'ENTITY', generator.format_entity_command, entity_kfs, start_frame, end_frame, animation_cache, sid_map)
            
        self.report({'INFO'}, f"Datapack '{props.folder_name}' generated successfully!")

    def execute_model(self, context):
        props = context.scene.mc_scene_props
        if not props.datapack_output_path or not props.folder_name or not props.scene_name:
            self.report({'ERROR'}, "Please set the Output Path, Folder Name, and Model Name."); return

        version_details = generator.VERSION_MAP.get(props.minecraft_version, generator.VERSION_MAP['1.21'])
        pack_format = version_details['pack_format']; function_folder_name = version_details['function_folder']
        ns = utils.sanitize_name(props.namespace); model_name = utils.sanitize_name(props.scene_name)
        datapack_root = os.path.join(props.datapack_output_path, props.folder_name)
        model_base_path = os.path.join(datapack_root, "data", ns, function_folder_name, "models")
        os.makedirs(model_base_path, exist_ok=True)

        pack_mcmeta = {"pack": {"pack_format": pack_format, "description": f"Model '{props.scene_name}' generated by MC Animaker"}}
        with open(os.path.join(datapack_root, "pack.mcmeta"), 'w', encoding='utf-8') as f: json.dump(pack_mcmeta, f, indent=4)
        
        all_objects = [obj for obj in bpy.data.objects if hasattr(obj, 'mc_props') and obj.mc_props.object_type != 'NONE']
        if not all_objects:
            self.report({'WARNING'}, "No MC Animaker objects found to export."); return
            
        generator.generate_model_files(context, props, model_base_path, model_name, all_objects)
        
        self.report({'INFO'}, f"Model '{model_name}' generated successfully!")