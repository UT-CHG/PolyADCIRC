#! /usr/bin/env python
# import necessary modules
import polyadcirc.run_framework.domain as dom
import polyadcirc.run_framework.random_wall as rmw

base_dir = '/h1/lgraham/workspace'
grid_dir = base_dir + '/ADCIRC_landuse/Inlet/inputs/poly_walls'
save_dir1 = base_dir + '/ADCIRC_landuse/Inlet/runs/poly_wall1'
save_dir2 = base_dir + '/ADCIRC_landuse/Inlet/runs/poly_wall2'
basis_dir = base_dir +'/ADCIRC_landuse/Inlet/landuse_basis/gap/beach_walls_2lands'

# setup and save to shelf
# set up saving
save_file = 'py_save_file'

main_run, domain, mann_pts, wall_pts, points = rmw.loadmat(save_file, base_dir,
        grid_dir, save_dir1, basis_dir)
other_run, domain, mann_pts2, wall_pts2, points2 = rmw.loadmat(save_file, base_dir,
        grid_dir, save_dir2, basis_dir)

cated = main_run.concatenate(other_run, points, points2)

mdat = dict()
mdat['points'] = cated[1]
mdat['mann_pts'] = np.concatenate((mann_pts1, mann_pts2), axis = points1.ndim-1)
mdat['wall_pts'] = np.concatenate((wall_pts1, wall_pts2), axis = points1.ndim-1)

main_run.update_mdict(mdat)
main_run.save(mdat, 'cat_file')


