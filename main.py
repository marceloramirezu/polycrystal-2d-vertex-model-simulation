
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

    
    if not os.path.isdir("out/borders"):
        os.makedirs("out/borders")
    if not os.path.isdir("out/vertices"):
        os.makedirs("out/vertices")
    if not os.path.isdir("out/grains"):
        os.makedirs("out/grains")
    
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
    l_errors = []
    while (vxm.actual_iter <= max_t):
        if(vxm.actual_iter % (OPTIONS_VERTEX_MODEL["MAX_ITER"]/100) ==0):
            print(f"Simulado: {actual_per}%, ITER: {vxm.actual_iter}")
            actual_per+=1

        #if(vxm.actual_iter == 0):        
        vxm.calcular_area_granos()
        
        # 2.- calcular vectores tangentes, largos de arco y energias
        vxm.calculate_len_and_energy_vertices()     
        
        # 3.- calcular velocidad de los vertices a partir del vector tangente
        vxm.calculate_vel_vertices()                

        # 4.- calcular tiempos de extincion para cada borde
        vxm.calculate_t_ext()                       

        # 5.- obtener bordes que se extinguen dentro del intervalo actual
        vxm.ordenar_ext_borders()  
             
        # 6.- actualiza posici??n de vertices (actualiza vertices asociados a bordes que se extinguen en la iteracion actual por separado)
        vxm.update_position_vertices()           

        vxm.calculate_grain_position()

        # 7.- actualiza iteracion y tiempo actual   
        vxm.next_iteration()               
                               
        # 8.- guarda estado actual 
        if( (vxm.actual_iter % OPTIONS_VERTEX_MODEL["ITERS_BETWEEN_PRINTS"] == 0) ):           
            vxm.save_actual_state()
        
        if(OPTIONS_VERTEX_MODEL["TEST"]):
            l_errors_aux = vxm.test_structure()
            if(len(l_errors_aux) > 0):
                exit()
            l_errors.append(l_errors_aux)
    vxm.save_all_states()
    # fin ciclo principal
    # obtener tiempo de ejecucion
    et = time.time()
    elapsed_time = et - st
    print(f"FIN ITER: {vxm.actual_iter-1}\n")
    print('Execution time:', elapsed_time, 'seconds')
    
    if(OPTIONS_VERTEX_MODEL["TEST"]):
        print(f"\n\nERRORES EN ESTRUCTURA: {len(l_errors)}")
        print(l_errors)
        
if __name__ == '__main__':
    main()
