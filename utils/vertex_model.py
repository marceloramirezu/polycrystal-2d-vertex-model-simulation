import numpy as np;
from utils.geometry import *
import math
from utils.datatypes import *



class vertex_model:
    """ ==================================================================================================================================== """
    """ ==================== CONSTRUCTOR Y VARIABLES INICIALES  ==================================================================================== """
    """ ==================================================================================================================================== """
    #GAMMA_0= 0
    #mov_vertex= 0
    last_timestep_saved = 0
    N_GRAINS = 0
    N_BORDERS = 0
    N_VERTICES = 0
    N_GRAINS_0 = 0
    N_BORDERS_0 = 0
    N_VERTICES_0 = 0
    ACTUAL_TIME = 0
    ACTUAL_TIMESTEP = 0
    vertices = []
    borders = []
    grains = []
    cont_ext_borders = 0
    ext_borders = []
    actual_print_lvl = 3
    energy = 0
    total_area = 0.0
    out_folder = ""
    DELTA_T = 0

    flips_on_actual_iter = 0
    removes_on_actual_iter = 0
    # Inicializa arreglos
    # lee estado inicial dado por algoritmo voronoi
    def __init__(self, OPTIONS_VERTEX_MODEL, out_folder):
        self.out_folder = out_folder
        self.N_GRAINS = OPTIONS_VERTEX_MODEL["INITIAL_N_GRAINS"]
        self.N_BORDERS = OPTIONS_VERTEX_MODEL["INITIAL_N_GRAINS"]*3
        self.N_VERTICES = OPTIONS_VERTEX_MODEL["INITIAL_N_GRAINS"]*2
        self.N_GRAINS_0 = self.N_GRAINS
        self.N_BORDERS_0 = self.N_BORDERS
        self.N_VERTICES_0 = self.N_VERTICES
        self.DELTA_T = OPTIONS_VERTEX_MODEL["DELTA_T"]
        self.GAMMA_0 = OPTIONS_VERTEX_MODEL["GAMMA_0"]
        self.MAX_TIMESTEP = OPTIONS_VERTEX_MODEL["MAX_TIMESTEP"]
        #self.mov_vertex = OPTIONS_VERTEX_MODEL["MOV_VERTEX"]
        #self.grad_eps = OPTIONS_VERTEX_MODEL["GRAND_EPS"]
        
        self.flips_on_actual_iter = 0
        self.removes_on_actual_iter = 0
        
        self.total_area = 0.0
        self.energy = 0

        self.vertices = np.zeros(self.N_VERTICES, dtype=dt_vertex)         
        self.borders = np.zeros(self.N_BORDERS, dtype=dt_border)         
        self.grains = np.zeros(self.N_GRAINS, dtype=dt_grain) 
        
        self.general = np.zeros(self.MAX_TIMESTEP+1, dtype=dt_general)
        self.ACTUAL_TIME = 0
        self.ACTUAL_TIMESTEP = 0

    
    """ ==================================================================================================================================== """
    """ ==================== CALCULOS EN ESTRUCTURA  ==================================================================================== """
    """ ==================================================================================================================================== """
    
    # setea bordes del vertice en sentido horario
    def vertex_set_boundaries_anticlockwise(self, vertex) :
        angles=[]
        id = vertex["id"]
        for i in range(0,3):
            delta_x = 0
            delta_y = 0
            t_wrap = {}
            if(self.borders[vertex["borders"][i]]["vertices"][0] == vertex["id"]):
                t_wrap = wrap_distances( self.vertices[self.borders[vertex["borders"][i]]["vertices"][1]]["pos_vector"] , vertex["pos_vector"])
            else:
                t_wrap = wrap_distances( self.vertices[self.borders[vertex["borders"][i]]["vertices"][0]]["pos_vector"] , vertex["pos_vector"])
            delta_x = t_wrap["delta_x"]
            delta_y = t_wrap["delta_y"]
            angles.append(math.atan2(delta_x, delta_y)) # angulo = arc_tan(y/x)
        
        for i in range(0, 2):
            for p in range(1, (3-i)):
                if(angles[p-1] < angles[p]):
                    aux = angles[p-1]
                    angles[p-1] = angles[p]
                    angles[p] = aux
                    auxb = vertex["borders"][p-1]
                    vertex["borders"][p-1] = vertex["borders"][p]
                    vertex["borders"][p] = auxb

    # t = t+DELTA_T, iter += 1
    def next_iteration(self):
        self.ACTUAL_TIMESTEP = self.ACTUAL_TIMESTEP+1
        self.ACTUAL_TIME = self.ACTUAL_TIME+self.DELTA_T

    # calcula largos de arco y energias de los vertices (FALTA ARREGLAR CALCULO DE GAMMA)
    def calculate_arclen_and_energy_all_borders(self):      
        with np.nditer(self.borders, op_flags=['readwrite']) as it:
            energy_aux = 0
            for border in it:
                if ( not border["not_enabled"]):
                    self.calculate_len_and_energy_border(border)
                    energy_aux += border["arc_len"]*border["gamma"]
            self.energy = energy_aux

    def calculate_len_and_energy_border(self, border):
        xi_index = border["vertices"][0]
        xf_index = border["vertices"][1]
        xi = self.vertices[xi_index]
        xf = self.vertices[xf_index]

        # calculo de vectores tangentes
        t_wrap = wrap_distances( xi["pos_vector"],  xf["pos_vector"] ) # calculate_arc_len
        border["arc_len"] = t_wrap["arc_len"]
        border["tangent_vector"][0] = t_wrap["x_u"]
        border["tangent_vector"][1] = t_wrap["y_u"]
        # calcular energia del borde con la orientacion de los dos granos asociados y gamma_o
        border["gamma"] = self.GAMMA_0 #*math.cos(0)
        
    # calcula velocidades de los vertices
    def calculate_vel_vertices(self):
        model = 1

        if(model == 1):
            with np.nditer(self.vertices, op_flags=['readwrite']) as it:
                for vertex in it:
                    if(not vertex["not_enabled"] ):
                        new_vel = self.calculate_vel_vertex(vertex["id"])
                        vertex["vel_vector"][0] = new_vel[0]
                        vertex["vel_vector"][1] = new_vel[1]    

        if(model == 2): # runge-kutta 2
            # copia de estructura actual para realizar calculos de velocidad en t + DELTA_T/2
            vertices_aux = self.vertices.copy()         
            borders_aux = self.borders.copy()    
            grains_aux = self.grains.copy()

            # calcular velocidad en i
            with np.nditer(self.vertices, op_flags=['readwrite']) as it:
                for vertex in it:
                    if(not vertex["not_enabled"] ):
                        new_vel = self.calculate_vel_vertex(vertex["id"])
                        vertex["vel_vector"][0] = new_vel[0]
                        vertex["vel_vector"][1] = new_vel[1] 

            # calcular posicion en i+1/2
            self.update_position_vertices()   
            # recalcular largos de bordes para poder calcular la velocidad en i+1/2 
            self.calculate_arclen_and_energy_all_borders()   
            
            # 4.- calcular tiempos de extincion para cada borde
            self.calculate_t_ext(self.DELTA_T/2)          
            
            # calcualr velocidad en i+1/2
            with np.nditer(self.vertices, op_flags=['readwrite']) as it:
                for vertex in it:
                    if(not vertex["not_enabled"] and not vertex["ext_border"]):
                        new_vel = self.calculate_vel_vertex(vertex["id"])
                        vertex["vel_vector"][0] = new_vel[0]
                        vertex["vel_vector"][1] = new_vel[1] 
                        
                        id = vertex["id"]
                        vertices_aux[id]["vel_vector"][0] = new_vel[0] # asignacion de velocidades a estructura en i
                        vertices_aux[id]["vel_vector"][1] = new_vel[1] # asignacion de velocidades a estructura en i

            # volver estructura a i, con velocidades calculadas
            self.vertices = vertices_aux.copy()   
            self.borders = borders_aux.copy()    
            self.grains = grains_aux.copy()
            
             

    # calcula velocidad de un solo vertice
    def calculate_vel_vertex(self, vertex_id):
        vel = [0.0, 0.0]
        vertex = self.vertices[vertex_id]
        for i in range(0, 3): # por cada borde del vertice
            borde = self.borders[ vertex["borders"][i] ]
            id_vertex_i = borde["vertices"][0]
            if(id_vertex_i == vertex["id"]): # si el vertice es el vertice inicial del borde se usa el vector tangente positivo
                vel[0] = vel[0] + borde["gamma"]*borde["tangent_vector"][0]
                vel[1] = vel[1] + borde["gamma"]*borde["tangent_vector"][1]
            else: # si el vertice es el vertice final del borde se usa el vector tangente negativo
                vel[0] = vel[0] - borde["gamma"]*borde["tangent_vector"][0]
                vel[1] = vel[1] - borde["gamma"]*borde["tangent_vector"][1]       
        vel[0] = vel[0] # *self.mov_vertex
        vel[1] = vel[1] # *self.mov_vertex 
        return vel
        
    def update_position_vertices_ext_borders(self):
        if(self.cont_ext_borders > 0):
            # avanza cada borde que se extingue en la iteracion actual antes de avanzar al estructura completa
            for c in range(0, self.cont_ext_borders):           
                # avanza localmente los vertices asociados a los bordes que se extinguen hasta ACTUAL_TIME + t_ext
                # realiza transicion topologica localmente
                self.advance_ext_border(c)  

    
    # no usado
    # llamar luego de actualizar la posicion de los vertices
    def final_update_position_vertices_ext_borders(self):
        # se ocupa de avanzar los vertices asociados a bordes que se extinguen luego de haber avanzado t_ext hasta t+DELTA_T
        for i in range(0, self.cont_ext_borders):    
            break # REVISAR (necesario?, falta revisar la posicion final del vertice en T2 y falta revisar la posicion y angulo de los vertices luego de T1)
            id_b = self.ext_borders[i]["id"]
            t_ext_b = self.ext_borders[i]["t_ext"]
            diff_t_ext_b = self.ext_borders[i]["diff_t_ext"]
            for i in range(0, 2):
                vertex = self.vertices[self.borders[id_b]["vertices"][i]]
                if(not vertex["not_enabled"]):
                    velx = vertex["vel_vector"][0]
                    vely = vertex["vel_vector"][1]
                    if(not vertex["not_enabled"]):
                        vertex["pos_vector"][0] = vertex["pos_vector"][0] + (diff_t_ext_b)    
                        vertex["pos_vector"][1] = vertex["pos_vector"][1] + (diff_t_ext_b)  

                    if vertex["pos_vector"][0] >= 1:
                        vertex["pos_vector"][0] = vertex["pos_vector"][0]-1
                    elif vertex["pos_vector"][0] < 0:
                        vertex["pos_vector"][0] = vertex["pos_vector"][0]+1
                    if vertex["pos_vector"][1] >= 1:
                        vertex["pos_vector"][1] = vertex["pos_vector"][1]-1
                    elif vertex["pos_vector"][1] < 0:
                        vertex["pos_vector"][1] = vertex["pos_vector"][1]+1

    # avanza los vertices a su nueva posicion
    def update_position_vertices(self):  
        # avanza a t+DELTA_T toda la estructura menos los vertices asociados a bordes que se extinguieron dentro de la iteracion actual
        if(False):  # prueba vectores: falta filtrar solo vertices activos y no asociados a bordes que se extinguen
            self.vertices["pos_vector"] = self.vertices["pos_vector"] + (self.vertices["vel_vector"]*self.DELTA_T)
        else:      # prueba inicial
            with np.nditer(self.vertices, op_flags=['readwrite']) as it:
                for vertex in it:
                    if(not vertex["not_enabled"] and not vertex["ext_border"]):
                        velx = vertex["vel_vector"][0]
                        vely = vertex["vel_vector"][1]
                        vertex["pos_vector"][0] = vertex["pos_vector"][0] + (velx*self.DELTA_T)    
                        vertex["pos_vector"][1] = vertex["pos_vector"][1] + (vely*self.DELTA_T)  
                        if vertex["pos_vector"][0] >= 1:
                            vertex["pos_vector"][0] = vertex["pos_vector"][0]-1
                        elif vertex["pos_vector"][0] < 0:
                            vertex["pos_vector"][0] = vertex["pos_vector"][0]+1
                        if vertex["pos_vector"][1] >= 1:
                            vertex["pos_vector"][1] = vertex["pos_vector"][1]-1
                        elif vertex["pos_vector"][1] < 0:
                            vertex["pos_vector"][1] = vertex["pos_vector"][1]+1
        
            

    # inicia arreglo con bordes que se extinguen en la iteracion actual.
    def iniciar_ext_borders(self):
        self.ext_borders = np.zeros(self.N_BORDERS_0, dtype=dt_ext_border)
        for i in range(0, self.N_VERTICES_0):
            if(not self.vertices[i]["not_enabled"]):
                self.vertices[i]["ext_border"] = False
                

    # ordena arreglo de bordes que se extinguen en la iteracion actual.
    def ordenar_ext_borders(self):
        Tcopy=self.ext_borders[['id','t_ext', 'diff_t_ext']].copy()
        I=np.argsort(Tcopy,order=['t_ext'])
        self.ext_borders = self.ext_borders[I]


    # calcula el area de todos los granos
    def calculate_grains_areas(self):
        area_total = 0
        cont_n = 0
        cont_p = 0

        for g in range(0, self.N_GRAINS_0):
            if(not self.grains[g]["not_enabled"]):
                area = self.calculate_grain_area(g) 
                if(area < 0):
                    cont_n += 1
                else:              
                    cont_p += 1     
                if(area < 0):
                    area = -1*area
                area_total += area          

        self.total_area = area_total

    # calcula area de un grano con teorema de green
    def calculate_grain_area(self, grano_id):
        grano = self.grains[grano_id]
        vertices_grano = grano["vertices"]
        area = 0.0
        n_vertices_grano = grano["n_vertices"]
        vertices = [] #eliminar
        x_list_v_i = []
        y_list_v_i = []
        for i in range(0, 50):
            v_grain_i = vertices_grano[i]
            if(v_grain_i != -1):
                v_i = self.vertices[v_grain_i]
                vertices.append(v_i["id"])
                x_list_v_i.append(v_i["pos_vector"][0])
                y_list_v_i.append(v_i["pos_vector"][1])
            else:
                break
        

        for v in range(0, len(x_list_v_i)):
            a = x_list_v_i[v]
            x_list_v_i[v] = a
            b= y_list_v_i[v]
            y_list_v_i[v] = b

        for v in range(0, (len(x_list_v_i))):
            v_p1 = v+1
            if(v == len(x_list_v_i)-1):
                v_p1 = 0

            x_i = x_list_v_i[v]
            x_i_p1 = x_list_v_i[v_p1]
            y_i = y_list_v_i[v]
            y_i_p1 = y_list_v_i[v_p1]
            if(abs(x_i-x_i_p1) > 0.5):
                if(x_i < x_i_p1):
                    x_i_p1 = x_i_p1-1
                    x_list_v_i[v_p1] = x_i_p1
                else:
                    x_i_p1 = x_i_p1+1
                    x_list_v_i[v_p1] = x_i_p1
            if(abs(y_i-y_i_p1) > 0.5):
                if(y_i < y_i_p1):
                    y_i_p1 = y_i_p1-1
                    y_list_v_i[v_p1] = y_i_p1
                else:
                    y_i_p1 = y_i_p1+1
                    y_list_v_i[v_p1] = y_i_p1
            
            area += (x_i*y_i_p1)-(x_i_p1*y_i)

        area = area/2
        self.grains[grano_id]["area"] = area

        return area


    def count_number_of_components(self):
        cont_grains = 0
        for i in range(0, self.N_GRAINS_0):
            if(not self.grains[i]["not_enabled"]):
                cont_grains +=1
        
        cont_vertices = 0
        for i in range(0, self.N_VERTICES_0):
            if(not self.vertices[i]["not_enabled"]):
                cont_vertices +=1
        
        cont_borders = 0
        for i in range(0, self.N_BORDERS_0):
            if(not self.borders[i]["not_enabled"]):
                cont_borders +=1
        
        self.N_GRAINS = cont_grains
        self.N_VERTICES = cont_vertices
        self.N_BORDERS = cont_borders
    """ ==================================================================================================================================== """
    """ ================== TRANSICIONES TOPOLOGICAS ========================================================================================="""
    """ ==================================================================================================================================== """

    
    """ ================== TRANSICION FLIP BORDER ========================================================================================== """

    def flip_border(self, vertice_1, vertice_2, flip_border):
        vertex_1 = self.vertices[vertice_1]
        p1 = vertex_1["pos_vector"]
        vertex_2 = self.vertices[vertice_2]
        p2 = vertex_2["pos_vector"]
        # 1.- rotacion de borde  ----------------------------------------------------------------------------------------------------------------

        segment_rotated = rotate_segment(p1, p2, 90)
        self.vertices[vertice_1]["pos_vector"] = segment_rotated[0]
        self.vertices[vertice_2]["pos_vector"] = segment_rotated[1]

        # 2.- BORDES
        # 2.1.- seteo de bordes dentro de vertices ----------------------------------------------------------------------------------------------------------------
        
        v1_borders = self.vertices[vertice_1]["borders"]
        v1_index_border_flip = 0
        for i in range(0, 3):
            if v1_borders[i] == flip_border:
                v1_index_border_flip = i
        v2_borders = self.vertices[vertice_2]["borders"]
        v2_index_border_flip = 0
        for i in range(0,3):
            if v2_borders[i] == flip_border:
                v2_index_border_flip = i

        v1_index_post_b = (v1_index_border_flip+1)%3
        v1_index_prev_b = (v1_index_border_flip-1)%3
        v1_post_b = self.vertices[vertice_1]["borders"][v1_index_post_b]
        v1_prev_b = self.vertices[vertice_1]["borders"][v1_index_prev_b]
        
        v2_index_post_b = (v2_index_border_flip+1)%3
        v2_index_prev_b = (v2_index_border_flip-1)%3
        v2_post_b = self.vertices[vertice_2]["borders"][v2_index_post_b]
        v2_prev_b = self.vertices[vertice_2]["borders"][v2_index_prev_b]

        self.vertices[vertice_1]["borders"][0] = v1_prev_b
        self.vertices[vertice_1]["borders"][1] = v2_post_b
        self.vertices[vertice_1]["borders"][2] = flip_border
        self.vertices[vertice_2]["borders"][0] = v2_prev_b
        self.vertices[vertice_2]["borders"][1] = v1_post_b
        self.vertices[vertice_2]["borders"][2] = flip_border
        
        # 2.2.- seteo de vertices dentro de bordes ----------------------------------------------------------------------------------------------------------------

        # v1_post_b se debe cambiar el vertice_1 por el vertice_2
        # v2_post_b se debe cambiar el vertice_2 por el vertice_1
        if (self.borders[v1_post_b]["vertices"][0] == vertice_1):
            self.borders[v1_post_b]["vertices"][0] = vertice_2
        else:
            self.borders[v1_post_b]["vertices"][1] = vertice_2

        if (self.borders[v2_post_b]["vertices"][0] == vertice_2):
            self.borders[v2_post_b]["vertices"][0] = vertice_1
        else:
            self.borders[v2_post_b]["vertices"][1] = vertice_1
            
        # 3.- GRANOS: ----------------------------------------------------------------------------------------------------------------------
        v1_grains = self.vertices[vertice_1]["grains"]
        v2_grains = self.vertices[vertice_2]["grains"]
        grains_involve = []
        # select distinct grains

        text_grains_involve = ""
        for grain in v1_grains:
            if grain not in grains_involve:
                grains_involve.append(grain)
                text_grains_involve = f"{text_grains_involve}, {grain}"
        for grain in v2_grains:
            if grain not in grains_involve:
                grains_involve.append(grain)
                text_grains_involve = f"{text_grains_involve}, {grain}"
                        
        # 3.1.- vertices en granos -----------------------------------------------------------
        # select grains with the two vertices of the border that flip
        pos_v1_in_two_vertices_grain = [] # pos in grain 1, pos in grain 2
        pos_v2_in_two_vertices_grain = [] # pos in grain 1, pos in grain 2
        two_vertices_grain = []
        v1_grain = 0
        v1_pos_in_v1_grain = 0
        v2_grain = 0
        v2_pos_in_v2_grain = 0
        for grain in grains_involve:
            pos = 0
            pos_v1 = 0
            pos_v2 = 0
            encontrado_v1 = False
            encontrado_v2 = False
            vertices_of_grain = self.grains[grain]["vertices"]
            for v in vertices_of_grain:
                if v == vertice_1:
                    pos_v1 = pos
                    encontrado_v1 = True
                if v == vertice_2:
                    pos_v2 = pos
                    encontrado_v2 = True
                pos += 1
            if (encontrado_v1 and encontrado_v2):
                two_vertices_grain.append(grain)
                pos_v1_in_two_vertices_grain.append(pos_v1) # POS DEL VERTICE 1 EN EL PRIMER GRANO CON LOS DOS VERTICES
                pos_v2_in_two_vertices_grain.append(pos_v2) # POS DEL VERTICE 2 EN EL PRIMER GRANO CON LOS DOS VERTICES
            elif(encontrado_v1):
                v1_pos_in_v1_grain = pos_v1
                v1_grain = grain
            elif(encontrado_v2):
                v2_pos_in_v2_grain = pos_v2
                v2_grain = grain
            else:
                pass

        # LOS GRANOS QUE CONTIENEN LOS DOS VERTICES INVOLUCRADOS, SIEMPRE DEJAN AL ULTIMO VERTICE QUE LES PERTENECE, EN SENTIDO HORARIO
        mantiene_solo_v1_tvg = 0 # TWO VERTICES GRAINS (GRANO CON LOS DOS VERTICES INVOLUCRADOS)
        mantiene_solo_v2_tvg = 0
        if( abs(pos_v1_in_two_vertices_grain[0] - pos_v2_in_two_vertices_grain[0]) == 1 ): # continuos dentro del grano -> el mayor es el ultimo
            if( pos_v1_in_two_vertices_grain[0] > pos_v2_in_two_vertices_grain[0] ): # en grano 1, el vertice 1 es mayor al vertice 2 (v1 ultimo), por lo que se mantiene en el grano el vertice 1 y se elimina el vertice 2
                mantiene_solo_v1_tvg = two_vertices_grain[0]
                mantiene_solo_v2_tvg = two_vertices_grain[1]
            else: # en grano 1 pos_v1, pos_v2
                mantiene_solo_v1_tvg = two_vertices_grain[1]
                mantiene_solo_v2_tvg = two_vertices_grain[0]
        else: # discontinuos -> el menor es el ultimo
            if( pos_v1_in_two_vertices_grain[0] > pos_v2_in_two_vertices_grain[0] ): # en grano 1 pos_v2, pos_v1
                mantiene_solo_v1_tvg = two_vertices_grain[1]
                mantiene_solo_v2_tvg = two_vertices_grain[0]
            else: # en grano 1 pos_v1, pos_v2
                mantiene_solo_v1_tvg = two_vertices_grain[0]
                mantiene_solo_v2_tvg = two_vertices_grain[1]

        self.delete_vertices_on_grain(mantiene_solo_v1_tvg, [vertice_2], vertice_1)
        self.delete_vertices_on_grain(mantiene_solo_v2_tvg, [vertice_1], vertice_2)

        # el vertice 1 se agrega luego del vertice 2 en el grano que solo contiene el vertice 2
        self.add_vertex_on_grain(v2_grain, vertice_1, v2_pos_in_v2_grain+1)
        # el vertice 2 se agrega luego del vertice 1 en el grano que solo contiene el vertice 1
        self.add_vertex_on_grain(v1_grain, vertice_2, v1_pos_in_v1_grain+1)

        # 3.2.- granos en vertices -----------------------------------------------------------
       
        self.vertices[vertice_1]["grains"][0] = v1_grain
        self.vertices[vertice_1]["grains"][1] = mantiene_solo_v1_tvg
        self.vertices[vertice_1]["grains"][2] = v2_grain
        
        self.vertices[vertice_2]["grains"][0] = v2_grain
        self.vertices[vertice_2]["grains"][1] = mantiene_solo_v2_tvg
        self.vertices[vertice_2]["grains"][2] = v1_grain 
        

        
    def add_vertex_on_grain(self, grain, add_vertex, pos):
        n_vertices = self.grains[grain]["n_vertices"]
        vertices = self.grains[grain]["vertices"]
        post_vertices = list(vertices[pos:n_vertices])
        self.grains[grain]["vertices"][pos] = add_vertex
        cont = 0
        for post_v in post_vertices:
            cont +=1
            if(pos + cont < n_vertices+1): 
                self.grains[grain]["vertices"][pos+cont] = post_v
            else:
                break
        self.grains[grain]["n_vertices"] = n_vertices+1
    
    """ ================== TRANSICION DELETE 3-SIDED GRAIN ================================================================================= """
    # Transicion Topologica borrar grano
    def delete_grain(self, id_grain):
        grain = self.grains[id_grain]
        if (self.grains[id_grain]["not_enabled"]):
            return 0
        self.grains[id_grain]["not_enabled"] = True
        
        n_vertices = grain["n_vertices"]
        vertices = grain["vertices"][0:n_vertices]
        
        initial_vertex = self.vertices[vertices[0]]
        id_initial_vertex = initial_vertex["id"]
        arr_pos_initial_vertex = [initial_vertex["pos_vector"][0], initial_vertex["pos_vector"][1]]
        arr_pos = [ arr_pos_initial_vertex ]
        sum_x = initial_vertex["pos_vector"][0]
        sum_y = initial_vertex["pos_vector"][1]
        cont_vertices = 1
        borders_delete_aux = []
        granos_resultantes = []
        arr_del_vertices = []
        arr_vertices_usados = [ id_initial_vertex ]

        # guarda bordes del primer vertice del grano, para luego eliminar los repetidos (entre los vertices del grano)
        for g in range(0, 3):
            # granos del primer vertice
            grain = initial_vertex["grains"][g]
            if(grain != id_grain and grain not in granos_resultantes):
                granos_resultantes.append(grain)
            # bordes del primer vertice
            border_id = initial_vertex["borders"][g]
            border = self.borders[border_id]
            # deshabilita bordes que contienen 2 vertices dentro de los vertices del grano
            if (border["vertices"][0] in vertices and border["vertices"][1] in vertices):
                self.borders[border_id]["not_enabled"] = True
            else:
                # guarda bordes eliminados
                borders_delete_aux.append(border_id)

        # por cada vertice del grano, empezando por el segudno
        for j in range(1, n_vertices):                       
            cont_vertices+=1             
            
            # desactiva vertices 
            self.vertices[vertices[j]]["not_enabled"] = True
            arr_vertices_usados.append(self.vertices[vertices[j]]["id"])
            arr_del_vertices.append(self.vertices[vertices[j]]["id"])

            # guarda bordes afectados, para luego eliminar los repetidos (entre los vertices del grano)
            for g in range(0, 3):
                # granos del vertice j
                grain = self.vertices[vertices[j]]["grains"][g]
                if(grain != id_grain and grain not in granos_resultantes):
                    granos_resultantes.append(grain)
                # bordes del vertice j
                border_id = self.vertices[vertices[j]]["borders"][g]
                border = self.borders[border_id]
                # deshabilita bordes que contienen 2 vertices dentro de los vertices del grano
                if (border["vertices"][0] in vertices and border["vertices"][1] in vertices):
                    self.borders[border_id]["not_enabled"] = True
                else:
                    # guarda bordes eliminados
                    borders_delete_aux.append(border_id)

            # suma posiciones para obtener promedio
            v_pos = self.vertices[vertices[j]]["pos_vector"]
            t_wrap = wrap_distances(arr_pos[j-1], v_pos)
            arr_pos.append( t_wrap["xf"] )
            sum_x = sum_x+t_wrap["xf"][0]
            sum_y = sum_y+t_wrap["xf"][1]


        # Cambia granos asociados a los vertices
        for i in range(0, 3):
            # busca ubicacion del grano dentro del vertice
            if(self.vertices[id_initial_vertex]["grains"][i] == id_grain): 
                for j in range(0, 3):
                    # busca grano que falta de los granos resultantes dentro del vertice resultante
                    if (granos_resultantes[j] not in self.vertices[id_initial_vertex]["grains"]): 
                        self.vertices[id_initial_vertex]["grains"][i] = granos_resultantes[j] # ERROR FALTA: NO SE GUARDAN BIEN LOS GRANOS RESULTANTE Y LUEGO SE INTENTAN ELIMINAR 

        # setea vertices asociados a los granos resultantes
        for g in granos_resultantes:
            if(g != id_grain):
                self.delete_vertices_on_grain(g, arr_del_vertices, id_initial_vertex)

        # setea vertices asociados a los bordes
        for b in range(0, 3):
            self.vertices[id_initial_vertex]["borders"][b] = borders_delete_aux[b]
            border = self.borders[borders_delete_aux[b]]
            # si no esta habilidado
            for i in range(0, 2): # vertices del borde
                if( self.vertices[border["vertices"][i]]["not_enabled"] ): 
                    self.borders[borders_delete_aux[b]]["vertices"][i] = id_initial_vertex
            
        # Cambia ubicacion de vertice resultante
        prom_x = (sum_x/(cont_vertices))
        prom_y = (sum_y/(cont_vertices))
        self.vertices[id_initial_vertex]["pos_vector"][0] = prom_x
        self.vertices[id_initial_vertex]["pos_vector"][1] = prom_y

        # calcula arcos de bordes resultantes
        for i in range(0, 3):
            borde = self.borders[self.vertices[id_initial_vertex]["borders"][i]]
            self.calculate_len_and_energy_border(borde)
        # calcula nueva velocidad del vertice resultante
        new_vel = self.calculate_vel_vertex(id_initial_vertex)
        self.vertices[id_initial_vertex]["vel_vector"][0] = new_vel[0]
        self.vertices[id_initial_vertex]["vel_vector"][1] = new_vel[1]    
        for i in range(0, 3):
            borde = self.borders[self.vertices[id_initial_vertex]["borders"][i]]
            if( borde["vertices"][0] != self.vertices[id_initial_vertex]["id"]):
                vertice = self.vertices[borde["vertices"][0]]
            else:
                vertice = self.vertices[borde["vertices"][1]]
            
            new_vel = self.calculate_vel_vertex(vertice["id"])
            self.vertices[vertice["id"]]["vel_vector"][0] = new_vel[0]
            self.vertices[vertice["id"]]["vel_vector"][1] = new_vel[1]  
            
    # elimina vertices del grano indicado 
    # id_grain: grano por cambiar
    # del_vertices: vertices por eliminar
    def delete_vertices_on_grain(self, id_grain, del_vertices, vertice_resultante):
        n_vertices = self.grains[id_grain]["n_vertices"]
        vertices = self.grains[id_grain]["vertices"]
        replace_vertex = False
        replaced = False
        if vertice_resultante not in vertices:
            replace_vertex = True

        # por cada vertice a eliminar
        cont_deleted = 0
        for v_del in del_vertices:
            # por cada vertice en el grano
            for i in range(0, (n_vertices-cont_deleted)):
                v = vertices[i]
                # si el vertice se elimina
                if v == v_del:
                    if replace_vertex and cont_deleted == 0 and not replaced: 
                        self.grains[id_grain]["vertices"][i] = vertice_resultante
                        replaced = True
                    else:
                        if (i < n_vertices-1):
                            for j in range(i, n_vertices-1):
                                self.swap_vertices_on_grain(id_grain, j, j+1)
                        self.grains[id_grain]["vertices"][n_vertices-1] = -1
                        self.grains[id_grain]["n_vertices"] = self.grains[id_grain]["n_vertices"]-1                    
                        cont_deleted += 1
                    break

    # utilizado para eliminar vertices de un grano, 
    # dejando el grano por eliminar al como el ultimo vertice distinto a -1, del grano dentro del arreglo del vertices
    def swap_vertices_on_grain(self, id_grain, pos_v1, pos_v2):
        x1 = self.grains[id_grain]["vertices"][pos_v1]
        x2 = self.grains[id_grain]["vertices"][pos_v2]
        self.grains[id_grain]["vertices"][pos_v1] = x2
        self.grains[id_grain]["vertices"][pos_v2] = x1

    # avanzar borde que se extingue en la iteracion actual
    def advance_ext_border(self, id_ext_border):
        b = self.ext_borders[(id_ext_border+1)*-1]
        id_borde = b["id"]
        t_ext = b["t_ext"]
        diff_t_ext = b["diff_t_ext"]
        self.ext_borders[(id_ext_border+1)*-1]["diff_t_ext"] = diff_t_ext - t_ext
        vertices = self.borders[id_borde]["vertices"]

        # eliminar granos de 3 lados
        del_grain = False
        deleted_grains = []
        for v in range(0, 2):
            vertex = self.vertices[vertices[v]]
            for g in range(0, 3):
                grain = self.grains[vertex["grains"][g]]
                if (grain["n_vertices"] == 3 and grain["id"] not in deleted_grains):
                    deleted_grains.append(grain["id"])
                    self.delete_grain(grain["id"])
                    del_grain = True
        # flips
        # se avanzan los vertices asociados a los flips hasta (ACTUAL_TIME + t_ext)
        if not del_grain:  
            
            p1_index = self.borders[id_borde]["vertices"][0]
            p2_index = self.borders[id_borde]["vertices"][1]     
            self.flip_border(p1_index, p2_index, id_borde)    
        
    def test_structure(self):
        l_errors = []
        # GRANOS
        # granos = 3 bordes = 2 vertices
        for g in range(0, self.N_GRAINS_0):
            grain = self.grains[g]
            if(not grain["not_enabled"]):
                # revisar que sus n vertices esten activos
                n_vertices = grain["n_vertices"]
                cont_vertices_enabled = 0     
                for v in range(0, 50):
                    vi = grain["vertices"][v]
                    vertex_i = self.vertices[vi]
                    if(vertex_i["not_enabled"]):
                        if(v < n_vertices):
                            desc = f"grain: {g}, contiene vertice ({vi}) no habilitado"
                            print(f"ERROR: {desc}")
                            error = [self.ACTUAL_TIMESTEP, "grain", b, desc]
                            l_errors.append(error)
                    else:
                        cont_vertices_enabled+=1

                if(cont_vertices_enabled != n_vertices):
                    desc = f"grain: {g}, contiene vertice ({cont_vertices_enabled}) habilitados pero se esperaban {n_vertices}"
                    print(f"ERROR: {desc}")
                    error = [self.ACTUAL_TIMESTEP, "grain", b, desc]
                    l_errors.append(error)


                # revisar que sus vertices esten en sentido horario
                pass

        # VERTICES
        # vertice = 3 bordes habilitados = 3 granos habilitados
        for v in range(0, self.N_VERTICES_0):
            vertex = self.vertices[v]
            if(not vertex["not_enabled"]):
                # revisar que sus granos esten activos
                for g in range(0, 3):
                    gi = vertex["grains"][g]
                    grain = self.grains[gi]
                    if(grain["not_enabled"] ):
                        desc = f"vertice: {v}, contiene grano ({gi}) no habilitado"
                        print(f"ERROR: {desc}")
                        error = [self.ACTUAL_TIMESTEP, "vertex", v, desc]
                        l_errors.append(error)
                # revisar que sus bordes esten activos
                for b in range(0, 3):
                    bi = vertex["borders"][g]
                    border_i = self.borders[bi]
                    if(border_i["not_enabled"] ):
                        desc = f"vertice: {v}, contiene borde ({bi}) no habilitado"
                        print(f"ERROR: {desc}")
                        error = [self.ACTUAL_TIMESTEP, "vertex", v, desc]
                        l_errors.append(error)
                    
        # BORDES        
        # borde = 2 vertices habilitados = 2 granos habilitados
        for b in range(0, self.N_BORDERS_0):
            border = self.borders[b]
            if(not border["not_enabled"]):
                # vertices habilitados                
                for v in range(0, 2):
                    vi = border["vertices"][v]
                    vertex_i = self.vertices[vi]
                    if(vertex_i["not_enabled"]):
                        desc = f"borde: {b}, contiene vertice ({vi}) no habilitado"
                        print(f"ERROR: {desc}")
                        error = [self.ACTUAL_TIMESTEP, "border", b, desc]
                        l_errors.append(error)

        return l_errors

    def calculate_grain_position(self):
        for i in range(0, self.N_GRAINS_0):
            grain = self.grains[i]
            if(not grain["not_enabled"]):
                vi_index = grain["vertices"][0]
                vi = self.vertices[vi_index]
                xi = vi["pos_vector"][0]
                yi = vi["pos_vector"][1]
                sum_x = xi
                sum_y = yi
                x_wrap = False
                y_wrap = False
                arr_vertices = [vi_index]
                arr_pos = [ [xi, yi] ]
                for j in range(1, grain["n_vertices"]):
                    vi_index = grain["vertices"][j]
                    v = self.vertices[vi_index]

                    x = v["pos_vector"][0]
                    y = v["pos_vector"][1]
                    x_prev = arr_pos[j-1][0]
                    y_prev = arr_pos[j-1][1]

                    diff_x = np.absolute(x - x_prev)
                    diff_y = np.absolute(y - y_prev)

                    x_dist_wrap = diff_x > 0.5
                    y_dist_wrap = diff_y > 0.5
                    
                    if(x_dist_wrap and x_prev <= 0.5):                        
                        x = x - 1
                        x_wrap = True
                    elif(x_dist_wrap and x_prev > 0.5):                        
                        x = x + 1
                        x_wrap = True
                    else:
                        pass

                    if(y_dist_wrap and y_prev <= 0.5):                        
                        y = y - 1
                        y_wrap = True
                    elif(y_dist_wrap and y_prev > 0.5):                        
                        y = y + 1
                        y_wrap = True
                    else:
                        pass
                    arr_pos.append( [x, y] )
                    sum_x += x
                    sum_y += y

                    
                self.grains[i]["pos_vector"][0] = sum_x/grain["n_vertices"]
                self.grains[i]["pos_vector"][1] = sum_y/grain["n_vertices"]
                self.grains[i]["x_wrap"] = x_wrap
                self.grains[i]["y_wrap"] = y_wrap
                
    # REVISAR =================================================
    # calcula tiempo de extincion de los bordes
    def calculate_t_ext(self, delta_t_used):
        self.iniciar_ext_borders()
        cont_ext_borders = 0
        for i in range(0, self.N_BORDERS_0):
            if (not self.borders[i]["not_enabled"]):
                border_xi_index = self.borders[i]["vertices"][0]
                border_xf_index = self.borders[i]["vertices"][1]

                vel_xi = self.vertices[border_xi_index]["vel_vector"]
                vel_xf = self.vertices[border_xf_index]["vel_vector"]
                delta_x_vel = vel_xf[0] - vel_xi[0]
                delta_y_vel = vel_xf[1] - vel_xi[1]

                norm = self.borders[i]["arc_len"]
                Tx = self.borders[i]["tangent_vector"][0]
                Ty = self.borders[i]["tangent_vector"][1]
                
                DotProd_x = Tx * delta_x_vel
                DotProd_y = Ty * delta_y_vel
                DotProd = DotProd_x + DotProd_y
                if(DotProd == 0):
                    self.borders[i]["t_ext"] = 100
                    self.borders[i]["ext"] = 0
                else:
                    aux = -norm/(DotProd) # t_ext =aprox=> -arc_len(t)/arc_len'(t)
                    
                    self.borders[i]["t_ext"] = aux
                    self.borders[i]["ext"] = 0                                                                                                                                                                                                 
                    if( aux >= 0 and aux <= (delta_t_used) ):
                        self.set_ext_border(i, [border_xi_index, border_xf_index])
                        self.ext_borders[cont_ext_borders]["id"] = self.borders[i]["id"]
                        self.ext_borders[cont_ext_borders]["t_ext"] = self.borders[i]["t_ext"]
                        self.ext_borders[cont_ext_borders]["diff_t_ext"] = delta_t_used
                        cont_ext_borders += 1
        self.cont_ext_borders = cont_ext_borders

    # setea ext_border para vertices asociados a los dos vertices de un borde
    # utilizado para calcular la posicion antes de llegar a la siguiente iteracion de los vertices asociados a bordes que colapsan en la iteracion actual        
    def set_ext_border(self, border_id, border_vertices):
        self.borders[border_id]["ext"] = 1
        self.vertices[border_vertices[0]]["ext_border"] = True
        self.vertices[border_vertices[1]]["ext_border"] = True
        
        for j in range(0, 2): # por cada vertice asociado al borde
            for i in range(0, 3): # por cada borde asociado a un vertice del borde
                borde_vertice = self.vertices[border_vertices[j]]["borders"][i]
                if borde_vertice != border_id: # si el borde es distinto al borde que va a colapsar 
                    xi_borde_vertice = self.borders[borde_vertice]["vertices"][0]
                    xf_borde_vertice = self.borders[borde_vertice]["vertices"][1]
                    if(xi_borde_vertice not in border_vertices): # si el vertice INICIAL no esta en los bordes del vertice a colapsar, se marca como ext_border
                        self.vertices[xi_borde_vertice]["ext_border"] = True
                    else: # si el vertice FINAL no esta en los bordes del vertice a colapsar, se marca como ext_border
                        self.vertices[xf_borde_vertice]["ext_border"] = True
        

    """ ================== READ VORONOI FUNCTIONS ============================================================================== """
    def read_initial_structure_voronoi(self):

        # VERTICES ------------------------------
        archivo = "vertices"
        file1 = open(f'utils/voronoi/salida/{archivo}.txt', 'r')
        Lines = file1.readlines()
        id_vertex = 0
        for line in Lines:
            aux = line.split(" ")            
            x = float(aux[0])
            y = float(aux[1])
            self.vertices[id_vertex]["id"] = id_vertex
            self.vertices[id_vertex]["pos_vector"][0] = x
            self.vertices[id_vertex]["pos_vector"][1] = y
            id_vertex += 1

        # BORDERS --------------------------------
        archivo = "borders"
        file1 = open(f'utils/voronoi/salida/{archivo}.txt', 'r')
        Lines = file1.readlines()
        id_border = 0
        for line in Lines:
            aux = line.split(" ")
            xi_index = int(aux[0])
            xf_index = int(aux[1])
            for i in range(0,3):
                b_aux = self.vertices[xi_index]["borders"][i]
                if(b_aux == 0):
                    self.vertices[xi_index]["borders"][i] = id_border
                    break
            
            for i in range(0,3):
                b_aux = self.vertices[xf_index]["borders"][i]
                if(b_aux == 0):
                    self.vertices[xf_index]["borders"][i] = id_border
                    break

            self.borders[id_border]["id"] = id_border
            self.borders[id_border]["vertices"][0] = xi_index
            self.borders[id_border]["vertices"][1] = xf_index
            id_border+=1


        # Set all the vertices's boundaries anticlockwise.
        for j in range(self.N_VERTICES_0):
            self.vertex_set_boundaries_anticlockwise(self.vertices[j])
            for g in range(0, 3):
                self.vertices[j]["grains"][g] = -1

        # set all grain vertices to -1
        for i in range(0, self.N_GRAINS_0):
            for j in range(0, 50):
                self.grains[i]["vertices"][j] = -1

        # GRAINS --------------------------------------------------------
        considerated = np.full(self.N_VERTICES_0*3, False)
        id_grain = 0
        for j in range(0, self.N_VERTICES_0): # por cada vertice
            start_vrt = j
            if(not self.vertices[start_vrt]["not_enabled"]) : # si el vertice esta activo
                for g in range(0, 3): # por cada grano del vertice
                    if(not considerated[j*3 + g]): # si no esta considerado el grano actual
                        current_vrt = start_vrt
                        current_side = g
                        while (True): # obtiene vertices asociados a cada grano del vertice inicial
                            current_vrt = current_vrt
                            if(considerated[(current_vrt * 3) + current_side] or self.vertices[current_vrt]["not_enabled"]) :
                                exit(1)
                            
                            considerated[(current_vrt * 3) + current_side] = True
                            for i in range(0, 50): # agrega vertice a grano
                                if(self.grains[id_grain]["vertices"][i] == -1):
                                    self.grains[id_grain]["vertices"][i] = current_vrt      
                                    break             

                            # busqueda de siguiente vertice en el grano a partir de los bordes
                            bnd = self.vertices[current_vrt]["borders"][current_side]
                            bnd_aux = self.borders[self.vertices[current_vrt]["borders"][current_side]]["vertices"]
                            new_current_vrt = 0
                            if(bnd_aux[0] == current_vrt):
                                new_current_vrt = bnd_aux[1]
                            else:
                                new_current_vrt = bnd_aux[0]
                            
                            i = -1
                            for i_aux in range(0, 3):
                                i = i_aux
                                if(self.vertices[new_current_vrt]["borders"][i] == bnd):
                                    break
                            current_vrt = new_current_vrt
                            current_side = (i+1) % 3
                            if (current_vrt == start_vrt): # al volver al inicio el grano esta completo 
                                break
                        self.grains[id_grain]["id"] = id_grain
                        id_grain +=1

        # READ ORIENTATION --------------------------------
        archivo = "orientations"
        file1 = open(f'utils/voronoi/salida/{archivo}.txt', 'r')
        Lines = file1.readlines()
        id_grain = 0
        for line in Lines:
            aux = line.split(" ")
            alpha = float(aux[0])
            self.grains[id_grain]["alpha"] = alpha
            id_grain += 1
            
        # set grains for each vertex 
        for i in range(0, self.N_GRAINS_0):
            id = self.grains[i]["id"]
            vertices = self.grains[i]["vertices"]
            for j in range(0, 50):
                id_v = vertices[j]
                if(id_v != -1):
                    grains_vertex = self.vertices[id_v]["grains"]
                    actual = -1
                    encontrado = False
                    for g in range(0, 3):
                        if(grains_vertex[g] == id):
                            encontrado = True
                        if(grains_vertex[g] == -1 and actual==-1):
                            actual = g
                    if(actual >= 0 and not encontrado):
                        self.vertices[id_v]["grains"][actual] = id
    
        self.update_cant_vertices_in_grains()     
        self.calculate_grain_position()

        self.all_vertex_set_grains_anticlockwise()
        self.reverse_grain_vertices_order()

    def reverse_grain_vertices_order(self):
        for g_index in range(0, self.N_GRAINS_0):
            n_vertices = self.grains[g_index]["n_vertices"]
            vertices = list(self.grains[g_index]["vertices"][0:n_vertices])
            vertices = vertices[::-1]
            for i in range(0, n_vertices):
                self.grains[g_index]["vertices"][i] = vertices[i]

    def all_vertex_set_grains_anticlockwise(self):
        for v_index in range(0, self.N_VERTICES_0):
            self.vertex_set_grains_anticlockwise(v_index)

    def vertex_set_grains_anticlockwise(self, v_index):
        vertex_pos = self.vertices[v_index]["pos_vector"]
        #if (vertex_pos[0]>=0.05 and vertex_pos[0] < 0.95): # porq?
        #    if (vertex_pos[1]>=0.05 and vertex_pos[1] < 0.95): # porq?
        grains = list(self.vertices[v_index]["grains"])
        angle_grains = []
        for g in range(0, 3):
            grain = self.grains[grains[g]]
            grain_pos = grain["pos_vector"]
            t_wrap = wrap_distances(vertex_pos, grain_pos)
            delta_x = t_wrap["delta_x"]
            delta_y = t_wrap["delta_y"]
            theta_radians = math.atan2(delta_y, delta_x) # angulo = atan(y/x)
            angle_grains.append(theta_radians)

        max_angle = max(angle_grains)
        max_pos = angle_grains.index(max_angle)
        min_angle = min(angle_grains)
        min_pos = angle_grains.index(min_angle)
        pos_max_min = [max_pos, min_pos]
        middle_pos = 0
        for i in range(0, 3):
            if i not in pos_max_min:
                middle_pos = i
        self.vertices[v_index]["grains"][0] = grains[min_pos]
        self.vertices[v_index]["grains"][1] = grains[middle_pos]
        self.vertices[v_index]["grains"][2] = grains[max_pos]
        
        self.vertices[v_index]["grains_angle"][0] = angle_grains[min_pos]
        self.vertices[v_index]["grains_angle"][1] = angle_grains[middle_pos]
        self.vertices[v_index]["grains_angle"][2] = angle_grains[max_pos]
            
                
    # actualiza la cantidad de vertices de cada grano
    # utilizado solo al inicio, luego las transiciones se ocupan de actualizar la cantidad de vertices
    def update_cant_vertices_in_grains(self):
        for g in range(0, self.N_GRAINS_0):
            if( not self.grains[g]["not_enabled"]):
                cont = 0
                for i in range(0, 50):
                    id = self.grains[g]["vertices"][i]
                    if (id != -1):
                        cont+=1
                if(cont == 3):
                    self.grains[g]["3_sided"] = 1
                if(cont < 3):
                    self.grains[g]["3_sided"] = -1
                else:
                    self.grains[g]["3_sided"] = 0
                self.grains[g]["n_vertices"] = cont

    
    """ ==================================================================================================================================== """
    """ ================== SAVE STATE FUNCTIONS ============================================================================== """
    """ ==================================================================================================================================== """
    

    """ 
    save_actual_state:
    call all functions to save actual state and structure
    """
    def save_actual_state(self): 
        self.last_timestep_saved = self.ACTUAL_TIMESTEP 
        self.save_general_state()
        self.save_vertices()
        self.save_borders()
        self.save_grains()

    
        

    """ 
    save_general_state:
    Save general state of the structure (#grains, #vertices, #borders, total energy, total area) for every timestep.
    """
    def save_general_state(self): 
        self.general[self.ACTUAL_TIMESTEP]["iter"] = self.ACTUAL_TIMESTEP
        self.general[self.ACTUAL_TIMESTEP]["t"] = round(self.ACTUAL_TIME, 6)
        self.general[self.ACTUAL_TIMESTEP]["energy"] = self.energy
        self.general[self.ACTUAL_TIMESTEP]["total_area"] = self.total_area 
        self.general[self.ACTUAL_TIMESTEP]["n_grains"] = self.N_GRAINS 
        self.general[self.ACTUAL_TIMESTEP]["n_vertices"] = self.N_VERTICES
        self.general[self.ACTUAL_TIMESTEP]["n_borders"] = self.N_BORDERS
        
    # guarda estado general en el tiempo actual
    def save_general_state_all_time(self):
        folder = f"out/{self.out_folder}"
        file_name = f"{folder}/general.npy"
        with open(file_name, 'wb+') as f:
            np.save(f, self.general)
        
    # guarda arreglo vertices en el tiempo actual
    def save_vertices(self):
        folder = f"out/{self.out_folder}"
        vertex_folder = f"{folder}/vertices"
        file_name = f"{vertex_folder}/{self.ACTUAL_TIMESTEP}.npy"
        with open(file_name, 'wb+') as f:
            np.save(f, self.vertices)
        
    # guarda arreglo de bordes en el tiempo actual
    def save_borders(self):
        folder = f"out/{self.out_folder}"
        border_folder = f"{folder}/borders"
        file_name = f"{border_folder}/{self.ACTUAL_TIMESTEP}.npy"
        with open(file_name, 'wb+') as f:
            np.save(f, self.borders)
        
    # guarda arreglo de granos en el tiempo actual
    def save_grains(self):
        folder = f"out/{self.out_folder}"
        grain_folder = f"{folder}/grains"
        file_name = f"{grain_folder}/{self.ACTUAL_TIMESTEP}.npy"
        with open(file_name, 'wb+') as f:
            np.save(f, self.grains)
        