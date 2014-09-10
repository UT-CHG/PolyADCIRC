#! /usr/bin/env python
# import necessary modules
import polyadcirc.run_framework.domain as dom
import polyadcirc.pyGriddata.file_management as fm
import polyadcirc.pyGriddata.table_to_mesh_map as tmm
import polyadcirc.pyADCIRC.fort13_management as f13
import glob

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

# create the shelf basis vector dictonary
shelf_limits = [0, 50] #[0, 100] [50, 100]
shelf_bv = tmm.create_shelf(domain, shelf_limits, bv_dict)

# write this out to an appropriately numbered basis vector mesh in the correct
# basis_dir
# get list of landuse folder names
folders = glob.glob(basis_dir+'/landuse_*')
# create new folder
folder_name = basis_dir+'/landuse_'+'{:=02d}'.format(len(folders))
fm.mkdir(folder_name)
# copy a fort.13 file to that folder
fm.copy(save_dir+'/fort.13', folder_name+'/fort.13')
f13.update_mann(shelf_bv, folder_name)


