import os
import reframe.utility.sanity as sn

from reframe.core.pipeline import RegressionTest


class IorCheck(RegressionTest):
    def __init__(self, name, fs_mount_point, **kwargs):
        super().__init__('IOR_%s_check_%s' % (name, os.path.basename(fs_mount_point)),
                         os.path.dirname(__file__), **kwargs)
        self.descr = 'IOR check (%s)' % fs_mount_point
        self.tags = {'ops', fs_mount_point}

        if fs_mount_point == '/scale_akl_nobackup/filesets/nobackup':
            self.valid_systems = ['kupe:compute']
            self.duplex_nodes = 52
            self.duplex_ppn = 2
            self.duplex_bsize = '2g'

            self.fs_reference = {
                # measurments are obtained in MiB (MiB *1024*1024 / 1000/ 1000 = MB/s = 0.95367431640625 MiB/s)
                '/scale_akl_nobackup/filesets/nobackup': {
                    's_read_bw_8m':  (2679, -0.2, None),  #2.62 GB/s write; 2.81GB/s read
                    's_write_bw_8m': (2498, -0.2, None),
                    's_read_bw_4k':  (3452, -0.2, None),  #2.69 GB/s write; 3.62GB/s read (in BM with IOBUF)
                    's_write_bw_4k': (2565, -0.2, None),
                    'd_read_bw_8m':  (3819, -0.2, None),  #40.05 GB/s read; 30.95GB/s write
                    'd_write_bw_8m': (2952, -0.2, None)
                }
            }
        elif fs_mount_point == '/scale_wlg_nobackup/filesets/nobackup':
            self.valid_systems = ['maui:compute', 'mahuika:compute']


        self.valid_prog_environs = ['PrgEnv-cray']
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'IOR')
        self.executable = os.path.join('src', 'C', 'IOR')
        self.fs_mount_point = fs_mount_point
#TODO get a IOR test directory
        self.test_file = os.path.join(self.fs_mount_point, 'schoenherrm', '.ior', #'read',
                                      'ior.dat')
        self.maintainers = ['Man']

        # Default umask is 0022, which generates file permissions -rw-r--r--
        # we want -rw-rw-r-- so we set umask to 0002
        os.umask(2)
        self.time_limit = (0, 30, 0)
        # Our references are based on fs types but regression needs reference
        # per system.
        self.reference = {
            '*': self.fs_reference[self.fs_mount_point]
        }

    def compile(self):
        super().compile(options='-C src/C posix mpiio')

class SingleIorCheck(IorCheck):
    def __init__(self, t_size, fs_mount_point, ior_type, **kwargs):
        super().__init__('single_r_w_%s'%t_size, fs_mount_point, **kwargs)

        self.num_tasks = 1
        self.num_tasks_per_node = 1
        blocksize='128g'
        
        self.variables = {
                       'IOBUF_PARAMS': '*IOR_POSIX*:count=32:size=1g:prefetch=8:preflush=8',
                       'DVS_BLOCKSIZE': '8388608',
                       'DVS_MAXNODES': '19'}
        self.executable_opts = ('-C -e -F -g -vv -w -r -a '+ ior_type +' -b ' + blocksize + ' -t ' + t_size + ' -o ' + self.test_file).split()

        self.sanity_patterns = sn.assert_found(r'^Max Read: ', self.stdout)

        p_name = 's_write_bw_%s'%t_size
        self.perf_patterns = {
            p_name: sn.extractsingle(
                r'^Max Write:\s+(?P<'+p_name+'>\S+) MiB/sec', self.stdout,
                p_name, float)
        }

        p_name = 's_read_bw_%s'%t_size
        self.perf_patterns = {
            p_name: sn.extractsingle(
                r'^Max Read:\s+(?P<'+p_name+'>\S+) MiB/sec', self.stdout,
                p_name, float)
        }
        self.tags |= {'read', 'write'}


#class SingleIorWriteCheck(IorCheck):
#    def __init__(self, t_size, fs_mount_point, ior_type, **kwargs):
#        super().__init__('single_ior_write_check_%s'%t_size, fs_mount_point, **kwargs)
#        self.num_tasks = 1
#        self.num_tasks_per_node = 1
#        blocksize='128g'
#
#        self.executable_opts = ('-w -k -a '+ ior_type +' -B -F -b ' + blocksize + ' -t ' + t_size + ' -e -D 240 -o ' + self.test_file).split()
#
#        self.sanity_patterns = sn.assert_found(r'^Max Write: ', self.stdout)
#        p_name = 's_write_bw_%s'%t_size
#        self.perf_patterns = {
#            p_name: sn.extractsingle(
#                r'^Max Write:\s+(?P<'+p_name+'>\S+) MiB/sec', self.stdout,
#                p_name, float) 
#        }
#        self.tags |= {'write'}

#TODO create file for reading, since we could handle the test asyncronously 
class DuplexIorCheck(IorCheck):
    def __init__(self, name, t_size, fs_mount_point, ior_type, **kwargs):
        super().__init__('%s_%s'%(name,t_size), fs_mount_point, **kwargs)

        self.num_tasks = self.duplex_nodes
        self.num_tasks_per_node = self.duplex_ppn
        blocksize= self.duplex_bsize

        self.variables = {'DVS_BLOCKSIZE': '8388608',
                       'DVS_MAXNODES': '2',
                       'DVS_CACHE': 'off',
                       'DVS_READONLY_CACHE': 'on'}

        self.executable_opts = ('-a '+ ior_type +' -B -F -b ' + blocksize + ' -t ' + t_size + ' -e -D 240 -o ' + self.test_file).split()

class DuplexIorReadCheck(DuplexIorCheck):
    def __init__(self, t_size, fs_mount_point, ior_type, **kwargs):
        super().__init__('duplex_read', t_size, fs_mount_point, ior_type, **kwargs)

        self.executable_opts.append('-r -E')

        self.sanity_patterns = sn.assert_found(r'^Max Read: ', self.stdout)
        p_name = 'd_read_bw_%s'%t_size
        self.perf_patterns = {
            p_name: sn.extractsingle(
                r'^Max Read:\s+(?P<'+p_name+'>\S+) MiB/sec', self.stdout,
                p_name, float)
        }
        self.tags |= {'read'}


class DuplexIorWriteCheck(DuplexIorCheck):
    def __init__(self, t_size, fs_mount_point, ior_type, **kwargs):
        super().__init__('duplex_write', t_size, fs_mount_point, ior_type, **kwargs)

        self.executable_opts.append('-w -k')

        self.sanity_patterns = sn.assert_found(r'^Max Write: ', self.stdout)
        p_name = 'd_write_bw_%s'%t_size
        self.perf_patterns = {
            p_name: sn.extractsingle(
                r'^Max Write:\s+(?P<'+p_name+'>\S+) MiB/sec', self.stdout,
                p_name, float)
        }
        self.tags |= {'write'}



def _get_checks(**kwargs):
    ret = [
           DuplexIorWriteCheck('8m', '/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs),
           DuplexIorReadCheck( '8m', '/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs),

           SingleIorCheck('8m', '/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs),
#           SingleIorReadCheck( '8m', '/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs),
           SingleIorCheck('4k', '/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs),
#           SingleIorReadCheck( '4k', '/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs),

    ]
    return ret
