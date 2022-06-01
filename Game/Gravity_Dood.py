#-----------------------------------------------------------------------------
# Name:        Assignment Template (assignment.py)
# Purpose:     A description of your program goes here.
#
# Author:      Mr. Brooks
# Created:     13-Sept-2020
# Updated:     13-Sept-2020
#-----------------------------------------------------------------------------
#I think this project deserves a level XXXXXX because ...
#
#Features Added:
#   ...
#   ...
#   ...
#-----------------------------------------------------------------------------

from random import randint, sample
import pygame
import json
from Assets.Player_Assets.Player import Player
from Assets.Collidables.Static.Short.Short import Spike, Saw
from Assets.Collidables.Static.Tall.Tall import Tall_Saw, Spear
from Assets.Collidables.Game_States.Start import Title
from Assets.Collidables.Game_States.Help import Help
from Assets.Collidables.Game_States.Game_Over import GameOver
import os
from time import sleep
import webbrowser

def main():
    #-----------------------------Setup------------------------------------------------------#
    """ Set up the game and run the main game loop """
    pygame.init()      # Prepare the pygame module for use
    surfaceSize = [750, 350]   # Desired physical surface size, in pixels.
    
    clock = pygame.time.Clock()  #Force frame rate to be slower

    # Create surface of (width, height), and its window.
    mainSurface = pygame.display.set_mode((surfaceSize[0], surfaceSize[1]))

    bg = pygame.image.load(os.path.join('Game', 'Assets', 'bg.png'))

    player_sprite = Player((150, 200), mainSurface, surfaceSize)

    spike_trap = Spike([100, 100], mainSurface)
    saw_trap = Saw((100, 200), mainSurface)

    spear_trap = Spear(mainSurface, [200, 100])
    tall_saw = Tall_Saw(mainSurface, [300, 100])

    title_screen = Title(mainSurface)
    help_screen = Help(mainSurface)
    game_over = GameOver(mainSurface)
    help_state = False
    #-----------------------------Program Variable Initialization----------------------------#

    instructions = 'file:///' + os.path.join(os.getcwd(), 'Game', 'Assets', 'Instructions.html')
    print(instructions)

    player_sprite.posY = surfaceSize[1] - player_sprite.shell[3] - 10
    player_sprite.upside_down = False
    falling = False
    player_gravity = 60

    # Opens up a json file and takes the limit values used for spawning traps and assign them variables
    with open(os.path.join(os.getcwd(), 'Game', 'Assets', 'Collidables', 'Limit.json'), 'r') as f:
        Limit = json.load(f)
        tall_range = range(Limit['static']['tall']['min'], Limit['static']['tall']['max'] + 1)
        short_range = range(Limit['static']['short']['min'], Limit['static']['short']['max'] + 1)

    point_in_sr = sample(short_range, 1)
    point_in_tr = sample(tall_range, 1)
    
    first_object = True

    trap_types = [spike_trap,
                  saw_trap,
                  spear_trap,
                  tall_saw]

    traps = []
    trap = randint(0, len(trap_types)-1) # The starting point of the infinite chain of trap spawning
                                         # Chooses a random number when the program starts to act as a starting point for the nex trap to be randomly chosen

    frame_count = 0
    game_start = False

    game_state = 'Start'

    #-----------------------------Main Program Loop---------------------------------------------#
    while True:       
        mainSurface.blit(bg, (-43, -95))

        mouse = pygame.mouse.get_pos()
        mouse_hitbox = pygame.Rect(mouse[0], mouse[1], 2, 2)

        #-----------------------------Event Handling-----------------------------------------#
        ev = pygame.event.poll()    # Look for any event
        if ev.type == pygame.QUIT:  # Window close button clicked?
            break                   #   ... leave game loop

        if game_state == 'Start':
            title_buttons = title_screen.draw_elements() # element 0 is the hitbox for the start button and 1 is the credits button

            if ev.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] == 1:
                if pygame.Rect.colliderect(mouse_hitbox, title_buttons[0]):
                    game_state = 'Game'

            if ev.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] == 1:
                if pygame.Rect.colliderect(mouse_hitbox, title_buttons[1]):
                    game_state = 'Help'
                    help_state = True

        if game_state == 'Help':
            if help_state:
                webbrowser.open_new_tab(instructions)
                help_state = not help_state
            back_button = help_screen.draw_element()
            if ev.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] == 1:
                if pygame.Rect.colliderect(mouse_hitbox, back_button):
                    game_state = 'Start'

        if game_state == 'Game':
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE and falling == False:
                    player_sprite.upside_down = not player_sprite.upside_down
                    falling = True   
            #-----------------------------Program Logic---------------------------------------------#
            # Update your game objects and data structures here...

            player_hitbox = player_sprite.draw_player()
            player_sprite.frame_update(frame_count)

            if game_start == False:
                start_of_game = pygame.time.get_ticks()
                game_start = not game_start

            # Spawning Algorithm
            # Picks a trap out of a predetermined list containing all trap types at random
            # Creates a new instance of the selected trap, if it is the first trap spawned
            # It will be defined as the first trap so that the next object will be spawned
            # Relative to the previous trap, being the start to the infintie chain
            if first_object:
                trap_types[trap].posX = 1000
                if isinstance(trap_types[trap], Saw) or isinstance(trap_types[trap], Tall_Saw):
                    trap_types[trap].posY = 10
                elif isinstance(trap_types[trap], Spike) or isinstance(trap_types[trap], Spear):
                    trap_types[trap].posY = surfaceSize[1] - trap_types[trap].shell[3] - 10
                traps.append(trap_types[trap])
                first_object = False
                
            elif first_object == False:
                if isinstance(trap_types[trap], Spike):
                    if traps[-1].posX <= 1000 - point_in_sr[0]:
                        point_in_sr = sample(short_range, 1)
                        spike_trap = Spike([1000, surfaceSize[1] - trap_types[trap].shell[3] - 10], mainSurface)
                        traps.append(spike_trap)
                        trap = randint(0 , len(trap_types)-1)
                elif isinstance(trap_types[trap], Saw):
                    if traps[-1].posX <= 1000 - point_in_sr[0]:
                        point_in_sr = sample(short_range, 1)
                        saw_trap = Saw([1000, 10], mainSurface)
                        traps.append(saw_trap)
                        trap = randint(0 , len(trap_types)-1)
                elif isinstance(trap_types[trap], Spear):
                    if traps[-1].posX <= 1000 - point_in_tr[0]:
                        point_in_tr = sample(tall_range, 1)
                        spear_trap = Spear(mainSurface, [1000, surfaceSize[1] - trap_types[trap].shell[3] - 10])
                        traps.append(spear_trap)
                        trap = randint(0 , len(trap_types)-1)
                elif isinstance(trap_types[trap], Tall_Saw):
                    if traps[-1].posX <= 1000 - point_in_tr[0]:
                        point_in_tr = sample(tall_range, 1)
                        tall_saw = Tall_Saw(mainSurface, [1000, 10])
                        traps.append(tall_saw)
                        trap = randint(0 , len(trap_types)-1)

            if falling:
                player_sprite.gravity(player_gravity)
                if player_sprite.upside_down:
                    if player_sprite.posY == 10:
                        falling = not falling
                        player_sprite.speed = 1
                elif player_sprite.upside_down == False:
                    if player_sprite.posY == surfaceSize[1] - player_sprite.shell[3] - 10:
                        falling = not falling
                        player_sprite.speed = 1
                

            for current_trap in traps:
                current_trap.posX -= 4

            for current_trap in traps:
                current_trap.update_animation(frame_count, current_trap.framerate)
                trap_hitbox = current_trap.draw_trap()
                if pygame.Rect.colliderect(player_hitbox, trap_hitbox):
                    game_state = 'Game Over'
                    final_time = pygame.time.get_ticks()
                    score = final_time - start_of_game
                    with open(os.path.join(os.getcwd(), 'Game', 'Assets', 'Highscore.json'), 'r') as f:
                        score_file = json.load(f)
                        if score_file['highscore'] == '\n':
                            with open(os.path.join(os.getcwd(), 'Game', 'Assets', 'Highscore.json'), 'w') as j:
                                data_to_write = {'highscore': score}
                                json.dump(data_to_write, j, indent=2)
                                highscore = score
                        else:
                            if score_file['highscore'] < score:
                               with open(os.path.join(os.getcwd(), 'Game', 'Assets', 'Highscore.json'), 'w') as j:
                                data_to_write = {'highscore': score}
                                json.dump(data_to_write, j, indent=2)
                                highscore = score
                            else:
                                highscore = score_file['highscore']
                    sleep(1)

            if traps:
                if traps[0] == (0 - traps[0].shell[2]):
                    try:
                        if traps[1]:
                            traps.remove(traps[0])
                    except IndexError:
                        pass

        if game_state == 'Game Over':
            game_over_buttons = game_over.draw_elements(score, highscore) # element 0 is quit button
                                                                          # element 1 is menu button
                                                                          # element 2 is restart button
            
            if ev.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] == 1:
                if pygame.Rect.colliderect(mouse_hitbox, game_over_buttons[0]):
                    break
                if pygame.Rect.colliderect(mouse_hitbox, game_over_buttons[1]):
                    game_state = 'Start'
                if pygame.Rect.colliderect(mouse_hitbox, game_over_buttons[2]):
                    player_sprite.upside_down = False
                    falling = False
                    player_sprite.posY = surfaceSize[1] - player_sprite.shell[3] - 10
                    traps = []
                    first_object = True
                    game_state = 'Game'


        # Now the surface is ready, tell pygame to display it!
        pygame.display.flip()
        
        frame_count += 1
        clock.tick(60) #Force frame rate to be slower
 

    pygame.quit()     # Once we leave the loop, close the window.

main()