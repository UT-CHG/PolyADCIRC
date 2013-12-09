#! /usr/bin/env/python

# test for playing around and testing stuff

# import necessary modules
import shelve

# setup and load from shelf
# set up saving
save_file = 'tides_Inlet_wd.pat'
# shelf = shelve.open(save_file)
save_dir = '/Users/troybutler/ADCIRC_landuse/Inlet/runs/tides'
shelf = shelve.open(save_dir+'/'+save_file)
# load the domain
domain = shelf['domain']
# load the run setup
main_run = shelf['main_run']
mann_pts = shelf['mann_pts']
shelf.close()

# the lines below are only necessary if you need to update what the directories
# are when swithcing from euclid to your desktop/laptop
# assumes that the landuse directory and ADCIRC_landuse directory are in the
# same directory
grid_dir = '/Users/troybutler/ADCIRC_landuse/Inlet/inputs/tides'
basis_dir = '/Users/troybutler/ADCIRC_landuse/Inlet/landuse_basis/gap/rand_wd'
domain.dir = grid_dir
main_run.save_dir = save_dir
main_run.grid_dir = grid_dir
main_run.basis_dir = basis_dir
main_run.base_dir = basis_dir.rpartition('/')[0]


# Plot stuff
main_run.make_plots(mann_pts, domain)
