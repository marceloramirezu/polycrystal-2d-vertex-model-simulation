import numpy as np;
from utils.geometry import *
import math
from utils.datatypes import *



class vertex_model:
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

        
    def next_iteration(self):
        #if(self.delta_t != self.initial_delta_t):
        self.delta_t = self.initial_delta_t
        self.actual_iter = self.actual_iter+1
        self.actual_t = self.actual_t+self.delta_t

    def calculate_len_and_energy_vertices(self):      
        with np.nditer(self.borders, op_flags=['readwrite']) as it:
            for border in it:
                if ( not border["not_enabled"]):
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


    def calculate_vel_vertices(self):
        model = 1
        with np.nditer(self.vertices, op_flags=['readwrite']) as it:
            for vertex in it:
                if(not vertex["not_enabled"] ):
                    new_vel = self.calculate_vel_vertex(vertex)
                    vertex["vel_vector"][0] = new_vel[0]
                    vertex["vel_vector"][1] = new_vel[1]    

    def calculate_vel_vertex(self, vertex):
        vel = [0.0, 0.0]
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

    def update_position_vertices(self):
        # avanza delta_t toda la estructura menos los vertices asociados a bordes que se extinguen dentro de la iteracion actual
        with np.nditer(self.vertices, op_flags=['readwrite']) as it:
            for vertex in it:
                vertex_ext = False
                for b in range(0, 3):
                    if(self.borders[ vertex["borders"][b] ]["ext"] == 1):
                        vertex_ext = True
                if(not vertex["not_enabled"] and not vertex_ext):
                    velx = vertex["vel_vector"][0]
                    vely = vertex["vel_vector"][1]
                    if(not vertex["not_enabled"]):
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
        
        # cada vertice asociado a un borde que se extingue en la iteracion actual avanza la diferencia entre t_ext y delta_t
        for i in range(0, self.cont_ext_borders):    
            break    # arreglar    
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
            
             

    def iniciar_ext_borders(self):
        self.ext_borders = np.zeros(self.n_borders, dtype=dt_ext_border)
                
    
        
    def ordenar_ext_borders(self):
        Tcopy=self.ext_borders[['id','t_ext', 'diff_t_ext']].copy()
        I=np.argsort(Tcopy,order=['t_ext'])
        self.ext_borders = self.ext_borders[I]


    def delete_grain(self, id_grain):
        print(f"ELIMINANDO GRANO {id_grain}")
        grain = self.grains[id_grain]
        self.grains[id_grain]["not_enabled"] = True
        
        alpha = grain["alpha"]
        n_vertices = grain["n_vertices"]
        vertices = grain["vertices"][0:n_vertices]
        id_initial_vertex = self.vertices[vertices[0]]["id"]
        arr_pos = [self.vertices[vertices[0]]["pos_vector"]]
        sum_x = self.vertices[vertices[0]]["pos_vector"][0]
        sum_y = self.vertices[vertices[0]]["pos_vector"][1]
        cont_vertices = 1
        borders_delete_aux = []
        granos_resultantes = []

        # revisa bordes y granos del primer vertice
        for g in range(0, 3):
            # granos
            grain = self.vertices[vertices[0]]["grains"][g]
            if(grain != id_grain):
                granos_resultantes.append(id_grain)
            # bordes
            border_id = self.vertices[vertices[0]]["borders"][g]
            border = self.borders[border_id]
            if (border["vertices"][0] in vertices and border["vertices"][1] in vertices):
                self.borders[border_id]["not_enabled"] = True
            else:
                borders_delete_aux.append(border_id)

        for j in range(1, n_vertices):                       
            cont_vertices+=1             
            
            # desactiva vertices excepto el primero
            self.vertices[vertices[j]]["not_enabled"] = True

            # guarda bordes afectados para luego eliminar los repetidos (entre los vertices del grano)
            for g in range(0, 3):
                grain = self.vertices[vertices[0]]["grains"][g]
                if(grain != id_grain):
                    granos_resultantes.append(id_grain)
                border_id = self.vertices[vertices[j]]["borders"][g]
                border = self.borders[border_id]
                if (border["vertices"][0] in vertices and border["vertices"][1] in vertices):
                    self.borders[border_id]["not_enabled"] = True
                else:
                    borders_delete_aux.append(border_id)
                #if(border not in borders_delete_aux):
                #else:

            v_pos = self.vertices[vertices[j]]["pos_vector"]
            t_wrap = wrap_distances(arr_pos[j-1], v_pos)
            arr_pos.append( t_wrap["xf"] )
            sum_x = sum_x+t_wrap["xf"][0]
            sum_y = sum_y+t_wrap["xf"][1]

        # setea bordes nuevos para vertice restante
        # setea vertice restante en bordes afectados
        # setea granos de vertices y bordes afectados
        for i in range(0, 3):
            if(self.vertices[id_initial_vertex]["grains"][i] == id_grain):
                for j in range(0, 3):
                    if (granos_resultantes[j] not in self.vertices[id_initial_vertex]["grains"]):
                        self.vertices[id_initial_vertex]["grains"][i] = granos_resultantes[j]
        for b in range(0, 3):
            self.vertices[id_initial_vertex]["borders"][b] = borders_delete_aux[b]
            border = self.borders[borders_delete_aux[b]]
            if( self.vertices[border["vertices"][0]]["not_enabled"] ): # si no esta habilidado
                self.borders[borders_delete_aux[b]]["vertices"][0] = id_initial_vertex
            
            if( self.vertices[border["vertices"][1]]["not_enabled"] ): # si no esta habilidado
                self.borders[borders_delete_aux[b]]["vertices"][1] = id_initial_vertex
            
        """ 
        else:
            self.borders[borders_delete_aux[b]]["vertices"][1] = id_initial_vertex
        #print(f"SETEANDO EN BORDE {borders_delete_aux[b]}")
        """
        prom_x = (sum_x/(cont_vertices))
        prom_y = (sum_y/(cont_vertices))
        self.vertices[id_initial_vertex]["pos_vector"][0] = prom_x
        self.vertices[id_initial_vertex]["pos_vector"][1] = prom_y

    def advance_ext_border(self, id_ext_border):
        b = self.ext_borders[(id_ext_border+1)*-1]
        id_borde = b["id"]
        t_ext = b["t_ext"]
        diff_t_ext = b["diff_t_ext"]
        self.ext_borders[(id_ext_border+1)*-1]["diff_t_ext"] = diff_t_ext - t_ext
        vertices = self.borders[id_borde]["vertices"]
        for v in range(0, 2):
            vertex = self.vertices[vertices[v]]
            for g in range(0, 3):
                grain = self.grains[vertex["grains"][g]]
                if (grain["n_vertices"] == 3):
                    self.delete_grain(grain["id"])

        for i in range(0, 2):
            vertex_id_aux = self.borders[id_borde]["vertices"][i]
            vertex = self.vertices[vertex_id_aux]
            velx = vertex["vel_vector"][0]
            vely = vertex["vel_vector"][1]
            if(not vertex["not_enabled"]):
                self.vertices[vertex_id_aux]["pos_vector"][0] = self.vertices[vertex_id_aux]["pos_vector"][0] + (velx*t_ext)    
                self.vertices[vertex_id_aux]["pos_vector"][1] = self.vertices[vertex_id_aux]["pos_vector"][1] + (vely*t_ext)  
            if self.vertices[vertex_id_aux]["pos_vector"][0] >= 1:
                self.vertices[vertex_id_aux]["pos_vector"][0] = self.vertices[vertex_id_aux]["pos_vector"][0]-1
            elif self.vertices[vertex_id_aux]["pos_vector"][0] < 0:
                self.vertices[vertex_id_aux]["pos_vector"][0] = self.vertices[vertex_id_aux]["pos_vector"][0]+1
            if self.vertices[vertex_id_aux]["pos_vector"][1] >= 1:
                self.vertices[vertex_id_aux]["pos_vector"][1] = self.vertices[vertex_id_aux]["pos_vector"][1]-1
            elif self.vertices[vertex_id_aux]["pos_vector"][1] < 0:
                self.vertices[vertex_id_aux]["pos_vector"][1] = self.vertices[vertex_id_aux]["pos_vector"][1]+1
            pass

    """ 
    ====================================================================================================================================================================================================================================
    REVISAR
    no se calcula bien el tiempo de extincion
    ==================================================================================================================================================================================================================================== 
    """
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
                    if( aux >= 0 and aux <= (2*self.delta_t) ):
                        self.borders[i]["ext"] = 1
                        self.ext_borders[cont_ext_borders]["id"] = self.borders[i]["id"]
                        self.ext_borders[cont_ext_borders]["t_ext"] = self.borders[i]["t_ext"]
                        self.ext_borders[cont_ext_borders]["diff_t_ext"] = self.delta_t
                        cont_ext_borders += 1
        self.cont_ext_borders = cont_ext_borders
    # REVISAR =================================================
                
    

        
        
    
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

        # set grains for each border
        """ for i in range(0, self.n_borders):
            xi = self.borders[i]["vertices"][0]
            xf = self.borders[i]["vertices"][1]
            gi = self.vertices[xi]["grains"]
            gf = self.vertices[xf]["grains"]
            cont = 0
            for j1 in range(0, 3):
                ind = False
                for j2 in range(0, 3):
                    if( self.vertices[xi]["grains"][j1]!= -1 and self.vertices[xi]["grains"][j1] == self.vertices[xf]["grains"][j2] ):
                        ind = True
                if ind:
                    self.borders[i]["grains"][cont] = self.vertices[xi]["grains"][j1]
                    cont+=1 """
    
    
    def calculate_cant_vertices_in_grains(self):
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


    """ ================== SAVE STATE FUNCTIONS ============================================================================== """
    def save_actual_state(self):  
        #self.save_general_t_state()
        self.save_vertices()
        self.save_borders()
        self.save_grains()

    def save_general_t_state(self):
        tipo = "a"
        if(self.actual_iter == 0):
            tipo = 'w+'
        
        folder = "out"
        file_name = f"{folder}/general.npy"
        with open(file_name, tipo) as f:
            start_line = f"{self.actual_iter}\n"
            f.write(start_line) 

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

    def save_grains(self):
        folder = "out"
        vertex_folder = f"{folder}/grains"
        file_name = f"{vertex_folder}/{self.actual_iter}.npy"
        with open(file_name, 'wb+') as f:
            np.save(f, self.grains)