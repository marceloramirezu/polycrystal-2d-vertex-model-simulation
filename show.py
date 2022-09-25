
from ast import For
from utils.vertex_model_show import vertex_model_show
from options import *
from utils.geometry import *
import pygame
import time


def events_pygame(list_states):
    keys = pygame.key.get_pressed()
    events = pygame.event.get()
    
    aux = False
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
            list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
            list_states["changes"] = True

    
    if keys[pygame.K_o]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_options"]):
                list_states["show_options"] = False   
            else:
                list_states["show_options"] = True                
            list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
            list_states["changes"] = True

    
    if keys[pygame.K_i]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_ids"]):
                list_states["show_ids"] = False   
            else:
                list_states["show_ids"] = True                
            list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
            list_states["changes"] = True
    if keys[pygame.K_t]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_t_ext"]):
                list_states["show_t_ext"] = False   
            else:
                list_states["show_t_ext"] = True                
            list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
            list_states["changes"] = True

    if keys[pygame.K_v]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_vertices"]):
                list_states["show_vertices"] = False   
            else:
                list_states["show_vertices"] = True                
            list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
            list_states["changes"] = True
    
    if keys[pygame.K_b]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_borders"]):
                list_states["show_borders"] = False     
            else:
                list_states["show_borders"] = True                
            list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
            list_states["changes"] = True
    
    if keys[pygame.K_c]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_velocities"]):
                list_states["show_velocities"] = False     
            else:
                list_states["show_velocities"] = True                
            list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
            list_states["changes"] = True
    if keys[pygame.K_g]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["show_alpha"]):
                list_states["show_alpha"] = False     
            else:
                list_states["show_alpha"] = True                
            list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
            list_states["changes"] = True
    if keys[pygame.K_0]:
        if(list_states["move_ticker"] == 0):        
            if(list_states["start"]):
                list_states["start"] = False     
            else:
                list_states["start"] = True                
            list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
            list_states["changes"] = True

    
    if keys[pygame.K_LEFT]:
            if(list_states["move_ticker"] == 0):         
                list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
                list_states["prev"] = True       
                list_states["changes"] = True
    if keys[pygame.K_RIGHT]:
            if(list_states["move_ticker"] == 0):         
                list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
                list_states["next"] = True      
                list_states["changes"] = True     

    if keys[pygame.K_DOWN]:
            if(list_states["move_ticker"] == 0):         
                list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
                list_states["prev_x2"] = True   
                list_states["changes"] = True            
    
    if keys[pygame.K_UP]:
            if(list_states["move_ticker"] == 0):         
                list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
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
                list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
                list_states["moves"]["plus_zoom"] = True  
                list_states["changes"] = True             
            
        if keys[pygame.K_e]:            
            if(list_states["move_ticker"] == 0):        
                list_states["moves"]["minus_zoom"] = True  
                list_states["changes"] = True             
                list_states["move_ticker"] = OPTIONS_SHOW["TICKS_WAIT_INPUT"]
                
        
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

 
 


def main():    
    
    pygame.init()
    screen = pygame.display.set_mode([OPTIONS_SHOW["RESOLUTION"], OPTIONS_SHOW["RESOLUTION"]]) 
    vxm_show = vertex_model_show(screen, OPTIONS_VERTEX_MODEL, OPTIONS_SHOW, OPTIONS_SHOW_COLOR, OPTIONS_SHOW_TAM)

    pygame.display.set_caption('POLICRISTALES')
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
        "show_alpha": False,
        "show_ids": False,
        "show_t_ext": False,
        "show_options": False,
        "start": False,
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
        fps_clock.tick(FPS)
        list_states_new = events_pygame(list_states)
        
        if list_states_new["move_ticker"] > 0:
            list_states_new["move_ticker"] -= 1

        screen.fill(BACKGROUND_COLOR) # background
        start = 0       
        if(list_states_new["start"]):
            list_states_new["start"] = False
            vxm_show.t = 0
            start = 1       
        plus_iters = 0
        """ Si no esta en pausa agrega una iteracion por frame """
        if not list_states_new["pause"]:
            plus_iters = 1*list_states_new["multi_iter"]
            list_states_new["show_ids"] = False
        else:
            """ si esta en pausa se revisan los inputs para avanzar o retroceder en el tiempo """
            plus_iters = 0
            if(list_states_new["next"]):
                plus_iters = 1                
            elif(list_states_new["next_x2"]):                
                plus_iters = OPTIONS_SHOW["FPS"]
            elif(list_states_new["prev"]):
                plus_iters = -1
            elif(list_states_new["prev_x2"]):
                plus_iters = -OPTIONS_SHOW["FPS"]
            else:
                pass
        
        """ asigna variables de movimiento  """
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

        """ asigna variables de zoom """
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
            
            #if(list_states_new[""])

        if(not list_states_new["pause"] or plus_iters !=0 or moves!=0 or start!=0 or list_states_new["changes"]): # si existe un cambio de estado o no se esta en pausa
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
            vxm_show.next_iteration(list_states_new, plus_iters, move_x, move_y, zoom, zoom_0)
            
            actual_fps = int(fps_clock.get_fps()),

            vxm_show.print_ui(actual_fps)
            pygame.display.flip()
            list_states = list_states_new 
            


    pygame.quit()


if __name__ == '__main__':
    main()



  