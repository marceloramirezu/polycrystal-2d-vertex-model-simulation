import numpy as np;
# (id, pos_vector, vel_vector, borders, energy, not_enabled)
# (id, (x, y), (vx, vy), (b1, b2, b3), energy, not_enabled))
# borders: contiene los indices de los bordes guardados en self.borders
dt_vertex = np.dtype([
    ('id', np.uint), 
    ('pos_vector', np.longdouble, (2,)), 
    ('vel_vector', np.longdouble, (2,)), 
    ('borders', np.uint, (3,)), 
    ('grains', np.int, (3,)), 
    ('grains_angle', np.longdouble, (3,)), 
    ('energy', np.longdouble), 
    ('not_enabled', np.bool_),
    ('ext_border', np.bool_), # FALTA IMPLEMENTAR, permite caclular posicion de vertices asociados a bordes o granos que colapsan por separado
    ('advanced_t', np.longdouble), # (FALTA IMPLEMENTAR) si el borde no se extingue en la iteracion actual, siempre sera 0
                                   # si el borde se extingue en la iteracion actual, sera el tiempo que avanza antes de llegar a actual_t + delta_t
                                   # usado para ver cuanto tiempo tienen que avanzar los bordes que se extinguen para llegar a actual_t + delta_t luego de haber avanzado localmente dentro del intervalo de tiempo de la iteracion actual      
])
# (id, vertices, diff_vector, gamma, arc_len, energy, not_enabled)
# (id, (x, y), (diff_x, diff_y), gamma, arc_len, energy, not_enabled))
# vertices: contiene los indices de los vertices guardados en self.vertices
dt_border = np.dtype([
    ('id', np.uint), 
    ('vertices', np.uint, (2,)),
    ('tangent_vector', np.longdouble, (2,)), 
    ('diff_vector', np.longdouble, (2,)), 
    ('gamma', np.longdouble), 
    ('energy', np.longdouble), 
    ('arc_len', np.longdouble), 
    ('t_ext', np.longdouble), 
    ('ext', np.int_),
    ('not_enabled', np.bool_), 
])

# (id, alpha, vertices)
# (id, alpha, (x0, x1, ...,xn))
# vertices: contiene los indices de los vertices guardados en self.vertices
dt_grain = np.dtype([
    ('id', np.uint), 
    ('alpha', np.longdouble), 
    ('pos_vector', np.longdouble, (2,)), 
    ('vertices', np.int, (50,)),
    ('n_vertices', np.uint), 
    ('3_sided', np.int), 
    ('not_enabled', np.bool_), 
    ('x_wrap', np.bool_), 
    ('y_wrap', np.bool_), 
])

dt_ext_border = np.dtype([
    ('id', np.uint), 
    ('t_ext', np.longdouble),
    ('diff_t_ext', np.longdouble),
])


dt_general = np.dtype([
    ('t', np.longdouble), 
    ('iter', np.longdouble), 
    ('n_vertices', np.uint),
    ('n_borders', np.uint),
    ('n_grains', np.uint),
    ('energy', np.longdouble),
    ('flip', np.bool_),
    ('remove', np.bool_),
    ('error', np.bool_),
])