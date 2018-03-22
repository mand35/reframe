import os
import reframe.utility.sanity as sn

from reframe.core.pipeline import RegressionTest


class StreamTest(RegressionTest):
    def __init__(self, **kwargs):
        super().__init__('stream_benchmark',
                         os.path.dirname(__file__), **kwargs)
        self.descr = 'STREAM Benchmark'
        self.exclusive_access = True
        # All available systems are supported
        self.valid_systems = ['kupe:compute', 'maui:compute', 'mahuika:compute']
        self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu',
                                    'PrgEnv-intel']
        self.prgenv_flags = {
            'PrgEnv-cray': ' -homp ',
            'PrgEnv-gnu': ' -fopenmp -O3',
            'PrgEnv-intel': ' -qopenmp -O3'
        }
        self.sourcepath = 'stream.c'
        self.tags = {'production'}
        self.sanity_patterns = sn.assert_found(
            r'Solution Validates: avg error less than', self.stdout)
        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.stream_cpus_per_task = {
            'kupe:compute': 36,
            'maui:compute': 36,
            'mahuika:compute': 36,
        }

        self.variables = {
            'OMP_PLACES': 'threads',
            'OMP_PROC_BIND': 'spread',
        }
        self.stream_bw_reference = {
            'PrgEnv-cray': {
                'kupe:compute': {'triad': (150000, -0.05, None)},
# TODO to be definded
                'maui:compute': {'triad': (55983.9, -0.05, None)},
                'mahuika:compute': {'triad': (55983.9, -0.05, None)},
            },
            'PrgEnv-gnu': {
                'kupe:compute': {'triad': (150000, -0.05, None)},
# TODO to be definded
                'maui:compute': {'triad': (44052.8, -0.05, None)},
                'mahuika:compute': {'triad': (44052.8, -0.05, None)},
            },
            'PrgEnv-intel': {
                'kupe:compute': {'triad': (150000, -0.05, None)},
# TODO to be definded
                'maui:compute': {'triad': (53394.7, -0.05, None)},
                'mahuika:compute': {'triad': (53394.7, -0.05, None)},
            }
        }
        self.perf_patterns = {
            'triad': sn.extractsingle(r'Triad:\s+(?P<triad>\S+)\s+\S+',
                                      self.stdout, 'triad', float)
        }

        self.maintainers = ['RS', 'VK']

    def setup(self, partition, environ, **job_opts):
        self.num_cpus_per_task = self.stream_cpus_per_task[partition.fullname]
        super().setup(partition, environ, **job_opts)

        self.reference = self.stream_bw_reference[self.current_environ.name]
        # On SLURM there is no need to set OMP_NUM_THREADS if one defines
        # num_cpus_per_task, but adding for completeness and portability
        self.current_environ.variables['OMP_NUM_THREADS'] = \
            str(self.num_cpus_per_task)
        if self.current_environ.name == 'PrgEnv-pgi':
            self.current_environ.variables['OMP_PROC_BIND'] = 'true'

    def compile(self):
        prgenv_flags = self.prgenv_flags[self.current_environ.name]
        self.current_environ.cflags = prgenv_flags
        super().compile()


def _get_checks(**kwargs):
    return [StreamTest(**kwargs)]
