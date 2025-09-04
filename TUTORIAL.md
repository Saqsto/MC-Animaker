# MC Animaker Tutorial

Welcome to the official tutorial for MC Animaker! This guide will walk you through the entire process of creating a Minecraft animation, from initial setup to exporting your final datapack.

## Table of Contents
1.  [Installation](#1-installation)
2.  [Interface Overview](#2-interface-overview)
    * [Object Tab](#object-tab)
    * [Assets Tab](#assets-tab)
    * [Export Tab](#export-tab)
3.  [Your First Animation: A Step-by-Step Guide](#3-your-first-animation-a-step-by-step-guide)
    * [Step 1: Project Setup(Assets Tab)](#step-1-project-setupassets-tab)
    * [Step 2: Creating and Managing Objects(Object Tab)](#step-2-creating-and-managing-objectsobject-tab)
    * [Step 3: Animating in Blender](#step-3-animating-in-blender)
    * [Step 4: Setting Export Options(Export Tab)](#step-4-setting-export-optionsexport-tab)
    * [Step 5: Generating the Datapack](#step-5-generating-the-datapack)
4.  [Using Your Creation in Minecraft](#4-using-your-creation-in-minecraft)
5.  [Advanced Features](#5-advanced-features)
    * [Solidify](#solidify)
    * [Entity Tracking](#entity-tracking)
    * [Custom Commands](#custom-commands)

---

## 1. Installation

1. Download the latest version of MC Animaker as a `.zip` file from the [Releases page](https://github.com/user/repo/releases),  [Blender Extensions](https://extensions.blender.org/add-ons/mc-animaker) or [Gumroad](https://priqnot.gumroad.com/l/mc-animaker).  
2. Open Blender and go to `Edit > Preferences`.
3. Navigate to the `Add-ons` tab.
4. Click `Install...` and select the `.zip` file you downloaded.  
5. Find "MC Animaker" in the list and enable it by clicking the checkbox.  
6. (Optional but recommended) Click **Save Preferences** in the bottom left of the window(or enable *Auto-Save Preferences*) to keep the addon enabled the next time you open Blender.  
7. The addon panel will now appear in the 3D Viewport's sidebar(press `N` to open it).  

---

## 2. Interface Overview

The MC Animaker panel is organized into three simple tabs.

### Object Tab
This is the primary workspace for creating and editing the elements of your animation.
* **Add Object:** This part allows you to import a Minecraft block model or create an empty to represent an entity.
* **Selected Object:** When you select an object created by the addon, its specific properties will appear here, allowing you to edit its ID, behavior, and other attributes.

### Assets Tab
This tab holds all the global settings for your project. **It's the first place you should go when starting a new project.**
* **Project Settings:** Define the name of your datapack folder, your project's namespace, and the target Minecraft version for the datapack.
* **File Paths:** Tells the addon where to find your vanilla Resource Pack(`.zip`) and where to save the generated datapack.

### Export Tab
Here, you'll configure all the options for the exported datapack.
* **Export Type:** Choose between exporting a full `Animation` or a static `Model`.
* **Animation/Model Name:** Give your creation a name that will be used in the Minecraft `/function` commands.
* **Other Options:** Control everything from frame range and interpolation to entity tracking.

---

## 3. Your First Animation: A Step-by-Step Guide

For example, let's create a simple animation of a spinning furnace.

### Step 1: Project Setup(Assets Tab)

Before doing anything else, let's set up our project.

1.  Go to the **Assets** tab.
2.  **Folder Name:** Give your datapack a name, like `MyFirstAnimation`.
3.  **Namespace:** Set a unique, lowercase namespace, like `test`. This prevents conflicts with other datapacks.
4.  **MC  Version:** Select the Minecraft version you are going to use.
5.  **Output Path:** Click the folder icon and choose a directory where your datapack will be saved(ex: Your world's datapack folder).
6.  **Resource Pack:** Click the folder icon and navigate to the `.zip` file for the vanilla Minecraft resource pack of your target version. This is crucial for the addon to import block models and textures correctly.

### Step 2: Creating and Managing Objects(Object Tab)

Now, let's add a block to our scene.

1.  Go to the **Object** tab.
2.  In the `Add Object` panel, in the **Block ID** field, type `minecraft:furnace`.
3.  Click the cube icon next to it.
4.  An furnace model will be imported into your scene at the 3D cursor's location.

Notice that when the furnace is selected, a new panel appears below `Create New Object` showing the properties for that specific furnace. Here you can change its Block ID, animate its brightness, or set it to `Solidify`.

### Step 3: Animating in Blender

This is where you use your standard Blender skills. Let's make the furnace spin.

1.  Select the furnace.
2.  Go to frame 1 in the timeline. Press `I` and insert a `Rotation` keyframe.
3.  Go to a later frame, like frame 60.
4.  Press `R`, then `Z` to rotate on the Z-axis, and type `360` to make it do a full spin.
5.  Press `I` again and insert another `Rotation` keyframe.

Play the animation(`Spacebar`) to see your furnace spin!

### Step 4: Setting Export Options(Export Tab)

With our animation ready, we need to tell the addon how to export it.

1.  Go to the **Export** tab.
2.  **Export as:** Ensure `Animation` is selected.
3.  **Scene Name:** Give your animation a simple, lowercase name, like `spinning_furnace`. This will be part of the `/function` command.
4.  Review the other options. The defaults are usually fine for a first export. `Use Interpolation` is highly recommended as it creates much smoother movement in-game.

### Step 5: Generating the Datapack

This is the final step. Click the big **Generate Datapack** button at the bottom of the panel.

If everything is set up correctly, you'll see a success message. The addon has now created a complete, ready-to-use datapack in the output folder you specified in Step 1.

---

## 4. Using Your Creation in Minecraft

1. Find the generated datapack folder(ex: MyFirstAnimation) and copy it into your Minecraft world’s datapacks folder.(You can skip this step if the output path was already set to your world’s datapacks folder.)
2.  Launch Minecraft and load your world.
3.  To spawn your animation, use the `create` function. The command is built from your namespace and scene name:
    ```
    /function test:animations/_main/spinning_furnace/create
    ```
4.  To start the animation, use the `play` function:
    ```
    /function test:animations/_main/spinning_furnace/play
    ```
5.  Other useful commands:
    * `/function test:animations/_main/spinning_furnace/stop` - Stops the animation.
    * `/function test:animations/_main/spinning_furnace/loop` - Plays the animation in a loop.
    * `/function test:animations/_main/spinning_furnace/remove` - Removes the animation from the world.
    * `/function test:animations/_main/spinning_furnace/pause` - Pauses the animation
    * `/function test:animations/_main/spinning_furnace/resume` - Resumes the animation.
    > Note: Pause and Resume commands will not be generated if `Pause/Resume Support` is disabled on general options(Export Tab).

---

## 5. Advanced Features

### Solidify

By default, animated blocks are visual-only(`block_display` entities). You can't stand on them. The **Solidify** feature allows you to place a *real* block(like `minecraft:stone` or `minecraft:barrier`) at the object's location during the animation.

1.  Select a block object.
2.  In the **Object** tab, check the **Solidify as** box.
3.  You can specify a block ID to place. If left empty, it will use the object's own Block ID.
4.  Animate this checkbox property on the timeline to turn the physical block on and off.

### Entity Tracking

In the **Export** tab, you can enable **Dynamic Tracking** to make entities automatically face a target during the animation. This is perfect for making good camera shots with low effort.

### Custom Commands

For entities, you can enable **Use Custom Commands** in the **Object** tab. This reveals a list where you can add any Minecraft command(like `/particle`). These commands will be executed at the entity's position on every frame of the animation.
