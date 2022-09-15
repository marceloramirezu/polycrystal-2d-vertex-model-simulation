import numpy as np;
from utils.geometry import *
import math

class vertex_model:
    gamma_0= 0
    mov_vertex= 0
    n_grains = 0
    n_borders = 0
    n_vertices = 0
    mov_vertex = 0
    t = 0
    vertices = []
    borders = []
    grains = []
    voronoi_folder = ""
    
    def __init__(self, OPTIONS_VERTEX_MODEL):
        self.voronoi_folder = OPTIONS_VERTEX_MODEL["VORONOI_OUT_FOLDER"]
        self.gamma_0 = OPTIONS_VERTEX_MODEL["GAMMA_0"]
        self.mov_vertex = OPTIONS_VERTEX_MODEL["MOV_VERTEX"]
        self.n_grains = OPTIONS_VERTEX_MODEL["INITIAL_N"]
        self.n_borders = OPTIONS_VERTEX_MODEL["INITIAL_N"]*3
        self.n_vertices = OPTIONS_VERTEX_MODEL["INITIAL_N"]*2
        self.delta_t = OPTIONS_VERTEX_MODEL["DELTA_T"]
        self.grad_eps = OPTIONS_VERTEX_MODEL["GRAND_EPS"]
        # (id, pos_vector, vel_vector, borders, energy, enabled)
        # (id, (x, y), (vx, vy), (b1, b2, b3), energy, enabled))
        # borders: contiene los indices de los bordes guardados en self.borders
        dt_vertex = np.dtype([('id', np.uint), ('pos_vector', np.float64, (2,)), ('vel_vector', np.float64, (2,)), ('borders', np.uint, (3,)), ('energy', np.float64), ('enabled', np.bool_)])
        self.vertices = np.zeros(self.n_vertices, dtype=dt_vertex) 
        
        # (id, vertices, diff_vector, gamma, arc_len, energy, enabled)
        # (id, (x, y), (diff_x, diff_y), gamma, arc_len, energy, enabled))
        # vertices: contiene los indices de los vertices guardados en self.vertices
        dt_border = np.dtype([('id', np.uint), ('vertices', np.uint, (2,)), ('diff_vector', np.float64, (2,)), ('gamma', np.float64), ('arc_len', np.float64), ('energy', np.float64), ('enabled', np.bool_)])
        self.borders = np.zeros(self.n_borders, dtype=dt_border) 
        
        # (id, alpha, vertices)
        # (id, alpha, (x0, x1, ...,xn))
        # vertices: contiene los indices de los vertices guardados en self.vertices
        dt_grain = np.dtype([('id', np.uint), ('alpha', np.float64), ('vertices', np.uint, (50,))])
        self.grains = np.zeros(self.n_grains, dtype=dt_grain) # (id, alpha, x1, x2, x3, ..., x50)
        self.t = 0
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

        # GRAINS ---------------------------- FALTA! ----------------------------
        considerated = np.full(self.n_vertices*3, False)
        id_grain = 0
        for j in range(0, self.n_vertices):
            #print(f"\nvertice(j) = {j}")
            start_vrt = j
            if(not self.vertices[start_vrt]["enabled"]) :
                for g in range(0, 3):
                    #print(f"\tlado(g) = {g}")
                    if(not considerated[j*3 + g]):
                        current_vrt = start_vrt
                        current_side = g
                        #print(f"\t\tid_grain = {id_grain}")
                        while (True):
                            
                            current_vrt = current_vrt
                            #print(f"\t\t\tcurrent_vrt = {current_vrt}")
                            #print(f"\t\t\tcurrent_side = {current_side}")
                            if(considerated[(current_vrt * 3) + current_side] or self.vertices[current_vrt]["enabled"]) :
                                #print("Illegal grains were detected!\n")
                                exit(1)
                            
                            considerated[(current_vrt * 3) + current_side] = True
                            for i in range(0, 50): # agrega vertice a grano
                                if(self.grains[id_grain]["vertices"][i] == 0):
                                    self.grains[id_grain]["vertices"][i] = current_vrt      
                                    #print(f"\t\t\tNEW VERTEX TO GRAIN  id_grain:{id_grain} current_vrt:{current_vrt}")     
                                    break             
                            bnd = self.vertices[current_vrt]["borders"][current_side]
                            bnd_aux = self.borders[self.vertices[current_vrt]["borders"][current_side]]["vertices"]
                            new_current_vrt = 0
                            if(bnd_aux[0] == current_vrt):
                                new_current_vrt = bnd_aux[1]
                            else:
                                new_current_vrt = bnd_aux[0]
                            #print(f"\t\t\tnew_current_vrt = {new_current_vrt}")
                            
                            i = -1
                            for i_aux in range(0, 3):
                                i = i_aux
                                if(self.vertices[new_current_vrt]["borders"][i] == bnd):
                                    #print(f"\t\t\t\t\t\t\ti_aux:{i_aux}")
                                    break
                            
                            if(i == -1):
                                #print(f"ERROR")
                                exit()
                            current_vrt = new_current_vrt
                            current_side = (i+1) % 3
                            if (current_vrt == start_vrt):
                                #print(f"\t\t\t\tbreak")
                                break
                        self.grains[id_grain]["id"] = id_grain
                        id_grain +=1
                    else:
                        #print(f"\t\tCONSIDERADO = {start_vrt}")
                        pass

                        
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
        #archivo = "orientations"
        #file1 = open(f'{self.voronoi_folder}/{archivo}.txt', 'r')
        #Lines = file1.readlines()
        #for line in Lines:
        #    orientation = float(line)
        #    self.orientations.append( orientation )
            
        
    def next_iteration(self):
        self.t = self.t+1

    def calculate_len_and_energy_vertices(self):      
        #print("\t1.- calculating arc lengths of borders and energy of vertices")  
        with np.nditer(self.borders, op_flags=['readwrite']) as it:
            for border in it:
                xi_index = border["vertices"][0]
                xf_index = border["vertices"][1]
                border["arc_len"] = self.calculate_arc_len(xi_index, xf_index)

        with np.nditer(self.vertices, op_flags=['readwrite']) as it:
            for vertex in it:
                borders = vertex["borders"]
                energy = 0.0
                for j in range(0,3):
                    border = self.borders[borders[j]]
                    # FALTA: calcular la energia de cada borde dependiendo del gamma_0 y los angulos de los granos asociados
                    energy += border["arc_len"]*border["energy"]*0.5
                vertex["energy"] = energy

    def calculate_arc_len(self, xi_index, xf_index):
        xi = self.vertices[xi_index]
        xf = self.vertices[xf_index]
        t_wrap = wrap_distances( xf["pos_vector"],  xi["pos_vector"] )
        return t_wrap["arc_len"]


    def calculate_vel_vertices(self):
        with np.nditer(self.vertices, op_flags=['readwrite']) as it:
            for vertex in it:
                if(not vertex["enabled"]):
                    new_vel_x = self.energy_diff(0, vertex)
                    new_vel_y = self.energy_diff(1, vertex)
                    vertex["vel_vector"][0] = new_vel_x
                    vertex["vel_vector"][1] = new_vel_y         
                
                        
        
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
    
    def polling_system(self):
        pass    
    def remove_3_sided_vertices(self):
        pass
    def aply_flips_vertices(self):
        pass    

    def update_position_vertices(self):
        # lo probe dentro de la funcion que calcula las nuevas posiciones y va mas lento, lo deje comentado en la parte de arriba. Se demora 44,7 segundos sin el cambio y 45,1 segundos con el cambio para 100 iteraciones de 1000 granos
        self.vertices[...]["pos_vector"] = self.vertices[...]["pos_vector"] + self.vertices[...]["vel_vector"]*self.delta_t
        return 0
        with np.nditer(self.vertices, op_flags=['readwrite']) as it:
            for vertex in it:
                velx = vertex["vel_vector"][0]
                vely = vertex["vel_vector"][1]
                if(not vertex["enabled"]):
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
                
        
        

    def save_actual_state(self):  
        self.save_general_t_state()
        self.save_vertices()
        self.save_borders()
        self.save_grains()

    def save_general_t_state(self):
        tipo = "a"
        if(self.t == 0):
            tipo = 'w+'
        
        folder = "out"
        file_name = f"{folder}/general.txt"
        with open(file_name, tipo) as f:
            start_line = f"{self.t}\n"
            f.write(start_line) 

    def save_vertices(self):
        #print(f"\tprinting vertices t={self.t}")
        folder = "out"
        vertex_folder = f"{folder}/vertices"
        file_name = f"{vertex_folder}/{self.t}.txt"
        with open(file_name, 'w+') as f:
            start_line = f"{self.t}\n"
            f.write(start_line) 
            for vertex in np.nditer(self.vertices, order='C'):
                id = vertex["id"]
                x = vertex["pos_vector"][0]
                y = vertex["pos_vector"][1]
                velx = vertex["vel_vector"][0]
                vely = vertex["vel_vector"][1]
                b1 = vertex["borders"][0]
                b2 = vertex["borders"][1]
                b3 = vertex["borders"][2]
                line = f"{id} {x} {y} {velx} {vely} {b1} {b2} {b3}\n"
                f.write(line) 
 
    def save_borders(self):
        #print(f"\tprinting borders t={self.t}")
        folder = "out"
        vertex_folder = f"{folder}/borders"
        file_name = f"{vertex_folder}/{self.t}.txt"
        with open(file_name, 'w+') as f:
            start_line = f"{self.t}\n"
            f.write(start_line) 
            for border in np.nditer(self.borders, order='C'):
                id = border["id"]
                xi = border["vertices"][0]
                xf = border["vertices"][1]
                arc_len = border["arc_len"]
                
                line = f"{id} {xi} {xf} {arc_len}\n"
                f.write(line) 

    def save_grains(self):
        #print(f"\tprinting borders t={self.t}")
        folder = "out"
        vertex_folder = f"{folder}/grains"
        file_name = f"{vertex_folder}/{self.t}.txt"
        with open(file_name, 'w+') as f:
            start_line = f"{self.t}\n"
            f.write(start_line) 
            for grain in np.nditer(self.grains, order='C'):
                id = grain["id"]
                angle = grain["alpha"]
                l_v = ""
                cont = 0
                for i in range(0,50):
                    v = grain["vertices"][i]
                    if(v!=0):
                        cont+=1
                        l_v = f"{l_v} {v}"
                
                line = f"{id} {angle}{l_v}\n"
                f.write(line) 