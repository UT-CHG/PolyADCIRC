# Lindley Graham 03/25/13
"""
Flags all of the nodes in a grid file accordining to the flagging scheme for
:program:`Griddata_v1.32.F90`

1. Averaging
   Flag_value: -999.0 (x1), -950.0 (x2), -960.0 (x4), -970.0 (x8)
   This scheme evaluate the average to count the GIS database points which are
   inside of Grid scale. And this scheme can use different Grid scale size 
   classified by flag_value.
2. Highest point
   Flag_value: -888.0
   This scheme pick up the highest point of GIS database inside of Grid_scale.
3. Nearest point
   Flag_value: -777.0
   This scheme pick up the nearest point of GIS database inside of Grid_scale.
"""
import glob

def flag_fort14(grid_file_name="fort.14", avg_scheme=2):
    """ 
    Modifiy grid_file_name so that all of the nodes are flagged
    appropriately for Griddata program and save to flagged_grid_file_name.

    :param string grid_file_name: name of ``fort.14`` formatted file
    :param int avg_scheme: flag to choose which averaging scheme to use

    :rtype: string
    :returns: flagged file path

    """
    avg_flag = {1: -999.0, 2: -950.0, 4: -960.0, 8: -970.0, 'h' : -888.0, 'n':
                -777.0}
    print "Flagging values with "+str(avg_flag[avg_scheme])
    grid_dir, _, grid_file_name = grid_file_name.rpartition('/')
    prefix = "flagged_"
    flagged_file_path = grid_dir+'/'+prefix+grid_file_name
    with open(grid_dir+'/'+grid_file_name, 'r') as fid_read:
        with open(flagged_file_path , 'w') as fid_write:
            # Read and write grid name 
            fid_write.write(fid_read.readline())
            header_line_2 = fid_read.readline()
            # Read and write number of elements and nodes
            fid_write.write(header_line_2)
            # Store number of nodes, this might not be needed
            #match = re.match(r" +(\d+) +(\d+)", header_line_2)
            #node_num = int(match.group(2))
            # Read in and write out flagged nodal coordinates
            for line in fid_read:
                # This could probably be simpler
                a = line.strip().split()
                if len(a) == 4:
                    a[0] = int(a[0])
                    a[1] = float(a[1])
                    a[2] = float(a[2])
                    a[-1] = avg_flag[avg_scheme]
                    temp = ' {0:7d} {1:-9.8E}  '.format(a[0], a[1])
                    temp += '{:-9.8E}           {:-7.2f}\n'.format(a[2], a[3])
                    fid_write.write(temp)
                else:
                    fid_write.write(line)
    return flagged_file_path

def flag_fort14_go(grid, avg_scheme=2):
    """ 
    Given a gridInfo object create a flagged version of the
    ``grid.file_name`` and save to ``grid.file_name``

    :param grid: :class:`polyadcirc.pyGriddata.gridInfo.gridObject`
    :param int avg_scheme: flag to choose which averaging scheme to use

    See :meth:`~polyadcirc.pyADCIRC.flag_fort14.flag_fort14`

    :rtype: string
    :returns: flagged file path

    """
    return flag_fort14(grid.basis_dir+'/'+grid.file_name, avg_scheme)

if __name__ == "__main__":
    flag_fort14()
