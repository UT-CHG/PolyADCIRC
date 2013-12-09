import polysim.run_framework.domain as dom
import polysim.mesh_mapping.manufacture_gap as manu
import polysim.mesh_mapping.table_management as tm
import polysim.mesh_mapping.gridObject as go
import polysim.mesh_mapping.prep_mesh as prep

grid_dir = '.'

domain = dom.domain(grid_dir)
domain.read_spatial_grid()

x_values = [n.x for n in domain.node.values()]
y_values = [n.y for n in domain.node.values()]
xr = max(x_values)
xl = min(x_values)
yu = max(y_values)
yl = min(y_values)

p = [[0, 0, 0, 1],
     [0, 0, 0, 1],
     [0, 0, 0, 1],
     [0, 0, 0, 1],
     [0, 0, 0, 1],
     [0, 0, 0, 1],
     [0, 0, 0, 1],
     [0.8, 0.2, 0.0, 0],
     [0.0, 0.2, 0.8, 0],
     [0.8, 0.2, 0, 0],
     [0.2, 0.4, 0.4, 0],
     [0.1, 0.2, 0.7, 0],
     [0.2, 0.4, 0.4, 0],
     [0.7, 0.3, 0, 0],
     [1, 0, 0, 0],
     [0, 0, 1, 0 ],
     [0.9, 0.1, 0, 0 ],
     [0.8, 0.1, 0.1, 0],
     [0.1, 0.2, 0.7, 0], 
     [0.2, 0.4, 0.4, 0], 
     [0, 0.1, 0.9, 0]]
x_points = (xl, 750, 1500, xr)
y_points = (yl, -1200, -750, 100, 500, 1150, 1300, yu)
rand_rect = manu.random_patches(x_points, y_points, [1, 2, 3, 4], p_sections = p)

manu.write_gapfile(rand_rect, xl, yl, 'band_sections.asc')

table = tm.read_table('rand_Manning.table')
gap_sec = tm.gapInfo('band_sections.asc', table)
gap_list = [gap_sec]
grid = go.gridInfo('flagged_fort.14', gap_list)

prep.prep_all(grid, path = grid_dir)
prep.prep_test(grid, path = grid_dir)

prep.prep_all(grid, path = grid_dir)
prep.prep_test(grid, path = grid_dir)
prep.compare(basis_dir = grid_dir)

