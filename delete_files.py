import os

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
    
delete_old_files()