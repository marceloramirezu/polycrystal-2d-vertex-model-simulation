
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
    while (vxm.t <= max_t):
        if(vxm.t%100==0):
            print(f"ITER: {vxm.t}")
        
        vxm.calculate_len_and_energy_vertices()     # 1.- calcula arc len y energias
        vxm.calculate_vel_vertices()                # 2.- calcula la velocidad de los vertices a partir del vector tangente
        #vxm.polling_system()                       # 3.- revisa que vertices y bordes se pueden actualizar en esta iteracion y cuales tienen que esperar a la siguiente
        #vxm.remove_3_sided_vertices()              # 4.- aplica transición topologica remove
        #vxm.aply_flips_vertices()                  # 5.- aplica transición topologica flip
        vxm.update_position_vertices()              # 6.- actualiza posicion de vertices

        vxm.next_iteration() # iter+=1; t = t+delta_t
        vxm.save_actual_state()
    
    # get the end time
    et = time.time()
    # get the execution time
    elapsed_time = et - st
    print(f"FIN ITER: {vxm.t-1}\n")
    print('Execution time:', elapsed_time, 'seconds')

        
if __name__ == '__main__':
    main()
