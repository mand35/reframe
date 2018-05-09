import os
import reframe.utility.sanity as sn

from reframe.core.pipeline import RegressionTest


class MDTestCheck(RegressionTest):
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
        self.perf_patterns = { mdtest_type: sn.extractsingle(
              r'^\s+File creation\s+:\s+(?P<'+mdtest_type+'>\S+) ', self.stdout, mdtest_type, float)
        }
        self.reference = {
            'kupe:compute': {
                'shared': (20000, None, 0.05), 
                'unique': (26245, None, 0.05), 
                'single': (36757, None, 0.05), 
            },
        }

        self.maintainers = ['Man']

    def compile(self):
        super().compile(options=' -C src/mdtest CC=cc ')

def _get_checks(**kwargs):
    ret = [
           #MDTestCheck('shared', **kwargs),
           MDTestCheck('unique', **kwargs),
           MDTestCheck('single', **kwargs),
    ]
    return ret
