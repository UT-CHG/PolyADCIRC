"""
This module given a ``*.table`` (and ``*.table`` and ``*.13 files`` from
:mod:`prep_table_to_mesh_map`) produces a ``*.13`` file of Manning's *n* 
values for that ``*.table``, or dict, or array of these values.
"""

import polyadcirc.pyADCIRC.fort13_management as f13
import numpy as np
import glob, os
from polyadcirc.pyADCIRC.basic import comm

size = comm.Get_size()
rank = comm.Get_rank()


class Error(Exception):
    """ Base class for exceptions in this module."""
    def __init__(self):
        super(Error, self).__init__()


class LenError(Error):
    """ Exception raised for errors in dimension or length.
    """

    def __init__(self, expr, msg):
        self.expr = expr #: input expression in wich the error occured
        self.msg = msg #:  explanation of the error
        super(LenError, self).__init__()


def get_basis_vectors(path=None):
    """
    Each dict is structured as follows:
    keys -- node number
    values -- weighting for spatial averaging
    currently assumes only 1 folder per landuse classification with the name
    ``landuse_*/``

    :param string path: folder containing the landuse folders
    :rtype: list
    :returns: list of dicts for each landuse classification.
    
    """
    landuse_folders = glob.glob(path+'/landuse_*')
    landuse_folders.sort()
    basis_vec = [f13.read_nodal_attr_dict(folder) for folder in landuse_folders]
    return basis_vec    

def get_basis_vec_array(path=None, node_num=None):
    """
    NOTE: this impementation currently assumes that there are no default nodes
    this will need to be updated later
    
    :param string path: folder containing the landuse folders
    :param int node_num: number of nodes in the mesh
    :rtype: :class:`numpy.ndarray`
    :returns: an array of size(node_num, num_basis_vec)
    
    """
    bv_list_of_dict = get_basis_vectors(path)
    if node_num == None:
        ex_folder = glob.glob(path+'/landuse_*')[0]
        node_num = f13.read_node_num(ex_folder)
    bv_array = np.zeros((len(bv_list_of_dict), node_num))
    for k, v in enumerate(bv_list_of_dict):
        bv_array[k, ...] = dict_to_array(v, 0, node_num)
    return bv_array.transpose()

def combine_bv_array(weights, array):
    """
    :type weights: :class:`numpy.array`
    :param weights: array of size (num_of_basis_vec, 1)
    :type array: :class:`numpy.array` of size (node_num, num_of_basis_vec)
    :param array: array of basis vectors
    :returns: an array of size (node_num, 1) containing the manningsn value at
        all nodes in numerical order

    """
    return np.dot(array, weights)

def combine_basis_vectors(weights, vectors, default_value=None, node_num=None):
    """

    Currently ``default_value`` and ``node_num`` are NOT being used to fill in
    default nodes.

    :type weights: :class:`numpy.array`
    :param weights: array of size (num_of_basis_vec, 1)
    :type vectors: list of dicts OR :class:`numpy.array` of size (node_num,
        num_of_basis_vec) 
    :param vectors: basis vectors
    :returns: an array of size (node_num, 1) containing the manningsn value at
        all nodes in numerical order or a dictionary
    
    """
    if len(weights) != len(vectors):
        raise LenError('weights, vectors', 'dimensions do not match')


    if type(vectors[0]) == np.array:
        combine_bv_array(weights, vectors)
    else:
        return add_dict(vectors, weights)[0]
        
def add_dict(dict_list, weights):
    """

    :param dict_list: list of dicts
    :param list() weights: list of weights
    :rtype: dict
    :returns: a dict[k] = weights[0]*dict_list[0] + ... +
        weights[-1]*dict_list[-1]
    
    """
    return reduce(add_dict_pair, zip(dict_list, weights))

def add_dict_pair(dict1, dict2):
    """
    :param dict dict1: first dict
    :param dict dict2: second dict
    :rtype: dict
    :returns: a dict[k] = dict1[k] + dict2[k]
    
    """
    dict_sum = {}
    for k, v in dict1[0].iteritems():
        dict_sum[k] = dict1[1]*dict1[0][k]
    for k, v in dict2[0].iteritems():
        if dict_sum.has_key(k):
            dict_sum[k] += dict2[1]*v
        else:
            dict_sum[k] = dict2[1]*v
    return (dict_sum, 1)

def dict_to_array(data, default_value, node_num):
    """
    Given a dictonary, default_value, and number of nodes converts a dictornary
    to an array of size(node_num, 1) and fills in the missing entires with the
    default_value

    :param data: dict
    :param float default_value: default
    :param int node_num: total number of nodes in the mesh
    :rtype: :class:`numpy.array`
    :returns: array version of the dict

    """
    array = np.ones((node_num,))*default_value
    for i in xrange(node_num):
        if data.has_key(i+1):
            array[i] = data[i+1]
    return array

def get_default_nodes(domain, vectors=None):
    """
    Given a set of basis vectors and a domain returns a list of default nodes.

    :param domain: a computational domain for a physical domain
    :type domain: :class:`~polyadcirc.run_framework.domain`
    :param vectors: basis vectors
    :type vectors: dict()

    :rtype: list()
    :returns: list of default nodes

    """
    if vectors:
        default_bv_array = combine_basis_vectors(np.zeros((len(vectors),)),
                vectors, 1.0, domain.node_num)
        alternate = combine_basis_vectors(np.ones((len(vectors),)), vectors)
        alt2 = np.ones((domain.node_num,))
        keys = [k-1 for k in alternate.keys()]
        alt2[keys] = 0
        list2 = np.nonzero(alt2)[0]
    else:
        default_bv_array = np.ones((domain.node_num,))
    default_node_list = np.nonzero(default_bv_array)[0]
    return default_node_list, list2

def create_shelf(domain, shelf_bathymetry, vectors):
    """
    Creates a contitnetal shelf basis vector where the value at default
    nodes between user defined bathymetric bounds are 1 and the other
    default nodes are untouched. This basis vector can now be used to create a
    ``fort.13`` file. Remember bathymetry is positive in the down direction.

    :param domain: a computational domain for a physical domain
    :type domain: :class:`~polyadcirc.run_framework.domain`
    :param shelf_bathymetry: the bathymetric limits of the continental shelf
        [min, max]
    :type shelf_bathymetry: :class:`numpy.array`
    :param vectors: basis vectors
    :type vectors: dict()

    :rtype: dict()
    :returns: basis vector that represents the continental shelf

    """
    bathymetry = domain.array_bathymetry()
    shelf_dict = dict()
    default_node_list = get_default_nodes(domain, vectors)
    for i in default_node_list:
        if bathymetry[i] >= shelf_bathymetry[0]:
            if bathymetry[i] <= shelf_bathymetry[1]:
                shelf_dict[i+1] = 1.0
    return shelf_dict

def create_from_fort13(domain, mann_dict, vectors):
    """
    Creates a basis vector where the value at default nodes is the value in the
    ``mann_dict`` created from reading in a ``fort.13`` formatted file. If the
    node is default in both ``mann_dict`` and ``vectors`` then it remains a
    default node.

    :param domain: a computational domain for a physical domain
    :type domain: :class:`~polyadcirc.run_framework.domain`
    :param dict mann_dict: a dictionary created from a ``fort.13`` formatted
        file or a dictionary of Manning's n values
    :param vectors: basis vectors
    :type vectors: dict()

    :rtype: dict()
    :returns: basis vector of values
    """
    new_mann_dict = {}
    default_node_list = get_default_nodes(domain, vectors)
    for i in default_node_list:
        if i in mann_dict:
            new_mann_dict[i] = mann_dict[i]

    return mann_dict

def condense_bv_dict(mann_dict, TOL=None):
    """
    Condenses the ``mann_dict`` land classificaiton mesh by removing values
    that are below ``TOL``.

    :param dict mann_dict: a dictionary created from a ``fort.13`` formatted
        file or a dictionary of Manning's n values
    :param double TOL: Tolerance close to zero, default is 1e-7

    :rtype: dict()
    :returns: basis vector of values
    """
    if TOL == None:
        TOL = 1e-7
    new_mann_dict = {}
    for k, v in mann_dict.iteritems():
        if v > TOL:
            new_mann_dict[k] = v
    return new_mann_dict

def condense_lcm_folder(basis_folder, TOL=None):
    """
    Condenses the ``fort.13`` lanudse classification mesh files in
    ``landuse_*`` folders in ``basis_dir`` by removing values taht are below
    ``TOL``.

    :param string basis_dir: the path to directory containing the
        ``landuse_##`` folders
    :param double TOL: Tolerance close to zero, default is 1e-7
    """

    folders = glob.glob(os.path.join(basis_folder, "landuse_*"))
    for i in range(0+rank, len(folders), size):
        mann_dict = f13.read_nodal_attr_dict(folders[i])
        mann_dict = condense_bv_dict(mann_dict, TOL)
        f13.update_mann(mann_dict, folders[i])

