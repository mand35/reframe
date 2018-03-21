import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RegressionTest


class UlimitCheck(RegressionTest):

    def __init__(self, **kwargs):
        super().__init__('ulimit_check', os.path.dirname(__file__), **kwargs)
        self.descr = 'Checking the output of ulimit -s in node.'

        self.valid_systems = ['kupe:compute', 'maui:compute']
        self.valid_prog_environs = ['PrgEnv-cray',  'PrgEnv-gnu',
                                    'PrgEnv-intel']
        self.sourcepath = 'ulimit.c'
        self.tags = {'production'}

        self.sanity_patterns = sn.all([
            sn.assert_found(r'The soft limit is unlimited', self.stdout),
            sn.assert_found(r'The hard limit is unlimited', self.stdout),
        ])

        self.maintainers = ['Man']


def _get_checks(**kwargs):
    return [UlimitCheck(**kwargs)]
