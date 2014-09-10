# Lindley Graham 6/12/2013

"""
This module contains functions to generate GAP formatted ``*.asc`` files as a
form of simulated data to be used by :program:`Griddata_v1.32.F90`. This module
requires `Numpy version 1.7.0 <http://www.numpy.org>`_ or above.

.. todo:: add support for polar coordinates

"""

import numpy as np
import subprocess, math, os

def write_gapfile(gap_data, xllcorner, yllcorner, file_name='gap_data.asc',
                  cellsize=30, NODATA_value=-9999):
    """
    Writes out a GAP formatted ``*.asc`` file to file_name

    :param string file_name: full path to file_name
    :type gap_data: :class:`np.array`
    :param gap_data: nrows by ncols 2D array
    :param float xllcorner: x UTM coordinate of lower left corner (SW) in meters
    :param float yllcorner: y UTM coordinate of lower left corner (SW) in meters
    :type cellsize: int or 30
    :param cellsize: size of cells(square grid) in meters, pixel resolution
    :param int NODATA_value: land classification number for no data

    """

    with open(file_name, 'w') as fid:
        # write out header information
        fid.write('{:<14} {:<d}\n'.format('ncols', gap_data.shape[1]))
        fid.write('{:<14} {:<d}\n'.format('nrows', gap_data.shape[0]))
        fid.write('{:<14} {:f}\n'.format('xllcorner', xllcorner))
        fid.write('{:<14} {:f}\n'.format('yllcorner', yllcorner))
        fid.write('{:<14} {:<d}\n'.format('cellsize', cellsize))
        fid.write('{:<14} {:<d}\n'.format('NODATA_value', NODATA_value))
    # write out gap_data
    np.savetxt('tmp_gap.txt', gap_data, fmt='%-2d')
    # concatenate the files
    subprocess.call('cat tmp_gap.txt >> '+file_name, shell=True)
    os.remove('tmp_gap.txt')

def random(xl, xr, yl, yu, landclasses, cellsize=30, p=None, path=None):
    """
    Generates a random matrix that covers the area defined by xl, xr, yl, yu
    where the land classification numbers are chosen from landclasses

    .. seealso:: `Numpy documenation <http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.choice.html#numpy.random.choice>`_

    :param float xl: leftmost value in meters
    :param float xr: rightmost value in meters
    :param float yl: lower value in meters
    :param float yu: upper value in meters
    :type landclasses: 1D array-like or int
    :param landclasses: list of land classification numbers
    :param int cellsize: size of the cell in meters
    :type p: 1D array-like of size num_land_classes
    :param p: probabilities associated with each land classification
    :param string path: folder to write out probability structure to as
        p_struct.txt
    :rtype: int or :class:`numpy.ndarray`
    :returns: See :class:`numpy.random.choice`

    """
    # Determine number of columns
    ncol = int(math.ceil((xr-xl)/cellsize)) + 1
    # Determine number of rows
    nrow = int(math.ceil((yu-yl)/cellsize)) + 1
    if path == None:
        path = os.getcwd()
    with open(path+'/p_struct.txt', 'w') as fid:
        fid.write(str(p))
    return np.random.choice(landclasses, (nrow, ncol), True, p)

def random_vertical(x_points, yl, yu, landclasses, cellsize=30, 
                    p_sections=None, path=None):
    """
    Generates a random matrix that covers the area defined by x_points, yl,
    yu where the land classification numbers are chosen from landclasses

    .. seealso:: `Numpy documenation <http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.choice.html#numpy.random.choice>`_

    :type x_points: ordered 1D array-like must be of size num_sections+1
    :param x_points: x values in meters that divde the grid into vertical
        intervals (x_min, ...., x_max)
    :param float yl: lower value in meters
    :param float yu: upper value in meters
    :type landclasses: 1D array-like or int
    :param landclasses: list of land classification numbers
    :param int cellsize: size of the cell in meters
    :type p_sections: list() of size num_sections of 1D array-like or int   
    :param p_sections: list of probabilities for each section associated with each 
        land classification
    :param string path: folder to write out probability structure to as
        p_struct.txt
    :rtype: int or :class:`numpy.ndarray`
    :returns: See :class:`numpy.random.choice`

    """
    # Determine number of rows
    nrow = int(math.ceil((yu-yl)/cellsize)) + 1
 
    # Determine column indices 
    xr = [int(round((x-x_points[0])/cellsize)) for x in x_points[1:-1]]
    xr.append(int(math.ceil((x_points[-1]-x_points[0])/cellsize)) + 1)
    xl = [x + 1 for x in xr]
    xl.insert(0, 0)
    
    gap_arrays = list()

    for prob, r, l in zip(p_sections, xr, xl):
        ncol = r - l + 1
        gap_arrays.append(np.random.choice(landclasses, (nrow, ncol), True,
            prob))
    if path == None:
        path = os.getcwd()
    with open(path+'/p_struct.txt', 'w') as fid:
        fid.write(str(p_sections))
    return np.hstack(gap_arrays)

def random_horizontal(y_points, xl, xr, landclasses, cellsize=30, 
                      p_sections=None, path=None):
    """
    Generates a random matrix that covers the area defined by xl, xr, y_points
    where the land classification numbers are chosen from landclasses

    .. seealso:: `Numpy documenation <http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.choice.html#numpy.random.choice>`_

    :type y_points: ordered 1D array-like must be of size num_sections+1
    :param y_points: y values in meters that divde the grid into vertical
        intervals (y_min, ...., y_max)
    :param float xl: lower value in meters
    :param float xr: upper value in meters
    :type landclasses: 1D array-like or int
    :param landclasses: list of land classification numbers
    :param int cellsize: size of the cell in meters
    :type p_sections: list() of size num_sections of 1D array-like or int   
    :param p_sections: list of probabilities for each section associated with each land 
        classification
    :param string path: folder to write out probability structure to as
        p_struct.txt
    :rtype: int or :class:`numpy.ndarray`
    :returns: See :class:`numpy.random.choice`

    """
    # Determine number of columns
    ncol = int(math.ceil((xr-xl)/cellsize)) + 1
 
    # Determine row indices 
    yu = [int(round((y-y_points[0])/cellsize)) for y in y_points[1:-1]]
    yu.append(int(math.ceil((y_points[-1]-y_points[0])/cellsize))+1)
    yl = [y + 1 for y in yu]
    yl.insert(0, 0)
    
    gap_arrays = list()

    for prob, u, l in zip(p_sections, yu, yl):
        nrow = u - l + 1
        gap_arrays.append(np.random.choice(landclasses, (nrow, ncol), True,
            prob))
    if path == None:
        path = os.getcwd()
    with open(path+'/p_struct.txt', 'w') as fid:
        fid.write(str(p_sections))
   
    return np.vstack(gap_arrays)

def random_patches(x_points, y_points, landclasses, cellsize=30, 
                   p_sections=None, path=None):
    """
    Generates a random matrix that covers the area defined by x_points,
    y_points where the land classification numbers are chosen from landclasses

    .. seealso:: `Numpy documenation <http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.choice.html#numpy.random.choice>`_
    
    :type x_points: ordered 1D array-like must be of size num_sections+1
    :param x_points: x values in meters that divde the grid into vertical
        intervals (x_min, ...., x_max)
    :type y_points: ordered 1D array-like must be of size num_sections+1
    :param y_points: y values in meters that divde the grid into vertical
        intervals (y_min, ...., y_max)
    :type landclasses: 1D array-like or int
    :param landclasses: list of land classification numbers
    :param int cellsize: size of the cell in meters
    :type p_sections: list() of size num_sections of 1D array-like or int   
    :param p_sections: list of probabilities for each section associated with each land 
        classification sections are numbered n = j + n_x_sections * i where i
        and j are the ith and jth x and y section respectively
    :param string path: folder to write out probability structure to as
        p_struct.txt
    :rtype: int or :class:`numpy.ndarray`
    :returns: See :class:`numpy.random.choice`

    """
    # Determine number of columns
    ncol = int(math.ceil((x_points[-1]-x_points[0])/cellsize)) + 1
 
    # Determine row indices 
    yu = [int(round((y-y_points[0])/cellsize)) for y in y_points[1:-1]]
    yu.append(int(math.ceil((y_points[-1]-y_points[0])/cellsize))+1)
    yl = [y + 1 for y in yu]
    yl.insert(0, 0)

    # Determine number of rows
    nrow = int(math.ceil((y_points[-1]-y_points[0])/cellsize)) + 1
 
    # Determine column indices 
    xr = [int(round((x-x_points[0])/cellsize)) for x in x_points[1:-1]]
    xr.append(int(math.ceil((x_points[-1]-x_points[0])/cellsize)) + 1)
    xl = [x + 1 for x in xr]
    xl.insert(0, 0)
    
    gap_arrays_v = list()
    gap_arrays_r = list()

    i = 0
    for r, l in zip(xr, xl):
        ncol = r - l + 1
        for u, b in zip(yu, yl):
            nrow = u - b + 1
            print i, r, l, u, b, p_sections[i]
            gap_arrays_v.append(np.random.choice(landclasses, (nrow, ncol), True,
                                p_sections[i]))
            i += 1
        gap_arrays_r.append(np.vstack(gap_arrays_v))
        gap_arrays_v = list()

    if path == None:
        path = os.getcwd()
    with open(path+'/p_struct.txt', 'w') as fid:
        fid.write(str(p_sections))

    return np.hstack(gap_arrays_r)

