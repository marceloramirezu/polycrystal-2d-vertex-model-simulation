import os
import json
import numpy as np 


def delete_old_files():
    path = "out/"
              
    for file_name in os.listdir(path):        
        file = path + file_name                
        if os.path.isfile(file):            
            os.remove(file)
        else:
            for file_name2 in os.listdir(file):        
                file2 = file +"/" +  file_name2      
                if os.path.isfile(file2):  
                    os.remove(file2)
                            
            path3 = file+"/vertices/"
            for file_name3 in os.listdir(path3):        
                file3 = path3 + file_name3       
                if os.path.isfile(file3):            
                    os.remove(file3)
            path4 = file+"/borders/"
            for file_name3 in os.listdir(path4):        
                file3 = path4 + file_name3        
                if os.path.isfile(file3):            
                    os.remove(file3)
            path5 = file+"/grains/"
            for file_name3 in os.listdir(path5):        
                file3 = path5 + file_name3        
                if os.path.isfile(file3):            
                    os.remove(file3)
            os.rmdir(path3)
            os.rmdir(path4)
            os.rmdir(path5)        
            os.rmdir(file)   

def delete_simulation(sim_name):
    sim_path = f"out/{sim_name}"
    for file_name2 in os.listdir(sim_path):        
        file2 = sim_path +"/" +  file_name2      
        if os.path.isfile(file2):  
            os.remove(file2)
    
    path3 = sim_path+"/vertices/"
    for file_name3 in os.listdir(path3):        
        file3 = path3 + file_name3       
        if os.path.isfile(file3):            
            os.remove(file3)
    os.rmdir(path3)
        
    path4 = sim_path+"/borders/"
    for file_name3 in os.listdir(path4):        
        file3 = path4 + file_name3        
        if os.path.isfile(file3):            
            os.remove(file3)
    os.rmdir(path4)

    path5 = sim_path+"/grains/"
    for file_name3 in os.listdir(path5):        
        file3 = path5 + file_name3        
        if os.path.isfile(file3):            
            os.remove(file3)
    os.rmdir(path5)        
    
    os.rmdir(sim_path) 

def create_folders(out_folder):
    os.mkdir(f"out/{out_folder}")
    os.mkdir(f"out/{out_folder}/grains")
    os.mkdir(f"out/{out_folder}/borders")
    os.mkdir(f"out/{out_folder}/vertices")
    
def save_options(out_folder, options):
    with open(f"out/{out_folder}/options.json", "w") as write_file:
        json.dump(options, write_file, indent=4)

def save_simulation_name(out_folder):
    with open(f"out/simulations.txt", "a+") as f:
        f.write(f"\n{out_folder}")
        
def save_simulation_time(ext_time, max_timestep):
    with open(f"out/simulations.txt", "a+") as f:
        f.write(f" ext_time:{ext_time}s max_timestep:{max_timestep}")



