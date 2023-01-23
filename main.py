
from utils.vertex_model import vertex_model
from options_simulation import OPTIONS
from utils.voronoi.voronoi import generate_voronoi
import time
from datetime import datetime, timezone;

from utils.file_functions import create_folders, save_options, save_simulation_name, save_simulation_time, delete_simulation;

def main():    
    actual_per = 0
    l_errors = []
    # Nombre de simulacion
    MIN_GRAINS = OPTIONS["OPTIONS_VERTEX_MODEL"]["MIN_GRAINS"]
    MAX_TIMESTEP = OPTIONS["OPTIONS_VERTEX_MODEL"]["MAX_TIMESTEP"]
    INITIAL_N_GRAINS = OPTIONS["OPTIONS_VERTEX_MODEL"]["INITIAL_N_GRAINS"]
    ct_utc = datetime.now(timezone.utc)
    ct_utc_str =ct_utc.strftime("%m-%d-%Y_%Hh%Mm%Ss")
    out_folder = f"out_N{INITIAL_N_GRAINS}_t{MAX_TIMESTEP}_{ct_utc_str}"

    create_folders(out_folder)
    save_options(out_folder, OPTIONS)
    save_simulation_name(out_folder)

    
    try:
        if(OPTIONS["OPTIONS_VORONOI"]["GENERATE_VORONOI"]):
            print(f"Generating initial structure (with voronoi)\n")
            seed_voronoi = OPTIONS["OPTIONS_VORONOI"]["SEED_VORONOI"]
            dist_voronoi = OPTIONS["OPTIONS_VORONOI"]["DIST_VORONOI"]
            generate_voronoi(INITIAL_N_GRAINS, seed_voronoi, dist_voronoi)

        
        print("START VERTEX MODEL")
        vxm = vertex_model(OPTIONS["OPTIONS_VERTEX_MODEL"], out_folder)
        vxm.read_initial_structure_voronoi()
        

        # start execution time
        start_execution_time = time.time()


        
        print(f"MAX_TIMESTEP: {MAX_TIMESTEP}")
        while ((vxm.ACTUAL_TIMESTEP < MAX_TIMESTEP) and ((vxm.N_GRAINS > MIN_GRAINS))):
    
            
            if( (vxm.ACTUAL_TIMESTEP % OPTIONS["OPTIONS_VERTEX_MODEL"]["ITERS_BETWEEN_PRINTS"] == 0) ):           
                vxm.save_actual_state()

            if(vxm.ACTUAL_TIMESTEP % (MAX_TIMESTEP/100) ==0): # imprime porcentaje de simulacion
                print(f"Max timestep Progress: {actual_per}%,\tactual timestep: {vxm.ACTUAL_TIMESTEP},\tN° Grains:{vxm.N_GRAINS}")
                actual_per+=1
        
            
            vxm.calculate_arclen_and_energy_all_borders()     
            vxm.calculate_grains_areas()
            
            vxm.calculate_vel_vertices()                
    
            vxm.calculate_t_ext(vxm.DELTA_T)                       

            vxm.ordenar_ext_borders()  
                
            vxm.update_position_vertices_ext_borders()    # advance_ext_borders_to_t_ext       
            vxm.update_position_vertices()       # advance_normal_vertices_to_delta_t     
            vxm.final_update_position_vertices_ext_borders()     # advance_ext_borders_to_delta_t      

            vxm.calculate_grain_position() 
            
            vxm.count_number_of_components()

            
            if(OPTIONS["OPTIONS_VERTEX_MODEL"]["TEST"]):
                l_errors_aux = vxm.test_structure()
                if(len(l_errors_aux) > 0):
                    exit()
                l_errors.append(l_errors_aux)
            
            vxm.next_iteration()    
            
        if( (vxm.ACTUAL_TIMESTEP % OPTIONS["OPTIONS_VERTEX_MODEL"]["ITERS_BETWEEN_PRINTS"] == 0) ):      
                print(f"Max timestep Progress: {actual_per}%\tactual timestep: {vxm.ACTUAL_TIMESTEP}\tN° Grains:{vxm.N_GRAINS}")
                vxm.save_actual_state()
        # END WHILE

        vxm.save_general_state_all_time()
        et = time.time()
        elapsed_time = et - start_execution_time
        print(f"Final timestep: {vxm.last_timestep_saved}\n")
        print('Execution time:', elapsed_time, 'seconds')
        save_simulation_time(elapsed_time, (vxm.last_timestep_saved))
        
        if(OPTIONS["OPTIONS_VERTEX_MODEL"]["TEST"]):
            print(f"\n\n# Structure errors: {len(l_errors)}\nerrors:")
            print(l_errors)
            
        print(f"\nSIMULATION SAVE IN {out_folder}")
    except Exception as e: 
        print(f"\nERROR IN SIMULATION")
        print(e)
        print(f"Deleting files...")
        delete_simulation(out_folder)



if __name__ == '__main__':
    main()
