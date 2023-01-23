import numpy as np
import pygame
from utils.geometry import *
from math import pi
from utils.datatypes import *

class vertex_model_show:
    n_grains = 0
    n_borders = 0
    n_vertices = 0

    t = 0
    vertices = []
    borders = []
    grains = []

    options_show = {}
    options_show_color = {}
    options_show_size = {}
    options_vertex_model = {}
    screen = None
    zoom = 1
    offsetx = 0
    offsety = 0
    multi_iter = 1
    states = []
    FINAL_TIMESTEP = 0
    def __init__(self, screen, OPTIONS_VERTEX_MODEL, OPTIONS_SHOW, OPTIONS_SHOW_COLOR, OPTIONS_SHOW_SIZE, FINAL_TIMESTEP):        
        self.n_grains = OPTIONS_VERTEX_MODEL["INITIAL_N_GRAINS"]
        self.n_borders = OPTIONS_VERTEX_MODEL["INITIAL_N_GRAINS"]*3
        self.n_vertices = OPTIONS_VERTEX_MODEL["INITIAL_N_GRAINS"]*2
        self.space_shown = [ [0, OPTIONS_SHOW["RESOLUTION"]], [0, OPTIONS_SHOW["RESOLUTION"]] ]
        self.options_show = OPTIONS_SHOW
        self.options_show_color = OPTIONS_SHOW_COLOR
        self.options_show_size = OPTIONS_SHOW_SIZE
        self.options_vertex_model = OPTIONS_VERTEX_MODEL
        self.FINAL_TIMESTEP = FINAL_TIMESTEP

        self.vertices = np.zeros(self.n_vertices, dtype=dt_vertex) 
        self.borders = np.zeros(self.n_borders, dtype=dt_border) 
        self.grains = np.zeros(self.n_grains, dtype=dt_grain) 
        self.general_status = np.zeros(self.FINAL_TIMESTEP, dtype=dt_general)

        self.ACTUAL_TIMESTEP = 0

        self.n_vertices_actual = self.n_vertices
        self.n_vertices_shown_actual = self.n_vertices
        self.n_grains_actual = self.n_grains
        self.n_grains_shown_actual = self.n_grains
        self.n_borders_actual = self.n_borders
        self.n_borders_shown_actual = self.n_borders

        self.space_wrap_y = False
        self.space_wrap_x = False
        
        self.show_vertices=True
        self.show_velocities=False
        self.show_borders=True
        self.show_ids =  False
        self.show_options =  False
        self.show_grain_orientation = False

        self.screen = screen
        if(self.options_vertex_model['DELTA_T'] < 1):
            aux = 1/self.options_vertex_model['DELTA_T']
            for i in range(0,20):
                if aux == 10**i:
                    self.n_zeros_delta_t = i
    
    def get_space_shown(self):
        #print(f"\noffset ({self.offsetx}, {self.offsety})")
        #print(f"zoom_aux: {self.aux_zoom} zoom: {self.zoom}")


        space_x = [self.offsetx, (self.offsetx+(1/self.zoom))]
        space_y = [self.offsety, (self.offsety+(1/self.zoom))]
        space_shown = [ space_x, space_y ]
        self.space_shown = space_shown
        
        if space_x[1] > 1:
            self.space_wrap_x = True
        else:
            self.space_wrap_x = False
        if space_y[1] > 1:
            self.space_wrap_y = True
        else:
            self.space_wrap_y = False
    
    def is_on_space_shown(self, x, y):
        return True
        space_x = self.space_shown[0]
        space_y = self.space_shown[1]
        in_space = False
        wrap_x = False
        wrap_y = False

        if(not self.space_wrap_x): # si no hay wrap 
            if (x >= space_x[0] and x < space_x[1]):
                in_space = True
        else: # si hay wrap
            if ( (x >= space_x[0] and x < 1) or (x>=0 and x < ( space_x[1]-(1/self.zoom) )) ):
                in_space = True


        if(in_space): 
            if(not self.space_wrap_y): # no hay wrap 
                if (y >= space_y[0] and y < space_y[1]):
                    in_space = True
                else:
                    in_space = False
            else: # si hay wrap 
                if ( (y >= space_y[0] and y < 1) or (y>=0 and y < ( space_y[1]-(1/self.zoom) )) ):
                    in_space = True
                else:
                    in_space = False
        """ if(not self.space_wrap_y): # si no hay wrap 
            if (y >= space_y[0] and y < space_y[1]):
                in_space = True
        else: # si hay wrap
            if ( (y >= space_y[0] and y < 1) or (y>=0 and y < ( space_y[1]-(1/self.zoom) )) ):
                in_space = True

        if(in_space): 
            if(not self.space_wrap_y): # no hay wrap 
                if (x >= space_x[0] and x < space_x[1]):
                    return True
            else: # si hax wrap 
                if ( (x >= space_x[0] and x < 1) or (x>=0 and x < ( space_x[1]-(1/self.zoom) )) ):
                    return True """
        return in_space
        
    def read_structure_timestep(self, sim_name):
        self.get_space_shown()
        self.vertices = np.zeros(self.n_vertices, dtype=dt_vertex) 
        self.borders = np.zeros(self.n_borders, dtype=dt_border) 
        self.grains = np.zeros(self.n_grains, dtype=dt_grain) # (id, alpha, x1, x2, x3, ..., x50)
        # VERTICES ------------------------------
        id_vertex = -1
        with open(f'out/{sim_name}/vertices/{self.ACTUAL_TIMESTEP}.npy', 'rb') as file1:
            self.vertices = np.load(file1)

        for i in range(self.n_vertices):
            self.vertices[i]["pos_vector"][1] = (1 - self.vertices[i]["pos_vector"][1])
            self.vertices[i]["vel_vector"][1] = (1 - self.vertices[i]["vel_vector"][1])

        # BORDERS --------------------------------
        if(self.show_borders):
            id_border = 0
            id_border = -1
            with open(f'out/{sim_name}/borders/{self.ACTUAL_TIMESTEP}.npy', 'rb') as file1:
                self.borders = np.load(file1)

        # GRAINS --------------------------------
        cont_grain = -1
        if(self.show_grain_orientation):
            with open(f'out/{sim_name}/grains/{self.ACTUAL_TIMESTEP}.npy', 'rb') as file1:
                self.grains = np.load(file1)

        # GENERAL --------------------------------
        with open(f'out/{sim_name}/general.npy', 'rb') as file1:
            self.general_status = np.load(file1)
        
        for g in range(self.n_grains):
            self.grains[g]["pos_vector"][1] = (1 - self.grains[g]["pos_vector"][1])
        
        if(self.show_borders):
            self.print_borders()
        if(self.show_grain_orientation):
            self.print_grains()
        self.print_vertices()
        
    def read_zoom_offset(self, move_x, move_y, zoom, zoom_0):
        
        if(self.zoom > 1200):
            zoom = zoom*25
        elif(self.zoom > 800):
            zoom = zoom*20
        elif(self.zoom > 250):
            zoom = zoom*15
        elif(self.zoom > 100):
            zoom = zoom*10
        elif(self.zoom > 50):
            zoom = zoom*5
        if(self.zoom > 10):
            zoom = zoom*2
        else:
            pass

        self.zoom = self.zoom + zoom
        if(zoom_0 == 1):
            self.zoom = 1
            self.offsetx = 0
            self.offsety = 0
        else:
            if(self.zoom < 1):
                self.zoom = 1

        self.aux_zoom = self.zoom*self.options_show["RESOLUTION"]
        
        offsetx = self.offsetx + (move_x*10/self.aux_zoom)
        offsety = self.offsety + (move_y*10/self.aux_zoom)
        vector_aux = (offsetx, offsety)
        vector_aux = self.adjust_offset(vector_aux)
        self.offsetx = vector_aux[0]
        self.offsety = vector_aux[1]

    def adjust_offset(self, vector_pos):
        x = vector_pos[0]
        y = vector_pos[1]
        if(x >= 1):
            x = x - 1
        if(x < 0):
            x = 1 + x

        if(y >= 1):
            y = y - 1
        if(y < 0):
            y = 1 + y
        vector_pos_return = [x, y]
        return vector_pos_return
        
    def next_iteration(self, list_states, plus_iters, move_x, move_y, zoom, zoom_0, sim_name):
        self.show_vertices =  list_states["show_vertices"]
        self.show_velocities =  list_states["show_velocities"]
        self.show_borders =  list_states["show_borders"]
        self.show_ids =  list_states["show_ids"]
        self.show_ids_vertices =  list_states["show_ids_vertices"]
        self.show_ids_grains =  list_states["show_ids_grains"]
        self.show_ids_borders =  list_states["show_ids_borders"]
        self.show_info_vertices =  list_states["show_info_vertices"]
        self.show_info_grains =  list_states["show_info_grains"]
        self.show_info_borders =  list_states["show_info_borders"]
        self.show_t_ext = list_states["show_t_ext"]
        self.show_options =  list_states["show_options"]
        self.show_grain_orientation =  list_states["show_grain_orientation"]
        self.multi_iter = list_states["multi_iter"]
        
        self.read_zoom_offset(move_x, move_y, zoom, zoom_0)

        if(plus_iters > 0):
            for i in range(0, plus_iters):
                #if((self.ACTUAL_TIMESTEP) < self.options_vertex_model["MAX_TIMESTEP"]):
                if((self.ACTUAL_TIMESTEP) < self.FINAL_TIMESTEP):
                    self.ACTUAL_TIMESTEP = self.ACTUAL_TIMESTEP+1*self.options_vertex_model["ITERS_BETWEEN_PRINTS"]
                else:
                    self.ACTUAL_TIMESTEP = 0
        if(plus_iters < 0):
            for i in range(0, (plus_iters*-1)):
                if(self.ACTUAL_TIMESTEP > 0):
                    self.ACTUAL_TIMESTEP = self.ACTUAL_TIMESTEP-1*self.options_vertex_model["ITERS_BETWEEN_PRINTS"]
                else:
                    #self.ACTUAL_TIMESTEP = self.options_vertex_model["MAX_TIMESTEP"]
                    self.ACTUAL_TIMESTEP = self.FINAL_TIMESTEP
        self.read_structure_timestep(sim_name)


    # PRINT TO SCREEN (GENERAL) ===================================================================================================

    def print_ui(self, actual_fps):    
        font_size = self.options_show_size["FONT_SIZE_UI"]
        corners = [
            (0,0), (0,1), (1,0), (1,1)
        ]
        textos_corr = [
                f"X: ({self.space_shown[0][0]}, {self.space_shown[0][1]})",   
                f"Y: ({self.space_shown[1][0]}, {self.space_shown[1][1]})",   
        ]
        textos_opciones = [
                textos_corr[0],
                textos_corr[1], 
                f"[ESC]: EXIT",        
                f"[O]: Toggle options",
                f"[C]: Toggle velocities",
                f"[V]: Toggle vertices",
                f"[B]: Toggle borders",    
                f"[G]: Toggle grain orientation",    
                f"[I]: Toggle IDS (Only on Pause)",        
                f"",        
                f"[A]: Move left",
                f"[D]: Move right",
                f"[W]: Move up",         
                f"[S]: Move down",       
                f"[Q]: - zoom",       
                f"[E]: + zoom",
                f"",           
                f"[VEL PLAY]: [1-9]",       
                f"[LEFT]: Prev timestep",               
                f"[RIGHT]: Next timestep",             
                f"[UP]: Next {self.options_show['FPS']} timestep",             
                f"[DOWN]: Prev {self.options_show['FPS']} timestep",           
                f"[SPACE]: PLAY/PAUSE",      
                f"[0]: Go to t=0",              
                f"[F1]: (Zoom:x1) + (pos:(0,0))",              
        ]
        if (not self.show_options):
            textos_opciones = [
                textos_corr[0],
                textos_corr[1], 
                f"[ESC]: EXIT",   
                f"[O]: Toggle options",
            ]
        textos = [
            textos_opciones,
            [
                f"delta_t: {self.options_vertex_model['DELTA_T']}",
                f"gamma_0: {self.options_vertex_model['GAMMA_0']}",
            ],
            [
                #f"actual t: {self.ACTUAL_TIMESTEP*self.options_vertex_model['DELTA_T']}",
                f"timestep: {self.ACTUAL_TIMESTEP} ({self.multi_iter} timestep x frame)",
                #f"t: {round(self.ACTUAL_TIMESTEP*self.options_vertex_model['DELTA_T'], self.n_zeros_delta_t)}",
                f"zoom: {self.zoom}x",
                f"FPS: {actual_fps}",
            ],
            [           
                f"n° grains: {self.general_status[self.ACTUAL_TIMESTEP]['n_grains']}",
                f"n° vertices: {self.general_status[self.ACTUAL_TIMESTEP]['n_vertices']}",
                f"n° borders: {self.general_status[self.ACTUAL_TIMESTEP]['n_borders']}",
                #f"n° grains shown: {self.n_grains_shown_actual}",
                #f"n° vertices shown: {self.n_vertices_shown_actual}",
                #f"n° borders shown: {self.n_borders_shown_actual}",
            ],
        ]
        for i in range(0,4):            
            font = pygame.font.Font('freesansbold.ttf', font_size)
            
            c = corners[i]
            lineas = textos[i]
            len_lineas = len(lineas)
            actual_line_height = 0
            height_between_lines = 4
            screen_margin = 10
            altura_lineas_final = len_lineas * font_size + len_lineas*height_between_lines
            for line_text in lineas:
                line = font.render(line_text, True, self.options_show_color["TEXT"], self.options_show_color["BACK_TEXT"])
                size = line.get_size()
                aux_x = 0
                if(c[0] == 0):
                    aux_x = ( size[0]/2 ) + screen_margin
                else:
                    aux_x = (self.options_show["RESOLUTION"]) - ( size[0]/2 ) - screen_margin

                if(c[1] == 0):
                    aux_y = ((font_size)) + actual_line_height + screen_margin
                else:
                    aux_y = (self.options_show["RESOLUTION"]-(altura_lineas_final)) +actual_line_height - screen_margin
                lineRect = line.get_rect()
                lineRect.center = (aux_x, aux_y)
                self.screen.blit(line, lineRect)
                actual_line_height += size[1] + height_between_lines # alto de linea no variable ARREGLAR
        
    def print_vertices(self):
        self.n_vertices_actual = 0
        self.n_vertices_shown_actual = 0
        for i in self.vertices:
            if( not i["not_enabled"]):
                self.n_vertices_actual += 1
                id = i["id"]
                x = i["pos_vector"][0]
                y = i["pos_vector"][1]    
                if(self.is_on_space_shown(x, y)):   
                    self.n_vertices_shown_actual += 1
                    vx = i["vel_vector"][0]
                    vy = i["vel_vector"][1]
                    ext_border = i["ext_border"]
                    xi_aux = (x+ self.offsetx, y+ self.offsety)
                    xi_aux = self.adjust_offset(xi_aux)
                    xi_aux = (xi_aux[0]*self.aux_zoom, xi_aux[1]*self.aux_zoom)
                    if(self.show_vertices):
                        original_pos = [x, y]
                        self.print_vertex(xi_aux[0], xi_aux[1], id, original_pos, ext_border)
                    if(self.show_velocities):
                        self.print_vertex_vel(xi_aux[0], xi_aux[1], vx*self.aux_zoom, vy*self.aux_zoom)
    
    def print_borders(self):
        self.n_borders_actual = 0
        self.n_borders_shown_actual = 0
        #pygame.draw.line(self.screen, (255, 0, 0), (0.2*self.aux_zoom, 0.2*self.aux_zoom), (0.7*self.aux_zoom, 0.2*self.aux_zoom), width=2)
        #pygame.draw.line(self.screen, (0, 255, 0), (0.2*self.aux_zoom, 0.2*self.aux_zoom), (0.2*self.aux_zoom, 0.7*self.aux_zoom), width=2)

        for i in self.borders:
            if (not i["not_enabled"]):
                self.n_borders_actual+=1
                id = i["id"]
                xi_index =  i["vertices"][0]
                xf_index = i["vertices"][1]
                arc_len = i["arc_len"]
                t_ext = i["t_ext"]
                t_ext_minor_to_delta_t = i["ext"]
                xi = self.vertices[xi_index]
                xf = self.vertices[xf_index]

                xi_aux = (xi["pos_vector"][0] + self.offsetx, xi["pos_vector"][1] + self.offsety)                
                xi_aux = self.adjust_offset(xi_aux)
                xf_aux = (xf["pos_vector"][0] + self.offsetx, xf["pos_vector"][1] + self.offsety)
                xf_aux = self.adjust_offset(xf_aux)
                if(self.is_on_space_shown(xi_aux[0], xi_aux[1]) or (self.is_on_space_shown(xf_aux[0], xf_aux[1]))):
                    self.n_borders_shown_actual += 1   

                    t_wrap = wrap_distances(xi_aux, xf_aux)
                    xi_wrap_aux = (t_wrap["xi"][0]*self.aux_zoom, t_wrap["xi"][1]*self.aux_zoom)
                    xf_wrap_aux = (t_wrap["xf"][0]*self.aux_zoom, t_wrap["xf"][1]*self.aux_zoom)

                    sum_x1 = (xi_aux[0] + xf_aux[0])*self.aux_zoom/2
                    sum_y1 = (xi_aux[1] + xf_aux[1])*self.aux_zoom/2
                    wrap = t_wrap["wrap"]
                    if(wrap): # si se produce wrap, se duplica el arco en el limite del area contrario
                        t_wrap2 = wrap_distances(xf_aux, xi_aux)
                        xi_wrap2_aux = (t_wrap2["xi"][0]*self.aux_zoom, t_wrap2["xi"][1]*self.aux_zoom)
                        xf_wrap2_aux = (t_wrap2["xf"][0]*self.aux_zoom, t_wrap2["xf"][1]*self.aux_zoom)
                        
                        self.print_border( xi_wrap2_aux, xf_wrap2_aux, t_ext_minor_to_delta_t)        
                                
                    self.print_border( xi_wrap_aux, xf_wrap_aux, t_ext_minor_to_delta_t)
                    if(not wrap):    
                        if(self.show_ids and self.show_ids_borders):
                            if(self.show_t_ext):
                                self.print_border_id(sum_x1, sum_y1, id, arc_len, xi_index, xf_index, t_ext, imprimir=1)
                            else:
                                self.print_border_id(sum_x1, sum_y1, id, arc_len, xi_index, xf_index, t_ext, imprimir=0)
                
    def print_grains(self):
        self.n_grains_actual = 0
        self.n_grains_shown_actual = 0
        for i in self.grains:
            if(not i["not_enabled"]):
                self.n_grains_actual += 1
                id_grain_aux = i["id"]
                alpha = i["alpha"]
                n_vertices = i["n_vertices"]
                arr_pos = i["pos_vector"]
                arr_vertices = i["vertices"][0:n_vertices]
                x_wrap = i["x_wrap"] # se puede usar pare repetir el grano en los ejes donde hace wrap
                y_wrap = i["y_wrap"] # se puede usar pare repetir el grano en los ejes donde hace wrap
                xpos = arr_pos[0]+self.offsetx
                if xpos >= 1:
                    xpos -=1
                elif xpos < 0:
                    xpos += 1
                ypos = arr_pos[1]+self.offsety
                if ypos >= 1:
                    ypos -=1
                elif ypos < 0:
                    ypos += 1
                
                if(self.is_on_space_shown(xpos, ypos)):  
                    self.n_grains_shown_actual += 1
                    arr_pos_screen = [(xpos)*self.aux_zoom, (ypos)*self.aux_zoom]                                
                    #arr_pos_screen = self.adjust_offset(arr_pos_screen)
                    self.print_grain(arr_pos_screen, id_grain_aux, alpha, n_vertices, arr_pos, arr_vertices)

    # PRINT TO SCREEN (BASICS) ===================================================================================================

    def print_border_id(self, xi, yi, id, arc_len, vi, vf, t_ext=0, imprimir=0):   
        xi_aux = (xi, yi)
        font = pygame.font.Font('freesansbold.ttf', self.options_show_size["FONT_SIZE_BORDER"])
        if(not self.show_info_borders):
            texto = str(id)
            line = font.render(texto, True, self.options_show_color["BORDER_TEXT"], self.options_show_color["BORDER_BACK"])
            lineRect = line.get_rect()
            lineRect.center = xi_aux
            self.screen.blit(line, lineRect)
        else:
            texto = str(id)
            line = font.render(texto, True, self.options_show_color["BORDER_TEXT"], self.options_show_color["BORDER_BACK"])
            lineRect = line.get_rect()
            lineRect.center = xi_aux
            self.screen.blit(line, lineRect)
            size = line.get_size()
            xi_aux2 = [xi, yi+size[1]+2]
            texto2=f'{vi}, {vf}'
            line2 = font.render(texto2, True, self.options_show_color["BORDER_TEXT"], self.options_show_color["BORDER_BACK"])
            lineRect2 = line2.get_rect()
            lineRect2.center = xi_aux2
            self.screen.blit(line2, lineRect2)
            
    def print_grain(self, xi_aux, id, alpha, n_vertices, original_pos, arr_vertices):
        if(self.show_grain_orientation):
            xf = xi_aux[0] + self.options_show_size["ALPHA_LEN"]
            yf = xi_aux[1] + self.options_show_size["ALPHA_LEN"]
            xf, yf = rotate((xi_aux[0], xi_aux[1]), (xf, yf), alpha)
            if(n_vertices == 3):
                pygame.draw.line(self.screen, self.options_show_color["ALPHA_3_SIDED"], xi_aux, (xf, yf), width=self.options_show_size["ALPHA_SIZE"])            
            else:
                pygame.draw.line(self.screen, self.options_show_color["ALPHA"], xi_aux, (xf, yf), width=self.options_show_size["ALPHA_SIZE"])
                
        if(self.show_ids and self.show_ids_grains):
            font = pygame.font.Font('freesansbold.ttf', self.options_show_size["FONT_SIZE_GRAIN"])

            t_vertices = ""
            for i in range(0, n_vertices):
                t_vertices = f"{t_vertices}{' ' if i!=0 else ''}{arr_vertices[i]}"

            if (not self.show_info_grains):
                texto1 = f"id:{id}"
                line = font.render(texto1, True, self.options_show_color["GRAIN_TEXT"], self.options_show_color["GRAIN_BACK"])
                size = line.get_size()
                lineRect = line.get_rect()
                lineRect.center = xi_aux
                self.screen.blit(line, lineRect)
            else:
                texto1 = f"id:{id} n_v: {n_vertices} p:[{original_pos[0]}, {original_pos[1]}]"
                texto1 = f"id:{id} n_v: {n_vertices}"
                line = font.render(texto1, True, self.options_show_color["GRAIN_TEXT"], self.options_show_color["GRAIN_BACK"])
                size = line.get_size()
                lineRect = line.get_rect()
                lineRect.center = xi_aux
                self.screen.blit(line, lineRect)

                line = font.render(t_vertices, True, self.options_show_color["GRAIN_TEXT"], self.options_show_color["GRAIN_BACK"])
                size = line.get_size()
                lineRect = line.get_rect()
                lineRect.center = [xi_aux[0], xi_aux[1]+size[1]+3]
                self.screen.blit(line, lineRect)
            
    def print_border(self, xi, xf, t_ext_minor_to_delta_t):
        if (t_ext_minor_to_delta_t == 0):            
            pygame.draw.line(self.screen, self.options_show_color["COLOR_BORDER_0"], xi, xf, width=self.options_show_size["BORDER_SIZE"])
        elif (t_ext_minor_to_delta_t == 1):
            pygame.draw.line(self.screen, self.options_show_color["COLOR_BORDER_1"], xi, xf, width=self.options_show_size["BORDER_SIZE"])
        else:
            print("ERROR")
            exit()

    def print_vertex_vel(self, xi, yi, vx, vy):                
        xi_aux = (xi, yi)
        xi_aux = self.adjust_offset(xi_aux)
        xi_aux = (xi_aux[0], xi_aux[1])
        xf_aux = (xi_aux[0] + vx*self.options_show_size["VERTEX_VEL_MULT"], xi_aux[1] + vy*self.options_show_size["VERTEX_VEL_MULT"])
        xf_aux = self.adjust_offset(xf_aux)
        xf_aux = (xf_aux[0], xf_aux[1])
        color_aux = ()
        if(vx > 0):
            if(vy > 0):
                color_aux = (153, 255, 102)
            else:
                color_aux = (255, 204, 102)
        else:
            if(vy > 0):
                color_aux = (255, 102, 204)
            else:
                color_aux = (51, 204, 255)

        pygame.draw.line(self.screen, color_aux, xi_aux, xf_aux, width=self.options_show_size["VERTEX_VEL_SIZE"])

    def print_vertex(self, xi, yi, id, original_pos, ext_border):
        xi_aux = (xi, yi)
        if(ext_border):
            pygame.draw.circle(self.screen, self.options_show_color["COLOR_VERTEX_1"], xi_aux, self.options_show_size["VERTEX_SIZE"])   
        else:
            pygame.draw.circle(self.screen, self.options_show_color["COLOR_VERTEX"], xi_aux, self.options_show_size["VERTEX_SIZE"])   
        
        if(self.show_ids and self.show_ids_vertices):
            font = pygame.font.Font('freesansbold.ttf', self.options_show_size["FONT_SIZE_VERTEX"])
            text = f'{id}'
            line = font.render(text, True, self.options_show_color["VERTEX_TEXT"], self.options_show_color["VERTEX_BACK"])        
            lineRect = line.get_rect()
            lineRect.center = xi_aux
            self.screen.blit(line, lineRect)
            size = line.get_size()

            if(self.show_info_vertices):                
                xi_aux2 = (xi_aux[0], xi_aux[1]+size[1]+1)
                text2 = f'g:[{self.vertices[id]["grains"][0]}, {self.vertices[id]["grains"][1]}, {self.vertices[id]["grains"][2]}]'
                line2 = font.render(text2, True, self.options_show_color["VERTEX_TEXT"], self.options_show_color["VERTEX_BACK"])        
                lineRect2 = line2.get_rect()
                lineRect2.center = xi_aux2
                self.screen.blit(line2, lineRect2)
                xi_aux2 = (xi_aux[0], xi_aux[1]+size[1]+1)
                size2 = line2.get_size()
                
                xi_aux3 = (xi_aux2[0], xi_aux2[1]+size2[1]+1)
                text4 = f'b:[{self.vertices[id]["borders"][0]}, {self.vertices[id]["borders"][1]}, {self.vertices[id]["borders"][2]}]'
                line4 = font.render(text4, True, self.options_show_color["VERTEX_TEXT"], self.options_show_color["VERTEX_BACK"])        
                lineRect4 = line4.get_rect()
                lineRect4.center = xi_aux3
                self.screen.blit(line4, lineRect4)
    