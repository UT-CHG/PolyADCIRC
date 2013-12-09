#! /usr/bin/env python
# import necessary modules
import polysim.run_framework.random_wall as rmw
import polysim.pyADCIRC.plotADCIRC as pa

base_dir = '/h1/lgraham/workspace'
grid_dir = base_dir + '/ADCIRC_landuse/Inlet/inputs/poly_walls'
save_dir = base_dir + '/ADCIRC_landuse/Inlet/runs/few_walls'
basis_dir = base_dir +'/ADCIRC_landuse/Inlet/landuse_basis/gap/beach_walls_2lands'

# setup and save to shelf
# set up saving
save_file = 'py_save_file'

main_run, domain, mann_pts, wall_pts, points = rmw.loadmat(save_file, base_dir,
        grid_dir, save_dir, basis_dir)

pt_nos = range(points.shape[-1])

pa.nts_pcolor(main_run.nts_data, domain, points = pt_nos, path = save_dir)
