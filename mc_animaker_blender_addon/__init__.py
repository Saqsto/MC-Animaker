bl_info = {
    "name": "MC Animaker",
    "author": "Priqnot",
    "version": (1, 0, 0),
    "blender": (4, 2, 12),
    "location": "View3D > Sidebar > MC Animaker",
    "description": "An all-in-one Blender toolkit for creating advanced Minecraft animations. Animate blocks and entities with the full power of Blender tools and export them directly to a ready-to-use Minecraft datapack. It supports Block Displays, Entity Positioning, Entity Tracking(for camera setups), Custom Commands, and NBT Data",
    "category": "MC Animaker",
}

import bpy
from bpy.props import PointerProperty, FloatProperty, StringProperty

def draw_mca_progress_bar(self, context):
    wm = context.window_manager
    if hasattr(wm, 'mca_progress_text') and wm.mca_progress_text:
        layout = self.layout
        row = layout.row(align=True)
        row.label(text=wm.mca_progress_text)
        row.progress(text="", factor=wm.mca_progress / 100.0, factor_text=f"{int(wm.mca_progress)}%")

from .properties import MC_CustomCommand, MC_ObjectProperties, MC_SceneProperties
from .ui import MC_UL_CustomCommands, MC_PT_Panel
from .operators import (
    MC_OT_AddCommand, MC_OT_RemoveCommand, MC_OT_AddBlock, MC_OT_AddEntity,
    MC_OT_ApplyTextures, MC_OT_GenerateDatapack, MC_OT_KeyframeProperty
)

classes = (
    MC_CustomCommand,
    MC_ObjectProperties,
    MC_SceneProperties,
    MC_UL_CustomCommands,
    MC_PT_Panel,
    MC_OT_AddCommand,
    MC_OT_RemoveCommand,
    MC_OT_AddBlock,
    MC_OT_AddEntity,
    MC_OT_ApplyTextures,
    MC_OT_GenerateDatapack,
    MC_OT_KeyframeProperty,
)

def register():
    """Registra todas as classes e propriedades do addon."""
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.mc_props = PointerProperty(type=MC_ObjectProperties)
    bpy.types.Scene.mc_scene_props = PointerProperty(type=MC_SceneProperties)
    
    bpy.types.WindowManager.mca_progress = FloatProperty(name="Progress", subtype='PERCENTAGE', min=0, max=100)
    bpy.types.WindowManager.mca_progress_text = StringProperty(name="Progress Text")
    
    bpy.types.STATUSBAR_HT_header.append(draw_mca_progress_bar)

def unregister():
    """Desregistra tudo na ordem inversa para uma limpeza segura."""
    bpy.types.STATUSBAR_HT_header.remove(draw_mca_progress_bar)

    del bpy.types.WindowManager.mca_progress
    del bpy.types.WindowManager.mca_progress_text

    del bpy.types.Object.mc_props
    del bpy.types.Scene.mc_scene_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()