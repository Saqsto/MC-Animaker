# Created using MC Animaker by Priqnot

execute as @e[tag=wood_hand_ref] at @s run tp @e[tag=wood_hand_entity_0,limit=1,sort=nearest] ~-2.566 ~3.174 ~-3.312 facing entity @e[tag=target,limit=1,sort=nearest] feet
execute as @e[tag=wood_hand_ref] at @s run tp @e[tag=wood_hand_entity_1,limit=1,sort=nearest] ~-1.018 ~3.583 ~-0.230 facing entity @e[tag=target,limit=1,sort=nearest] eyes
execute if entity @e[tag=wood_hand_playing] run schedule function priqnot:animations/scenes/wood_hand/keyframes/entity/3 1t
execute if entity @e[tag=wood_hand_paused] run schedule function priqnot:animations/scenes/wood_hand/keyframes/entity/2 1t