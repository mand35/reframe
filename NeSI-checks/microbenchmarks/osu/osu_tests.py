import os
import itertools
import reframe.utility.sanity as sn

from reframe.core.pipeline import RegressionTest


class AlltoallBaseTest(RegressionTest):
    def __init__(self, name, **kwargs):
        super().__init__(name,
                         os.path.dirname(__file__), **kwargs)
        self.strict_check = False
        self.valid_systems = ['kupe:compute', 'maui:compute', 'mahuika:compute']
        self.descr = 'Alltoall osu microbenchmark'
        self.executable = './osu_alltoall'
        # The -x option controls the number of warm-up iterations
        # The -i option controls the number of iterations
        self.executable_opts = ['-m', '8', '-x', '1000', '-i', '20000']
        self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu',
                                    'PrgEnv-intel']
        self.maintainers = ['Man']
        self.sanity_patterns = sn.assert_found(r'^8', self.stdout)
        self.perf_patterns = {
            'perf': sn.extractsingle(r'^8\s+(?P<perf>\S+)',
                                     self.stdout, 'perf', float)
        }
        self.num_tasks_per_node = 1
        self.num_gpus_per_node  = 1
        if self.current_system.name == 'mauhika':
            self.num_tasks = 6

        if self.current_system.name == 'kupe':
            self.num_tasks = 16

        self.extra_resources = {
            'switches': {
                'num_switches': 1
            }
        }

    def compile(self):
        super().compile(makefile='Makefile_alltoall')


class AlltoallProdTest(AlltoallBaseTest):
    def __init__(self, **kwargs):
        super().__init__('alltoall_osu_microbenchmark', **kwargs)
        self.tags = {'production'}
        self.reference = {
            'kupe:compute': {
                'perf': (11, None, 0.1)
            },
            'maui:compute': {
#TODO update the value
                'perf': (20.73, None, 2.0)
            },
        }

def _get_checks(**kwargs):
    #fixed_tests = [AlltoallProdTest(**kwargs)]
    #return list(itertools.chain(fixed_tests, range(2, 10, 2)))
    return [AlltoallProdTest(**kwargs)] 
