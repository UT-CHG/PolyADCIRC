# Copyright (C) 2013 Lindley Graham

#pylint: disable=E1101, C0324
"""
A set of functions for plotting data from :class:`runSet`
"""
# import necessary modules
import numpy as np
import os
import polyadcirc.pyGriddata.file_management as fm
import polyadcirc.pyADCIRC.fort15_management as f15
import polyadcirc.pyGriddata.table_to_mesh_map as tmm
# import plotting modules
import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
import matplotlib.tri as tri
from matplotlib.collections import LineCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable

_stationmarkers = {'fort61':'bo', 'fort62':'go', 'fort71':'ro', 'fort72':'co',
                   'fort81':'yo', 'fort91':'ko'}

def get_Triangulation(domain, path=None, save=True, show=False, ics=1,
                      ext='.png', title=False):
    """
    :param domain: :class:`~polyadcirc.run_framework.domain`
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param int ics: coordinate system (1 cartisian, 2 polar)
    :param string ext: file extesion
    :rtype: :class:`matplotlib.tri.Triangulation`
    :returns: triangulation of ``domain``

    """

    x = np.array([n.x for n in domain.node.itervalues()])
    y = np.array([n.y for n in domain.node.itervalues()])
    triangles = np.array([e-1 for e in domain.element.itervalues()])
    triangulation = tri.Triangulation(x, y, triangles)
    plt.figure()
    if path == None:
        path = os.getcwd()
    fig_folder = os.path.join(path, 'figs')
    if not os.path.exists(fig_folder):
        fm.mkdir(fid_folder)
    if save or show:
        plt.triplot(triangulation, 'g-')
        if title:
            plt.title('grid')
        plt.gca().set_aspect('equal')
        add_2d_axes_labels(ics=ics)    
        save_show(os.path.join(fig_folder,'grid'), save, show, ext)
    domain.triangulation = triangulation
    return triangulation

def bathymetry(domain, path=None, save=True, show=False, mesh = False,
               contour = False, ics=1, ext='.png', title=False):
    """
    Given a domain, plot the bathymetry

    :param domain: :class:`~polyadcirc.run_framework.domain`
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :type mesh: boolean
    :param mesh: flag for whether or not to show mesh
    :param boolean contour: use :meth:`~np.pyplot.tripcolor` or
        :meth:`~np.pyplot.tricontour`
    :param int ics: coordinate system (1 cartisian, 2 polar)
    :param string ext: file extesion

    """
    z = domain.array_bathymetry()
    vmax = np.max(z)
    vmin = np.min(z)
    clim = (vmin, vmax)
    if path == None:
        path = os.getcwd()
    plt.figure()
    if mesh:
        plt.triplot(domain.triangulation, 'k-')
    if not contour:
        plt.tripcolor(domain.triangulation, z, shading='gouraud',
                      cmap=plt.cm.ocean)
    else:
        plt.tricontourf(domain.triangulation, z, cmap=plt.cm.ocean)
    plt.gca().set_aspect('equal')
    add_2d_axes_labels(ics=ics)    
    if clim:
        plt.clim(clim[0], clim[1])
    if title:
        plt.title('bathymetry')
    colorbar()
    save_show(os.path.join(path, 'figs', 'bathymetry'), save, show, ext)

def station_locations(domain, path=None, bathy = False, save=True, 
                      show=False, ics=1, ext='.png', station_markers=None):
    """
    Given a domain, plot the observation stations 
   
    :param domain: :class:`~polyadcirc.run_framework.domain`
    :type path: string or None
    :param path: directory to store plots
    :type bathy: boolean
    :param bathy: flat for whether or not to show bathymetry
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param int ics: coordinate system (1 cartisian, 2 polar)
    :param string ext: file extesion
 
    """
    plt.figure()
    if path == None:
        path = os.getcwd()
    if bathy:
        z = np.array([n.bathymetry for n in domain.node.itervalues()])
        plt.tripcolor(domain.triangulation, z, shading='gouraud',
                      cmap=plt.cm.ocean)
        plt.gca().set_aspect('equal')
    else:
        plt.triplot(domain.triangulation, 'k-')
        plt.gca().set_aspect('equal')

    if station_markers is None:
        station_markers = _stationmarkers
    
    for k, v in domain.stations.iteritems():
        x = np.array([e.x for e in v])
        y = np.array([e.y for e in v])
        plt.plot(x, y, station_markers[k], label = k)
    
    #plt.title('station locations')
    add_2d_axes_labels(ics=ics)    
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               ncol=2, mode="expand", borderaxespad=0.)
    save_show(os.path.join(path, 'figs', 'station_locations'), save, show, ext)

def field(domain, z, title, clim = None,  path=None, save=True, show =
          False, ics=1, ext='.png', cmap=plt.cm.jet):
    """
    Given a domain, plot the nodal value z
   
    :param domain: :class:`~polyadcirc.run_framework.domain`
    :param z: :class:`np.array`
    :param string title: plot title
    :param clim: :class:`np.clim`
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param int ics:  polar coordinate option (1 = cart coords, 2 = polar
        coords)
    :param string ext: file extension

    """
    if path == None:
        path = os.getcwd()
    plt.figure()
    plt.tripcolor(domain.triangulation, z, shading='gouraud',
                  cmap=cmap)
    plt.gca().set_aspect('equal')
    plt.autoscale(tight=True)
    if clim:
        plt.clim(clim[0], clim[1])
    add_2d_axes_labels(ics=ics)    
    colorbar()
    #plt.title(title)
    save_show(os.path.join(path, 'figs', title), save, show, ext)

def basis_functions(domain, bv_array, path=None, save=True, show=False,
                    ics=1, ext='.png', cmap = plt.cm.jet):
    """
    Given a ``bv_array`` containing basis functions, plot them
   
    :param domain: :class:`~polyadcirc.run_framework.domain`
    :type bv_array: :classnp.array`
    :param bv_array: array of basis vectors based on land classification
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param string ext: file extension

    """
    for i in xrange(bv_array.shape[1]):
        z = bv_array[..., i]
        field(domain, z, 'basis_function_'+str(i), (0.0,1.0) , path, save,
              show, ics, ext, cmap)

def random_fields(domain, points, bv_dict, path=None, save=True, show =
                  False, ics=1, ext='.png', cmap = plt.cm.jet):
    """
    Given a ``bv_dict`` a set of random points, plot the ``r_fields``
    generated in
    :meth:`~polyadcirc.run_framework.random_manningsn.runSet.run_points`
   
    :param domain: :class:`~polyadcirc.run_framework.domain`
    :type points: :class:`np.array`
    :param points: weights for points at which the random domain was sampled
    :type bv_dict: list of ``dict``
    :param bv_dict: list of basis vectors based on land classification
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param int ics:  polar coordinate option (1 = cart coords, 2 = polar
        coords)
    :param string ext: file extension

    """
    vmax = np.max(points)
    if vmax == 1.0:
        vmax = np.max(points[range(points.shape[0]-1), :])
    vmin = np.min(points)
    clim = (vmin, vmax)
    default = domain.read_default()
    for i in xrange(points.shape[1]):
        z = tmm.combine_basis_vectors(points[..., i], bv_dict, default,
            domain.node_num)
        field(domain, z, 'random_field_'+str(i), clim, path, save, show, ics,
              ext, cmap)

def mean_field(domain, points, bv_dict, path=None, save=True, show =
               False, ics=1, ext='.png'): 
    """
    Given a bv_dict a set of random points, plot the r_fields generated in
    random_manningsn.runSet.run_points
   
    :param domain: :class:`~polyadcirc.run_framework.domain`
    :type points: :class:`np.array`
    :param points: weights for points at which the random domain was sampled
    :type bv_dict: list of ``dict``
    :param bv_dict: list of basis vectors based on land classification    
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param int ics:  polar coordinate option (1 = cart coords, 2 = polar
        coords)
    :param string ext: file extension

    """
    vmax = np.max(points)
    if vmax == 1.0:
        vmax = np.max(points[range(points.shape[0]-1), :])
    vmin = np.min(points)
    clim = (vmin, vmax)
    default = domain.read_default()
    z = tmm.combine_basis_vectors(np.mean(points, 1), bv_dict, default,
        domain.node_num)
    field(domain, z, 'mean_field', clim, path, save, show, ics,  ext)

def station_data(ts_data, time_obs, keys=None, stations = None, path=None,
                 save=True, show=False, ext='.png'): 
    """
    Plot the station data in ``ts_data`` with ``time_obs`` as the x axis. To
    plot only a subset of this data list which ADCIRC Output types to plot in
    keys.

    :type ts_data: :class:`dict`
    :param ts_data: ``ts_data`` from
        :class:`~polyadcirc.run_framework.random_manningsn.runSet`
    :type time_obs: :class:`dict`
    :param time_obs: ``time_obs`` from
        :class:`~polyadcirc.run_framework.random_manningsn.runSet`
    :param list() keys: list of types of ADCIRC output data to plot 
    :param dict stations: dictonary of lists of stations to plot
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param string ext: file extension
    
    """
    if path == None:
        path = os.getcwd()
    


    if keys == None:
        keys = ts_data.keys()
    s_keys = list()
    for k in keys:
        if f15.filetype[k][0]:
            s_keys.append(k)
    keys = s_keys

    for k in keys:
        fm.mkdir(os.path.join(path, 'figs', k))
        if stations[k] == None:
            stations = xrange(ts_data[k].shape[0]) 
        for i in stations:
            fig = plt.figure()
            x = time_obs[k]

            num_plts = f15.filetype[k][1]
            
            if num_plts  == 1:
                ax = fig.add_subplot(111)
                ax.set_xlim((np.min(x),np.max(x)))
                ax.set_ylim((np.min(ts_data[k]),np.max(ts_data[k])))

                segs = list()
                for j in xrange(ts_data[k].shape[2]):
                    segs.append(zip(x, ts_data[k][i,...,j]))

                line_segs = LineCollection(segs, linestyles = 'solid')
                line_segs.set_array(np.arange(ts_data[k].shape[2]))
                ax.add_collection(line_segs)
                ax.set_xlabel('time')
                colorbar(line_segs)

            elif num_plts == 2:
                ax1 = fig.add_subplot(121)
                ax2 = fig.add_subplot(122)
                
                ax1.set_xlim((np.min(x),np.max(x)))
                ax1.set_ylim((np.min(ts_data[k][:,:,0,:]),
                              np.max(ts_data[k][:,:,0,:])))
                ax2.set_xlim((np.min(x),np.max(x)))
                ax2.set_ylim((np.min(ts_data[k][:,:,1,:]),
                              np.max(ts_data[k][:,:,1,:])))
                segs1 = list()
                segs2 = list()
                for j in xrange(ts_data[k].shape[-1]):
                    segs1.append(zip(x, ts_data[k][i,:,0,j]))
                    segs2.append(zip(x, ts_data[k][i,:,1,j]))

                line_segs1 = LineCollection(segs1, linestyles = 'solid')
                line_segs1.set_array(np.arange(ts_data[k].shape[-1]))
                ax1.add_collection(line_segs1)
                ax1.set_ylabel('u (m/s)')
                ax1.set_xlabel('time')
                line_segs2 = LineCollection(segs2, linestyles = 'solid')
                line_segs2.set_array(np.arange(ts_data[k].shape[-1]))
                ax2.add_collection(line_segs2)
                ax2.set_xlabel('time')
                ax2.set_ylabel('v (m/s)')
                colorbar(line_segs2)

            save_show(os.path.join(path, 'figs', k, 'station'+str(i)), save, show, ext)

def nts_line_data(nts_data, keys=None, path=None, save=True, show=False, 
                  ext='.png'): 
    """
    Plot the non timeseries data in ``data`` with ``points`` as the x axis. To
    plot only a subset of this data list which ADCIRC Output types to plot in
    keys.

    .. note:: This only applies to 1D nts data (``irtype`` = 1)

    :type nts_data: :class:`dict`
    :param nts_data: ``nts_data`` from
        :class:`~polyadcirc.run_framework.random_manningsn.runSet`
    :param list() keys: list of types of ADCIRC output data to plot 
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param string ext: file extension
    
    """
    if path == None:
        path = os.getcwd()

    if keys == None:
        keys = nts_data.keys()
    s_keys = list()
    for k in keys:
        if not(f15.filetype[k][0]) and f15.filetype[k][1] == 1:
            s_keys.append(k)
    keys = s_keys

    fm.mkdir(os.path.join(path, 'figs', 'nts'))

    for k in keys:
        fig = plt.figure()

        x = np.arange(nts_data[k].shape[0])
        ax = fig.add_subplot(111)
        ax.set_xlim((np.min(x),np.max(x)))
        ax.set_ylim((np.min(nts_data[k]),np.max(nts_data[k])))

        segs = list()

        for j in xrange(nts_data[k].shape[1]):
            segs.append(zip(x, nts_data[k][...,j]))

        line_segs = LineCollection(segs, linestyles = 'solid')
        line_segs.set_array(np.arange(nts_data[k].shape[1]))
        ax.add_collection(line_segs)
        colorbar(line_segs)
        fig.title(k)
        fig.xlabel('node number')
        save_show((os.path.join(path, 'figs', 'nts', k), save, show, ext)

def nts_pcolor(nts_data, domain, keys=None, points=None, path=None, 
               save=True, show=False, ics=1, ext='.png'): 
    """
    Plot the non timeseries data in ``nts_data`` as a set of 2D color plots. To
    plot only a subset of this data list which ADCIRC Output types to plot in
    keys, and which runs in ``points``.

    .. note:: This only applies to 1D nts data (``irtype`` = 1)

    :type nts_data: :class:``dict``
    :param nts_data: ``nts_data`` from
        :class:``~polyadcirc.run_framework.random_manningsn.runSet``
    :param domain: :class:`~polyadcirc.run_framework.domain`
    :param list() keys: list of types of ADCIRC output data to plot 
    :param list() points: list of runs to plot
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param int ics:  polar coordinate option (1 = cart coords, 2 = polar
    :param string ext: file extension

    """
    if path == None:
        path = os.getcwd()

    if keys == None:
        keys = nts_data.keys()
    s_keys = list()
    for k in keys:
        if k == 'timemax63':
            s_keys.append(k)
        elif not(f15.filetype[k][0]) and f15.filetype[k][1] == 1:
            s_keys.append(k)
    keys = s_keys

    if points == None:
        points = (0, nts_data[keys[0]].shape[-1]-1)

    if not os.path.exists(os.path.join(path, 'figs', 'nts')):
        fm.mkdir(os.path.join(path, 'figs', 'nts'))

    for k in keys:
        
        clim = (np.min(nts_data[k]),np.max(nts_data[k]))
        for j in points:
            plt.figure()
            plt.tripcolor(domain.triangulation, nts_data[k][:,j],
                          shading='gouraud', cmap=plt.cm.jet)
            plt.gca().set_aspect('equal')
            plt.clim(clim[0], clim[1])
            colorbar()
            add_2d_axes_labels(ics=ics)    
            plt.title(k+'_'+str(j))
            save_show(os.path.join(path, 'figs',
                'nts',k+'_'+str(j)+'_contour'), save, show, ext)

        if len(points) == 2:
            plt.figure(figsize=(6,9))
            plt.subplot(311)
            plt.tripcolor(domain.triangulation, nts_data[k][:,points[0]],
                          shading='gouraud', cmap=plt.cm.jet)
            plt.gca().set_aspect('equal')
            plt.clim(clim[0], clim[1])
            cb = colorbar()
            #add_2d_axes_labels(ics=ics)    
            cb.set_label(k+'_'+str(points[0]))
            
            plt.subplot(312)
            plt.tripcolor(domain.triangulation, nts_data[k][:,points[-1]],
                          shading='gouraud', cmap=plt.cm.jet)
            plt.gca().set_aspect('equal')
            plt.clim(clim[0], clim[1])
            cb = colorbar()
            #add_2d_axes_labels(ics=ics)    
            cb.set_label(k+'_'+str(points[-1]))

            plt.subplot(313)
            diff = nts_data[k][:,points[-1]] - nts_data[k][:,points[0]]
            plt.tripcolor(domain.triangulation, diff, shading='gouraud',
                          cmap=plt.cm.jet)
            plt.gca().set_aspect('equal')
            cb = colorbar()
            add_2d_axes_labels(ics=ics)    
            cb.set_label(k+'_'+'diff_{0}_{0}'.format(points))
            save_show(os.path.join(path, 'figs', 'nts', k+'_diff_contour'),
                    save, show, ext)

def ts_pcolor(ts_data, time_obs, domain, keys=None, points=None, 
              path=None, save=True, show=False, ics=1, ext='.png'): 
    """
    Plot the timeseries data in ``ts_data`` as a series of 2D color plots. To
    plot only a subset of this data list which ADCIRC Output types to plot in
    keys and which runs in points.

    .. note:: This only applies to 1D nts data (``irtype`` = 1)

    :type ts_data: :class:`dict`
    :param ts_data: ``ts_data`` from
        :class:`~polyadcirc.run_framework.random_manningsn.runSet`
    :type time_obs: :class:``dict``
    :param time_obs: ``time_obs`` from
        :class:`~polyadcirc.run_framework.random_manningsn.runSet`
    :param domain: :class:`~polyadcirc.run_framework.domain`
    :param list() keys: list of types of ADCIRC output data to plot 
    :param list() points: list of runs or points to plot
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param int ics:  polar coordinate option (1 = cart coords, 2 = polar)
    :param string ext: file extension
    
    """
    if path == None:
        path = os.getcwd()

    if keys == None:
        keys = ts_data.keys()
    s_keys = list()
    for k in keys:
        if not(f15.filetype[k][0]) and f15.filetype[k][1] == 1:
            s_keys.append(k)
    keys = s_keys

    if points == None:
        points = (0, ts_data[keys[0]].shape[-1]-1)

    fm.mkdir(os.path.join(path, 'figs', 'ts'))
    
    for k in keys:
        fig_folder = os.path.join(path, 'figs', 'ts', k)
        fm.mkdir(fig_folder)
        clim = (np.min(ts_data[k]),np.max(ts_data[k]))
        for j in points:
            subfig_folder = os.path.join(fig_folder, 'run'+str(j))
            fm.mkdir(subfig_folder)        
            for i, t in enumerate(time_obs[k]):
                plt.figure()
                add_2d_axes_labels(ics=ics)    
                plt.tripcolor(domain.triangulation, ts_data[k][:,i,j],
                              shading='gouraud', cmap=plt.cm.jet)
                plt.gca().set_aspect('equal')
                plt.clim(clim[0], clim[1])
                colorbar()
                plt.title('time = '+str(t))
                save_show(os.path.join(subfig_folder, str(i)), save, show, ext)

        if len(points) == 2:
            #TODO: stopped working here
            fm.mkdir(path+'/figs/ts/'+k+'/diff')
            
            diff = ts_data[k][:,:,points[-1]] - ts_data[k][:,:,points[0]]
            cdiff = (np.min(diff), np.max(diff))

            for i, t in enumerate(time_obs[k]):
                plt.figure(figsize=(6,9))
                ax1 = plt.subplot(311)
                plt.tripcolor(domain.triangulation, ts_data[k][:,i,points[0]],
                              shading='gouraud', cmap=plt.cm.jet)
                plt.gca().set_aspect('equal')
                plt.clim(clim[0], clim[1])
                cb = colorbar()
                #add_2d_axes_labels(ics=ics)    
                cb.set_label(k+'_'+str(points[0]))
                
                ax2 = plt.subplot(312)
                plt.tripcolor(domain.triangulation, ts_data[k][:,i,points[-1]],
                              shading='gouraud', cmap=plt.cm.jet)
                plt.gca().set_aspect('equal')
                plt.clim(clim[0], clim[1])
                cb = colorbar()
                #add_2d_axes_labels(ics=ics)    
                cb.set_label(k+'_'+str(points[-1]))

                ax3 = plt.subplot(313)
                plt.tripcolor(domain.triangulation, diff[:,i] ,
                              shading='gouraud', cmap=plt.cm.jet)
                plt.gca().set_aspect('equal')
                plt.clim(cdiff[0], cdiff[1])
                cb = colorbar()
                add_2d_axes_labels(ics=ics)    
                cb.set_label(k+'_'+'diff')
                plt.tight_layout()
                plt.suptitle('time = '+str(t))
                save_show(path+'/figs/ts/'+k+'/diff/'+str(i), save, show, ext)
 
def ts_quiver(ts_data, time_obs, domain, keys=None, points=None, 
              path=None, save=True, show=False, ics=1, ext='.png'): 
    """
    Plot the timeseries data in ``ts_data`` as a series of 2D quiver plots. To
    plot only a subset of this data list which ADCIRC Output types to plot in
    keys and which runs in points.

    .. note:: This only applies to 2D nts data (``irtype`` = 2)

    :type ts_data: :class:`dict`
    :param ts_data: ``ts_data`` from
        :class:`~polyadcirc.run_framework.random_manningsn.runSet`
    :type time_obs: :class:`dict`
    :param time_obs: ``time_obs`` from
        :class:`~polyadcirc.run_framework.random_manningsn.runSet`
    :param domain: :class:`~polyadcirc.run_framework.domain`
    :param list() keys: list of types of ADCIRC output data to plot 
    :param list() points: list of runs or points to plot
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param int ics:  polar coordinate option (1 = cart coords, 2 = polar
   

    .. todo:: maybe add plt.streamplot, but this requires a regularly spaced
        grid and is therefore more expenseive to do

    """
    if path == None:
        path = os.getcwd()

    if keys == None:
        keys = ts_data.keys()
    s_keys = list()
    for k in keys:
        if not f15.filetype[k][0] and f15.filetype[k][1] == 2:
            s_keys.append(k)
    keys = s_keys

    if points == None:
        points = (0, ts_data[keys[0]].shape[-1]-1)

    fm.mkdir(path+'/figs/ts_quiver')

    x = domain.array_x()
    y = domain.array_y()

    for k in keys:
        fm.mkdir(path+'/figs/ts_quiver/'+k)        
        mag = np.sqrt(pow(ts_data[k][:,:,0,:],2)+pow(ts_data[k][:,:,1,:],2))
        clim = (np.min(mag),np.max(mag))
        for j in points:
            fm.mkdir(path+'/figs/ts_quiver/'+k+'/run'+str(j))        
            for i, t in enumerate(time_obs[k]):
                plt.figure()
                add_2d_axes_labels(ics=ics)    
                plt.quiver(x, y, ts_data[k][:,i,0,j], ts_data[k][:,i,1,j],
                           mag[:,i,j])
                plt.gca().set_aspect('equal')
                plt.clim(clim[0], clim[1])
                colorbar()
                plt.title('time = '+str(t))
                save_show(path+'/figs/ts_quiver/'+k+'/run'+str(j)+'/'+str(i),
                          save, show, ext)

        if len(points) == 2:
            fm.mkdir(path+'/figs/ts_quiver/'+k+'/diff')
            
            diff = ts_data[k][:,:,:,points[-1]] - ts_data[k][:,:,:,points[0]]
            mag_diff = np.sqrt(pow(diff[:,:,0],2)+pow(diff[:,:,1],2))
            cdiff = (np.min(mag_diff), np.max(mag_diff))

            for i, t in enumerate(time_obs[k]):
                plt.figure(figsize=(6,9))
                ax1 = plt.subplot(311)
                plt.quiver(x, y, ts_data[k][:,i,0,points[0]],
                           ts_data[k][:,i,1,points[0]], mag[:,i,points[0]])                
                plt.gca().set_aspect('equal')
                plt.clim(clim[0], clim[1])
                cb = colorbar()
                #add_2d_axes_labels(ics=ics)    
                cb.set_label(k+'_'+str(points[0]))
                
                ax2 = plt.subplot(312)
                plt.quiver(x, y, ts_data[k][:,i,0,points[-1]],
                           ts_data[k][:,i,1,points[-1]], mag[:,i,points[-1]]) 
                plt.gca().set_aspect('equal')
                plt.clim(clim[0], clim[1])
                cb = colorbar()
                #add_2d_axes_labels(ics=ics)    
                cb.set_label(k+'_'+str(points[-1]))

                ax3 = plt.subplot(313)
                plt.quiver(x, y, diff[:,i,0], diff[:,i,1], mag_diff[:,i]) 
                plt.gca().set_aspect('equal')
                plt.clim(cdiff[0], cdiff[1])
                cb = colorbar()
                add_2d_axes_labels(ics=ics)    
                cb.set_label(k+'_'+'diff')
                plt.tight_layout()
                plt.suptitle('time = '+str(t))
                save_show(path+'/figs/ts_quiver/'+k+'/diff/'+str(i), save,
                          show, ext) 

def add_2d_axes_labels(fig = None , ics=1):
    """
    Add 2D axes labels for either cartesian or polar coordinates

    :param figure fig: :class:`matplotlib.pyplot.figure` object
    :param int ics:  polar coordinate option (1 = cart coords, 2 = polar)
    
    """
    if fig == None:
        fig = plt.gcf()
    if ics == 1:
        plt.xlabel('x (m)')
        plt.ylabel('y (m)')
    elif ics == 2:
        plt.xlabel('Longitude (degrees)')
        plt.ylabel('Latitude (degrees)')

def save_show(full_name, save, show, ext):
    """
    Save or show the current figure

    :param string full_name: path to save the figure
    :param boolean save: flag for whether or not to save plots
    :param boolean show: flag for whether or not to show plots
    :param string ext: file extension

    """
    plt.tight_layout()
    if save:
        plt.savefig(full_name+ext, bbox_inches='tight', transparent=True,
                    pad_inches=0.1)
    if show:
        plt.show()
    else:
        plt.close()

def colorbar(mappable = None):
    """
    Add a colorbar to the current figure/plot/subfigure/axes

    :param mappable: See `matplotlib <matplotlib.org>`_
    :param figure fig: Figure to add the colorbar to
    
    """
    ax = plt.gca()
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", "5%", pad="3%")
    return plt.colorbar(mappable, cax=cax)

def load_fig_gen_cmap():
    """
    .. todo:: Color map to match :program:`FigureGen`
    """
    pass

def nts_contour(nts_data, domain, keys=None, points=None, path=None, 
                save=True, show=False, ics=1, ext='.png'): 
    """
    Plot the non timeseries data in ``nts_data`` as a set of 2D contour plots.
    To plot only a subset of this data list which ADCIRC Output types to plot
    in keys, and which runs in ``points``.

    .. note:: This only applies to 1D nts data (``irtype`` = 1)

    :type nts_data: :class:`dict`
    :param nts_data: ``nts_data`` from
        :class:`~polyadcirc.run_framework.random_manningsn.runSet`
    :param domain: :class:`~polyadcirc.run_framework.domain`
    :param list() keys: list of types of ADCIRC output data to plot 
    :param list() points: list of runs to plot
    :type path: string or None
    :param path: directory to store plots
    :type save: boolean
    :param save: flag for whether or not to save plots
    :type show: boolean
    :param show: flag for whether or not to show plots
    :param int ics:  polar coordinate option (1 = cart coords, 2 = polar
    :param string ext: file extension
    
    """
    if path == None:
        path = os.getcwd()

    if keys == None:
        keys = nts_data.keys()
    s_keys = list()
    for k in keys:
        if not f15.filetype[k][0] and f15.filetype[k][1] == 1:
            s_keys.append(k)
    keys = s_keys

    if points == None:
        points = (0, nts_data[keys[0]].shape[-1]-1)

    fm.mkdir(path+'/figs/nts_contour')

    for k in keys:
        
        for j in points:
            plt.figure()
            plt.tricontour(domain.triangulation, nts_data[k][:,j],
                           shading='gouraud', cmap=plt.cm.jet)
            plt.gca().set_aspect('equal')
            colorbar()
            add_2d_axes_labels(ics=ics)    
            plt.title(k+'_'+str(j))
            save_show(path+'/figs/nts_contour/'+k+'_'+str(j)+'_contour', save,
                      show, ext)

        if len(points) == 2:
            plt.figure(figsize=(6,9))
            plt.subplot(311)
            plt.tricontour(domain.triangulation, nts_data[k][:,points[0]],
                           shading='gouraud', cmap=plt.cm.jet)
            plt.gca().set_aspect('equal')
            cb = colorbar()
            #add_2d_axes_labels(ics=ics)    
            cb.set_label(k+'_'+str(points[0]))
            
            plt.subplot(312)
            plt.tricontour(domain.triangulation, nts_data[k][:,points[-1]],
                           shading='gouraud', cmap=plt.cm.jet)
            plt.gca().set_aspect('equal')
            cb = colorbar()
            #add_2d_axes_labels(ics=ics)    
            cb.set_label(k+'_'+str(points[-1]))

            plt.subplot(313)
            diff = nts_data[k][:,points[-1]] - nts_data[k][:,points[0]]
            plt.tricontour(domain.triangulation, diff, shading='gouraud',
                           cmap=plt.cm.jet)
            plt.gca().set_aspect('equal')
            cb = colorbar()
            add_2d_axes_labels(ics=ics)    
            cb.set_label(k+'_'+'diff')
            save_show(path+'/figs/nts_contour/'+k+'_diff_contour', save, show,
                      ext)

