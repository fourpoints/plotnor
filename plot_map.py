#!/usr/bin/python -i

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.cm as cm
import matplotlib.colorbar as cbar
import matplotlib.colors as colors
import shapely.geometry as sg
import numpy as np

from pop_data_extractor import pop_data
from map_data import land_borders, kommunes
from math import isnan
from shapely.ops import cascaded_union

LANDMASS = cascaded_union([sg.Polygon(border) for border in land_borders])

# Make a plot
f = plt.figure()
ax = f.add_subplot(1, 1, 1)

ax.set_title("Befolkningsvekst")
ax.set_xlabel("breddegrad")
ax.set_ylabel("lengdegrad")

# EPSG:32633 coordinate format
ax.set_xlim(-112947.41679, 1170000.50000)
ax.set_ylim(6392426.00308, 7994762.25179)

# Plot coastal and island borders
for border in land_borders:
    ax.plot(*zip(*border), color='k', linewidth=0.5)

# We find the smallest and largest population growth (in percent)
# If a kommune is removed, its population is decreased by 100 %
#   so we filter out these (we cannot plot removed kommunes)
min_inc = min(filter((-100.0).__lt__, (p.inc for p in pop_data.values())))
max_inc = max((p.inc for p in pop_data.values()))

# https://matplotlib.org/api/_as_gen/matplotlib.colors.Normalize.html
inc_normalize = colors.Normalize(min_inc, max_inc)

# ANTALL_KOMMUNER = 422
for kommune_id, kommune_loop in kommunes.items():

    # get color based on population growth
    pop_inc = pop_data.get(kommune_id).inc
    color = cm.coolwarm(inc_normalize(pop_inc)) if not isnan(pop_inc) else 'k'

    kommune_land = LANDMASS.intersection(sg.Polygon(kommune_loop))

    # The kommune is inland
    if type(kommune_land) == sg.polygon.Polygon:
        x, y = kommune_land.exterior.xy
        ax.fill(x, y, alpha=0.5, fc=color)

    # The kommune is split by sea
    elif type(kommune_land) == sg.multipolygon.MultiPolygon:
        for kommune_land_part in kommune_land:
            x, y = kommune_land_part.exterior.xy
            ax.fill(x, y, alpha=0.5, fc=color)

    # The kommune is in the sea
    elif type(kommune_land) == sg.collection.GeometryCollection:
        print("Error, no intersection")


cax, _ = cbar.make_axes(ax, location='right')
cb = cbar.ColorbarBase(
    cax, cmap=cm.coolwarm, norm = inc_normalize,
    orientation='vertical', format='%.0f%%', label="Økning"
)

f.show()
f.savefig("Befolkningsvekst.png")
