#! /usr/bin/env python
# import necessary modules
import polyadcirc.run_framework.domain as dom
import polyadcirc.run_framework.random_manningsn as rmn
import numpy as np
import os, glob

adcirc_dir = '/work/01837/lcgraham/v50release_130626/work'
grid_dir = adcirc_dir + '/ADCIRC_landuse/Inlet/inputs/tides'
save_dir = adcirc_dir + '/ADCIRC_landuse/Inlet/runs/vel_test'
basis_dir = adcirc_dir + '/ADCIRC_landuse/Inlet/landuse_basis/gap/bands'
# assume that in.prep* files are one directory up from basis_dir
script = "runRUNrun.sh"
save_file = 'py_save_file'
timeseries_files = ["fort.61", "fort.63", "fort.62", "fort.64"]
nontimeseries_files = ["tinun.63", "maxvel.63"]

# NoNx12/TpN where NoN is number of nodes and TpN is tasks per node, 12 is the
# number of cores per node See -pe line in submission_script <TpN>way<NoN x
# 12>
nprocs = 2 # number of processors per PADCIRC run
ppnode = 12
NoN = 2
num_of_parallel_runs = (ppnode*NoN)/nprocs # procs_pnode * NoN / nproc

domain = dom.domain(grid_dir)
domain.update()

main_run = rmn.runSet(grid_dir, save_dir, basis_dir, num_of_parallel_runs,
        base_dir = adcirc_dir, script_name = script)
main_run.initialize_random_field_directories(num_procs = nprocs)

# Set samples
lam_domain = np.array([[.02, .2], [.02, .2], [.02, .2]])
lam1 = np.linspace(lam_domain[0, 0], lam_domain[0, 1], 3)
lam2 = np.linspace(lam_domain[1, 0], lam_domain[1, 1], 3)
lam3 = np.linspace(lam_domain[2, 0], lam_domain[2, 1], 3)
lam4 = 0.02
lam1, lam2, lam3, lam4 = np.meshgrid(lam1, lam2, lam3, lam4)
lam_samples = np.column_stack((lam1.ravel(), lam2.ravel(), lam3.ravel(), lam4.ravel()))

mann_pts = lam_samples.transpose()


# Run experiments
# MainFile_RandomMann
main_run.run_points(domain, mann_pts, save_file, num_procs = nprocs,
        procs_pnode = ppnode, ts_names = timeseries_files, 
        nts_names = nontimeseries_files, screenout=True)

