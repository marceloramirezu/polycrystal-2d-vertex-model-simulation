""" 
------------------------------------------------------------------------------------------------
SIMULATION OPTIONS
------------------------------------------------------------------------------------------------
"""

# 1.- VORONOI ----------------------------------------------------------------------------------
GENERATE_VORONOI=True
SEED_VORONOI=12           # voronoi seed
DIST_VORONOI=-1
VORONOI_OUT_FOLDER="utils/voronoi/salida"


# 2.- SIMULATION OPTIONS ----------------------------------------------------------------------
TEST = False              # test structure 
ITERS_BETWEEN_PRINTS =  5 # timesteps between saves
MAX_ITER = 10000           # max timesteps
INITIAL_N = 1000          # number of grains
MIN_GRAINS = 50           # min number of grains
GAMMA_0 = 1 
DELTA_T = 1e-4  
SAVE_STRUCTURE=False


""" ------------------------------------------------------------------------------------------------
VISUALIZATION OPTIONS
------------------------------------------------------------------------------------------------ """
# 3.- PYGAME AND COLORS
FPS = 60
FPS_X2 = 60
RESOLUTION = 800
RESOLUTION_X = 800
RESOLUTION_Y = 800
TICKS_WAIT_INPUT = 30
COLOR_ALPHA = (100, 100, 100)
COLOR_ALPHA_3_SIDED = (255, 0, 0)
COLOR_VERTEX = (150, 150, 150)
COLOR_VERTEX_1 = (250, 10, 10)
COLOR_BORDER_0 = (80, 80, 80)
COLOR_BORDER_1 = (250, 0, 250)
COLOR_VEL_VERTEX = (255, 255, 255)
BACKGROUND_COLOR = (10,10,10)

# 4.- SIZES
VERTEX_SIZE = 4
VERTEX_VEL_SIZE = 4
ALPHA_SIZE= 4
ALPHA_LEN= 10
VERTEX_VEL_MULT = DELTA_T*10
BORDER_SIZE= 5
FONT_SIZE_GRAIN = 12
FONT_SIZE_BORDER = FONT_SIZE_GRAIN
FONT_SIZE_VERTEX = FONT_SIZE_GRAIN


# 5.- STATS
FIGURE_FOLDER = "figures"



""" ============================================================== DICTIONARIES ============================================================== """
OPTIONS_VORONOI = {
    "GENERATE_VORONOI": GENERATE_VORONOI,
    "SEED_VORONOI": SEED_VORONOI,
    "DIST_VORONOI": DIST_VORONOI,
    "VORONOI_OUT_FOLDER": VORONOI_OUT_FOLDER
}
# MOV_VERTEX = 1 # vertex movility # not used 
# GRAND_EPS = 1e-8 # not used 
OPTIONS_VERTEX_MODEL = {
    "TEST": TEST,
    "ITERS_BETWEEN_PRINTS": ITERS_BETWEEN_PRINTS,
    "MAX_ITER": MAX_ITER,
    "MIN_GRAINS": MIN_GRAINS,
    "GAMMA_0": GAMMA_0,
    "INITIAL_N": INITIAL_N,
    "DELTA_T": DELTA_T,
    "VORONOI_OUT_FOLDER": VORONOI_OUT_FOLDER,
    "SAVE_STRUCTURE":SAVE_STRUCTURE
    #"MOV_VERTEX": MOV_VERTEX,
    #"GRAND_EPS": GRAND_EPS,
}
OPTIONS_SHOW = {
    "RESOLUTION": RESOLUTION,
    "RESOLUTION_X": RESOLUTION_X,
    "RESOLUTION_Y": RESOLUTION_Y,
    "FPS": FPS,
    "FPS_X2": FPS_X2,
    "TICKS_WAIT_INPUT":TICKS_WAIT_INPUT,
}
OPTIONS_SHOW_COLOR = {
    "COLOR_VERTEX":COLOR_VERTEX,
    "COLOR_VERTEX_1":COLOR_VERTEX_1,
    "COLOR_BORDER_0":COLOR_BORDER_0,
    "COLOR_BORDER_1": COLOR_BORDER_1,
    "COLOR_VEL_VERTEX":COLOR_VEL_VERTEX,
    "BACKGROUND_COLOR":BACKGROUND_COLOR,
    "ALPHA": COLOR_ALPHA,
    "ALPHA_3_SIDED": COLOR_ALPHA_3_SIDED,
    "WHITE": (255, 255, 255),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 128),
    "GRAIN_TEXT": (255, 0, 0),
    "GRAIN_BACK": (0, 0, 0),
    "BORDER_TEXT": (0, 0, 128),
    "BORDER_BACK": (0, 255, 0),
    "VERTEX_TEXT": (255, 255, 255),
    "VERTEX_BACK": (0, 0, 0),
    "TEXT": (255, 255, 255),
    "BACK_TEXT": (0, 0, 0),
}
OPTIONS_SHOW_TAM = {
    "VERTEX_SIZE": VERTEX_SIZE,
    "VERTEX_VEL_SIZE": VERTEX_VEL_SIZE,
    "ALPHA_SIZE":ALPHA_SIZE,
    "ALPHA_LEN":ALPHA_LEN,
    "VERTEX_VEL_MULT": VERTEX_VEL_MULT,
    "BORDER_SIZE": BORDER_SIZE,
    "FONT_SIZE_GRAIN": FONT_SIZE_GRAIN,
    "FONT_SIZE_BORDER": FONT_SIZE_BORDER,
    "FONT_SIZE_VERTEX": FONT_SIZE_VERTEX,
}