import bpy
import os
import mathutils
import json

from . import utils

VERSION_MAP = {
    '1.21':   {'pack_format': 34, 'function_folder': 'function'},
    '1.20.5': {'pack_format': 32, 'function_folder': 'function'},
    '1.20.3': {'pack_format': 26, 'function_folder': 'functions'},
    '1.20.2': {'pack_format': 18, 'function_folder': 'functions'},
    '1.20':   {'pack_format': 15, 'function_folder': 'functions'},
    '1.19.4': {'pack_format': 12, 'function_folder': 'functions'},
}

def generate_main_functions(props, main_path, scene_name, ns, all_objects, start_frame, block_kfs, entity_kfs):
    play_cmds = []
    if props.pause_support:
        play_cmds.extend([f"tag @e[tag={scene_name}_ref] remove {scene_name}_paused", f"tag @e[tag={scene_name}_ref] add {scene_name}_playing"])
    else:
        play_cmds.append(f"tag @e[tag={scene_name}_ref] add {scene_name}_playing")
    if props.export_blocks and block_kfs:
        first_frame = sorted(block_kfs.keys())[0]; delay = first_frame - start_frame
        path = f"{ns}:animations/scenes/{scene_name}/keyframes/blocks/0"
        if delay > 0: play_cmds.append(f"schedule function {path} {delay}t")
        else: play_cmds.append(f"function {path}")
    if props.export_entities and entity_kfs:
        first_frame = sorted(entity_kfs.keys())[0]; delay = first_frame - start_frame
        path = f"{ns}:animations/scenes/{scene_name}/keyframes/entity/0"
        if delay > 0: play_cmds.append(f"schedule function {path} {delay}t")
        else: play_cmds.append(f"function {path}")
    with open(os.path.join(main_path, "play.mcfunction"), 'w', encoding='utf-8') as f:
        f.write(utils.watermark + "\n".join(play_cmds))
    loop_cmds = [f"tag @e[tag={scene_name}_ref] add {scene_name}_looping"] + play_cmds
    with open(os.path.join(main_path, "loop.mcfunction"), 'w', encoding='utf-8') as f:
        f.write(utils.watermark + "\n".join(loop_cmds))
    stop_cmds = [f"tag @e[tag={scene_name}_ref] add {scene_name}_playing"]
    if props.export_blocks and block_kfs:
        stop_cmds.append(f"function {ns}:animations/scenes/{scene_name}/keyframes/blocks/0")
    if props.export_entities and entity_kfs:
        stop_cmds.append(f"function {ns}:animations/scenes/{scene_name}/keyframes/entity/0")
    stop_cmds.extend([f"tag @e[tag={scene_name}_ref] remove {scene_name}_looping", f"tag @e[tag={scene_name}_ref] remove {scene_name}_playing", f"tag @e[tag={scene_name}_ref] remove {scene_name}_paused"])
    with open(os.path.join(main_path, "stop.mcfunction"), 'w', encoding='utf-8') as f:
        f.write(utils.watermark + "\n".join(stop_cmds))
    if props.pause_support:
        with open(os.path.join(main_path, "pause.mcfunction"), 'w', encoding='utf-8') as f: f.write(utils.watermark + f"tag @e[tag={scene_name}_ref] remove {scene_name}_playing\ntag @e[tag={scene_name}_ref] add {scene_name}_paused")
        with open(os.path.join(main_path, "resume.mcfunction"), 'w', encoding='utf-8') as f: f.write(utils.watermark + f"tag @e[tag={scene_name}_ref] remove {scene_name}_paused\ntag @e[tag={scene_name}_ref] add {scene_name}_playing")
    
    move_cmd = f"tp @e[type=block_display,tag={scene_name}_ref,sort=nearest,limit=1] @s"
    with open(os.path.join(main_path, "move.mcfunction"), 'w', encoding='utf-8') as f:
        f.write(utils.watermark + move_cmd)


def generate_create_commands(props, main_path, scene_name, all_objects, start_frame, animation_cache):
    all_passengers = []
    
    block_objects = [obj for obj in all_objects if obj.mc_props.object_type == 'BLOCK' and props.export_blocks]
    if block_objects:
        block_display_passengers = []
        for i, obj in enumerate(block_objects):
            mc_props = obj.mc_props
            world_matrix, _, block_light, sky_light = animation_cache[obj.name][start_frame]
            final_matrix = utils.get_final_minecraft_matrix(world_matrix, props)
            matrix_str = utils.format_matrix(final_matrix)
            block_id = mc_props.block_id.strip()
            tags = [f"{scene_name}_block_{i}", "mca_animation"] 
            tags_nbt = ",".join([f'"{tag}"' for tag in tags])
            brightness_nbt = f',brightness:{{sky:{sky_light},block:{block_light}}}'
            block_display_passengers.append(f'{{id:"minecraft:block_display",block_state:{{Name:"{block_id}"}},transformation:[{matrix_str}],Tags:[{tags_nbt}]{brightness_nbt}}}')
        
        parent_tag = f"{scene_name}_blocks"
        passengers_str = ",".join(block_display_passengers)
        all_passengers.append(f'{{id:"minecraft:block_display",Tags:["{parent_tag}","mca_animation"],Passengers:[{passengers_str}]}}')

    passengers_nbt_str = f"Passengers:[{','.join(all_passengers)}]" if all_passengers else ""
    
    custom_name_nbt = f"CustomName:'{{\"text\":\"{scene_name}\"}}',CustomNameVisible:false"
    create_cmds = [f'summon block_display ~ ~ ~ {{block_state:{{Name:"minecraft:air"}},Tags:["{scene_name}_ref","mca_animation"],{custom_name_nbt},{passengers_nbt_str}}}']

    entity_objects = [obj for obj in all_objects if obj.mc_props.object_type == 'ENTITY' and props.export_entities]
    for i, obj in enumerate(entity_objects):
         mc_props = obj.mc_props
         tags = [f"{scene_name}_entity_{i}", "mca_animation"]
         if mc_props.is_tracking_target: tags.append("target")
         tags_nbt = ",".join([f'"{tag}"' for tag in tags])
         custom_nbt = f",{mc_props.custom_nbt.strip()}" if mc_props.custom_nbt else ""
         create_cmds.append(f"execute as @e[tag={scene_name}_ref] at @s run summon {mc_props.entity_id} ~ ~ ~ {{Tags:[{tags_nbt}]{custom_nbt}}}")

    with open(os.path.join(main_path, "create.mcfunction"), 'w', encoding='utf-8') as f:
        f.write(utils.watermark + "\n".join(create_cmds))
        
    remove_cmds = [f"kill @e[tag={scene_name}_ref]"]
    if block_objects:
        remove_cmds.append(f"kill @e[tag={scene_name}_blocks]")
        for i in range(len(block_objects)):
            remove_cmds.append(f"kill @e[tag={scene_name}_block_{i}]")
    for i in range(len(entity_objects)):
        remove_cmds.append(f"kill @e[tag={scene_name}_entity_{i}]")
        
    with open(os.path.join(main_path, "remove.mcfunction"), 'w', encoding='utf-8') as f:
        f.write(utils.watermark + "\n".join(remove_cmds))

def get_optimized_keyframes(props, all_objects, obj_type_filter, animation_cache, comparison_func, start_frame, end_frame):
    keyframes = {}
    filtered_objects = [obj for obj in all_objects if obj.mc_props.object_type == obj_type_filter]
    if not filtered_objects: return {}
    for frame in range(start_frame, end_frame + 1):
        frame_has_changes = False
        if frame == start_frame: frame_has_changes = True
        else:
            for obj in filtered_objects:
                if not comparison_func(animation_cache[obj.name][frame], animation_cache[obj.name][frame - 1]):
                    frame_has_changes = True; break
        if frame_has_changes: keyframes[frame] = {}
    for frame in keyframes.keys():
        frame_data = {}; local_index = 0
        for obj in filtered_objects:
            frame_data[local_index] = (obj, animation_cache[obj.name][frame]); local_index += 1
        keyframes[frame] = frame_data
    return keyframes

def generate_keyframes(props, kf_path, scene_name, ns, all_objects, obj_type_filter, command_formatter, keyframes, start_frame, end_frame, animation_cache, sid_map={}):
    if not keyframes:
        os.makedirs(kf_path, exist_ok=True)
        with open(os.path.join(kf_path, "0.mcfunction"), 'w', encoding='utf-8') as f: f.write(utils.watermark + "# No keyframes for this object type.")
        return
    path_map = {'BLOCK': 'blocks', 'ENTITY': 'entity'}; path_segment = path_map.get(obj_type_filter, obj_type_filter.lower())
    sorted_frames = sorted(keyframes.keys())
    last_known_states = {}
    for i, frame in enumerate(sorted_frames):
        frame_cmds = []; frame_data = keyframes[frame]
        for obj_index_local, (obj, data) in frame_data.items():
            prev_frame_state = animation_cache[obj.name].get(frame - 1) if frame > start_frame else data
            prev_data = last_known_states.get(obj, prev_frame_state)
            frame_cmds.extend(command_formatter(props, scene_name, ns, obj_index_local, obj, data, prev_data, sid_map, is_first_keyframe=(i == 0)))
            last_known_states[obj] = data
        is_last_keyframe = (i + 1 == len(sorted_frames))
        if not is_last_keyframe:
            delay = sorted_frames[i+1] - frame
            frame_cmds.append(f"execute if entity @e[tag={scene_name}_playing] run schedule function {ns}:animations/scenes/{scene_name}/keyframes/{path_segment}/{i + 1} {delay}t")
        else:
            delay = (end_frame - frame) + 1
            frame_cmds.append(f"execute if entity @e[tag={scene_name}_looping] run schedule function {ns}:animations/scenes/{scene_name}/keyframes/{path_segment}/0 {delay}t")
        if props.pause_support:
            frame_cmds.append(f"execute if entity @e[tag={scene_name}_paused] run schedule function {ns}:animations/scenes/{scene_name}/keyframes/{path_segment}/{i} 1t")
        with open(os.path.join(kf_path, f"{i}.mcfunction"), 'w', encoding='utf-8') as f:
            f.write(utils.watermark + "\n".join(frame_cmds))

def generate_custom_command_files(props, commands_path, scene_name, ns, all_objects, sid_map={}):
    entity_objects = [obj for obj in all_objects if obj.mc_props.object_type == 'ENTITY']
    for obj in entity_objects:
        mc_props = obj.mc_props
        if mc_props.use_custom_commands and mc_props.sid:
            final_sid = sid_map.get(obj)
            if not final_sid: continue
            file_path = os.path.join(commands_path, f"{final_sid}.mcfunction")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(utils.watermark); f.write(f"# Custom commands for SID: {mc_props.sid} (Object: {obj.name})\n")
                for command_item in mc_props.custom_commands:
                    if command_item.command.strip(): f.write(f"{command_item.command.strip()}\n")

def format_block_command(props, scene_name, ns, obj_index, obj, current_state, prev_state, sid_map, is_first_keyframe=False):
    mc_props = obj.mc_props; commands = []
    world_matrix, is_solidified, block_light, sky_light = current_state
    _, was_solidified, _, _ = prev_state if prev_state else (None, None, 0, 0)
    if is_solidified != was_solidified:
        loc = world_matrix.to_translation()
        mc_x = -loc.x; mc_y = loc.z; mc_z = loc.y
        block_pos = f"~{round(mc_x)} ~{round(mc_y)} ~{round(mc_z)}"
        solidify_id = mc_props.solidify_as.strip() or mc_props.block_id.strip()
        if is_solidified: commands.append(f"execute at @e[tag={scene_name}_ref] run setblock {block_pos} {solidify_id}")
        else: commands.append(f"execute at @e[tag={scene_name}_ref] run setblock {block_pos} minecraft:air")
    if is_first_keyframe or not utils.are_states_equal(current_state, prev_state):
        final_matrix_input = world_matrix
        solidify_id = mc_props.solidify_as.strip() or mc_props.block_id.strip()
        if is_solidified and 'barrier' not in solidify_id:
            final_matrix_input = utils.get_morphed_matrix(world_matrix, mathutils.Vector((0.001, 0.001, 0.001)))
        final_matrix = utils.get_final_minecraft_matrix(final_matrix_input, props)
        matrix_str = utils.format_matrix(final_matrix)
        interp_str = f",interpolation_duration:{props.interpolation_duration},start_interpolation:{props.start_interpolation}" if props.use_interpolation else ""
        brightness_nbt = f',brightness:{{sky:{sky_light},block:{block_light}}}'
        target_tag = f"{scene_name}_block_{obj_index}"
        command_prefix = f"execute if entity @e[tag={scene_name}_playing] run "
        nbt_to_merge = f"{{transformation:[{matrix_str}]{brightness_nbt}{interp_str}}}"
        commands.append(f"{command_prefix}data merge entity @e[type=block_display,tag={target_tag},limit=1] {nbt_to_merge}")
    return commands

def format_entity_command(props, scene_name, ns, obj_index, obj, state, prev_state, sid_map, is_first_keyframe=False):
    mc_props = obj.mc_props; location = state[0].to_translation()
    mc_x = -location.x; mc_y = location.z; mc_z = location.y
    target_tag = f"{scene_name}_entity_{obj_index}"
    main_cmd = f"execute as @e[tag={scene_name}_ref] at @s run tp @e[tag={target_tag},limit=1,sort=nearest] ~{mc_x:.3f} ~{mc_y:.3f} ~{mc_z:.3f}"
    if props.dynamic_tracking and props.tracking_mode != 'OFF':
        anchor = props.global_tracking_anchor.lower()
        if props.global_tracking_anchor == 'INDIVIDUAL': anchor = mc_props.tracking_anchor
        if props.tracking_mode == 'CENTER': main_cmd += f" facing entity @e[tag={scene_name}_ref,limit=1,sort=nearest] {anchor}"
        elif props.tracking_mode == 'PLAYER': main_cmd += f" facing entity @p {anchor}"
        elif props.tracking_mode == 'TARGET': main_cmd += f" facing entity @e[tag=target,limit=1,sort=nearest] {anchor}"
    commands = [main_cmd]
    if mc_props.use_custom_commands and mc_props.sid:
        final_sid = sid_map.get(obj)
        if final_sid:
            commands.append(f"execute as @e[tag={target_tag}] at @s run function {ns}:animations/scenes/{scene_name}/keyframes/entity/commands/{final_sid}")
    return commands

def generate_model_files(context, props, model_base_path, model_name, all_objects):
    model_dir = os.path.join(model_base_path, model_name)
    os.makedirs(model_dir, exist_ok=True)
    
    ref_tag = f"{model_name}_ref"
    all_passengers = []
    
    original_frame = context.scene.frame_current
    context.scene.frame_set(props.model_export_frame)
    
    block_objects = [obj for obj in all_objects if obj.mc_props.object_type == 'BLOCK' and props.export_blocks]
    if block_objects:
        block_display_passengers = []
        for i, obj in enumerate(block_objects):
            mc_props = obj.mc_props; world_matrix = obj.matrix_world.copy()
            final_matrix = utils.get_final_minecraft_matrix(world_matrix, props)
            matrix_str = utils.format_matrix(final_matrix)
            block_id = mc_props.block_id.strip(); tags = [f"{model_name}_block_{i}", "mca_model"]
            tags_nbt = ",".join([f'"{tag}"' for tag in tags])
            brightness_nbt = f',brightness:{{sky:{mc_props.sky_light_level},block:{mc_props.block_light_level}}}'
            block_display_passengers.append(f'{{id:"minecraft:block_display",block_state:{{Name:"{block_id}"}},transformation:[{matrix_str}],Tags:[{tags_nbt}]{brightness_nbt}}}')
        parent_tag = f"{model_name}_blocks"
        passengers_str = ",".join(block_display_passengers)
        all_passengers.append(f'{{id:"minecraft:block_display",Tags:["{parent_tag}","mca_model"],Passengers:[{passengers_str}]}}')

    entity_objects = [obj for obj in all_objects if obj.mc_props.object_type == 'ENTITY' and props.export_entities]
    for i, obj in enumerate(entity_objects):
        mc_props = obj.mc_props; world_matrix = obj.matrix_world.copy()
        loc, _, _ = world_matrix.decompose()
        rel_x = loc.x; rel_y = loc.y; rel_z = loc.z
        mc_x = -rel_x; mc_y = rel_z; mc_z = rel_y
        tags = [f"{model_name}_entity_{i}", "mca_model"]
        if mc_props.is_tracking_target: tags.append("target")
        tags_nbt = ",".join([f'"{tag}"' for tag in tags])
        custom_nbt = f",{mc_props.custom_nbt.strip()}" if mc_props.custom_nbt else ""
        all_passengers.append(f'{{id:"{mc_props.entity_id}",Pos:[{mc_x:.3f}d,{mc_y:.3f}d,{mc_z:.3f}d],Tags:[{tags_nbt}]{custom_nbt}}}')
        
    passengers_nbt_str = f"Passengers:[{','.join(all_passengers)}]" if all_passengers else ""
    
    custom_name_nbt = f"CustomName:'{{\"text\":\"{model_name}\"}}',CustomNameVisible:false"
    create_cmds = [f'summon block_display ~ ~ ~ {{block_state:{{Name:"minecraft:air"}},Tags:["{ref_tag}","mca_model"],{custom_name_nbt},{passengers_nbt_str}}}']
    
    context.scene.frame_set(original_frame)
    
    with open(os.path.join(model_dir, "create.mcfunction"), 'w', encoding='utf-8') as f:
        f.write(utils.watermark + "\n".join(create_cmds))
        
    remove_cmds = [f"kill @e[tag={ref_tag}]"]
    if block_objects:
        remove_cmds.append(f"kill @e[tag={model_name}_blocks]")
        for i in range(len(block_objects)): remove_cmds.append(f"kill @e[tag={model_name}_block_{i}]")
    for i in range(len(entity_objects)): remove_cmds.append(f"kill @e[tag={model_name}_entity_{i}]")
    with open(os.path.join(model_dir, "remove.mcfunction"), 'w', encoding='utf-8') as f:
        f.write(utils.watermark + "\n".join(remove_cmds))
        
    move_cmd = f"tp @e[type=block_display,tag={ref_tag},sort=nearest,limit=1] @s"
    with open(os.path.join(model_dir, "move.mcfunction"), 'w', encoding='utf-8') as f:
        f.write(utils.watermark + move_cmd)