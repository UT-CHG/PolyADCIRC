# test for playing around and testing stuff

# import necessary modules
import polysim.run_framework.domain as dom
import polysim.run_framework.random_manningsn as rmn
import numpy as np
import shelve

# assumes that the landuse directory and ADCIRC_landuse directory are in the
# same directory
grid_dir = '../../../ADCIRC_landuse/Ebbshoal_wd/winds'
save_dir = '../../../ADCIRC_landuse/Ebbshoal_wd/runs'
basis_dir = '../../../ADCIRC_landuse/Ebbshoal'

obs_times = 36
# Euclid has 23 blades so be courteous and leave some free
num_of_parallel_runs = 8

domain = dom.domain(grid_dir)
domain.update()
domain.time_grid_data()

main_run = rmn.runSet(grid_dir, save_dir, basis_dir, obs_times,
        num_of_parallel_runs)
main_run.sensitive_all(domain)
main_run.initialize_random_field_directories()

# Setup nD array of coefficients that will be used to construct Manning's n
# fields to run ADCIRC on
# Manning's n between 0.005 and 0.2
# TODO: Check run times and recording times in fort.15 files
# NOTE: Talea ran for 5 days
x1 = np.linspace(.01, .2, 7)
# x1 = np.arange(.02, .2, .01)
x2 = np.linspace(.01, .2, 7)
# x2 = np.arange(.02, .2, .01)
x1, x2 = np.meshgrid(x1, x2)
mann_pts = np.column_stack((x1.ravel(), x2.ravel())).transpose()



# setup and save to shelf
# set up saving
save_file = 'py_save_file.pat'
# shelf = shelve.open(save_file)
shelf = shelve.open(save_dir+'/'+save_file)
# shelf['dirs'] = (grid_dir, save_dir, basis_dir)
# save the domain
shelf['domain'] = domain
# save the run setup
shelf['main_run'] = main_run
shelf['mann_pts'] = mann_pts
shelf.close()

# Run experiments
# MainFile_RandomMann
main_run.run_points(domain, mann_pts, save_file)


