# VORONOI
GENERATE_VORONOI=True
SEED_VORONOI=12
DIST_VORONOI=-1
VORONOI_OUT_FOLDER="utils/voronoi/salida"
OPTIONS_VORONOI = {
    "GENERATE_VORONOI": GENERATE_VORONOI,
    "SEED_VORONOI": SEED_VORONOI,
    "DIST_VORONOI": DIST_VORONOI,
    "VORONOI_OUT_FOLDER": VORONOI_OUT_FOLDER
}


# 30 fps * 10 seg = 300 iters
# VERTEX MODEL
# 3 min: 600 N, 1000 iters
# 50 seg 200 N, 1000 iters
# out_1: 1500, 200 iters
INITIAL_N= 100
ITERS_BETWEEN_PRINTS =  1
MAX_ITER = 1500
MIN_GRAINS = 50
GAMMA_0 = 1
MOV_VERTEX = 1
DELTA_T = 1e-4   # 0.1 ms
GRAND_EPS = 1e-8 # 10 nm
OPTIONS_VERTEX_MODEL = {
    "ITERS_BETWEEN_PRINTS": ITERS_BETWEEN_PRINTS,
    "MAX_ITER": MAX_ITER,
    "MIN_GRAINS": MIN_GRAINS,
    "GAMMA_0": GAMMA_0,
    "MOV_VERTEX": MOV_VERTEX,
    "INITIAL_N": INITIAL_N,
    "DELTA_T": DELTA_T,
    "GRAND_EPS": GRAND_EPS,
    "VORONOI_OUT_FOLDER": VORONOI_OUT_FOLDER
}


# PYGAME AND COLORS
FPS = 30

RESOLUTION = 800
RESOLUTION_X = 800
RESOLUTION_Y = 800

TICKS_WAIT_INPUT = 5

COLOR_ALPHA = (100, 100, 100)
COLOR_ALPHA_3_SIDED = (255, 0, 0)
COLOR_VERTEX = (150, 150, 150)
COLOR_VERTEX_1 = (250, 10, 10)
COLOR_BORDER_0 = (80, 80, 80)
COLOR_BORDER_1 = (250, 0, 250)
COLOR_VEL_VERTEX = (255, 255, 255)
BACKGROUND_COLOR = (10,10,10)
OPTIONS_SHOW = {
    "RESOLUTION": RESOLUTION,
    "RESOLUTION_X": RESOLUTION_X,
    "RESOLUTION_Y": RESOLUTION_Y,
    "FPS": FPS,
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
    "VERTEX": 4,
    "VERTEX_VEL": 4,
    "ALPHA":5,
    "ALPHA_LEN":10,
    "VERTEX_VEL_MULT": DELTA_T,
    "BORDER": 5,
    "FONT_SIZE_GRAIN": 10,
    "FONT_SIZE_BORDER": 10,
    "FONT_SIZE_VERTEX": 10,

}

