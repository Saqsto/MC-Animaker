# Created using MC Animaker by Priqnot

execute as @e[tag=wood_hand_ref] at @s run tp @e[tag=wood_hand_entity_0,limit=1,sort=nearest] ~-2.504 ~3.214 ~-5.031 facing entity @e[tag=target,limit=1,sort=nearest] feet
execute as @e[tag=wood_hand_ref] at @s run tp @e[tag=wood_hand_entity_1,limit=1,sort=nearest] ~-0.860 ~3.776 ~-0.248 facing entity @e[tag=target,limit=1,sort=nearest] eyes
execute if entity @e[tag=wood_hand_playing] run schedule function priqnot:animations/scenes/wood_hand/keyframes/entity/15 1t
execute if entity @e[tag=wood_hand_paused] run schedule function priqnot:animations/scenes/wood_hand/keyframes/entity/14 1t