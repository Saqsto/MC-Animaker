import bpy
from bpy.props import (
    StringProperty, PointerProperty, EnumProperty, BoolProperty, IntProperty, FloatVectorProperty,
    CollectionProperty
)
from bpy.types import PropertyGroup

def update_multi_object_value(self, context):
    if context.active_object and hasattr(context.active_object, 'mc_props'):
        prop_name = self.path_from_id().split('.')[-1]
        active_value = getattr(context.active_object.mc_props, prop_name)
        
        for obj in context.selected_objects:
            if obj != context.active_object and hasattr(obj, 'mc_props'):
                if getattr(obj.mc_props, prop_name) != active_value:
                    setattr(obj.mc_props, prop_name, active_value)

def update_solidify(self, context):
    is_solid = self.solidify
    if hasattr(self, 'id_data') and self.id_data:
        owner_obj = self.id_data
        owner_obj.lock_location = [is_solid, is_solid, is_solid]
        owner_obj.lock_rotation = [is_solid, is_solid, is_solid]
        owner_obj.lock_scale = [is_solid, is_solid, is_solid]

    for obj in context.selected_objects:
        if hasattr(obj, 'mc_props'):
            if obj.mc_props.solidify != is_solid:
                obj.mc_props.solidify = is_solid
            
            obj.lock_location = [is_solid, is_solid, is_solid]
            obj.lock_rotation = [is_solid, is_solid, is_solid]
            obj.lock_scale = [is_solid, is_solid, is_solid]

class MC_CustomCommand(PropertyGroup):
    command: StringProperty(name="Command", default="particle dust{color:[0.0,0.98,1.0],scale:1} ~ ~1 ~ 0 0 0 0 1")

class MC_ObjectProperties(PropertyGroup):
    object_type: EnumProperty(
        name="Object Type",
        items=[('NONE', "Not Set", "This object will be ignored by the exporter"),
               ('BLOCK', "Block", "Represents a Minecraft block (block_display)"), 
               ('ENTITY', "Entity", "Represents a Minecraft entity (e.g., armor_stand)")],
        default='NONE',
        description="Choose the object's function for the datapack. 'Not Set' will be ignored."
    )
    block_id: StringProperty(name="Block ID", default="minecraft:oak_log")
    entity_id: StringProperty(name="Entity ID", default="minecraft:allay")
    block_light_level: IntProperty(name="Block Light", default=0, min=0, max=15, update=update_multi_object_value)
    sky_light_level: IntProperty(name="Sky Light", default=15, min=0, max=15, update=update_multi_object_value)
    solidify: BoolProperty(name="Solidify", default=False, options={'ANIMATABLE'}, update=update_solidify)
    solidify_as: StringProperty(name="Solidify as", default="minecraft:stone")
    is_tracking_target: BoolProperty(name="Mark as Target", default=False)
    tracking_anchor: EnumProperty(name="Anchor", items=[('eyes', "Eyes", ""), ('feet', "Feet", "")], default='eyes')
    use_custom_commands: BoolProperty(name="Use Custom Commands", default=False)
    sid: StringProperty(name="Scene ID", default="Cool_Name")
    custom_commands: CollectionProperty(type=MC_CustomCommand)
    active_command_index: IntProperty()
    custom_nbt: StringProperty(name="Custom NBT Data", default="NoAI:true,NoGravity:true,Invulnerable:true")

class MC_SceneProperties(PropertyGroup):
    export_type: EnumProperty(
        name="Export Type",
        items=[('ANIMATION', "Animation", "Export a full animation sequence"),
               ('MODEL', "Model", "Export a single static model from a specific frame")],
        default='ANIMATION'
    )
    
    minecraft_version: EnumProperty(
        name="Version",
        items=[('1.21', "1.21+", "pack_format 34+"),
               ('1.20.5', "1.20.5 - 1.20.6", "pack_format 32"),
               ('1.20.3', "1.20.3 - 1.20.4", "pack_format 26"),
               ('1.20.2', "1.20.2", "pack_format 18"),
               ('1.20', "1.20 - 1.20.1", "pack_format 15"),
               ('1.19.4', "1.19.4", "pack_format 12")],
        default='1.21',
        description="Select the target Minecraft version to ensure datapack compatibility"
    )

    model_export_frame: IntProperty(name="Frame", default=1, min=0, description="The timeline frame to export as a static model")
    
    add_block_id: StringProperty(name="", default="minecraft:oak_log")
    add_entity_id: StringProperty(name="", default="minecraft:allay")
    resource_pack_path: StringProperty(name="Resource Pack Path", subtype='FILE_PATH')
    datapack_output_path: StringProperty(name="Output Path", subtype='DIR_PATH')
    folder_name: StringProperty(name="Folder Name", default="MC Animaker Datapack")
    scene_name: StringProperty(name="Scene Name", default="Scene_Name")
    namespace: StringProperty(name="Namespace", default="mca")
    export_blocks: BoolProperty(name="Export Blocks", default=True)
    export_entities: BoolProperty(name="Export Entities", default=True)
    pause_support: BoolProperty(name="Pause/Resume Support", default=True)
    use_interpolation: BoolProperty(name="Use Interpolation", default=True)
    interpolation_duration: IntProperty(name="Duration (ticks)", default=2, min=0)
    start_interpolation: IntProperty(name="Start (ticks)", default=0, min=0)
    invert_normals_on_export: BoolProperty(name="Invert Normals on Export", default=False)
    dynamic_tracking: BoolProperty(name="Dynamic Tracking", default=False)
    tracking_mode: EnumProperty(name="Mode", items=[('OFF', "Off", ""), ('CENTER', "Center", ""), ('PLAYER', "Player", ""), ('TARGET', "Target", "")], default='OFF')
    global_tracking_anchor: EnumProperty(name="Anchor", items=[('EYES', "Eyes", ""), ('FEET', "Feet", ""), ('INDIVIDUAL', "Individual", "")], default='EYES')
    use_custom_frame_range: BoolProperty(name="Use Custom Frame Range", default=False)
    start_frame: IntProperty(name="Start Frame", default=1)
    end_frame: IntProperty(name="End Frame", default=250)
    show_object_panel: BoolProperty(name="Object Management", default=True)
    show_assets_panel: BoolProperty(name="Assets & Export", default=True)
    show_generation_panel: BoolProperty(name="Generation Options", default=True)
    show_advanced_options: BoolProperty(name="Advanced Options", default=False)