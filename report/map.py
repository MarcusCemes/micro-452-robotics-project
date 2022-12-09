import numpy as np 
import matplotlib
import matplotlib.pyplot as plt

#colormap
colormap = matplotlib.colors.ListedColormap(['#FFFFFF', 'black', 'red']) #in order: void,ground,walls,fire1,e-pouck ext, e-pouck int, arrow, fire2, fire3
bounds = [0.5, 1.5, 2.5]
perso_norm = matplotlib.colors.BoundaryNorm(bounds, colormap.N)

DIMX = 168
DIMY = 168

class Map_obj(object):
    def __init__(self, ctx):
        self.ctx = ctx
        #creation of the map matrix
        self.map_matrix = np.zeros((DIMX, DIMY))

    def display_map(self):
        fig = plt.imshow(self.map_matrix, colormap)

    def clear_map(self):
        self.map_matrix = np.zeros((DIMX, DIMY))
        self.display_map()

    def update_map(self):
        (x, y) = self.ctx.state.position
        self.map_matrix[int(x), int(y)] = 2.0
        
        self.display_map()
