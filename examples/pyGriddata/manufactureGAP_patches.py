import polyadcirc.run_framework.domain as dom
import polyadcirc.pyGriddata.manufacture_gap as manu

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
     [0.7, 0.2, 0.1, 0],
     [0.1, 0.1, 0.8, 0],
     [0.8, 0.2, 0, 0],
     [0.2, 0.4, 0.4, 0],
     [0.1, 0.2, 0.7, 0],
     [0.2, 0.4, 0.4, 0],
     [0.7, 0.3, 0, 0]]
x_points = (xl, 750, xr)
y_points = (yl, -1225, -750, 100, 500, 1150, 1300, yu)
rand_rect = manu.random_patches(x_points, y_points, [1, 2, 3, 4], p_sections=p)
manu.write_gapfile(rand_rect, xl, yl, 'band_sections.asc')

