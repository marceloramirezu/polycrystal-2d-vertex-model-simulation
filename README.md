# polycrystal-2d-vertex-model-simulation

## Requirements
Python3\
Anaconda3\

## Create and activate environment
conda create --name python-env python=3.11\
conda activate python-env\

## Install required libraries
pip install -r requirements.txt\
*pip is necessary for pygame library\

## Options file
options_simulation.py: Parameters for the simulation (Voronoi seed, Initial grains, Delta t, etc...)\
options_visualization.py: Parameters for the visualization (Resolution, Colors, font size, etc...)\

## Run simulation and generate files
py main.py \
or\
python main.py\

## Run visualization
py show.py\
or\
python show.py\
