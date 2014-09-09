#! /usr/bin/env python
# import necessary modules
import polyadcirc.run_framework.domain as dom
import numpy as np
import polyadcirc.pyGriddata.table_to_mesh_map as tmm
import polyadcirc.pyADCIRC.plotADCIRC as plotA

# Specify run parameter folders 
adcirc_dir = '/h1/lgraham/workspace'
grid_dir = adcirc_dir + '/ADCIRC_landuse/Katrina_small/inputs'
save_dir = adcirc_dir + '/ADCIRC_landuse/Katrina_small/runs/output_test'
basis_dir = adcirc_dir +'/ADCIRC_landuse/Katrina_small/landuse_basis/gap/shelf_test'

# load in the small katrina mesh
domain = dom.domain(grid_dir)
domain.update()

# load in basis vectors for domain
bv_dict = tmm.get_basis_vectors(basis_dir)

# create and save images of the mesh with various manning's n values to
# visualize the location of different types of nodes
# show the location of the non default nodes
# show the location of the shelf nodes
# show the location of the default nodes
domain.get_Triangulation()
# convert basis vectors to an array
bv_array = np.zeros((domain.node_num, len(bv_dict)+1))
default_nodes = tmm.get_default_nodes(domain, bv_dict)
bv_array[default_nodes, -1] = 1.0
for i, b_vect in enumerate(bv_dict):
    ind = np.array(b_vect.keys())-1
    bv_array[ind, i] = 1
plotA.basis_functions(domain, bv_array)

# plot bathymetry contours (in a separate plot, but with contours where the
# shelf should be)
plotA.bathymetry(domain, contour=True)

# everything should look fine if it does then we're good :)


