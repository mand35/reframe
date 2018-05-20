import os
import reframe.utility.sanity as sn

from reframe.core.pipeline import RegressionTest


class MDTest_BM(RegressionTest):
    def __init__(self, mdtest_type, **kwargs):
        super().__init__('MDTest_%s'%mdtest_type, os.path.dirname(__file__), **kwargs)
        self.descr = 'MDTest check (%s)' % mdtest_type
        self.tags = {'ops', mdtest_type}

        self.valid_systems = ['kupe:compute']
        self.num_tasks = 64
        self.num_tasks_per_node = 2
        self.time_limit = (0, 35, 0)

        self.valid_prog_environs = ['PrgEnv-cray']

        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'MDTest')
        self.executable = os.path.join('src', 'mdtest', 'mdtest')
        items_per_rank = 1048576 / self.num_tasks
        test_dir = os.path.join('testdir')
        exe_opts = '-v -F -C -T -r -n %s -d %s -N %s -i 1 ' % (items_per_rank, test_dir, self.num_tasks_per_node) 

        if mdtest_type == 'shared':
          self.executable_opts = ('%s' % exe_opts).split()
        elif mdtest_type == 'unique':
          self.executable_opts = ('%s -u ' % exe_opts).split()
        elif mdtest_type == 'single':
          self.executable_opts = ('%s -s ' % exe_opts).split()

        self.sanity_patterns = sn.assert_found(r'^\s+File creation', self.stdout)

        p_name = "{}_creation".format(mdtest_type)
        self.perf_patterns = { p_name: sn.extractsingle(
              r'^\s+File creation\s+:\s+(?P<'+p_name+'>\S+) ', self.stdout, p_name, float)
        }
        p_name = "{}_stat".format(mdtest_type)
        self.perf_patterns = { p_name: sn.extractsingle(
              r'^\s+File stat\s+:\s+(?P<'+p_name+'>\S+) ', self.stdout, p_name, float)
        }
        p_name = "{}_remove".format(mdtest_type)
        self.perf_patterns = { p_name: sn.extractsingle(
              r'^\s+File removal\s+:\s+(?P<'+p_name+'>\S+) ', self.stdout, p_name, float)
        }


        self.reference = {
            'kupe:compute': {
                'shared_creation': (20000, None, 0.05), 
                'unique_creation': (26245, None, 0.05), 
                'single_creation': (36757, None, 0.05), 
            },
        }

        self.maintainers = ['Man']
        self.tags |= {'BM'}

    def compile(self):
        super().compile(options=' -C src/mdtest CC=cc ')

class MDTest_PDT(RegressionTest):
    def __init__(self, procs, **kwargs):
        super().__init__('MDTest_PDT', os.path.dirname(__file__), **kwargs)
        self.descr = 'MDTest check PDT' 

        if procs == 64:
#TODO was Maui also running on 64 treads?
          self.valid_systems = ['kupe:compute', 'maui:compute']
        elif procs ==36:
#TODO how mani PPN were used?
          self.valid_systems = ['mahuika:compute']
        self.num_tasks = procs
        self.num_tasks_per_node = 16
        self.time_limit = (0, 35, 0)

        self.valid_prog_environs = ['PrgEnv-cray']

        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'MDTest')
        self.executable = os.path.join('src', 'mdtest', 'mdtest')
        test_dir = os.path.join('testdir')
        self.executable_opts = '-F -C -T -r -n 16384 -N 16 -d {}'.format(test_dir).split()

        self.sanity_patterns = sn.assert_found(r'^\s+File creation', self.stdout)

        self.perf_patterns = {}
        p_names = {'creation', 'stat', 'removal'}
        for p_name in p_names:
           self.perf_patterns[p_name] = sn.extractsingle(r'^\s+File '+p_name+'\s+:\s+(?P<'+p_name+'>\S+) ', self.stdout, p_name, float)

        kupe_mdres = {}
        kupe_mdres['creation'] = (7747,  -(2*223.1)/7747, None)
        kupe_mdres['stat'] =     (16527, -(2*558.2)/16527,None)
        kupe_mdres['removal'] =  (7355, -(2*173.1)/7355, None)
        self.reference = {
            'kupe:compute' : {
                'creation' : (7747,  -(2*223.1)/7747, None),
                'stat' :     (16527, -(2*558.2)/16527,None),
                'removal' :  (7355, -(2*173.1)/7355, None)
            },
            'mahuika:compute' : {
                'creation' : (8347,  -(2*108)/8347, None),
                'stat' :     (12213, -(2*256)/12213,None),
                'removal' :  (4672, -(2*84)/4672, None)
            },
           'maui:compute' : {
                'creation' : (9432,  -(2*239)/9432, None),
                'stat' :     (14119, -(2*302)/14119,None),
                'removal' :  (6739, -(2*271)/6739, None)
        }
    
        self.maintainers = ['Man']
        self.tags |= {'PDT'}

    def compile(self):
        super().compile(options=' -C src/mdtest CC=cc ')


def _get_checks(**kwargs):
    ret = [
           #MDTest_BM('shared', **kwargs),
           MDTest_BM('unique', **kwargs),
           MDTest_BM('single', **kwargs),
           MDTest_PDT(64, **kwargs)
           MDTest_PDT(36, **kwargs) # Mahuika
    ]
    return ret
