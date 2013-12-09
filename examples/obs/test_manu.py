# IPython log file

import polysim.mesh_mapping.file_management as fm
import polysim.mesh_mapping.manufacture_gap as manu
import polysim.mesh_mapping.table_management as tm
import polysim.mesh_mapping.gridObject as go
import shelve
save_file = 'py_save_file.pat'
save_dir = '/h1/lgraham/workspace/ADCIRC_landuse/Ebbshoal/talea'
shelf = shelve.open(save_dir+'/'+save_file)
domain = shelf['domain']
main_run = shelf['main_run']
mann_pts = shelf['mann_pts']
shelf.close()
grid_dir = '/h1/lgraham/workspace/ADCIRC_landuse/Ebbshoal/winds'
basis_dir = '/h1/lgraham/workspace/ADCIRC_landuse/Ebbshoal'
domain.dir = grid_dir
main_run.save_dir = save_dir
main_run.grid_dir = grid_dir
main_run.base_dir = basis_dir.rpartition('/')[0]
x_values = [n.x for n in domain.node.values()]
y_values = [n.y for n in domain.node.values()]
xr = max(x_values)
xl = min(x_values)
yu = max(y_values)
yl = min(y_values)
rand_rect = manu.random(xl, xr, yl, yu, [1,2,3])
manu.write_gapfile(rand_rect, xl, yl)
x_points = (xl, 150, 750, xr)
p1 = [.8,.2,0]
p2 = None
p3 = [.15, .45, .4]
rand_rect = manu.random_vertical(x_points, yl, yu, [1,2,3], p_sections =
        [p1,p2,p3])
manu.write_gapfile(rand_rect, xl, yl, 'sections.asc')
# run prep_rand_mesh.py
# run compare_rand.py
