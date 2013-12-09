"""
prep_mesg prepares *.table and *.13 files needed for
T:**_manning.table-->fort.13 and creates the nxm matrix of multiplier
factors where n = # nodes, and m = # land classification values.

.. todo:: This script must currently be run where path is None or cwd. Later I
        need to add the ability to run it from different directories.
"""

import polysim.pyGriddata.file_management as fm
import polysim.pyGriddata.table_management as tm
import glob, subprocess, os
import polysim.pyADCIRC.fort14_management as f14
import polysim.run_framework.domain as dom
import polysim.pyADCIRC.fort13_management as f13
import polysim.pyADCIRC.plotADCIRC as plt
import polysim.pyGriddata.table_to_mesh_map as tmm
import numpy as np

def prep_all(grid, flag = 1, path = None):
    """
    Assumes that all the necessary input files are in ``path``. Given a
    :class:`~polysim.pyGriddata.gridInfo` object this function generates a
    ``landuse_##`` folder for every land classification number containing a
    ``fort.13`` file specific to that land classification number.

    :param grid: :class:`~polyim.pyGriddata.gridInfo`
    :param string path: THIS MUST BE CWD (``'.'``) or ``None``

    .. todo:: Update so that landuse folders can be prepped n at a time and so
        that this could be run on a HPC system
    
    """
    if path == None:
        path = os.getcwd()

    f14.flag_go(grid, flag)
    first_landuse_folder_name = 'landuse_00'
    first_script = fm.setup_landuse_folder(0, grid,
        folder_name = first_landuse_folder_name)
    # run grid_all_data in this folder 
    subprocess.call(['./'+first_script], cwd = path)
    # set up remaining land-use classifications
    script_list = fm.setup_landuse_folders(grid, False)

    # THERE IS AN ERROR HERE WRT ODD/EVEN HANDLING FIX IT SEE SOLUTION IN
    # RANDOM_MANNINGSN MODULE
    for s in script_list:
        subprocess.call(['./'+s], cwd = path)

    binaries = glob.glob('*.asc.binary')
    for f in binaries:
        os.remove(f)

    # now clean out unecessary files and convert *.14 to *.13 when appropriate
    fm.cleanup_landuse_folders(grid)
    fm.convert(grid)
    fm.rename13()

def prep_test(grid, path = None):
    """
    Assumes :meth:`~polysim.pyGriddata.prep_mesh.prep_all` has been run
    first. Prepares a fort.13 file for testing purposes.

    :param grid: :class:`~polyim.pyGriddata.gridInfo`
    :param string path: THIS MUST BE CWD (``'.'``) or ``None``

    """
    if path == None:
        path = os.getcwd()

    subprocess.call(['./'+fm.setup_folder(grid, 'test')], cwd = path)
    grid.convert('test')
    #fm.cleanup_landuse_folder('test')
    fm.rename13(['test'])

def compare(basis_dir = None, default = 0.012):
    """
    Create a set of diagnostic plots in basis_dir/figs

    :param string basis_dir: directory containing the test folder and landuse
        folders
    :param float default: default Manning's *n*
    """
    if basis_dir == None:
        basis_dir = os.getcwd()
    tables = tm.read_tables(basis_dir+'/test')
    domain = dom.domain(basis_dir)
    domain.read_spatial_grid()
    fm.mkdir(basis_dir+'/figs')
    old_files = glob.glob(basis_dir+'/figs/*.png')
    for fid in old_files:
        os.remove(fid)
    domain.get_Triangulation(path = basis_dir)
    original = f13.read_nodal_attr_dict(basis_dir+'/test')
    original = tmm.dict_to_array(original, default, domain.node_num)
    weights = np.array(tables[0].land_classes.values())
    lim = (np.min(weights), np.max(weights))
    bv_dict = tmm.get_basis_vectors(basis_dir)
    combo = tmm.combine_basis_vectors(weights, bv_dict, default, domain.node_num)
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
            bv_dict,default, domain.node_num)
    plt.field(domain, combo_bv, 'combo_bv', path = basis_dir)

