# Created using MC Animaker by Priqnot

execute as @e[tag=wood_hand_ref] at @s run tp @e[tag=wood_hand_entity_0,limit=1,sort=nearest] ~3.362 ~7.044 ~-6.855 facing entity @e[tag=target,limit=1,sort=nearest] feet
execute as @e[tag=wood_hand_ref] at @s run tp @e[tag=wood_hand_entity_1,limit=1,sort=nearest] ~-0.137 ~5.440 ~0.104 facing entity @e[tag=target,limit=1,sort=nearest] eyes
execute if entity @e[tag=wood_hand_playing] run schedule function priqnot:animations/scenes/wood_hand/keyframes/entity/65 1t
execute if entity @e[tag=wood_hand_paused] run schedule function priqnot:animations/scenes/wood_hand/keyframes/entity/64 1t