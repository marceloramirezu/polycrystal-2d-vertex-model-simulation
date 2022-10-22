from inspect import ClassFoundException
from subprocess import IDLE_PRIORITY_CLASS
import numpy as np;
from utils.geometry import *
import math
from utils.datatypes import *



class vertex_model:
    """ ==================================================================================================================================== """
    """ ==================== CONSTRUCTOR Y VARIABLES INICIALES  ==================================================================================== """
    """ ==================================================================================================================================== """
    gamma_0= 0
    mov_vertex= 0
    n_grains = 0
    n_borders = 0
    n_vertices = 0
    mov_vertex = 0
    actual_t = 0
    actual_iter = 0
    vertices = []
    borders = []
    grains = []
    voronoi_folder = ""
    initial_delta_t = 0
    cont_ext_borders = 0
    ext_borders = []
    actual_print_lvl = 3
    # Inicializa arreglos
    # lee estado inicial dado por algoritmo voronoi
    def __init__(self, OPTIONS_VERTEX_MODEL):
        self.voronoi_folder = OPTIONS_VERTEX_MODEL["VORONOI_OUT_FOLDER"]
        self.gamma_0 = OPTIONS_VERTEX_MODEL["GAMMA_0"]
        self.mov_vertex = OPTIONS_VERTEX_MODEL["MOV_VERTEX"]
        self.n_grains = OPTIONS_VERTEX_MODEL["INITIAL_N"]
        self.n_borders = OPTIONS_VERTEX_MODEL["INITIAL_N"]*3
        self.n_vertices = OPTIONS_VERTEX_MODEL["INITIAL_N"]*2
        self.delta_t = OPTIONS_VERTEX_MODEL["DELTA_T"]
        self.initial_delta_t = OPTIONS_VERTEX_MODEL["DELTA_T"]
        self.grad_eps = OPTIONS_VERTEX_MODEL["GRAND_EPS"]
        
        self.vertices = np.zeros(self.n_vertices, dtype=dt_vertex)         
        self.borders = np.zeros(self.n_borders, dtype=dt_border)         
        self.grains = np.zeros(self.n_grains, dtype=dt_grain) # (id, alpha, x1, x2, x3, ..., x50)
        
        self.actual_t = 0
        self.actual_iter = 0
        self.leer_granos_voronoi()

    
    """ ==================================================================================================================================== """
    """ ==================== CALCULOS EN ESTRUCTURA  ==================================================================================== """
    """ ==================================================================================================================================== """
    
    # setea bordes del vertice en sentido horario
    def vertex_set_boundaries_clockwise(self, vertex) :
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
            angles.append(math.atan2(delta_x, delta_y))
        
        for i in range(0, 2):
            for p in range(1, (3-i)):
                if(angles[p-1] < angles[p]):
                    aux = angles[p-1]
                    angles[p-1] = angles[p]
                    angles[p] = aux
                    auxb = vertex["borders"][p-1]
                    vertex["borders"][p-1] = vertex["borders"][p]
                    vertex["borders"][p] = auxb

    # t = t+delta_t, iter += 1
    def next_iteration(self):
        #if(self.delta_t != self.initial_delta_t):
        self.delta_t = self.initial_delta_t
        self.actual_iter = self.actual_iter+1
        self.actual_t = self.actual_t+self.delta_t

    # calcula largos de arco y energias de los vertices
    def calculate_len_and_energy_vertices(self):      
        with np.nditer(self.borders, op_flags=['readwrite']) as it:
            for border in it:
                if ( not border["not_enabled"]):
                    self.calculate_len_and_energy_border(border)

    def calculate_len_and_energy_border(self, border):
        xi_index = border["vertices"][0]
        xf_index = border["vertices"][1]
        xi = self.vertices[xi_index]
        xf = self.vertices[xf_index]
        t_wrap = wrap_distances( xi["pos_vector"],  xf["pos_vector"] ) # calculate_arc_len
        border["arc_len"] = t_wrap["arc_len"]
        border["tangent_vector"][0] = t_wrap["x_u"]
        border["tangent_vector"][1] = t_wrap["y_u"]
        # calcular energia del borde con la orientacion de los dos granos asociados y gamma_o
        border["gamma"] = self.gamma_0*math.cos(0)
        
    # calcula velocidades de los vertices
    def calculate_vel_vertices(self):
        model = 1
        with np.nditer(self.vertices, op_flags=['readwrite']) as it:
            for vertex in it:
                if(not vertex["not_enabled"] ):
                    new_vel = self.calculate_vel_vertex(vertex["id"])
                    vertex["vel_vector"][0] = new_vel[0]
                    vertex["vel_vector"][1] = new_vel[1]    

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
        vel[0] = vel[0]*self.mov_vertex
        vel[1] = vel[1]*self.mov_vertex 
        return vel
        
    # calcula diferencia de energia (NO UTILIZADO)
    def energy_diff(self, comp, vertex):
        xi = vertex["pos_vector"][0]
        xf = vertex["pos_vector"][0]
        yi = vertex["pos_vector"][1]
        yf = vertex["pos_vector"][1]
        
        if(comp==0): # x comp
            xf = xi+self.grad_eps
        else:
            yf = yi+self.grad_eps
            

        new_arc_lengths = []
        nei = []
        for v in range(0,3):
            border_xi_index = self.borders[vertex["borders"][v]]["vertices"][0]
            border_xf_index = self.borders[vertex["borders"][v]]["vertices"][1]
            vecino_i = None
            if ( border_xi_index == vertex["id"]):
                vecino_i = border_xf_index
            else:
                vecino_i = border_xi_index
            nei.append(vecino_i)
            vecino_pos = self.vertices[vecino_i]["pos_vector"]

            t_wrap_v = wrap_distances([xf,yf], vecino_pos)
            arc_len = t_wrap_v["arc_len"]
            new_arc_lengths.append(arc_len)

        bnd_term = 0.0
        for b in range(0,3):
            diff_arc = new_arc_lengths[b] - self.borders[vertex["borders"][b]]["arc_len"]
            bnd_term += diff_arc

   
            
        return (-bnd_term / self.grad_eps)

    # avanza los vertices a su nueva posicion
    def update_position_vertices(self):
        if(self.cont_ext_borders > 0):
            #self.imprimir(f"self.cont_ext_borders t:{self.actual_iter} cont_ext:{self.cont_ext_borders}", 2)
            
            # por cada borde
            for c in range(0, self.cont_ext_borders):           
                # avanza localmente los vertices asociados a los bordes que se extinguen hasta actual_t + t_ext
                # realiza transicion topologica localmente
                self.advance_ext_border(c)    

        # avanza delta_t toda la estructura menos los vertices asociados a bordes que se extinguen dentro de la iteracion actual
        with np.nditer(self.vertices, op_flags=['readwrite']) as it:
            for vertex in it:
                if(not vertex["not_enabled"] and not vertex["ext_border"]):
                    velx = vertex["vel_vector"][0]
                    vely = vertex["vel_vector"][1]
                    vertex["pos_vector"][0] = vertex["pos_vector"][0] + (velx*self.delta_t)    
                    vertex["pos_vector"][1] = vertex["pos_vector"][1] + (vely*self.delta_t)  

                    if vertex["pos_vector"][0] >= 1:
                        vertex["pos_vector"][0] = vertex["pos_vector"][0]-1
                    elif vertex["pos_vector"][0] < 0:
                        vertex["pos_vector"][0] = vertex["pos_vector"][0]+1
                    if vertex["pos_vector"][1] >= 1:
                        vertex["pos_vector"][1] = vertex["pos_vector"][1]-1
                    elif vertex["pos_vector"][1] < 0:
                        vertex["pos_vector"][1] = vertex["pos_vector"][1]+1
        
        # cada vertice asociado a un borde que se extingue en la iteracion actual avanza la  delta_t - t_ext
        for i in range(0, self.cont_ext_borders):    
            break    # arreglar, falta hacer flip
                     # si se activa sin los flips implementados los bordes tienen la posibilidad de crecer si las velocidades de los vertices asociados apuntan en direcciones contrarias (el borde dejaria de estar clasificado como ext y se podria mover)                     
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
            
    # inicia arreglo con bordes por colapsar
    def iniciar_ext_borders(self):
        self.ext_borders = np.zeros(self.n_borders, dtype=dt_ext_border)
        for i in range(0, self.n_vertices):
            if(not self.vertices[i]["not_enabled"]):
                self.vertices[i]["ext_border"] = False
                

    # ordena arreglo de bordes por colapsar
    def ordenar_ext_borders(self):
        Tcopy=self.ext_borders[['id','t_ext', 'diff_t_ext']].copy()
        I=np.argsort(Tcopy,order=['t_ext'])
        self.ext_borders = self.ext_borders[I]



    """ ==================================================================================================================================== """
    """ ================== TRANSICIONES TOPOLOGICAS ========================================================================================="""
    """ ==================================================================================================================================== """

    
    """ ================== TRANSICION FLIP BORDER ========================================================================================== """

    def flip_border(self, vertice_1, vertice_2, flip_border):
        print(f"\n\nFLIP BORDER: {flip_border}, v: ({vertice_1}, {vertice_2}); t:{self.actual_iter}")
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
        
        #print("VERTICES PRE")
        #print(f'BORDES VERTICE 1: {self.vertices[vertice_1]["borders"][0]}, {self.vertices[vertice_1]["borders"][1]}, {self.vertices[vertice_1]["borders"][2]}')
        #print(f'BORDES VERTICE 2: {self.vertices[vertice_2]["borders"][0]}, {self.vertices[vertice_2]["borders"][1]}, {self.vertices[vertice_2]["borders"][2]}')
        
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

        #print(f"v1_index_border_flip: {v1_index_border_flip}, v1_index_prev_b: {v1_index_prev_b}, v1_index_post_b: {v1_index_post_b}")
        #print(f"v2_index_border_flip: {v2_index_border_flip}, v2_index_prev_b: {v2_index_prev_b}, v2_index_post_b: {v2_index_post_b}")
        #print(f"v1_prev_b: {v1_prev_b}, v1_post_b: {v1_post_b}")
        #print(f"v2_prev_b: {v2_prev_b}, v2_post_b: {v2_post_b}")
        self.vertices[vertice_1]["borders"][0] = v1_prev_b
        self.vertices[vertice_1]["borders"][1] = v2_post_b
        self.vertices[vertice_1]["borders"][2] = flip_border
        self.vertices[vertice_2]["borders"][0] = v2_prev_b
        self.vertices[vertice_2]["borders"][1] = v1_post_b
        self.vertices[vertice_2]["borders"][2] = flip_border
        
        #print("VERTICES POST")
        #print(f'BORDES VERTICE 1: {self.vertices[vertice_1]["borders"][0]}, {self.vertices[vertice_1]["borders"][1]}, {self.vertices[vertice_1]["borders"][2]}')
        #print(f'BORDES VERTICE 2: {self.vertices[vertice_2]["borders"][0]}, {self.vertices[vertice_2]["borders"][1]}, {self.vertices[vertice_2]["borders"][2]}')
        
        # 2.2.- seteo de vertices dentro de bordes ----------------------------------------------------------------------------------------------------------------

        #print("\nBORDES PRE")
        #print(f"vertice_1: {vertice_1}  vertice_2: {vertice_2}")
        #print(f"VERTICES BORDE 1: {self.borders[v1_post_b]['vertices'][0]}, {self.borders[v1_post_b]['vertices'][1]}")
        #print(f"VERTICES BORDE 2: {self.borders[v2_post_b]['vertices'][0]}, {self.borders[v2_post_b]['vertices'][1]}")
        
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

            
        #print("BORDES POST")
        #print(f"VERTICES BORDE 1: {self.borders[v1_post_b]['vertices'][0]}, {self.borders[v1_post_b]['vertices'][1]}")
        #print(f"VERTICES BORDE 2: {self.borders[v2_post_b]['vertices'][0]}, {self.borders[v2_post_b]['vertices'][1]}")

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

        #print(f"GRAINS INVOLVE: {text_grains_involve[2:]}")
        
        
        # 3.1.- vertices en granos -----------------------------------------------------------
        #print("\nVERTICES ON GRAIN START")
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
                pos_v1_in_two_vertices_grain.append(pos_v1)
                pos_v2_in_two_vertices_grain.append(pos_v2)
            elif(encontrado_v1):
                v1_pos_in_v1_grain = pos_v1
                v1_grain = grain
            elif(encontrado_v2):
                v2_pos_in_v2_grain = pos_v2
                v2_grain = grain
            else:
                pass
        #print(f"\nTWO VERTICES GRAIN: ({two_vertices_grain[0]}, {two_vertices_grain[1]})")
        #print(f"pos v1 in two vertices grain: ({pos_v1_in_two_vertices_grain[0]}, {pos_v1_in_two_vertices_grain[1]})")
        #print(f"pos v2 in two vertices grain: ({pos_v2_in_two_vertices_grain[0]}, {pos_v2_in_two_vertices_grain[1]})")
        #print(f"V1 GRAIN: {v1_grain}, pos_v1:{v1_pos_in_v1_grain}")
        #print(f"V2 GRAIN: {v2_grain}, pos_v2:{v2_pos_in_v2_grain}")
        #print(f"")
        mantiene_solo_v1_two_vertices_grain = 0
        mantiene_solo_v2_two_vertices_grain = 0
        pos_del_vertice_two_vertices_grain = [0, 0] # grano 1, grano 2
        if( pos_v1_in_two_vertices_grain[0] > pos_v2_in_two_vertices_grain[0] ): # en grano 1 pos_v2, pos_v1
            # se elimina el vertice 1 en el grano 1 => grano 1 mantiene a vertice 2
            mantiene_solo_v2_two_vertices_grain = two_vertices_grain[0]
            # se elimina el vertice 2 en el grano 2 => grano 2 mantiene a vertice 1
            mantiene_solo_v1_two_vertices_grain = two_vertices_grain[1]
        else: # en grano 1 pos_v1, pos_v2
            # se elimina el vertice 2 en el grano 1 => grano 1 mantiene a vertice 1
            mantiene_solo_v1_two_vertices_grain = two_vertices_grain[0]
            # se elimina el vertice 1 en el grano 2 => grano 2 mantiene a vertice 2
            mantiene_solo_v2_two_vertices_grain = two_vertices_grain[1]


        #print(f"MANTIENE V1: {mantiene_solo_v1_two_vertices_grain}")
        #print(f"MANTIENE V2: {mantiene_solo_v2_two_vertices_grain}")

        self.delete_vertices_on_grain(mantiene_solo_v1_two_vertices_grain, [vertice_1], vertice_2)
        self.delete_vertices_on_grain(mantiene_solo_v2_two_vertices_grain, [vertice_2], vertice_1)
        # el vertice 1 se agrega luego del vertice 2 en el grano que solo contiene el vertice 2
        self.add_vertex_on_grain(v2_grain, vertice_1, v2_pos_in_v2_grain+1)
        # el vertice 2 se agrega luego del vertice 1 en el grano que solo contiene el vertice 1
        self.add_vertex_on_grain(v1_grain, vertice_2, v1_pos_in_v1_grain+1)

        #print("VERTICES ON GRAIN POST")

        # 3.2.- granos en vertices -----------------------------------------------------------
        print("GRAIN ON VERTICES START")
        v1_grains_id = [self.grains[v1_grains[0]]["id"], self.grains[v1_grains[1]]["id"], self.grains[v1_grains[2]]["id"]]
        v2_grains_id = [self.grains[v2_grains[0]]["id"], self.grains[v2_grains[1]]["id"], self.grains[v2_grains[2]]["id"]]
        print(f"V1 GRAINS: {v1_grains_id}")
        print(f"V2 GRAINS: {v2_grains_id}")
        print(f"GRAIN_v1: {mantiene_solo_v1_two_vertices_grain}")
        print(f"GRAIN_v2: {mantiene_solo_v2_two_vertices_grain}")

        pos_grain_mantiene_solo_v1 = 0
        pos_grain_mantiene_solo_v2 = 0
        
        for i in range(0, 3):
            if mantiene_solo_v1_two_vertices_grain == v1_grains_id[i]:
                pos_grain_mantiene_solo_v1 = i
            if mantiene_solo_v2_two_vertices_grain == v2_grains_id[i]:
                pos_grain_mantiene_solo_v2 = i
        
        pre_pos_grain_mantiene_solo_v1 = (pos_grain_mantiene_solo_v1+1)%3
        pre_pos_grain_mantiene_solo_v2 = (pos_grain_mantiene_solo_v2+1)%3
        print(f"pre_pos_v1: {pre_pos_grain_mantiene_solo_v1}")
        print(f"pre_pos_v2: {pre_pos_grain_mantiene_solo_v2}")
        
        pre_grain_mantiene_solo_v1 = v1_grains_id[pre_pos_grain_mantiene_solo_v1]
        pre_grain_mantiene_solo_v2 = v2_grains_id[pre_pos_grain_mantiene_solo_v2]
        print(f"pre_v1: {pre_grain_mantiene_solo_v1}")
        print(f"pre_v2: {pre_grain_mantiene_solo_v2}")
        
        
        self.vertices[vertice_2]["grains"][0] = mantiene_solo_v1_two_vertices_grain
        self.vertices[vertice_2]["grains"][1] = pre_grain_mantiene_solo_v1
        self.vertices[vertice_2]["grains"][2] = pre_grain_mantiene_solo_v2

        
        self.vertices[vertice_1]["grains"][0] = mantiene_solo_v2_two_vertices_grain
        self.vertices[vertice_1]["grains"][1] = pre_grain_mantiene_solo_v2
        self.vertices[vertice_1]["grains"][2] = pre_grain_mantiene_solo_v1
        print("GRAIN ON VERTICES POST")
        print(f"V1 GRAINS: ({v1_grains[0]}, {v1_grains[1]}, {v1_grains[2]})")
        print(f"V2 GRAINS: ({v2_grains[0]}, {v2_grains[1]}, {v2_grains[2]})")
        
        """  """        

        
    def add_vertex_on_grain(self, grain, add_vertex, pos):
        print(f"add_vertex_on_grain: (grain: {grain}), (add_vertex: {add_vertex}), (pos: {pos})")
        n_vertices = self.grains[grain]["n_vertices"]
        vertices = self.grains[grain]["vertices"]
        print(f"initial vertices: {self.grains[grain]['vertices'][0:(n_vertices+5)]}")
        post_vertices = list(vertices[pos:n_vertices])
        print(f"post_vertices: {post_vertices}")
        self.grains[grain]["vertices"][pos] = add_vertex
        cont = 0
        for post_v in post_vertices:
            cont +=1
            if(pos + cont < n_vertices+1): 
                self.grains[grain]["vertices"][pos+cont] = post_v
            else:
                break
        self.grains[grain]["n_vertices"] = n_vertices+1
        print(f"final vertices: {self.grains[grain]['vertices'][0:n_vertices+5]}\n")
    
    """ ================== TRANSICION DELETE 3-SIDED GRAIN ================================================================================= """
    # Transicion Topologica borrar grano
    def delete_grain(self, id_grain):
        self.imprimir(f"\n===============================================\nELIMINANDO GRANO t:{self.actual_iter} grano:{id_grain}", 2)
        grain = self.grains[id_grain]
        if (self.grains[id_grain]["not_enabled"]):
            self.imprimir("ERROR, ELIMINANDO GRANO DESACTIVADO", 1)
            return 0
        self.grains[id_grain]["not_enabled"] = True
        
        alpha = grain["alpha"]
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
        # se avanzan los vertices asociados a los flips hasta (actual_t + t_ext)
        if not del_grain:  
            
            p1_index = self.borders[id_borde]["vertices"][0]
            p2_index = self.borders[id_borde]["vertices"][1]     
            self.flip_border(p1_index, p2_index, id_borde)    
        
        

    def test_structure(self):
        # granos = 3 bordes = 2 vertices
        # vertice = 3 bordes habilitados = 3 granos habilitados
        # grano = n_vertices habilitados
        # borde = 2 vertices habilitados = 2 granos habilitados
        pass

    def calculate_grain_position(self):
        for i in range(0, self.n_grains):
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
    def calculate_t_ext(self):
        self.iniciar_ext_borders()
        cont_ext_borders = 0
        for i in range(0, self.n_borders):
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
                    if( aux >= 0 and aux <= (self.delta_t) ):
                        self.set_ext_border(i, [border_xi_index, border_xf_index])
                        self.ext_borders[cont_ext_borders]["id"] = self.borders[i]["id"]
                        self.ext_borders[cont_ext_borders]["t_ext"] = self.borders[i]["t_ext"]
                        self.ext_borders[cont_ext_borders]["diff_t_ext"] = self.delta_t
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
    def leer_granos_voronoi(self):

        # VERTICES ------------------------------
        archivo = "vertices"
        file1 = open(f'{self.voronoi_folder}/{archivo}.txt', 'r')
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
        file1 = open(f'{self.voronoi_folder}/{archivo}.txt', 'r')
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


        # Set all the vertices's boundaries clockwise.
        for j in range(self.n_vertices):
            self.vertex_set_boundaries_clockwise(self.vertices[j])
            for g in range(0, 3):
                self.vertices[j]["grains"][g] = -1

        # set all grain vertices to -1
        for i in range(0, self.n_grains):
            for j in range(0, 50):
                self.grains[i]["vertices"][j] = -1
        for i in range(self.n_borders):
                self.borders[i]["grains"][0] = -1
                self.borders[i]["grains"][1] = -1

        # GRAINS --------------------------------------------------------
        considerated = np.full(self.n_vertices*3, False)
        id_grain = 0
        for j in range(0, self.n_vertices):
            start_vrt = j
            if(not self.vertices[start_vrt]["not_enabled"]) :
                for g in range(0, 3):
                    if(not considerated[j*3 + g]):
                        current_vrt = start_vrt
                        current_side = g
                        while (True):
                            
                            current_vrt = current_vrt
                            if(considerated[(current_vrt * 3) + current_side] or self.vertices[current_vrt]["not_enabled"]) :
                                exit(1)
                            
                            considerated[(current_vrt * 3) + current_side] = True
                            for i in range(0, 50): # agrega vertice a grano
                                if(self.grains[id_grain]["vertices"][i] == -1):
                                    self.grains[id_grain]["vertices"][i] = current_vrt      
                                    break             
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
                            if (current_vrt == start_vrt):
                                break
                        self.grains[id_grain]["id"] = id_grain
                        id_grain +=1

        # READ ORIENTATION --------------------------------
        archivo = "orientations"
        file1 = open(f'{self.voronoi_folder}/{archivo}.txt', 'r')
        Lines = file1.readlines()
        id_grain = 0
        for line in Lines:
            aux = line.split(" ")
            alpha = float(aux[0])
            self.grains[id_grain]["alpha"] = alpha
            id_grain += 1
            
        # set grains for each vertex 
        for i in range(0, self.n_grains):
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
    
    
        # alcular cantidad de vertices en cada grano
        self.update_cant_vertices_in_grains()     
        self.calculate_grain_position()

        self.vertex_set_grains_clockwise()
        self.grain_set_vertex_clockwise()

    def grain_set_vertex_clockwise(self):
        for g_index in range(0, self.n_grains):
            n_vertices = self.grains[g_index]["n_vertices"]
            vertices = list(self.grains[g_index]["vertices"][0:n_vertices])
            vertices = vertices[::-1]
            for i in range(0, n_vertices):
                self.grains[g_index]["vertices"][i] = vertices[i]

    def vertex_set_grains_clockwise(self):
        for v_index in range(0, self.n_vertices):
            print(f"\n SET GRAINS CLOCKWISE ON VERTEX ({v_index})")
            pos = self.vertices[v_index]["pos_vector"]
            grains = list(self.vertices[v_index]["grains"])
            angle_grains = []
            for g in range(0, 3):
                grain = self.grains[grains[g]]
                t_wrap = wrap_distances(pos, grain["pos_vector"])
                delta_x = t_wrap["delta_x"]
                delta_y = t_wrap["delta_y"]
                theta_radians = math.atan2(delta_y, delta_x)
                angle_grains.append(theta_radians)

            print(f"angle_grains: {angle_grains}")
            max_angle = max(angle_grains)
            max_pos = angle_grains.index(max_angle)
            min_angle = min(angle_grains)
            min_pos = angle_grains.index(min_angle)
            pos_max_min = [max_pos, min_pos]
            middle_pos = 0
            for i in range(0, 3):
                if i not in pos_max_min:
                    middle_pos = i
            self.vertices[v_index]["grains"][2] = grains[2]
            self.vertices[v_index]["grains"][1] = grains[1]
            self.vertices[v_index]["grains"][0] = grains[0]
            
            self.vertices[v_index]["grains_angle"][2] = angle_grains[2]
            self.vertices[v_index]["grains_angle"][1] = angle_grains[1]
            self.vertices[v_index]["grains_angle"][0] = angle_grains[0]


                
    # actualiza la cantidad de vertices de cada grano
    # utilizado solo al inicio, luego las transiciones se ocupan de actualizar la cantidad de vertices
    def update_cant_vertices_in_grains(self):
        for g in range(0, self.n_grains):
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

    # funcion auxiliar para imprimir por consola con niveles de prioridad
    def imprimir(self, texto, lvl):
        if(lvl <= self.actual_print_lvl):
            print(texto)


    """ ==================================================================================================================================== """
    """ ================== SAVE STATE FUNCTIONS ============================================================================== """
    """ ==================================================================================================================================== """
    # Guarda estado actual de la estructura (llama a las otras funciones de guardar)
    def save_actual_state(self):  
        #self.save_general_t_state()
        self.save_vertices()
        self.save_borders()
        self.save_grains()

    # guarda estado general en el tiempo actual
    def save_general_t_state(self):
        tipo = "a"
        if(self.actual_iter == 0):
            tipo = 'w+'
        
        folder = "out"
        file_name = f"{folder}/general.npy"
        with open(file_name, tipo) as f:
            start_line = f"{self.actual_iter}\n"
            f.write(start_line) 

    # guarda arreglo vertices en el tiempo actual
    def save_vertices(self):
        folder = "out"
        vertex_folder = f"{folder}/vertices"
        file_name = f"{vertex_folder}/{self.actual_iter}.npy"
        with open(file_name, 'wb+') as f:
            np.save(f, self.vertices)

        file_name = f"{vertex_folder}/{self.actual_iter}.txt"
        with open(file_name, 'w+') as f:
            for i in self.vertices:
                line = f'{i["id"]} x:{i["pos_vector"][0]} y:{i["pos_vector"][1]} vx:{i["vel_vector"][0]} vy:{i["vel_vector"][1]} b:({i["borders"][0]}, {i["borders"][1]}, {i["borders"][2]})\n'
                f.write(line)
            
    # guarda arreglo de bordes en el tiempo actual
    def save_borders(self):
        folder = "out"
        border_folder = f"{folder}/borders"
        file_name = f"{border_folder}/{self.actual_iter}.npy"
        with open(file_name, 'wb+') as f:
            np.save(f, self.borders)

        file_name = f"{border_folder}/{self.actual_iter}.txt"
        with open(file_name, 'w+') as f:
            for i in self.borders:
                line = f'{i["id"]} {i["arc_len"]} {i["tangent_vector"][0]} {i["tangent_vector"][1]}\n'
                f.write(line)

    # guarda arreglo de granos en el tiempo actual
    def save_grains(self):
        folder = "out"
        vertex_folder = f"{folder}/grains"
        file_name = f"{vertex_folder}/{self.actual_iter}.npy"
        with open(file_name, 'wb+') as f:
            np.save(f, self.grains)