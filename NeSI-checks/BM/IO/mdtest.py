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
    def __init__(self, **kwargs):
        super().__init__('MDTest_PDT', os.path.dirname(__file__), **kwargs)
        self.descr = 'MDTest check PDT' 

        self.valid_systems = ['kupe:compute']
        self.num_tasks = 64
        self.num_tasks_per_node = 16
        self.time_limit = (0, 35, 0)

        self.valid_prog_environs = ['PrgEnv-cray']

        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'MDTest')
        self.executable = os.path.join('src', 'mdtest', 'mdtest')
        test_dir = os.path.join('testdir')
        exe_opts = '-F -C -T -r -n 16384 -N 16 -d {}'.format(test_dir)

        self.sanity_patterns = sn.assert_found(r'^\s+File creation', self.stdout)

        p_name = "creation"
        self.perf_patterns = { p_name: sn.extractsingle(
              r'^\s+File creation\s+:\s+(?P<'+p_name+'>\S+) ', self.stdout, p_name, float)
        }
        p_name = "stat"
        self.perf_patterns = { p_name: sn.extractsingle(
              r'^\s+File stat\s+:\s+(?P<'+p_name+'>\S+) ', self.stdout, p_name, float)
        }
        p_name = "remove"
        self.perf_patterns = { p_name: sn.extractsingle(
              r'^\s+File removal\s+:\s+(?P<'+p_name+'>\S+) ', self.stdout, p_name, float)
        }

        self.reference = {
            'kupe:compute': {
                'creation': (7747,  -(2*223.1)/7747, None),
                'stat':     (16527, -(2*558.2)/16527,None),
                'remove':   (7355,  -(2*173.1)/7355, None),
            },
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
           MDTest_PDT(**kwargs)
    ]
    return ret
