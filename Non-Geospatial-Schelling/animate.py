"""
author: Benjamin Panny
"""

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.animation import FuncAnimation

color_map = {0: "blue", 1: "red"}

def network_visualization(Gs):

    fig, ax = plt.subplots()
    y_pos = {node: np.random.uniform(0, 3) for node in Gs[0].nodes()}
    def update(ii):
        ax.clear()
        
        G = Gs[ii]
        
        pos = {node: (data['frac_red'], y_pos[node]) for node, data in G.nodes(data=True)}
        color_sequence = [color_map[data['my_color']] for node, data in G.nodes(data=True)]
        nx.draw(G, node_color = color_sequence, pos = pos)  
        limits=plt.axis('on') # turns on axis
        ax.tick_params(left=False, bottom=True, labelleft=False, labelbottom=True)
        ax.set_xlabel("Red Fraction")
        ax.set_title(f"Timestep {ii}")
        return None,
    
    # use `interval` to change animation transitions
    animation = FuncAnimation(fig, update, interval=1000, frames=len(Gs), blit=False)  # Increased interval
    return animation