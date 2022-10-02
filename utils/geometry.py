import math 
import numpy as np


def mag_vector(x, y):
    p = max(abs(x), abs(y))
    if(p == 0):
        return 0
    q = min(abs(x), abs(y))
    return p * math.sqrt(1.0 + (q/p)*(q/p))
    #return math.sqrt((x*x)+(y*y))


def wrap_distances(vi, vf):
    xi = vi[0]
    yi = vi[1]
    xf = vf[0]
    yf = vf[1]
    dist_x = np.absolute(xf-xi)
    dist_y = np.absolute(yf-yi)
    x_dist_wrap = dist_x > 0.5
    y_dist_wrap = dist_y > 0.5
    wrap = False

    if(x_dist_wrap and xi <= 0.5):
        xf = xf-1
        wrap = True
    elif(x_dist_wrap and xi > 0.5):
        xf = xf+1
        wrap = True
    else:
        pass

    if(y_dist_wrap and yi <= 0.5):
        yf = yf-1
        wrap = True
    elif(y_dist_wrap and yi > 0.5):
        yf = yf+1
        wrap = True
    else:
        pass
    
    delta_x= (xf-xi)
    delta_y= (yf-yi)
    arc_len = mag_vector(delta_x, delta_y)
    x_u = 0
    y_u = 0
    if(arc_len != 0):
        angle = math.atan2(delta_y, delta_x)
        x_u = math.cos(angle)
        y_u = math.sin(angle)
    
    dict_return = {
        "xi":[xi,yi],
        "xf":[xf,yf],
        "wrap":wrap,
        "delta_x": delta_x,
        "delta_y": delta_y,
        "x_u": (x_u),
        "y_u": (y_u),
        "arc_len":arc_len
    }
    return dict_return


# angle in radians
def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy