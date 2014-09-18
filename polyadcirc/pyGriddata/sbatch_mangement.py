"""
This module is designed to read/write slurm batch (sbatch) submission scripts.
"""

import glob, os, re, subprocess

def read_sbatch(sbatch_file=None):
    """
    Read in job submission script and store sbatch options in a dictionary. The
    annotated list is a list of tuples where the first member is "o"-sbatch
    option, "c"-bash comment, or "b"-bash command and the second member is
    either the string for the line or 

    :param string sbatch_file: job submission script name
    :rtype: :class:`dict`, :class:`list`
    :returns: dictonary where the keys are option flags and the values are
        tuples of the (option values, comment), and an annotated list of the
        lines in the submission script.

    """
    sbatch_dict = dict()
    sbatch_list = list()
    with open(sbatch_file, 'r') as sf:
        for line in sf:
            m = re.match(r"^#SBATCH -([-\w]*[=|\s])(.*) #(.*)", line)
            c = re.match(r"^#.*", line)
            if m != None:
                sbatch_dict[m.group(1)] = (m.group(2), m.group(3))
                sbatch_list.append(('o', m.group(1)))
            elif c != None:
                sbatch_list.append(('c', line))
            else:
                sbatch_list.append(('b', line))
    return sbatch_dict, sbatch_list

def write_sbatch(sbatch_file, sbatch_dict, sbatch_list):
    """
    Given an annotated list of file lines and a :class:`dict` of sbatch options
    write a sbatch job submission script with the give comments, bash commands,
    and sbatch options.

    :param string sbatch_file: job submission script name
    :param dict sbatch_dict: dictionary of sbatch options
    :param list sbatch_list: annotated list of lines
    
    """
    with open(sbatch_file, 'w') as sf:
        for type, line in sbatch_list:
            # if the line is a comment or bash command print as is
            if type == "c" or type == "b":
                sf.write(line)
                # if the line is a sbatch option reformat the line and print it
            elif type == "o":
                option_line = '#SBATCH -{0}{1[0]} #{1[1]}\n'.format(line, sbatch_dict[line])
                sf.write(option_line)

def submit_job(sbatch_file):
    """
    Submits the job using the job submission script ``sbatch_file`` and returns
    the jobid.

    :param string sbatch_file: job submission script name
    :rtype: string
    :returns: jobid
    """
    pass


def add_dependency(sbatch_dict, jobid_list):
    """
    """
    pass
            
