#! /usr/bin/env/python
# import necessary modulees
import polysim.run_framework.subdomain as subdom
import polysim.run_framework.fulldomain as fulldom
import glob
import polysim.run_framework.plotADCIRC as pa

adcirc_dir = '/h1/lgraham/workspace'
fulldomain = fulldom.fulldomain(adcirc_dir+'/ADCIRC_landuse/Inlet/inputs/tides')
subdomain = subdom.subdomain(adcirc_dir+'/ADCIRC_landuse/Inlet_subdomain/inputs/tides')
subdomain.set_fulldomain(fulldomain)
num_procs = 2

fulldomain.update()
subdomain.update()

# Compare subdomain and fulldomain results
ts_names = ['fort.63', 'fort.64']
nts_names = ['maxele.63','maxvel.63', 'tinun.63','elemaxdry.63']
subdomain.update_sub2full_map()
ts_error, nts_error, time_obs, ts_data, nts_data = subdomain.compare_to_fulldomain(ts_names, 
        nts_names)
subdomain.get_Triangulation(path = subdomain.path)
pa.ts_pcolor(ts_data, time_obs, subdomain, path = subdomain.path)
pa.nts_pcolor(nts_data, subdomain, path = subdomain.path)
pa.ts_quiver(ts_data, time_obs, subdomain, path = subdomain.path)
