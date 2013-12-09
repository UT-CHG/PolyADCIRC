"""
prep_table_to_mesh_map prepares *.table and *.13 files needed for
T:**_manning.table-->fort.13 and creates the nxm matrix of multiplier
factors where n = # nodes, and m = # land classification values.
"""

import polysim.mesh_mapping.table_management as tm
import polysim.mesh_mapping.gridObject as go
import polysim.mesh_mapping.prep_mesh as prep

# read in an input file that designates the following:
#   name of grid file
#   order to read in GAP/NLCD data file(s)
#   GAP/NLCD data file(s) with the associated data: THIS SHOULD BE A TUPLE
#       name of GAP/NLCD data file
#       name of classified value table
#       horizontal system
#       UTM Zone number
table = tm.read_table('CCAP_Manning.table')
gap15 = tm.gapInfo('15N.asc', table, 2, 15 )
gap16_1 = tm.gapInfo('16N_part1.asc', table, 2, 16 )
gap16_2 = tm.gapInfo('16N_part2.asc', table, 2, 16 )
gap17 = tm.gapInfo('17N.asc', table, 2, 17)
gap_list = [gap15, gap16_1]
grid = go.gridInfo('flagged_fort.14', gap_list)

grid_dir = '.'

prep.prep_all(grid, path = grid_dir)
prep.prep_test(grid, path = grid_dir)

prep.prep_all(grid, path = grid_dir)
prep.prep_test(grid, path = grid_dir)
prep.compare(basis_dir = grid_dir)

