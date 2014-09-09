#! /usr/bin/env/python
# import necessary modulees
import polyadcirc.run_framework.subdomain as subdom
import polyadcirc.run_framework.fulldomain as fulldom
import polyadcirc.run_framework.random_manningsn as rmn
import polyadcirc.pyADCIRC.volume as vol
import numpy as np
import scipy.io as sio

adcirc_dir = '/h1/lgraham/workspace'
fulldomain = fulldom.fulldomain(adcirc_dir+'/ADCIRC_landuse/Inlet/inputs/tides')
subdomain = subdom.subdomain(adcirc_dir+'/ADCIRC_landuse/Inlet_subdomain/inputs/tides')
subdomain.set_fulldomain(fulldomain)

# The following steps correspond to Table 1 in Subdomain ADICRC v.50 User Guide
# Step 1a Generate Sudomain
# subdomain.circle(0, 0, 3000)
# subdomain.setup()

# Read in fort.14, fort.15 data to subdomain and fulldomain objects
fulldomain.update()
subdomain.update()

# Read in and mapping between subdomain and fulldomain
subdomain.update_sub2full_map()

# Get list of elements in the subdomain in terms of fulldomain element numbers
elements = subdomain.sub2full_element.values()

# Get fort.63 data
fort63, time_obs = rmn.get_ts_sr(fulldomain.path, 'fort.63')
total_obs = fort63.shape[1]

# Calculate volumes
fulldomain.array_bathymetry()
volume = np.empty((total_obs,))
for i in xrange(total_obs):
    volume[i] = vol.sub_volume(fulldomain, fort63[:, i], elements)[0]

# Save to a MATLAB FILEi
# CHANGE THIS SO THAT IT JUST SAVES TO A TEXT FILE
mdict = {}
mdict['fort63'] = fort63
mdict['time_obs'] = time_obs
mdict['volume'] = volume
sio.savemat('volume_data', mdict, do_compression=True)
