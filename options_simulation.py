""" 
------------------------------------------------------------------------------------------------
SIMULATION OPTIONS
------------------------------------------------------------------------------------------------
"""

# 1.- VORONOI ----------------------------------------------------------------------------------
GENERATE_VORONOI = True     # generate new structure, must be true if the initial number of grains change
SEED_VORONOI = 12           # voronoi seed
DIST_VORONOI = -1


# 2.- SIMULATION OPTIONS ----------------------------------------------------------------------
TEST = False                    # test structure 
ITERS_BETWEEN_PRINTS =  2       # timesteps between saves
MAX_TIMESTEP = 2000             # max timesteps
INITIAL_N_GRAINS = 300          # number of grains
MIN_GRAINS = 10                 # min number of grains
GAMMA_0 = 1                     # 
DELTA_T = 1e-4                  # lenght of timestep
SAVE_STRUCTURE=False            # True: save structure (grains, borders, vertices, general state), Flase: (general state)



""" ============================================================== DICTIONARIES ============================================================== """
OPTIONS_VORONOI = { # options for generation of initial state of structure with voronoi algorithm
    "GENERATE_VORONOI": GENERATE_VORONOI,
    "SEED_VORONOI": SEED_VORONOI,
    "DIST_VORONOI": DIST_VORONOI,
}

# MOV_VERTEX = 1 # vertex movility # not used 
OPTIONS_VERTEX_MODEL = { # options used in vertex model simulation
    "TEST": TEST,
    "ITERS_BETWEEN_PRINTS": ITERS_BETWEEN_PRINTS,
    "MAX_TIMESTEP": MAX_TIMESTEP,
    "MIN_GRAINS": MIN_GRAINS,
    "GAMMA_0": GAMMA_0,
    "INITIAL_N_GRAINS": INITIAL_N_GRAINS,
    "DELTA_T": DELTA_T,
    "SAVE_STRUCTURE":SAVE_STRUCTURE
    #"MOV_VERTEX": MOV_VERTEX,
}

OPTIONS = { # All options
    "OPTIONS_VORONOI": OPTIONS_VORONOI,
    "OPTIONS_VERTEX_MODEL": OPTIONS_VERTEX_MODEL,
}