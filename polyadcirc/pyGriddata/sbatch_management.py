"""
This module is designed to read/write slurm batch (sbatch) submission scripts.
"""

import glob, os, re, subprocess

class sbatch_option(object):
    """
    Class that parses and stores a sbatch option line.
    """
    def __init__(self, line):
        """
        Initialization
        """
        #: string, comment
        split_line  = line.split("#")
        self.comment = None
        if len(split_line) == 2:
            # there is no comment
            _, left = split_line
        elif len(split_line) == 3:
            # there is a comment
            _, left, self.comment = split_line
        #: string, option - sbatch option flag
        #: string, separator - separator between the flag and the value
        #: string, value - assigned to the option
        m = re.match(r"SBATCH\s*-(-\w[^= ]*|\w*)(=|\s*)(.*)", left)
        self.option, self.separator, self.value = m.groups()
        super(sbatch_option, self).__init__()
    
    def __str__(self):
        """
        Formats the sbatch job submission option

        :rtype: string
        :returns: Formatted sbatch option line

        """
        line = "#SBATCH -{}{}{}".format(self.option, self.separator,
                self.value)
        if self.comment:
            line += " #{}".format(self.comment)
        else:
            line +="\n"
        return line

def read_sbatch(sbatch_file=None):
    """
    Read in job submission script and store sbatch options in a dictionary. The
    annotated list is a list of tuples where the first member is "o"-sbatch
    option, "c"-bash comment, or "b"-bash command and the second member is
    either the string for the line or a
        :class:`~bet.pyGriddata.sbatch_management` object

    :param string sbatch_file: job submission script name
    :rtype: :class:`list`
    :returns: An annotated list of the lines in the submission script.

    """
    sbatch_list = list()
    with open(sbatch_file, 'r') as sf:
        for line in sf:
            m = re.match(r"^#SBATCH -.*", line)
            c = re.match(r"^#.*", line)
            if m != None:
                sbatch_op = sbatch_option(line)
                sbatch_list.append(('o', sbatch_op))
            elif c != None:
                sbatch_list.append(('c', line))
            else:
                sbatch_list.append(('b', line))
    return sbatch_list

def write_sbatch(sbatch_file, sbatch_list):
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
                sf.write(str(line))

def submit_job(sbatch_file, dir):
    """
    Submits the job using the job submission script ``sbatch_file`` and returns
    the jobid.

    :param string sbatch_file: job submission script name
    :param string dir: directory to submit the script in, if ``None`` uses
        ``os.path`` to determine the dir from ``sbatch_file``
    :rtype: string
    :returns: jobid
    """
    if dir == None:
        dir = os.path.dirname(sbatch_file)
        sbatch_file = os.path.basename(sbatch_file)
    #output = subprocess.check_call(['sbatch','sbatch_file'], shell=True, cwd=dir)
    output = subprocess.check_output(["tail", "submitout.txt"], shell=True)
    for line in output.split('\n'):
        m = re.match("Submitted batch job (\d*)", line)
        if m:
            break
    jobid = m.groups()[-1]
    return jobid

def add_dependency(sbatch_list, jobid_list):
    """
    """
    pass
            
