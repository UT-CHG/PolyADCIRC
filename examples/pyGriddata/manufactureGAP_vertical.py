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
x_points = (xl, 150, 750, xr)
p1 = [0, 0, 0, 1]
p2 = [0, 0, 0, 1]
p3 = [.2, .3, .4, .1]
rand_rect = manu.random_vertical(x_points, yl, yu, [1, 2, 3, 4], p_sections=
                                 [p1, p2, p3])
manu.write_gapfile(rand_rect, xl, yl, 'sections.asc')
