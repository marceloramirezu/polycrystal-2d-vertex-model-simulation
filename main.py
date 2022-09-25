
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
    delete_old_files()    
    if(OPTIONS_VORONOI["GENERATE_VORONOI"]):
        print(f"GENERATE_VORONOI")
        generate_voronoi(OPTIONS_VERTEX_MODEL["INITIAL_N"], OPTIONS_VORONOI["SEED_VORONOI"], OPTIONS_VORONOI["DIST_VORONOI"])


    print(f"\nSTART VERTEX MODEL")
    vxm = vertex_model(OPTIONS_VERTEX_MODEL)
    
    vxm.save_actual_state()


    # get the start time
    st = time.time()

    max_t = OPTIONS_VERTEX_MODEL["MAX_ITER"]
    while (vxm.actual_iter <= max_t):
        if(vxm.actual_iter%100==0):
            print(f"ITER: {vxm.actual_iter}")
        
        vxm.calculate_len_and_energy_vertices()     # 1.- calcula arc len y energias
        vxm.calculate_vel_vertices()                # 2.- calcula la velocidad de los vertices a partir del vector tangente
        
        vxm.calculate_t_ext()                       # 3.- revisa que vertices y bordes se pueden actualizar en esta iteracion y cuales tienen que esperar a la siguiente
        vxm.order_borders_by_t_ext()  
        #vxm.polling_system()                       # 3.- revisa que vertices y bordes se pueden actualizar en esta iteracion y cuales tienen que esperar a la siguiente
        #vxm.remove_3_sided_grains()                # 4.- aplica transición topologica remove
        #vxm.aply_flips_vertices()                  # 5.- aplica transición topologica flip
        vxm.update_position_vertices()              # 6.- actualiza posicion de vertices

        vxm.next_iteration() # iter+=1; t = t+delta_t
        if(vxm.actual_iter % OPTIONS_VERTEX_MODEL["ITERS_BETWEEN_PRINTS"] == 0):
            vxm.save_actual_state()
    
    # get the end time
    et = time.time()
    # get the execution time
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