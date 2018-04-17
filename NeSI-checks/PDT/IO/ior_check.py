import os
import reframe.utility.sanity as sn

from reframe.core.pipeline import RegressionTest


class IorCheck(RegressionTest):
    def __init__(self, name, fs_mount_point, **kwargs):
        super().__init__('%s_%s' % (name, os.path.basename(fs_mount_point)),
                         os.path.dirname(__file__), **kwargs)
        self.descr = 'IOR check (%s)' % fs_mount_point
        self.tags = {'ops', fs_mount_point}

        self.valid_systems = ['kupe:compute']
        self.num_tasks = 40
        self.num_tasks_per_node = 40

        self.valid_prog_environs = ['PrgEnv-cray']
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'IOR')
        self.executable = os.path.join('src', 'C', 'IOR')
        self.fs_mount_point = fs_mount_point
        self.maintainers = ['Man']
        self.fs_reference = {
            '/scale_akl_nobackup/filesets/nobackup': {
                'read_bw': (64326, -0.2, None),
                'write_bw': (151368, -0.2, None)
            },
            '/scale_akl_persistent/filesets/home': {
                'read_bw': (64326, -0.2, None),
                'write_bw': (151368, -0.2, None)
            },
        }



        # Default umask is 0022, which generates file permissions -rw-r--r--
        # we want -rw-rw-r-- so we set umask to 0002
        os.umask(2)
        self.time_limit = (0, 7, 0)
        # Our references are based on fs types but regression needs reference
        # per system.
        self.reference = {
            '*': self.fs_reference[self.fs_mount_point]
        }

    def compile(self):
        super().compile(options='-C src/C posix mpiio')

#TODO create file for reading, since we could handle the test asyncronously 
class IorReadCheck(IorCheck):
    def __init__(self, fs_mount_point, ior_type, **kwargs):
        super().__init__('ior_read_check', fs_mount_point, **kwargs)

        self.test_file = os.path.join(self.fs_mount_point, 'schoenherrm', '.ior', #'read',
                                      'ior_write.dat')
#        self.executable_opts = ('-r -a POSIX -B -E -F -t 1m -b 100m -D 60 '
#                                    '-k -o %s' % self.test_file).split()
        self.executable_opts = ('-r -E -a ' + ior_type + ' -B -F -b 8388608 -t 4m -e -D 240 -o ' + self.test_file).split()

        self.sanity_patterns = sn.assert_found(r'^Max Read: ', self.stdout)
        self.perf_patterns = {
            'read_bw': sn.extractsingle(
                r'^Max Read:\s+(?P<read_bw>\S+) MiB/sec', self.stdout,
                'read_bw', float)
        }
        self.tags |= {'read'}


class IorWriteCheck(IorCheck):
    def __init__(self, fs_mount_point, ior_type, **kwargs):
        super().__init__('ior_write_check', fs_mount_point, **kwargs)
        self.test_file = os.path.join(self.fs_mount_point, 'schoenherrm', '.ior', #'write',
                                      'ior_write.dat')
        self.executable_opts = ('-w -k -a ' + ior_type + ' -B -F -b 8388608 -t 4m -e -D 240 -o ' + self.test_file).split()

        self.sanity_patterns = sn.assert_found(r'^Max Write: ', self.stdout)
        self.perf_patterns = {
            'write_bw': sn.extractsingle(
                r'^Max Write:\s+(?P<write_bw>\S+) MiB/sec', self.stdout,
                'write_bw', float)
        }
        self.tags |= {'write'}

def _get_checks(**kwargs):
    ret = [
           IorWriteCheck('/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs),
           IorReadCheck('/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs),
           IorWriteCheck('/scale_akl_persistent/filesets/home', 'POSIX', **kwargs),
           IorReadCheck('/scale_akl_persistent/filesets/home', 'POSIX', **kwargs),
           IorWriteCheck('/scale_akl_persistent/filesets/home', 'MPIIO', **kwargs),
           IorReadCheck('/scale_akl_persistent/filesets/home', 'MPIIO', **kwargs),
    ]
    return ret
