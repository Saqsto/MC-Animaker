import bpy
from bpy.types import UIList, Panel

class MC_UL_CustomCommands(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "command", text="", emboss=False)

class MC_PT_Panel(Panel):
    bl_label = "MC Animaker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MC Animaker'
    
    def draw(self, context):
        layout = self.layout; props = context.scene.mc_scene_props; obj = context.active_object
        row = layout.row()
        icon = 'TRIA_DOWN' if props.show_object_panel else 'TRIA_RIGHT'
        row.prop(props, "show_object_panel", text="Object Management", icon=icon, emboss=False)
        if props.show_object_panel:
            box = layout.box()
            sub_box = box.box()
            col = sub_box.column(align=True)
            col.label(text="Create Object:")
            row = col.row(align=True)
            split = row.split(factor=0.35); split.label(text="Block ID"); split.prop(props, "add_block_id", text="")
            row.operator("mc.add_block", text="", icon='CUBE')
            row = col.row(align=True)
            split = row.split(factor=0.35); split.label(text="Entity ID"); split.prop(props, "add_entity_id", text="")
            row.operator("mc.add_entity", text="", icon='EMPTY_DATA')
            
            if obj and hasattr(obj, 'mc_props'):
                sub_box = box.box()
                col = sub_box.column()
                col.label(text=f"Selected: '{obj.name}' ({len(context.selected_objects)} total)")
                mc_props = obj.mc_props
                
                split = col.split(factor=0.4); split.label(text="Object Type"); split.prop(mc_props, "object_type", text="")
                
                if mc_props.object_type == 'BLOCK':
                    split = col.split(factor=0.4); split.label(text="Block ID"); split.prop(mc_props, "block_id", text="")
                    col.separator()
                    col.label(text="Brightness:")
                    
                    row = col.row(align=True)
                    row.prop(mc_props, "block_light_level", text="Block")
                    op = row.operator("mc.keyframe_property", text="", icon='KEYINGSET')
                    op.property_name = "block_light_level"

                    row = col.row(align=True)
                    row.prop(mc_props, "sky_light_level", text="Sky")
                    op = row.operator("mc.keyframe_property", text="", icon='KEYINGSET')
                    op.property_name = "sky_light_level"
                    
                    col.separator()
                    
                    solidify_row = col.row(align=True)
                    solidify_row.prop(mc_props, "solidify", text="Solidify as")
                    sub_row = solidify_row.row(align=True)
                    sub_row.enabled = mc_props.solidify
                    sub_row.prop(mc_props, "solidify_as", text="")
                    op = solidify_row.operator("mc.keyframe_property", text="", icon='KEYINGSET')
                    op.property_name = "solidify"

                elif mc_props.object_type == 'ENTITY':
                    split = col.split(factor=0.4); split.label(text="Entity ID"); split.prop(mc_props, "entity_id", text="")
                    if props.dynamic_tracking and props.tracking_mode == 'TARGET':
                        col.prop(mc_props, "is_tracking_target")
                    if props.dynamic_tracking and props.tracking_mode != 'OFF' and props.global_tracking_anchor == 'INDIVIDUAL':
                        split = col.split(factor=0.4); split.label(text="Anchor"); split.prop(mc_props, "tracking_anchor", text="")
                    col.separator()
                    row = col.row()
                    icon = 'TRIA_DOWN' if props.show_advanced_options else 'TRIA_RIGHT'
                    row.prop(props, "show_advanced_options", text="Advanced Options", icon=icon, emboss=False)
                    if props.show_advanced_options:
                        adv_box = col.box()
                        adv_box.label(text="Custom NBT Data:")
                        adv_box.prop(mc_props, "custom_nbt", text="")
                        adv_box.separator()
                        adv_box.prop(mc_props, "use_custom_commands")
                        if mc_props.use_custom_commands:
                            split = adv_box.split(factor=0.35); split.label(text="Scene ID"); split.prop(mc_props, "sid", text="")
                            adv_box.template_list("MC_UL_CustomCommands", "", mc_props, "custom_commands", mc_props, "active_command_index")
                            row = adv_box.row(align=True)
                            row.operator("mc.add_command", icon='ADD', text="")
                            row.operator("mc.remove_command", icon='REMOVE', text="")

        row = layout.row()
        icon = 'TRIA_DOWN' if props.show_assets_panel else 'TRIA_RIGHT'
        row.prop(props, "show_assets_panel", text="Assets & Export", icon=icon, emboss=False)
        if props.show_assets_panel:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Datapack Settings:")
            col.prop(props, "datapack_output_path", text="Output Path")
            split = col.split(factor=0.4); split.label(text="Folder Name"); split.prop(props, "folder_name", text="")
            split = col.split(factor=0.4); split.label(text="Scene Name"); split.prop(props, "scene_name", text="")
            split = col.split(factor=0.4); split.label(text="Namespace"); split.prop(props, "namespace", text="")
            col.separator()
            col.prop(props, "resource_pack_path", text="Resource Pack")
            op_row = col.row(); op_row.scale_y = 1.2; op_row.operator("mc.apply_textures", icon='BRUSH_DATA')

        row = layout.row()
        icon = 'TRIA_DOWN' if props.show_generation_panel else 'TRIA_RIGHT'
        row.prop(props, "show_generation_panel", text="Generation Options", icon=icon, emboss=False)
        if props.show_generation_panel:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="General:")
            row = col.row(align=True)
            row.prop(props, "export_blocks"); row.prop(props, "export_entities")
            col.prop(props, "pause_support")
            col.separator()
            col.label(text="Frame Range:")
            col.prop(props, "use_custom_frame_range")
            if props.use_custom_frame_range:
                frame_box = col.box()
                row = frame_box.row(align=True)
                row.prop(props, "start_frame"); row.prop(props, "end_frame")
            col.separator()
            col.label(text="Block Options:")
            block_box = col.box()
            block_box.enabled = props.export_blocks
            block_box.prop(props, "use_interpolation")
            if props.use_interpolation:
                interp_box = block_box.box()
                split = interp_box.split(factor=0.5); split.label(text="Duration (ticks)"); split.prop(props, "interpolation_duration", text="")
                split = interp_box.split(factor=0.5); split.label(text="Start (ticks)"); split.prop(props, "start_interpolation", text="")
            block_box.prop(props, "invert_normals_on_export")
            col.separator()
            col.label(text="Tracking Options:")
            entity_box = col.box()
            entity_box.enabled = props.export_entities
            entity_box.prop(props, "dynamic_tracking")
            if props.dynamic_tracking:
                track_box = entity_box.box()
                split = track_box.split(factor=0.3); split.label(text="Mode"); split.prop(props, "tracking_mode", text="")
                if props.tracking_mode != 'OFF':
                    split = track_box.split(factor=0.3); split.label(text="Anchor"); split.prop(props, "global_tracking_anchor", text="")
        
        layout.separator()
        row = layout.row(); row.scale_y = 2.0; row.operator("mc.generate_datapack", icon='PLAY')