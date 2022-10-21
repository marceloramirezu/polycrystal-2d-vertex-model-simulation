
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
    

    # guarda tiempo de ejecucion actual
    st = time.time()


    # 1.- calcular cantidad de vertices en cada grano
    vxm.update_cant_vertices_in_grains()     

    # ciclo principal
    vxm.calculate_len_and_energy_vertices()     
    vxm.calculate_vel_vertices()                
    vxm.calculate_t_ext()                       
    vxm.ordenar_ext_borders()   
    vxm.calculate_grain_position()
    # guardar estado inicial (t=0)
    vxm.save_actual_state()
    max_t = OPTIONS_VERTEX_MODEL["MAX_ITER"]
    actual_per = 0
    while (vxm.actual_iter <= max_t):
        if(vxm.actual_iter % (OPTIONS_VERTEX_MODEL["MAX_ITER"]/100) ==0):
            print(f"Simulado: {actual_per}%, ITER: {vxm.actual_iter}")
            actual_per+=1
                
        # 2.- calcular vectores tangentes, largos de arco y energias
        vxm.calculate_len_and_energy_vertices()     
        
        # 3.- calcular velocidad de los vertices a partir del vector tangente
        vxm.calculate_vel_vertices()                

        # 4.- calcular tiempos de extincion para cada borde
        vxm.calculate_t_ext()                       

        # 5.- obtener bordes que se extinguen dentro del intervalo actual
        vxm.ordenar_ext_borders()  
             
        # 6.- actualiza posición de vertices (actualiza vertices asociados a bordes que se extinguen en la iteracion actual por separado)
        vxm.update_position_vertices()           

        vxm.calculate_grain_position()

        # 7.- actualiza iteracion y tiempo actual   
        vxm.next_iteration()               
                               
        # 8.- guarda estado actual 
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
