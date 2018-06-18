#
# ReFrame generic settings
#


class ReframeSettings:
    _reframe_module = 'reframe'
    _job_poll_intervals = [1, 2, 3]
    _job_submit_timeout = 60
    _checks_path = ['checks/']
    _checks_path_recurse = True
    _site_configuration = {
        'systems': {
            # Generic system used also in unit tests
            'kupe': {
                'descr': 'NIWA HPC3 system KUPE (XC50 A/C)',
                # Adjust to your system's hostname
                'hostnames': ['kupe01'],
#                'resourcesdir': '/home/schoenherrm/projects/reframe/kupe_tests',
                'resourcesdir': '/scale_akl_nobackup/filesets/nobackup/schoenherrm/180405_BM_tests/',
                'modules_system': 'tmod',
                'stagedir': '/scale_akl_nobackup/filesets/nobackup/schoenherrm/reframe',
                'partitions': {
                    'login': {
                        'scheduler': 'local',
                        #'modules': ['craype-x86-skylake'],
			# due to the issue that the default gcc is 4.8.1, 
                        #   which does not support skylake
                        'modules': ['craype-broadwell'],
                        'access':  [],
                        'environs': ['PrgEnv-cray', 'PrgEnv-gnu',
                                     'PrgEnv-intel'],
                        'descr': 'Login nodes',
                        'max_jobs': 4
                    },
                    'compute': {
                        'scheduler': 'nativeslurm',
                        #'modules': ['craype-x86-skylake'],
			# due to the issue that the default gcc is 4.8.1, 
                        #   which does not support skylake
                        'modules': ['craype-broadwell'],  
                        'access':  ['--partition=NeSI --account=nesi99999'],
                        'environs': ['PrgEnv-cray', 'PrgEnv-gnu',
                                     'PrgEnv-intel'],
                        'descr': 'XC compute nodes',
                        'max_jobs': 100
                    },
                    'CS_compute': {
                        'scheduler': 'nativeslurm',
                        #'modules': ['craype-x86-skylake'],
			# due to the issue that the default gcc is 4.8.1, 
                        #   which does not support skylake
                        'modules': ['craype-broadwell'],
                        'access':  ['--partition=General --account=nesi99999'],
                        'environs': ['PrgEnv-gnu'],
                        'descr': 'CS compute nodes',
                        'max_jobs': 100
                    }
                }
            },
            'mahuika': {
                'descr': 'NIWA HPC1 system Mahuika (CS500)',
                # Adjust to your system's hostname
                'hostnames': ['mahuika02'],
                'resourcesdir': '/scale_wlg_nobackup/filesets/nobackup/schoenherrm/180405_BM_tests/',
                #'modules_system': 'tmod',
                'stagedir': '/scale_wlg_nobackup/filesets/nobackup/schoenherrm/reframe',
                'partitions': {
                    'login': {
                        'scheduler': 'local',
                        'modules': ['PrgEnv-cray'],
                        #'modules': ['craype-broadwell'],
                        #'access':  [],
                        'environs': ['PrgEnv-cray','gnu','intel'],
                        'descr': 'Login nodes',
                        'max_jobs': 4
                    },
                    'compute': {
                        # TODO 
                        #'scheduler': 'nativeslurm',
                        'scheduler': 'squeue+srun',
                        #'modules': ['craype-broadwell'],
                        #'access':  [''],
                        'environs': ['PrgEnv-cray','gnu','intel'],
                        'descr': 'CS500 compute nodes',
                        'max_jobs': 100
                    },
                    'gpu': {
                        # TODO 
                        #'scheduler': 'nativeslurm',
                        'scheduler': 'squeue+srun',
                        'access':  ['-p gpu'],
                        'environs': ['PrgEnv-cray','gnu','intel'],
                        'descr': 'CS500 gpu nodes',
                        'max_jobs': 100
                    },
                }
            }
        },
        'environments': {
            '*': {
                'PrgEnv-cray': {
                    'type': 'ProgEnvironment',
                    'modules': ['PrgEnv-cray'],
                },
    
                'PrgEnv-gnu': {
                    'type': 'ProgEnvironment',
                    'modules': ['PrgEnv-gnu'],
                },
    
                'PrgEnv-intel': {
                    'type': 'ProgEnvironment',
                    'modules': ['PrgEnv-intel'],
                },
                'intel': {
                    'type': 'ProgEnvironment',
                    'modules': ['intel/compiler', 'intel/mpi'],
                    'ftn': 'ifort', 'cc': 'icc', 'cxx': 'icpc',
                },
                'gnu': {
                    'type': 'ProgEnvironment',
                    'modules': ['gcc', 'openmpi/gcc/64/1.10.3'],
                    'ftn': 'mpifort', 'cc': 'mpicc', 'cxx': 'mpiCC',
                }
            }
        }
    }
    _logging_config = {
        'level': 'DEBUG',
        'handlers': {
            'reframe.log': {
                'level': 'DEBUG',
                'format': '[%(asctime)s] %(levelname)s: '
                          '%(check_info)s: %(message)s',
                'append': False,
            },

            # Output handling
            '&1': {
                'level': 'INFO',
                'format': '%(message)s'
            },
            'reframe.out': {
                'level': 'INFO',
                'format': '%(message)s',
                'append': False,
            }
        }
    }

    @property
    def version(self):
        return self._version

    @property
    def reframe_module(self):
        return self._reframe_module

    @property
    def job_poll_intervals(self):
        return self._job_poll_intervals

    @property
    def job_submit_timeout(self):
        return self._job_submit_timeout

    @property
    def checks_path(self):
        return self._checks_path

    @property
    def checks_path_recurse(self):
        return self._checks_path_recurse

    @property
    def site_configuration(self):
        return self._site_configuration

    @property
    def logging_config(self):
        return self._logging_config


settings = ReframeSettings()
