from utils.vertex_model_show import vertex_model_show
from options_visualization import OPTIONS_SHOW, OPTIONS_SHOW_COLOR, OPTIONS_SHOW_SIZE 
import json
from utils.geometry import *
import pygame
from pygame.locals import *
import os

def events_pygame(list_states, ticks_wait_input):
    keys = pygame.key.get_pressed()
    events = pygame.event.get()
    
    for evento in events:
        if evento.type == pygame.QUIT:
            list_states["running"] = False


    if keys[pygame.K_ESCAPE]:
        list_states["running"] = False

    if keys[pygame.K_SPACE]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["pause"]):
                list_states["pause"] = False    
            else:
                list_states["pause"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True

    
    if keys[pygame.K_o]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_options"]):
                list_states["show_options"] = False   
            else:
                list_states["show_options"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True

    
    if keys[pygame.K_i]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_ids"]):
                list_states["show_ids"] = False   
            else:
                list_states["show_ids"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True

    if keys[pygame.K_F2]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_ids_vertices"]):
                list_states["show_ids_vertices"] = False   
            else:
                list_states["show_ids_vertices"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True
        
        
    if keys[pygame.K_F3]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_ids_grains"]):
                list_states["show_ids_grains"] = False   
            else:
                list_states["show_ids_grains"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True
    if keys[pygame.K_F4]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_ids_borders"]):
                list_states["show_ids_borders"] = False   
            else:
                list_states["show_ids_borders"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True

    if keys[pygame.K_F5]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_info_vertices"]):
                list_states["show_info_vertices"] = False   
            else:
                list_states["show_info_vertices"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True
    if keys[pygame.K_F6]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_info_grains"]):
                list_states["show_info_grains"] = False   
            else:
                list_states["show_info_grains"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True
    if keys[pygame.K_F7]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_info_borders"]):
                list_states["show_info_borders"] = False   
            else:
                list_states["show_info_borders"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True

    if keys[pygame.K_t]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_t_ext"]):
                list_states["show_t_ext"] = False   
            else:
                list_states["show_t_ext"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True

    if keys[pygame.K_v]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_vertices"]):
                list_states["show_vertices"] = False   
            else:
                list_states["show_vertices"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True
    
    if keys[pygame.K_b]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_borders"]):
                list_states["show_borders"] = False     
            else:
                list_states["show_borders"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True
    
    if keys[pygame.K_c]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_velocities"]):
                list_states["show_velocities"] = False     
            else:
                list_states["show_velocities"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True
    if keys[pygame.K_g]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_grain_orientation"]):
                list_states["show_grain_orientation"] = False     
            else:
                list_states["show_grain_orientation"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True
    if keys[pygame.K_0]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["to_start"]):
                list_states["to_start"] = False     
            else:
                list_states["to_start"] = True                
            list_states["move_ticker"] = ticks_wait_input
            list_states["changes"] = True

    
    if keys[pygame.K_LEFT]:
            if(list_states["move_ticker"] == 0):         
                list_states["move_ticker"] = ticks_wait_input
                list_states["prev"] = True       
                list_states["changes"] = True
    if keys[pygame.K_RIGHT]:
            if(list_states["move_ticker"] == 0):         
                list_states["move_ticker"] = ticks_wait_input
                list_states["next"] = True      
                list_states["changes"] = True     

    if keys[pygame.K_DOWN]:
            if(list_states["move_ticker"] == 0):         
                list_states["move_ticker"] = ticks_wait_input
                list_states["prev_x2"] = True   
                list_states["changes"] = True            
    
    if keys[pygame.K_UP]:
            if(list_states["move_ticker"] == 0):         
                list_states["move_ticker"] = ticks_wait_input
                list_states["next_x2"] = True  
                list_states["changes"] = True

    
    if keys[pygame.K_a]:
        list_states["moves"]["left"] = True  
        list_states["changes"] = True     
        
    if keys[pygame.K_d]:
        list_states["moves"]["right"] = True  
        list_states["changes"] = True         
        
    if keys[pygame.K_w]:
        list_states["moves"]["up"] = True  
        list_states["changes"] = True             
        
    if keys[pygame.K_s]:
        list_states["moves"]["down"] = True  
        list_states["changes"] = True        
        
    if keys[pygame.K_F1]:
        list_states["moves"]["zoom_0"] = True  
        list_states["changes"] = True              
    else:
        if keys[pygame.K_q]:
            if(list_states["move_ticker"] == 0):         
                list_states["move_ticker"] = ticks_wait_input
                list_states["moves"]["plus_zoom"] = True  
                list_states["changes"] = True             
            
        if keys[pygame.K_e]:            
            if(list_states["move_ticker"] == 0):        
                list_states["moves"]["minus_zoom"] = True  
                list_states["changes"] = True             
                list_states["move_ticker"] = ticks_wait_input
                
        
    if keys[pygame.K_1]:
        list_states["multi_iter"] = 1  
        list_states["changes"] = True    
    if keys[pygame.K_2]:
        list_states["multi_iter"] = 2  
        list_states["changes"] = True    
    if keys[pygame.K_3]:
        list_states["multi_iter"] = 3  
        list_states["changes"] = True    
    if keys[pygame.K_4]:
        list_states["multi_iter"] = 4  
    if keys[pygame.K_5]:
        list_states["multi_iter"] = 5  
        list_states["changes"] = True    
    if keys[pygame.K_6]:
        list_states["multi_iter"] = 6    
    if keys[pygame.K_7]:
        list_states["multi_iter"] = 7  
        list_states["changes"] = True    
    if keys[pygame.K_8]:
        list_states["multi_iter"] = 8  
        list_states["changes"] = True    
    if keys[pygame.K_9]:
        list_states["multi_iter"] = 9  
        list_states["changes"] = True    
    
              
    
    return list_states

 
 

from os import system, name
def clear_console():
   # for windows
   if name == 'nt':
        _ = system('cls')
   # for mac and linux
   else:
        _ = system('clear')

def main():    
    simulations = []
    with open('out/simulations.txt') as f:
        simulations_aux = f.readlines()
        for s in simulations_aux:
            if(len(s.strip()) > 0):
                try:
                    sim_name_s = s.split(" ")[0]        
                    sim_ext_time = s.split(" ")[1].split(":")[1]     
                    sim_final_timestep = int(s.split(" ")[2].split(":")[1] )    
                    vals = sim_name_s.split("_")      
                    n_grains = vals[1][1:-1]
                    max_timestep = vals[2][1:-1]
                    date_gen = vals[3]
                    time_gen = vals[4]
                    sim_val = {
                        "name": sim_name_s,
                        "n_grains": n_grains,
                        "max_timestep": max_timestep,
                        "date_gen": date_gen,
                        "time_gen": time_gen,
                        "ext_time": sim_ext_time,
                        "final_timestep": sim_final_timestep,
                        
                    }
                    simulations.append(sim_val)
                except:
                    pass
    """ try:
    except:
        print("No simulations to visualize")
        return 0 """

    if(len(simulations) == 0):        
        clear_console()
        print("\n")
        print("No simulations to vizualize")
        return -1
    sim_input = -1
    error = False
    while(sim_input not in [(x+1) for x in range(len(simulations))]):
        clear_console()
        print("\n")
        print(f"Select a simulation to vizualize: ")
        print(f"Enter a number between: [1-{len(simulations)}]")
            
        print(f"Simulations: ")
        for s in range(len(simulations)):
            print(f"\t{s+1}.- {simulations[s]['name']}\tfinal_timestep:{simulations[s]['final_timestep']}")

            
        if(error):
            print(f"Try again")
        sim_input = input("\n>>>")
        try:
            sim_input = int(sim_input)
        except:
            pass
        error = True

    
    print("Opening visualization in new window")
    sim_name = simulations[sim_input-1]["name"]
    final_timestep = simulations[sim_input-1]['final_timestep']


    OPTIONS = {}
    with open(f'out/{sim_name}/options.json') as json_file:
        OPTIONS = json.load(json_file)

    TICKS_WAIT_INPUT = OPTIONS_SHOW["TICKS_WAIT_INPUT"]

    initial_load = 0
    pygame.init()
    res_x = OPTIONS_SHOW["RESOLUTION_X"]
    res_y = OPTIONS_SHOW["RESOLUTION_X"]
    windowSize = [res_x, res_y]
    screen = pygame.display.set_mode(windowSize) 
    vxm_show = vertex_model_show(screen, OPTIONS["OPTIONS_VERTEX_MODEL"], OPTIONS_SHOW, OPTIONS_SHOW_COLOR, OPTIONS_SHOW_SIZE, final_timestep)

    # set title and icon
    pygame.display.set_caption(f'VERTEX MODEL [sim[{sim_input}]: {sim_name}]')
    programIcon = pygame.image.load('assets/icon.png')
    pygame.display.set_icon(programIcon)

    
    fps_clock = pygame.time.Clock()

    moves_states = {
        "left": False,
        "right": False,
        "up": False,
        "down": False,
        "plus_zoom": False,
        "minus_zoom": False,        
        "zoom_0": False,
    }
    list_states = {
        "running": True,
        "pause": True,
        "show_vertices": True,
        "show_borders": True,
        "show_velocities": False,
        "show_grain_orientation": False,
        "show_ids": False,
        "show_ids_vertices": True,
        "show_ids_grains": True,
        "show_ids_borders": True,
        "show_info_vertices": False,
        "show_info_grains": False,
        "show_info_borders": False,
        "show_t_ext": False,
        "show_options": False,
        "to_start": False,
        "prev": False,
        "next": False,
        "prev_x2": False,
        "next_x2": False,
        "move_ticker": 0,
        "changes": False,
        "multi_iter": 1,
        "moves": moves_states
    }


    while list_states["running"]:
        screen.fill(OPTIONS_SHOW_COLOR["BACKGROUND_COLOR"]) # background
        fps_clock.tick(OPTIONS_SHOW["FPS"])
        list_states_new = events_pygame(list_states, TICKS_WAIT_INPUT)
        
        if list_states_new["move_ticker"] > 0:
            list_states_new["move_ticker"] -= 1

        to_start = 0       
        if(list_states_new["to_start"]):
            list_states_new["to_start"] = False
            vxm_show.ACTUAL_TIMESTEP = 0
            to_start = 1       
        plus_iters = 0

        if not list_states_new["pause"]: # if not pause, add multi_iter
            plus_iters = list_states_new["multi_iter"]
            list_states_new["show_ids"] = False
        else: # if pause == true, check arrows inputs 
            plus_iters = 0
            if(list_states_new["next"]):
                plus_iters = 1                
            elif(list_states_new["next_x2"]):                
                plus_iters = OPTIONS_SHOW["FPS_X2"]
            elif(list_states_new["prev"]):
                plus_iters = -1
            elif(list_states_new["prev_x2"]):
                plus_iters = -OPTIONS_SHOW["FPS_X2"]
            else:
                pass
        
        """ movement state variables  """
        moves = 0
        move_x = 0.0
        move_y = 0.0
        if(list_states_new["moves"]["left"]):
            moves = 1
            move_x = -1
        elif(list_states_new["moves"]["right"]):
            moves = 1
            move_x = 1
        elif(list_states_new["moves"]["up"]):
            moves = 1
            move_y = -1
        elif(list_states_new["moves"]["down"]):
            moves = 1
            move_y = 1
        else:
            pass

        """ zoom state variables """
        zoom = 0
        zoom_0 = 0
        if(list_states_new["moves"]["zoom_0"]):
            list_states_new["moves"]["zoom_0"] = False
            zoom_0 = 1
        else:
            if(list_states_new["moves"]["plus_zoom"]):
                moves = 1
                zoom = -1
            elif(list_states_new["moves"]["minus_zoom"]):
                moves = 1
                zoom = 1
            else:
                pass

        if( (not list_states_new["pause"]) or (plus_iters !=0) or (moves!=0) or (to_start!=0) or (list_states_new["changes"]) or (initial_load == 0)): # si existe un cambio de estado o no se esta en pausa
            
            initial_load = 1
            list_states_new["next"] = False
            list_states_new["changes"] = False
            list_states_new["next_x2"] = False
            list_states_new["prev"] = False
            list_states_new["prev_x2"] = False
            list_states_new["moves"]["left"] = False
            list_states_new["moves"]["right"] = False
            list_states_new["moves"]["up"] = False
            list_states_new["moves"]["down"] = False
            list_states_new["moves"]["plus_zoom"] = False
            list_states_new["moves"]["minus_zoom"] = False
            vxm_show.next_iteration(list_states_new, plus_iters, move_x, move_y, zoom, zoom_0, sim_name)

            actual_fps = int(fps_clock.get_fps()),
            vxm_show.print_ui(actual_fps)
            pygame.display.flip()
            list_states = list_states_new 
            


    pygame.quit()


if __name__ == '__main__':
    main()



  