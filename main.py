
from utils.vertex_model import vertex_model
from options import OPTIONS_VERTEX_MODEL, OPTIONS_VORONOI
from utils.voronoi.voronoi import generate_voronoi
import os
import time



def delete_old_files():
    path = "out/borders/"
    for file_name in os.listdir(path):        
        file = path + file_name                
        if os.path.isfile(file):            
            os.remove(file)
    path = "out/vertices/"
    for file_name in os.listdir(path):        
        file = path + file_name        
        if os.path.isfile(file):            
            os.remove(file)
    path = "out/grains/"
    for file_name in os.listdir(path):        
        file = path + file_name        
        if os.path.isfile(file):            
            os.remove(file)
    file = "out/general.txt"    
    if os.path.isfile(file):        
        os.remove(file)


def main():    
    # elimina archivos antiguos
    delete_old_files()    

    # generar estructura inicial con algoritmo voronoi
    if(OPTIONS_VORONOI["GENERATE_VORONOI"]):
        print(f"GENERATE_VORONOI")
        generate_voronoi(OPTIONS_VERTEX_MODEL["INITIAL_N"], OPTIONS_VORONOI["SEED_VORONOI"], OPTIONS_VORONOI["DIST_VORONOI"])

    # iniciar vertices, bordes y granos con estructura generada con algoritmo voronoi
    print(f"\nSTART VERTEX MODEL")
    vxm = vertex_model(OPTIONS_VERTEX_MODEL)
    
    # guardar estado inicial (t=0)
    vxm.save_actual_state()

    # guarda tiempo de ejecucion actual
    st = time.time()


    # ciclo principal
    max_t = OPTIONS_VERTEX_MODEL["MAX_ITER"]
    while (vxm.actual_iter <= max_t):
        if(vxm.actual_iter%100==0):
            print(f"ITER: {vxm.actual_iter}")
        
        # 1.- calcular cantidad de vertices en cada grano
        vxm.calculate_cant_vertices_in_grains()     
        
        # 2.- calcular vectores tangentes, largos de arco y energias
        vxm.calculate_len_and_energy_vertices()     
        
        # 3.- calcular velocidad de los vertices a partir del vector tangente
        vxm.calculate_vel_vertices()                

        # 4.- calcular tiempos de extincion para cada borde
        # genera arreglo con bordes que se extinguen en la iteracion actual
        # genera arreglo con vertices asociados a los bordes que se extinguen en la iteracion ac
        vxm.calculate_t_ext()                       

        # 5.- obtener bordes que se extinguen dentro del intervalo actual
        vxm.ordenar_ext_borders()  
        
        if(vxm.cont_ext_borders == 0):
            vxm.update_position_vertices()              
            vxm.next_iteration()                        
        else:
            # por cada borde
            for c in range(0, vxm.cont_ext_borders):           
                vxm.advance_ext_border(c)         
                # avanzar localmente los vertices asociados a los bordes que se extinguen hasta actual_t + t_ext
                # realizar transicion topologica localmente
            vxm.update_position_vertices()              
            vxm.next_iteration()               
                               
        # guardar estado actual 
        if(vxm.actual_iter % OPTIONS_VERTEX_MODEL["ITERS_BETWEEN_PRINTS"] == 0):
            vxm.save_actual_state()
    
    # fin ciclo principal
    # obtener tiempo de ejecucion
    et = time.time()
    elapsed_time = et - st
    print(f"FIN ITER: {vxm.actual_iter-1}\n")
    print('Execution time:', elapsed_time, 'seconds')

        
if __name__ == '__main__':
    main()

""" 
P1
    iter: 1407
    delta_t: 0.0001
    grand_eps: 1e-9
    vertices:
        id |            x        |         y           |          vx          |         vy          | b1 | b2 | b3  
        75 | 0.08348524345324795 | 0.4026821867776551  | 0.3304459066132744   | 0.1722722300505656  | 4  | 32 | 2
        76 | 0.08349734234186193 | 0.40269980430334473 | 0.018317460720972123 | -0.2824418466305673 | 11 | 2  | 41
    bordes:
        id: 2 
        vi: 75 
        vf: 76 
        arc: 7.652528827313167e-05 
        t_ext: 0.00014868415993071546 10

"""