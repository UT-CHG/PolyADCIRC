"""
This module given a ``*.table`` (and ``*.table`` and ``*.13 files`` from
:mod:`prep_table_to_mesh_map`) produces a ``*.13`` file of Manning's *n* 
values for that ``*.table``, or dict, or array of these values.
"""

import polyadcirc.pyADCIRC.fort13_management as f13
import numpy as np
import glob

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


def get_basis_vectors(path = None):
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

def get_basis_vec_array(path = None, node_num = None):
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
    :returns: an array of size (node_num, 1) containing the manningsn value at all
        nodes in numerical order

    """
    return np.dot(array, weights)

def combine_basis_vectors(weights, vectors, default_value, node_num):
    """
    :type weights: :class:`numpy.array`
    :param weights: array of size (num_of_basis_vec, 1)
    :type array: list of dicts OR :class:`numpy.array` of size (node_num, num_of_basis_vec)
    :param vectors: basis vectors
    :returns: an array of size (node_num, 1) containing the manningsn value at all
        nodes in numerical order
    
    """
    if len(weights) != len(vectors):
        raise LenError('weights, vectors', 'dimensions do not match')

    if type(vectors[0]) == np.array:
        combine_bv_array(weights, vectors)
    else:
        return dict_to_array(add_dict(vectors, weights)[0], default_value,
                node_num)
        
def add_dict(dict_list, weights):
    """

    :param dict_list: list of dicts
    :param list() weights: list of weights
    :rtype: dict
    :returns: a dict[k] = weights[0]*dict_list[0] + ... + weights[-1]*dict_list[-1]
    
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



    
