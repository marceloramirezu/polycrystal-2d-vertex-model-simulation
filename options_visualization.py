from options_simulation import DELTA_T

""" ------------------------------------------------------------------------------------------------
VISUALIZATION OPTIONS
------------------------------------------------------------------------------------------------ """
# 0.- SIMULATION SHOWN
SIMULATION = "out_N100_t5000_01-15-2023_21h48m34s"


# 1.- PYGAME 
FPS = 60                            # Max. fps of visualization
FPS_X2 = 60                         # Max. fps of X2 Velocity () visualization
RESOLUTION = 800                    # 
RESOLUTION_X = RESOLUTION           # must be equal to y resolution
RESOLUTION_Y = RESOLUTION
TICKS_WAIT_INPUT = 30               # frames until new input

# 2.- colors
COLOR_ALPHA = (100, 100, 100)
COLOR_ALPHA_3_SIDED = (255, 0, 0)
COLOR_VERTEX = (150, 150, 150)
COLOR_VERTEX_1 = (250, 10, 10)
COLOR_BORDER_0 = (80, 80, 80)
COLOR_BORDER_1 = (250, 0, 250)
COLOR_VEL_VERTEX = (255, 255, 255)
BACKGROUND_COLOR = (10,10,10)

# 2.- SIZES
VERTEX_SIZE = 4                     # size of vertices (px)
ALPHA_SIZE= 4                       # weight of grain orientation
ALPHA_LEN= 10                       # length of grain orientation
VERTEX_VEL_SIZE = 4                 # weight of velocity segment
VERTEX_VEL_MULT = DELTA_T           # velocity length multiplayer
BORDER_SIZE= 5                      # weight of borders
FONT_SIZE_UI = 20
FONT_SIZE_GRAIN = 7                 # font size of grains id's
FONT_SIZE_BORDER = FONT_SIZE_GRAIN  # font size of borders id's
FONT_SIZE_VERTEX = FONT_SIZE_GRAIN  # font size of vertices id's





""" ============================================================== DICTIONARIES ============================================================== """
OPTIONS_SHOW = {
    "SIMULATION": SIMULATION,
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
OPTIONS_SHOW_SIZE = {
    "VERTEX_SIZE": VERTEX_SIZE,
    "VERTEX_VEL_SIZE": VERTEX_VEL_SIZE,
    "ALPHA_SIZE":ALPHA_SIZE,
    "ALPHA_LEN":ALPHA_LEN,
    "VERTEX_VEL_MULT": VERTEX_VEL_MULT,
    "BORDER_SIZE": BORDER_SIZE,
    "FONT_SIZE_GRAIN": FONT_SIZE_GRAIN,
    "FONT_SIZE_BORDER": FONT_SIZE_BORDER,
    "FONT_SIZE_VERTEX": FONT_SIZE_VERTEX,
    "FONT_SIZE_UI": FONT_SIZE_UI,
}

OPTIONS = {
    "OPTIONS_SHOW": OPTIONS_SHOW,
    "OPTIONS_SHOW_COLOR": OPTIONS_SHOW_COLOR,
    "OPTIONS_SHOW_SIZE": OPTIONS_SHOW_SIZE,
}