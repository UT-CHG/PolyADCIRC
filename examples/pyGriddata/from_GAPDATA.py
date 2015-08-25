#! /usr/bin/env python
# import necessary modules
import polyadcirc.run_framework.domain as dom
import polyadcirc.pyGriddata.table_management as tm
import polyadcirc.pyGriddata.grid_management as gm
import glob

# Specify run parameter folders 
adcirc_dir = '/h1/lgraham/workspace'
grid_dir = adcirc_dir + '/ADCIRC_landuse/Katrina_small/inputs'
save_dir = adcirc_dir + '/ADCIRC_landuse/Katrina_small/runs/output_test'
basis_dir = adcirc_dir +'/ADCIRC_landuse/Katrina_small/landuse_basis/gap/shelf_test'

# load in the small katrina mesh
domain = dom.domain(grid_dir)
domain.update()
# map manning's n values to the mesh (this could be a separate file)
table = tm.read_table('CCAP_Manning_20100922.table',
                      adcirc_dir+'/landuse/tables') 
gap_files = glob.glob('/h1/lgraham/workspace/landuse/data/CCAP_Data/Job*/*.asc')
gap_list = tm.create_gap_list(table, gap_files) 
grid = gm.gridInfo(basis_dir, grid_dir, gap_list,
        executable_dir='../../polyadcirc/pyGriddata')
grid.prep_all()
# test and compare
grid.prep_test()
gm.compare(basis_dir)



