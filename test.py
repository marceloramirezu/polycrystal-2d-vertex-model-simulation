from tempfile import TemporaryFile

import math 
import numpy as np

def mag_vector(x, y):
    p = max(abs(x), abs(y))
    if(p == 0):
        return 0
    q = min(abs(x), abs(y))
    return p * math.sqrt(1.0 + (q/p)*(q/p))

x=0.29953285587042366 
y=0.7530851792931553 
vx=0.385214817000365 
vy=0.05298158302871836 

xf=0.1861014109378206 
yf=0.7686030475753663 
vxf=0.019580292840491342 
vyf=-0.2469166782380249 


Tx = -0.9903555090179892 
Ty = 0.13854950652282974
arc = 0.11416689196847737

diff_x = xf-x
diff_y = yf-y
arc_len = mag_vector(diff_x, diff_y)
print(f"arc_len: {arc_len}")
print(f"arc:     {arc}")
x_u = 0
y_u = 0
if(arc_len != 0):
    angle = math.atan2(diff_y, diff_x)
    x_u = math.cos(angle)
    y_u = math.sin(angle)
print(f"x_u:     {x_u}")
print(f"Tx:      {Tx}")
print(f"y_u:     {y_u}")
print(f"Ty:      {Ty}")
print(f"normal tangente:      {math.sqrt((Tx*Tx) + (Ty*Ty))}")

