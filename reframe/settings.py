#
# ReFrame generic settings
#


class ReframeSettings:
    reframe_module = None
    job_poll_intervals = [1, 2, 3]
    job_submit_timeout = 60
    checks_path = ['checks/']
    checks_path_recurse = True
    site_configuration = {
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
            'maui': {
                'descr': 'NIWA HPC2 system Maui (XC50 CS500)',
                # Adjust to your system's hostname
                'hostnames': ['maui01','maui02', 'maui-internallogin01'],
                'resourcesdir': '/nesi/project/nesi99999/NeSI_ReFrame/_BM_test_cases/'
                'modules_system': 'tmod',
                'stagedir': '/nesi/nobackup/nesi99999/reframe/maui',
                'outputdir': '/nesi/project/nesi99999/NeSI_ReFrame/output/maui',
                'logdir': '/nesi/project/nesi99999/NeSI_ReFrame/logs/maui'
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
                        #TODO
                        #'scheduler': 'nativeslurm',
                        'scheduler': 'squeue+srun',
                        #'modules': ['craype-x86-skylake'],
                        # due to the issue that the default gcc is 4.8.1,
                        #   which does not support skylake
                        'modules': ['craype-broadwell'],
                        'access':  [''],
                        'environs': ['PrgEnv-cray', 'PrgEnv-gnu',
                                     'PrgEnv-intel'],
                        'descr': 'XC compute nodes',
                        'max_jobs': 100
                    },
                    'gpu': {
                        'scheduler': 'nativeslurm',
                        #'modules': ['craype-x86-skylake'],
                        # due to the issue that the default gcc is 4.8.1,
                        #   which does not support skylake
                        'modules': ['craype-broadwell'],
                        'access':  [''],
                        'environs': ['PrgEnv-cray', 'PrgEnv-gnu',
                                     'PrgEnv-intel'],
                        'descr': 'CS gpu nodes',
                        'max_jobs': 10
                    },
                    'CS_compute': {
                        'scheduler': 'nativeslurm',
                        #'modules': ['craype-x86-skylake'],
                        # due to the issue that the default gcc is 4.8.1,
                        #   which does not support skylake
                        'modules': ['craype-broadwell'],
                        'access':  ['-p gpu'],
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
                'resourcesdir': '/nesi/project/nesi99999/NeSI_ReFrame/_BM_test_cases/'
                #'modules_system': 'tmod',
                'stagedir': '/nesi/nobackup/nesi99999/reframe/mahuika/',
                'outputdir': '/nesi/project/nesi99999/NeSI_ReFrame/output/mahuika/',
                'logdir': '/nesi/project/nesi99999/NeSI_ReFrame/logs/mahuika/',
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
                        'access':  ['--exclusive'],
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
    logging_config = {
        'level': 'DEBUG',
        'handlers': [
            {
                'type': 'file',
                'name': 'reframe.log',
                'level': 'DEBUG',
                'format': '[%(asctime)s] %(levelname)s: '
                          '%(check_info)s: %(message)s',
                'append': False,
            },

            # Output handling
            {
                'type': 'stream',
                'name': 'stdout',
                'level': 'INFO',
                'format': '%(message)s'
            },
            {
                'type': 'file',
                'name': 'reframe.out',
                'level': 'INFO',
                'format': '%(message)s',
                'append': False,
            }
        ]
    }

    perf_logging_config = {
        'level': 'DEBUG',
        'handlers': [
            {
                'type': 'filelog',
                'prefix': '%(check_system)s/%(check_partition)s',
                'level': 'INFO',
                'format': (
                    '%(asctime)s|reframe %(version)s|'
                    '%(check_info)s|jobid=%(check_jobid)s|'
                    '%(check_perf_var)s=%(check_perf_value)s|'
                    'ref=%(check_perf_ref)s '
                    '(l=%(check_perf_lower_thres)s, '
                    'u=%(check_perf_upper_thres)s)'
                ),
                'append': True
            }
        ]
    }


settings = ReframeSettings()
