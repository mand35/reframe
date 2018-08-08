import os
import reframe.utility.sanity as sn

from reframe.core.pipeline import RegressionTest
from reframe.utility.multirun import multirun


class IorCheck(RegressionTest):
    def __init__(self, name, procs, t_size, b_size, fs_mount_point, io_type, 
                 **kwargs):
        super().__init__('IOR_check_{0}_{1}_{2}_{3}_{4}'.format(
                         procs,b_size, io_type, 
                         os.path.basename(fs_mount_point),name),
                         os.path.dirname(__file__), **kwargs)
        self.descr = ('IOR check: {0} processes, {1} transfer size, '
                     '{2} block size on {3} '.format(procs,t_size,b_size, 
                     io_type, fs_mount_point))

        self.sourcesdir = os.path.join(self.current_system.resourcesdir, 'IOR')
        self.executable = os.path.join('src', 'C', 'IOR')
        self.fs_mount_point = fs_mount_point

        self.valid_prog_environs = ['PrgEnv-cray']
        #TODO get a IOR test directory
        self.test_file = os.path.join(self.fs_mount_point,'nesi99999/ReFrame',
           '.ior', 'ior_{0}_{1}_{2}.dat'.format(self.current_system.name, 
           t_size, b_size))
        os.umask(2)
        self.time_limit = (0, 55, 0)
        
        self.num_tasks = procs
        self.num_tasks_per_node = procs

        self.executable_opts = ['-a ', io_type, ' -C -e -F -g -t ', t_size, 
                                ' -b ', b_size, ' -vv -w -r -o ',
                                self.test_file]

        self.multirun_san_pat = [r'^Max Read: ', self.stdout]
        self.sanity_patterns = sn.assert_found(*self.multirun_san_pat)

        self.multirun_perf_pat = {}
        self.perf_patterns = {}
        for case in ['Write', 'Read']:
           p_name = '{0}_{1}_{2}_{3}'.format(case.lower(), procs,t_size,b_size)
           self.multirun_perf_pat[p_name] = [
              r'^Max {0}:\s+(?P<{1}>\S+) MiB/sec'.format(case, p_name), 
              self.stdout, p_name, float]
           self.perf_patterns[p_name] = sn.extractsingle(
              *(self.multirun_perf_pat[p_name]))

        if fs_mount_point == '/scale_akl_nobackup/filesets/nobackup':
            self.valid_systems = ['kupe:compute']
            
        elif fs_mount_point == '/scale_wlg_nobackup/filesets/nobackup':
            if procs == 36:
               self.valid_systems = ['mahuika:compute']
            else:
               self.valid_systems = ['maui:compute']


        self.multirun_ref = {
            'kupe:compute' : {
                'read_64_4m_8g' :  (8887, -(2*25.1)/8887, None),
                'write_64_4m_8g' : (6872, -(2*84.4)/6872, None),
                'read_1_4k_4g' :   (64, -(2*1.0)/64, None),
                'write_1_4k_4g' :  (70, -(2*2.3)/70, None)
            },
#TODO are 4k tests really on 64 / 36 threads?
            'maui:compute' : {
                'read_64_4m_8g' :  (8834, -(2*31)/8834, None),
                'write_64_4m_8g' : (6995, -(2*88)/6695, None),
                'read_64_4k_4g' :  (62, -(2*2.2)/62, None),
                'write_64_4k_4g' : (70, -(2*1.7)/70, None)
            },
            'mahuika:compute' : {
                'read_36_4m_8g' :  (6467, -(2*61)/6467, None),
                'write_36_4m_8g' : (5032, -(2*78)/5032, None),
                'read_36_4k_4g' :  (1025, -(2*20)/1025, None),
                'write_36_4k_4g' : (1936, -(2*46)/1936, None)
            }
        }

        self.maintainers = ['Man']
        self.tags |= {'PDT', fs_mount_point}

    def compile(self):
        super().compile(options='-C src/C posix mpiio')

def _get_checks(**kwargs):
    ret = [
           #IorCheck(64, '4m', '8g', '/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs), ## already defined for WLG BM set
           multirun(IorCheck)('', 1, '4k', '4g', 
              '/scale_akl_nobackup/filesets/nobackup', 'POSIX', **kwargs)]
    for case in ((36, '4m', '8g'),  (64, '4m', '8g'), 
                 (36, '4k', '4g'), (64, '4k', '4g')):
       ret.append(multirun(IorCheck)('', *case, 
              '/scale_wlg_nobackup/filesets/nobackup', 'POSIX', **kwargs))
    return ret
