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
import scipy.io as sio
from polysim.pyADCIRC.basic import pickleable

class adaptiveSamples(pickleable):
    """
    This class provides methods for adaptive sampling of parameter space to
    provide samples to be used by algorithms to solve inverse problems. 

    num_batches
        number of batches of samples
    samples_per_batch
        number of samples per batch (either a single int or a list of int)
    metric
        metric on the data space, a function d(x,y) where d: M x M --> \Real
    model
        runs the model at a given set of parameter samples and returns data
    """
    def __init__(self, num_batches, samples_per_batch, metric = None):
        """
        Initialization
        """
        self.num_batches = num_batches
        self.samples_per_batch = samples_per_batch
        if metric == None:
            self.metric = adaptiveSamples.default_metric
        else:
            self.metric = metric
        self.model = model

    def adaptive_algorithm(self, param_min, param_max, transition_kernel,
            heuristic, savefile):
        """
        Basic adaptive sampling algorithm.
        
        :param param_min: minimum value for each parameter dimension
        :type param_min: np.array (ndim,)
        :param param_max: maximum value for each parameter dimension
        :type param_max: np.array (ndim,)
        :param transition_kernel: method for creating new parameter steps using
            given a step size based on the paramter domain size
        :type transition_kernel: :class:~`transition_kernel`
        :param function heuristic: functional that acts on the data used to
            determine the ``step_size``
        :param string savefile: filename to save samples and data
        :rtype: tuple
        :returns: (``parameter_samples``, ``data_samples``) where
            ``parameter_samples`` is np.ndarray of shape (ndim, num_samples)
            and ``data_samples`` is np.ndarray of shape (num_samples, mdim)

        """
        # Initiative first batch of N samples (maybe taken from latin
        # hypercube/space-filling curve to fully explore parameter space - not
        # necessarily random). Call these Samples_old.
        samples_old = np.ones(len(param_min), self.samples_per_batch)
        samples = samples_old

        # Why don't we solve the problem at initial samples?
        data_old = self.model(initial_samples)
        heur_old = heuristic(data_old)
         
        # Initialize Nx1 vector Step_size = something reasonable (based on size
        # of domain and transition kernel type)
        # Calculate domain size
        param_width = param_max - param_min
        # Calculate step_size
        max_ratio = transition_kernel.max_ratio
        min_ratio = transition_kernel.min_ratio
        step_ratio = transition_kernel.init_ratio

        for batch in xrange(1, self.num_batches):
            # For each of N samples_old, create N new parameter samples using
            # transition kernel and step_ratio. Call these samples samples_new.
            step = transition_kernel.step(step_ratio, param_width)
            samples_new = samples_old + step 
            samples = np.concatenate((samples, samples_new), axis=1)

            # Solve the model for the samples_new.
            data_new = self.model(samples_new)

            # Make some decision about changing step_size(k).  There are
            # multiple ways to do this.
            # Determine proposed step size:
            # Assume that the heuristic acts as a functional on the data so
            # that heuristic(data).shape = (num_samples,)
            # Evaluate heuristic for new data.
            heur_new = heuristic(data_new)
            heur_diff = (heur_new-heur_old)/heuristic.MAX
            # Compare to heuristic for old data.
            # Is the heuristic NOT close?
            heur_close = np.logical_not(np.isclose(heur_diff, 0,
                atol=heuristic.TOL))
            # Is the heuristic greater/lesser?
            heur_greater = np.logical_and(heur_diff > 0, heur_close)
            heur_lesser = np.logical_and(heur_diff < 0, heur_close)

            # Determine step size
            proposal = np.ones(heur_new.shape)
            proposal[heur_greater] = 2.0
            proposal[heur_lesser] = 0.5
            step_ratio = proposal*step_ratio
            # Is the ratio greater than max?
            step_ratio[step_ratio > max_ratio] = max_ratio
            # Is the ratio less than min?
            step_ratio[step_ratio < min_ratio] = min_ratio

            # Save and export concatentated arrays
            print str(batch)+"th batch of "+str(self.num_batches)+" batches"
            samples = np.concatenate((samples, samples_new), axis=1)
            data = np.concatenate((data, data_new))
            mdat['samples'] = samples
            mdat['data'] = data
            sio.savemat(savefile, mdat, do_compression=True)

            # samples_old = samples_new
            samples_old = samples_new
            heur_old = heur_new


def class transition_kernel(pickleable):
    """
    Basic class that is used to create a step to move from samples_old to
    samples_new based. This class generates steps for a random walk using a
    very basic algorithm. Future classes will inherit from this one with
    different implementations of the
    :meth:~`polysim.run_framework.apdative_sampling.step` method.

    This basic transition kernel is designed without a preferential direction.

    init_ratio
        Initial step size ratio compared to the parameter domain.
    min_ratio
        Minimum step size compared to the inital step size.
    max_ratio
        Maximum step size compared to the maximum step size.
    """

    def __init__(self, init_ratio, min_ratio, max_ratio):
        """
        Initialization
        """
        self.init_ratio = ratio
        self.min_ratio = ratio
        self.max_ratio = ratio
    
    def step(self, step_ratio, param_width):
        """
        Generate ``num_samples`` new steps using ``step_ratio`` and
        ``param_width`` to calculate the ``step size``. Each step will have a
        random direction. For simplicity we constain all steps to be within a
        ball of L_1 norm defined by ``step_ratio*param_width``.

        :param step_ratio: define maximum step_size = ``step_ratio*param_width``
        :type step_ratio: :class:`np.array` of shape (num_samples,)
        :param param_width: width of the parameter domain
        :type param_width: np.array (ndim,)
        :rtype: :class:`np.array` of shape (ndim, num_samples)
        :returns: step

        """
        # calculate maximum step size
        step_size = np.outer(param_width, step_ratio)
        # randomize the direction (and size)
        step = step_size*(2.0*np.random.random(step_size.shape) - 1)
        return step


def class heuristic(pickleable):

    def __init__(self, maximum, tolerance):
        self.MAX = maximum
        self.TOL = tolerance



