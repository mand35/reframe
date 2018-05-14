import os
import reframe.utility.sanity as sn

from reframe.core.pipeline import RegressionTest


class IorCheck(RegressionTest):
    def __init__(self, procs, t_size, b_size, fs_mount_point, io_type, **kwargs):
        super().__init__('IOR_check_{0}procs_{1}blocksize_{2}_{3}'.format(procs,b_size, io_type, os.path.basename(fs_mount_point)),
                         os.path.dirname(__file__), **kwargs)
        self.descr = 'IOR check using {0} processes, {1} transfer size, {2} block size on {3} '.format(procs,t_size,b_size, io_type, fs_mount_point)

        self.sourcesdir = os.path.join(self.current_system.resourcesdir, 'IOR')
        self.executable = os.path.join('src', 'C', 'IOR')
        self.fs_mount_point = fs_mount_point

        self.valid_prog_environs = ['PrgEnv-cray']
#TODO get a IOR test directory
        self.test_file = os.path.join(self.fs_mount_point, 'schoenherrm', '.ior', #'read',
                                      'ior.dat')
        os.umask(2)
        self.time_limit = (0, 30, 0)
        
        self.num_tasks = procs
        self.num_tasks_per_node = procs

        self.executable_opts = ('-a '+io_type+' -C -e -F -g -t ' + t_size + ' -b ' + b_size + ' -vv -w -r -o ' + self.test_file).split()

        self.sanity_patterns = sn.assert_found(r'^Max Read: ', self.stdout)

        self.perf_patterns = {}
        p_name = 'write_{0}_{1}_{2}'.format(procs,t_size,b_size)
        self.perf_patterns[p_name] = sn.extractsingle(
                r'^Max Write:\s+(?P<'+p_name+'>\S+) MiB/sec', self.stdout,
                p_name, float)

        p_name = 'read_{0}_{1}_{2}'.format(procs,t_size,b_size)
        self.perf_patterns[p_name] = sn.extractsingle(
                r'^Max Read:\s+(?P<'+p_name+'>\S+) MiB/sec', self.stdout,
                p_name, float)

        if fs_mount_point == '/scale_akl_nobackup/filesets/nobackup':
            self.valid_systems = ['kupe:compute']

            kupe_res = {}
            # measurments are obtained in MiB (MiB *1024*1024 / 1000/ 1000 = MB/s = 0.95367431640625 MiB/s)
            kupe_res['read_64_4m_8g']  =  (8887, -(2*25.1)/8887, None)
            kupe_res['write_64_4m_8g'] = (2498, -(2*84.4)/6872, None)
            kupe_res['read_1_4k_4g']   =  (64, -(2*1.0)/64, None)
            kupe_res['write_1_4k_4g']  = (70, -(2*2.3)/70, None)
            self.fs_reference = {
                '/scale_akl_nobackup/filesets/nobackup': kupe_res
            }
        elif fs_mount_point == '/scale_wlg_nobackup/filesets/nobackup':
            self.valid_systems = ['maui:compute', 'mahuika:compute']
            # TODO TBD

        # Our references are based on fs types but regression needs reference
        # per system.
        self.reference = {
            '*': self.fs_reference[self.fs_mount_point]
        }

        self.maintainers = ['Man']
        self.tags |= {'PDT', fs_mount_point}

    def compile(self):
        super().compile(options='-C src/C posix mpiio')

def _get_checks(**kwargs):
    ret = [
           IorCheck(64, '4m', '8g', '/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs),
           IorCheck( 1, '4k', '4g', '/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs),
    ]
    return ret
