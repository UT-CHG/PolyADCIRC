#! /usr/bin/env/python
# import necessary modulees
import polyadcirc.run_framework.subdomain as subdom
import polyadcirc.run_framework.fulldomain as fulldom
import glob

adcirc_dir = '/work/01837/lcgraham/v50_subdomain/work'
fulldomain = fulldom.fulldomain(adcirc_dir+'/ADCIRC_landuse/Inlet/inputs/tides')
subdomain = subdom.subdomain(adcirc_dir+'/ADCIRC_landuse/Inlet_subdomain/inputs/tides')
subdomain.set_fulldomain(fulldomain)
num_procs = 2

# The following steps correspond to Table 1 in Subdomain ADICRC v.50 User Guide
# Step 1a Generate Sudomain
subdomain.circle(2500, 0, 3000)
print subdomain.flag
subdomain.setup()
#subdomain.setup(flag = 1)
# Step 1b Generate Full Domain Control File
subdomain.genfull()
# Step 2 Run ADCIRC on the full domain
fulldomain.update()
if subdomain.check_fulldomain():
    disp =  "Output files ``fort.06*`` exist, but running ADCIRC on fulldomain"
    print disp+"anyway."
else:
    print "Output files ``fort.06*`` do not exist, running ADCIRC on fulldomain."
fulldomain.run(num_procs, adcirc_dir)
# Step 3 Exract Subdomain Boundary Conditions
subdomain.update()
subdomain.genbcs(h0 = 0)
# Step 4 Run ADCIRC on the subdomain
if subdomain.check():
    subdomain.run(num_procs, adcirc_dir)
else:
    print "Input file ``fort.019`` does not exit."

# Compare subdomain and fulldomain results
subdomain.update_sub2full_map()
ts_data, nts_data, time_obs = subdomain.compare_to_fulldomain(['fort.63',
                                'fort.64'],['maxele.63','maxvel.63'])
