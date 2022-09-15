import numpy as np;
import pygame
from utils.geometry import *
from math import pi

dt_vertex = np.dtype([('id', np.uint), ('pos_vector', np.float64, (2,)), ('vel_vector', np.float64, (2,)), ('energy', np.float64), ('enable', np.bool_)])
dt_border = np.dtype([('id', np.uint), ('vertices', np.uint, (2,)), ('diff_vector', np.float64, (2,)), ('gamma', np.float64), ('arc_len', np.float64), ('energy', np.float64), ('enable', np.bool_)])
dt_grain = np.dtype([('id', np.uint), ('alpha', np.float64), ('vertices', np.uint, (50,))])

class vertex_model_show:
    gamma_0= 0
    mov_vertex= 0
    n_grains = 0
    n_borders = 0
    n_vertices = 0

    t = 0
    vertices = []
    borders = []
    grains = []

    options_show = {}
    options_show_color = {}
    options_show_tam = {}
    options_vertex_model = {}
    screen = None
    zoom = 1
    offsetx = 0
    offsety = 0
    multi_iter = 1
    states = []
    def __init__(self, screen, OPTIONS_VERTEX_MODEL, OPTIONS_SHOW, OPTIONS_SHOW_COLOR, OPTIONS_SHOW_TAM):        
        self.n_grains = OPTIONS_VERTEX_MODEL["INITIAL_N"]
        self.n_borders = OPTIONS_VERTEX_MODEL["INITIAL_N"]*3
        self.n_vertices = OPTIONS_VERTEX_MODEL["INITIAL_N"]*2
        
        self.options_show = OPTIONS_SHOW
        self.options_show_color = OPTIONS_SHOW_COLOR
        self.options_show_tam = OPTIONS_SHOW_TAM
        self.options_vertex_model = OPTIONS_VERTEX_MODEL

        self.vertices = np.zeros(self.n_vertices, dtype=dt_vertex) 
        self.borders = np.zeros(self.n_borders, dtype=dt_border) 
        self.grains = np.zeros(self.n_grains, dtype=dt_grain) # (id, alpha, x1, x2, x3, ..., x50)
        self.t = 0

        self.show_vertices=True
        self.show_velocities=False
        self.show_borders=True
        self.show_ids =  False
        self.show_options =  False
        self.show_alpha = False

        self.screen = screen
        if(self.options_vertex_model['DELTA_T'] < 1):
            aux = 1/self.options_vertex_model['DELTA_T']
            for i in range(0,20):
                if aux == 10**i:
                    self.n_zeros_delta_t = i
                    
        
        #self.leer_granos_t()

    
    def print_ui(self):
        

        corners = [
            (0,0), (0,1), (1,0), (1,1)
        ]
        list_font_sizes = [
            12, 12, 12, 12
        ]
        textos_corr = [
                f"(Xo: {0+self.offsetx})",   
                f"(Yo: {0+self.offsety})"
        ]
        textos_opciones = [
                textos_corr[0],
                textos_corr[1], 
                f"[ESC]: EXIT",        
                f"[O]: Toggle Options",
                f"[C]: Toggle velocities",
                f"[V]: Toggle vertices",
                f"[B]: Toggle borders",    
                f"[G]: Toggle alpha",    
                f"[I]: Toggle IDS (Only on Pause)",        
                f"",        
                f"[A]: Move Left",
                f"[D]: Move Right",
                f"[W]: Move Up",         
                f"[S]: Move Down",       
                f"[Q]: - ZOOM",       
                f"[E]: + ZOOM",
                f"",           
                f"[VEL PLAY]: [1-9]",       
                f"[LEFT]: Prev iter",               
                f"[RIGHT]: Next iter",             
                f"[UP]: Next {self.options_show['FPS']} iter",             
                f"[DOWN]: Prev {self.options_show['FPS']} iter",           
                f"[SPACE]: PLAY/PAUSE",      
                f"[0]: START",              
        ]
        if (not self.show_options):
            textos_opciones = [
                textos_corr[0],
                textos_corr[1], 
                f"[ESC]: EXIT",   
                f"[O]: Toggle Options",
            ]
        textos = [
            textos_opciones,
            [
                f"delta_t: {self.options_vertex_model['DELTA_T']}",
                f"gamma_0: {self.options_vertex_model['GAMMA_0']}",
                f"grand_eps: {self.options_vertex_model['GRAND_EPS']}",
            ],
            [
                f"iter: {self.t} ({self.multi_iter} iter x frame)",
                #f"t: {round(self.t*self.options_vertex_model['DELTA_T'], self.n_zeros_delta_t)}",
                f"zoom: {self.zoom}x",
            ],
            [           
            ],
        ]
        for i in range(0,4):
            font_size = list_font_sizes[i]
            font = pygame.font.Font('freesansbold.ttf', font_size)
            
            c = corners[i]
            lineas = textos[i]
            len_lineas = len(lineas)
            aux = (len_lineas*font_size)*0
            for line_text in lineas:
                line = font.render(line_text, True, self.options_show_color["TEXT"], self.options_show_color["BACK_TEXT"])
                size = line.get_size()
                aux_x = c[0]*(self.options_show["RESOLUTION"]-(self.options_show["RESOLUTION"]/10)) + (1- c[0])*( size[0]/2 )
                aux_y = c[1]*(self.options_show["RESOLUTION"]-(self.options_show["RESOLUTION"]/10)) + (1- c[1])*(self.options_show["RESOLUTION"]/(font_size*2)) +aux
                lineRect = line.get_rect()
                lineRect.center = (aux_x, aux_y)
                self.screen.blit(line, lineRect)
                aux += 20
        


    def leer_granos_t(self):
        color_vertex = self.options_show_color["COLOR_VERTEX"]
        color_border = self.options_show_color["COLOR_BORDER"]
        color_vel = self.options_show_color["COLOR_VEL_VERTEX"]
        
        tam_vertice = self.options_show_tam["VERTEX"]
        tam_vel_vertice = self.options_show_tam["VERTEX_VEL"]
        tam_vel_vertice_multi = self.options_show_tam["VERTEX_VEL_MULT"]
        
                
        self.vertices = np.zeros(self.n_vertices, dtype=dt_vertex) 
        self.borders = np.zeros(self.n_borders, dtype=dt_border) 
        self.grains = np.zeros(self.n_grains, dtype=dt_grain) # (id, alpha, x1, x2, x3, ..., x50)
        # VERTICES ------------------------------
        carpeta = "vertices"
        archivo = f"{self.t}"
        id_vertex = -1
        with open(f'out/{carpeta}/{archivo}.txt', 'r') as file1:
            for line in file1:
                aux = line.split(" ")          
                if(len(aux) == 8):  
                    id = aux[0]
                    x = float(aux[1])
                    y = float(aux[2])        
                    vx = float(aux[3])
                    vy = float(aux[4])
                    self.vertices[id_vertex]["id"] = id
                    self.vertices[id_vertex]["pos_vector"][0] = x
                    self.vertices[id_vertex]["pos_vector"][1] = y
                    self.vertices[id_vertex]["vel_vector"][0] = vx
                    self.vertices[id_vertex]["vel_vector"][1] = vy
                    xi_aux = (x+ self.offsetx, y+ self.offsety)
                    xi_aux = self.adjust_offset(xi_aux)
                    xi_aux = (xi_aux[0]*self.aux_zoom, xi_aux[1]*self.aux_zoom)
                    if(self.show_vertices):
                        self.imprimir_vertice(xi_aux[0], xi_aux[1], id)
                    if(self.show_velocities):
                        self.imprimir_vel_vertice(xi_aux[0], xi_aux[1], vx*self.aux_zoom, vy*self.aux_zoom)
                id_vertex += 1

        # BORDERS --------------------------------
        if(self.show_borders):
            carpeta = "borders"
            archivo = f"{self.t}"
            id_border = 0
            id_border = -1
            with open(f'out/{carpeta}/{archivo}.txt', 'r') as file1:
                for line in file1:
                    aux = line.split(" ") 
                    if(len(aux) == 4):  
                        id = aux[0]
                        xi_index = int(aux[1])
                        xf_index = int(aux[2])
                        xi = self.vertices[xi_index]
                        xf = self.vertices[xf_index]

                        xi_aux = (xi["pos_vector"][0] + self.offsetx, xi["pos_vector"][1] + self.offsety)
                        xi_aux = self.adjust_offset(xi_aux)
                        xf_aux = (xf["pos_vector"][0] + self.offsetx, xf["pos_vector"][1] + self.offsety)
                        xf_aux = self.adjust_offset(xf_aux)
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
                            
                            self.imprimir_borde( xi_wrap2_aux, xf_wrap2_aux)          
                            #sum_x1 = x_xi+x_xf
                            #sum_y1 = y_xi+y_xf
                            #self.imprimir_id_borde( (sum_x2/2), (sum_y2/2), id) 
                        else:    
                            if(self.show_ids):
                                self.imprimir_id_borde( sum_x1, sum_y1, id)
                        self.imprimir_borde( xi_wrap_aux, xf_wrap_aux)
                        id_border+=1
            
        carpeta = "grains"
        archivo = f"{self.t}"
        cont_grain = -1
        with open(f'out/{carpeta}/{archivo}.txt', 'r') as file1:
            for line in file1:
                if(cont_grain >= 0  and len(aux)>=3):
                    aux = line.split(" ") 
                    id_grain_aux = aux[0]
                    alpha = float(aux[1])
                    v_pos = self.vertices[int(aux[2])]["pos_vector"]
                    arr_pos = [v_pos]
                    sum_x = v_pos[0]
                    sum_y = v_pos[1]
                    len_aux_2 = len(aux)-2
                    for i in range(3, len(aux)):
                        
                        v_pos = self.vertices[int(aux[i])]["pos_vector"]
                        t_wrap = wrap_distances(arr_pos[i-3], v_pos)
                        arr_pos.append( [t_wrap["xf"][0], t_wrap["xf"][1]] )
                        sum_x = sum_x+t_wrap["xf"][0]
                        sum_y = sum_y+t_wrap["xf"][1]
                    sum_x = (sum_x/(len_aux_2))+self.offsetx
                    sum_y = (sum_y/(len_aux_2))+self.offsety
                    xi_aux = (sum_x, sum_y)
                    xi_aux = self.adjust_offset( xi_aux )                        
                    xi_aux = (xi_aux[0]*self.aux_zoom, xi_aux[1]*self.aux_zoom)

                    self.imprimir_grano(xi_aux[0], xi_aux[1], id_grain_aux, alpha)
                cont_grain+=1
        
    def read_zoom_offset(self, move_x, move_y, zoom, zoom_0):
        self.zoom = self.zoom + zoom
        if(zoom_0 == 1):
            self.zoom = 1
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
        
    def next_iteration(self, list_states, plus_iters, move_x, move_y, zoom, zoom_0):
        self.show_vertices =  list_states["show_vertices"]
        self.show_velocities =  list_states["show_velocities"]
        self.show_borders =  list_states["show_borders"]
        self.show_ids =  list_states["show_ids"]
        self.show_options =  list_states["show_options"]
        self.show_alpha =  list_states["show_alpha"]
        self.multi_iter = list_states["multi_iter"]
        
        self.read_zoom_offset(move_x, move_y, zoom, zoom_0)

        if(plus_iters > 0):
            for i in range(0, plus_iters):
                if((self.t) < self.options_vertex_model["MAX_ITER"]):
                    self.t = self.t+1
                else:
                    self.t = 0
        if(plus_iters < 0):
            for i in range(0, (plus_iters*-1)):
                if(self.t > 0):
                    self.t = self.t-1
                else:
                    self.t = self.options_vertex_model["MAX_ITER"]
        self.leer_granos_t()



    def imprimir_id_borde(self, xi, yi, id):         
        xi_aux = (xi, yi)
        font = pygame.font.Font('freesansbold.ttf', self.options_show_tam["FONT_SIZE_BORDER"])
        line = font.render(id, True, self.options_show_color["BORDER_TEXT"], self.options_show_color["BORDER_BACK"])
        size = line.get_size()
        lineRect = line.get_rect()
        lineRect.center = xi_aux
        self.screen.blit(line, lineRect)
            


    def imprimir_grano(self, xi, yi, id, alpha):
        if(self.show_ids):
            xi_aux = (xi, yi)
            font = pygame.font.Font('freesansbold.ttf', self.options_show_tam["FONT_SIZE_GRAIN"])
            line = font.render(id, True, self.options_show_color["GRAIN_TEXT"], self.options_show_color["GRAIN_BACK"])
            size = line.get_size()
            lineRect = line.get_rect()
            lineRect.center = xi_aux
            self.screen.blit(line, lineRect)
        if(self.show_alpha):
            xf = xi + self.options_show_tam["ALPHA_LEN"]
            yf = yi + self.options_show_tam["ALPHA_LEN"]
            xf, yf = rotate((xi, yi), (xf, yf), alpha)
            """ tan_alpha = np.tan(alpha)
            tan_alpha = tan_alpha
            xf = xf*tan_alpha
            yf = yf*tan_alpha """
            pygame.draw.line(self.screen, self.options_show_color["ALPHA"], (xi, yi), (xf, yf), width=self.options_show_tam["ALPHA"])
            
    def imprimir_borde(self, xi, xf):
        pygame.draw.line(self.screen, self.options_show_color["COLOR_BORDER"], xi, xf, width=self.options_show_tam["BORDER"])

    def imprimir_vel_vertice(self, xi, yi, vx, vy):                
        xi_aux = (xi, yi)
        xi_aux = self.adjust_offset(xi_aux)
        xi_aux = (xi_aux[0], xi_aux[1])
        xf_aux = (xi_aux[0] + vx*self.options_show_tam["VERTEX_VEL_MULT"], xi_aux[1] + vy*self.options_show_tam["VERTEX_VEL_MULT"])
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

        pygame.draw.line(self.screen, color_aux, xi_aux, xf_aux, width=self.options_show_tam["VERTEX_VEL"])

    def imprimir_vertice(self, xi, yi, id):
        xi_aux = (xi, yi)
        pygame.draw.circle(self.screen, self.options_show_color["COLOR_VERTEX"], xi_aux, self.options_show_tam["VERTEX"])   
        
        if(self.show_ids):
            font = pygame.font.Font('freesansbold.ttf', self.options_show_tam["FONT_SIZE_VERTEX"])
            text = f'{id}'
            line = font.render(text, True, self.options_show_color["VERTEX_TEXT"], self.options_show_color["VERTEX_BACK"])        
            lineRect = line.get_rect()
            lineRect.center = xi_aux
            self.screen.blit(line, lineRect)

    