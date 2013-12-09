import polysim.run_framework.domain as dom
import polysim.utils.fort13_management as f13
import polysim.run_framework.plotADCIRC as plt
import polysim.mesh_mapping.table_to_mesh_map as tmm
import numpy as np
import polysim.mesh_mapping.table_management as tm

#tables = tm.read_tables()

grid_dir = '.'
basis_dir = grid_dir
tables = tm.read_tables(basis_dir+'/test')

domain = dom.domain(grid_dir)
domain.read_spatial_grid()
domain.get_Triangulation(path = basis_dir)
original = f13.read_nodal_attr_dict(basis_dir+'/test')
original = tmm.dict_to_array(original, .022, domain.node_num)
weights = np.array(tables[0].land_classes.values())
lim = (np.min(weights), np.max(weights))
bv_dict = tmm.get_basis_vectors(basis_dir)
combo = tmm.combine_basis_vectors(weights, bv_dict, .022, domain.node_num)
bv_array = tmm.get_basis_vec_array(basis_dir, domain.node_num)
plt.basis_functions(domain, bv_array, path = basis_dir)
plt.field(domain, original, 'original', clim = lim,  path = basis_dir)
plt.field(domain, combo, 'reconstruction', clim = lim, path = basis_dir)
plt.field(domain, original-combo, 'difference', path = basis_dir)
combo_array = tmm.combine_bv_array(weights, bv_array)
plt.field(domain, combo_array, 'combo_array',  clim = lim, path = basis_dir)
plt.field(domain, original-combo_array, 'diff_ori_array', path = basis_dir)
plt.field(domain, combo-combo_array, 'diff_com_array', path = basis_dir)
combo_bv = tmm.combine_basis_vectors(np.ones(weights.shape),
        bv_dict,.022, domain.node_num)
plt.field(domain, combo_bv, 'combo_bv', path = basis_dir)
