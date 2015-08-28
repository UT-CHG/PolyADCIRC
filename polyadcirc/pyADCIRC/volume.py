# Copyright (C) 2013 Lindley Graham

"""
This module contains methods used in calculating the volume of water present in
an ADCIRC simulation.

.. todo:: Some of these routines could be parallelized.

"""

import numpy as np

quad_faces = [[0, 1], [1, 2], [2, 0]]

def total_volume(domain, elevation):
    """
    Calculates the total volume of water contained in an ADCIRC simulation with
    sea surface height given by elevation.

    :param domain: :class:`~polyadcirc.run_framework.domain`
    :param elevation: eta, sea surface height (NOT WATER COLUMN HEIGHT)
    :rtype: tuple
    :returns: total volume, element-wise volume

    """
    e_volume = np.empty((len(domain.element),))
    for k, e in domain.element.iteritems():
        e_volume[k-1] = element_volume(domain, e, elevation)
    t_volume = e_volume.sum()
    return t_volume, e_volume

def sub_volume(domain, elevation, elements):
    """
    Calculates the total volume of water contained in an ADCIRC simulation for
    a given set of elements with sea surface height given by elevation.

    :param domain: :class:`~polyadcirc.run_framework.domain`
    :param elevation: eta, sea surface height (NOT WATER COLUMN HEIGHT)
    :param elements: list of element numbers to calcuate volumes for
    :rtype: tuple
    :returns: total volume, element-wise volume

    """
    e_volume = np.empty((len(elements),))
    for k in elements:
        e_volume[k-1] = element_volume(domain, domain.element[k], elevation)
    t_volume = e_volume.sum()
    return t_volume, e_volume

def element_volume(domain, element, elevation):
    """
    Calculates the volume of water contained an element with a given sea
    surface elevation at each of the nodes.

    :param domain: :class:`~polyadcirc.run_framework.domain`
    :param element: list of nodes defining an element 
    :type element: array_like  
    :param elevation: eta, sea surface height (NOT WATER COLUMN HEIGHT)
    :rtype: double
    :returns: volume

    """
    volume = 0
    # Check if the element is dry
    local_z = [elevation[i-1] for i in element]
    if not np.array_equal(local_z, -99999.0*np.ones(3,)):
        volume += triangle(domain, element, elevation)/3.0
        volume += triangle(domain, element, -domain.bathymetry, -1.0)/3.0
        for i in xrange(3):
            volume += side(domain, element, i, elevation)/3.0
    return volume

def triangle(domain, element, z, norm_dir=1.0):
    """
    Calculates dot(x, n*A) where x is the barycenter, n is the normal vector to
    the surface defined by z and the element verticies, and A is the area of
    the surface defined by z and the element vertices.

    :param domain: :class:`~polyadcirc.run_framework.domain`
    :param element: list of nodes defining an element 
    :type element: array_like  
    :param z: z-coordinate relative to the geiod, z = eta OR z = -h 
    :param double norm_dir: 1.0 up, -1.0 down, direction of the normal vector 
    :type z: :class:`np.array`
    :rtype: double
    :returns: dot(x, n*A)

    """
    points = []
    for i in element:
        n = domain.node[i]
        points.append(np.array([n.x, n.y, z[i-1]]))
    barycenter = np.average(points, 0)
    normal = norm_dir*np.cross(points[0]-points[1], points[0]-points[2])
    #area = .5* np.linalg.norm(normal)
    #normal = normal/(2*area)
    #bna = np.dot(barycenter, normal*area)

    bna = np.dot(barycenter, normal/2)
    return bna

def side(domain, element, side_num, elevation):
    """
    Calculates dot(x, n*A) where x is the barycenter, n is the normal vector to
    the surface defined by z and the element verticies, and A is the area of
    the surface defined by z and the element vertices.

    :param domain: :class:`~polyadcirc.run_framework.domain`
    :param element: list of nodes defining an element 
    :type element: array_like  
    :param elevation: eta, sea surface height (NOT WATER COLUMN HEIGHT)
    :type z: :class:`np.array` 
    :rtype: double
    :returns: dot(x, n*A)

    """
    surface_points = []
    bottom_points = []
    points = []
    for i in element[quad_faces[side_num]]:
        n = domain.node[i]
        if elevation[i-1] != -99999.000: # if node is wet
            surface_points.append(np.array([n.x, n.y, elevation[i-1]]))
            bottom_points.append(np.array([n.x, n.y, -domain.bathymetry[i-1]]))
        else: # node is dry
            points.append(np.array([n.x, n.y, -domain.bathymetry[i-1]]))
    # check to see if dry, partially dry, or wet
    if len(points) == 2: # Dry
        bna = 0 
    elif len(points) == 1: # Partially dry
        points.append(surface_points[0])
        points.append(bottom_points[0])
        barycenter = np.average(points, 0)
        normal = np.cross(points[0]-points[1], points[0]-points[2])
        bna = np.dot(barycenter, normal/2)
    else: # Wet
        barycenter = np.average(np.vstack((surface_points, bottom_points)), 0)
        normal = np.cross(bottom_points[0]-surface_points[1],
                          bottom_points[1]-surface_points[0])
        bna = np.dot(barycenter, normal/2)

    return bna
