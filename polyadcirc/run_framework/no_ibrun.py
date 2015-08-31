# Copyright (C) 2013 Lindley Graham

"""
This file provides a mpirun work-around for clusters that do not have the ibrun
command.
"""
import os, stat

class random_manningsn(object):
    """
    This class is an implementation of
    :class:`polyadcirc.run_framework.random_manningsn` that provides a
    ``mpirun`` based work-around for clusters that do not have ibrun. It is
    probabaly system dependent and might need to be modified.
    """

    def __init__(self, script_name, fdir):
        self.script_name = script_name
        self.base_dir = fdir
        self.rf_dirs = ['dirone', 'dirtwo', 'dirthree']

    def write_run_script_no_ibrun(self, num_procs, num_jobs, procs_pnode, TpN,
                                  screenout=True, num_writers=None):
        """
        Creates a bash script called ``self.script_name`` in ``self.base_dir``
        and a set of rankfiles named ``rankfile_n`` to run multiple
        non-interacting parallel programs in parallel.

        :type num_procs: int
        :param num_procs: number of processes per job
        :type num_jobs: int
        :param num_jobs: number of jobs to run
        :param int procs_pnode: number of processors per node
        :param boolean screenout: flag (True --  write ``ADCIRC`` output to
            screen, False -- write ``ADCIRC`` output to temp file)
        :param int num_writers: number of MPI processes to dedicate soley to
            the task of writing ascii files
        :param int TpN: number of tasks (processors to use) per node (wayness)
        :rtype: string
        :returns: name of bash script for running a batch of jobs within our
            processor allotment

        """
        tmp_file = self.script_name.partition('.')[0]+'.tmp'
        # num_nodes = int(math.ceil(num_procs*num_jobs/float(TpN)))
        with open(os.path.join(self.base_dir, self.script_name), 'w') as f:
            f.write('#!/bin/bash\n')
            # change i to 2*i or something like that to no use all of the
            # processors on a node?
            for i in xrange(num_jobs):
                # write the bash file containing mpi commands
                #line = 'ibrun -n {:d} -o {:d} '.format(num_procs,
                #        num_procs*i*(procs_pnode/TpN))
                rankfile = 'rankfile{:d}'.format(i)
                line = 'mpirun -machinefile $TMP/machines -rf '
                line += rankfile+' -np {:d} '.format(num_procs)
                line += './padcirc -I {0} -O {0} '.format(self.rf_dirs[i])
                if num_writers:
                    line += '-W '+str(num_writers)+' '
                if not screenout:
                    line += '> '+tmp_file
                line += ' &\n'
                f.write(line)
                # write the rankfile containing the bindings
                with open(os.path.join(self.base_dir, rankfile), 'w') as frank:
                    for j in xrange(num_procs):
                        # rank, node_num, slot_nums
                        if TpN == procs_pnode:
                            line = 'rank {:d}=n+{:d} slot={:d}'.format(j,\
                                    (i*num_procs+j)/procs_pnode,\
                                    (i*num_procs+j)%procs_pnode)
                        else:
                            processors_per_process = procs_pnode/TpN
                            line = 'rank {:d}=n+{:d} slot={:d}-{:d}'.format(j,\
                                    (i*num_procs+j)/TpN,\
                                    ((i*num_procs+j)*processors_per_process)\
                                    %procs_pnode,\
                                    ((i*num_procs+j)*processors_per_process)\
                                    %procs_pnode+processors_per_process-1)
                        if j < num_procs-1:
                            line += '\n'
                        frank.write(line)
            f.write('wait\n')
        curr_stat = os.stat(os.path.join(self.base_dir, self.script_name))
        os.chmod(os.path.join(self.base_dir, self.script_name),
                 curr_stat.st_mode | stat.S_IXUSR)
        return self.script_name
