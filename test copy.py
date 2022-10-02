from random import randint
from tempfile import TemporaryFile

import math 
import numpy as np
from utils.datatypes import *

def iniciar_ext_borders():
    a = np.zeros(10, dtype=dt_ext_border)
    for i in range(0, 10):
        a[i]["id"] = randint(0, 1000)
        a[i]["t_ext"] = randint(0, 1000)
    return a
                
    
def ordenar_ext_borders(ext_borders):
    Tcopy=ext_borders[['id','t_ext']].copy()
    I=np.argsort(Tcopy,order=['t_ext'])
    return ext_borders[I]

ext_borders = iniciar_ext_borders()
print("INICIO")
print(ext_borders)
ext_borders = ordenar_ext_borders(ext_borders)
print("\nFIN")
print(ext_borders)