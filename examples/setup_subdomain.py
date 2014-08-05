#! /usr/bin/env/python
# import necessary modules
import polysim.run_framework.subdomain as subdom
import polysim.run_framework.fulldomain as fulldom
import glob

adcirc_dir = '/work/01837/lcgraham/v50_subdomain/work'
fulldomain = fulldom.fulldomain(adcirc_dir+'/fulldomain')
subdomain = subdom.subdomain(adcirc_dir+'/subdomain')
subdomain.set_fulldomain(fulldomain)
num_procs = 2

# check to see if shape file exists, if not make it
if len(glob.glob(subdomain.path+'/shape.*14')) <= 0:
    subdomain.ellipse([40824.6, 98559.5], [98559.5, 40824,6], 60000)

# The following steps correspond to Table 1 in Subdomain ADICRC v.50 User Guide
# Step 1a Generate Sudomain
subdomain.setup()
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
