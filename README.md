# MC Animaker

[![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)](https://github.com/priqnot/MC-Animaker/releases/tag/v1.0.0)
[![Blender Version](https://img.shields.io/badge/Blender-4.2+-orange.svg)](https://www.blender.org/download/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

> MC Animaker is the definitive tool for map makers, content creators, and animators who want to push the boundaries of what's possible in Minecraft.

> The addon can be used to create extremely advanced Minecraft animations. Animate blocks and entities with the full power of Blender tools and export them directly to a ready-to-use Minecraft datapack. It supports Block Displays, Entity Positioning, Entity Tracking(for camera setups), Custom Commands, and NBT Data.

# Key Features:

- 1:1 Blender to Minecraft Animation: What you see in the Blender viewport is exactly what you get in-game. Animate with confidence thanks to a perfectly synchronized coordinate system.

- Advanced Datapack Controls: Automatically generates a robust datapack with intuitive functions to play, pause, resume, loop, and stop your animation.

- Resource Pack Integration: Simply point to your resource pack, and MC Animaker will automatically find and apply the correct textures to your blocks in the Blender viewport, including directional and animated textures like furnaces and command blocks. It was designed to work perfectly with "VanillaDefault 1.21.7" and similar resource packs.
 
---

## Showcase

Check out this video to get a tast of what MC Animaker can do:
[![MC Animaker Showcase](https://img.youtube.com/vi/C-nmq5UASCU/maxresdefault.jpg)]([https://youtu.be/yUUkNl-F2ZI](https://www.youtube.com/watch?v=C-nmq5UASCU))



## 📦 Installation

1.  Go to the **[Releases](https://github.com/Priqnot/mc-animaker/releases)** page of this repository.
2.  Download the latest MC Animator `.zip` file.
3.  Open Blender and go to **Edit > Preferences... > Add-ons**.
4.  Click the **Install...** button and select the downloaded `.zip` file.
5.  Find "MC Animaker" in the list and enable the checkbox next to it.
6.  A new **MC Animaker** tab will appear in the 3D View's sidebar (press `N` to open).

## 🚀 In-game commands
1. Launch Minecraft and load your world.
2. Run `/reload` in the chat.
3. To create your animation, run: `/function <namespace>:animations/_main/<scene_name>/create`
4. To play it, run: `/function <namespace>:animations/_main/<scene_name>/play`
(Replace `<namespace>` and `<scene_name>` with the values from your panel, e.g., `mca:animations/_main/intro_scene/play`)
