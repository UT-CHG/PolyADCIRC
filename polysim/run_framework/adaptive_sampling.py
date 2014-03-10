# Lindley Graham 3/10/2014
"""
This modules contains functions for adaptive random sampling. We assume we are
given access to a model, a parameter space, and a data space. The model is a
map from the paramter space to the data space. We desire to build up a set of
samples to solve an inverse problem thus giving us information about the
inverse mapping. The each sample consists of a parameter coordinate, data
coordinate pairing. We assume we are given a measure on both spaces.

We employ an approach based on using multiple sample chains in a MCMC type
approach.
"""

import numpy as np
from polysim.pyADCIRC.basic import pickleable

class adaptiveSamples(pickleable):
    """
    This class provides methods for adaptive sampling of parameter space to
    provide samples to be used by algorithms to solve inverse problems. 

    samples
        list of num_batches of samples (samples_0, samples_1, ...)
    num_batches
        number of batches of samples
    samples_per_batch
        number of samples per batch (either a single int or a list of int)
    metric
        metric on the data space, a function d(x,y) where d: M x M --> \Real
    model
        runs the model at a given set of parameter samples and returns data
    """
    def __init__(self, num_batches, samples_per_batch, metric):
        """
        Initialization
        """
        self.samples = list()
        self.num_batches = num_batches
        self.samples_per_batch = samples_per_batch
        self.metric = metric
        self.model = model

    def adaptive_algorithm(self):
        """
        Basic adaptive sampling algorithm.
        
        :rtype: tuple
        :returns: (``parameter_samples``, ``data_samples``) where
            ``parameter_samples`` is np.ndarray of shape 


