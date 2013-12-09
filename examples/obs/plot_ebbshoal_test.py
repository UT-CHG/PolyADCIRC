# test for playing around and testing stuff

# import necessary modules
import shelve

# setup and load from shelf
# set up saving
save_file = 'py_save_file.pat'
# shelf = shelve.open(save_file)
save_dir = '../../../ADCIRC_landuse/Ebbshoal/talea'
shelf = shelve.open(save_dir+'/'+save_file)
# load the domain
domain = shelf['domain']
# load the run setup
main_run = shelf['main_run']
mann_pts = shelf['mann_pts']
shelf.close()

# Plot stuff
main_run.make_plots(mann_pts, domain)
