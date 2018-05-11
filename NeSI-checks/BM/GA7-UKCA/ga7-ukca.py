import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RunOnlyRegressionTest


class GA7UKCAcheck(RunOnlyRegressionTest):
    def __init__(self, name, s_x, s_y, **kwargs):
        super().__init__(name, os.path.dirname(__file__), **kwargs)
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'GA7-UKCA/input')
        self.descr = 'GA7 UKCA {} processes, 2 OMP threads'.format(s_x*s_y)

        self.valid_systems = ['kupe:compute', 'maui:compute']
        self.valid_prog_environs = ['PrgEnv-cray']

        self.num_tasks = s_x*s_y
        self.num_cpus_per_task = 2
        self.num_tasks_per_node = 20
        self.time_limit = (2, 00,0)
        self.use_multithreading = False


        self.modules = ['craype-hugepages8M']
        self.modules = ['craype-broadwell']
        self.modules = ['cray-hdf5/1.10.1.1']
        self.modules = ['cray-netcdf/4.4.1.1.6']

        self.readonly_files = ['ad317.astart']

        base_dir = os.path.join(self.current_system.resourcesdir,'GA7-UKCA')
        prescript = os.path.join(self.sourcesdir, '../scripts/nesi_um-atmos')
        self.pre_run = ["source " + prescript, 'ulimit -s unlimited']

        self.pre_run.append('mkdir History_Data/')
        self.pre_run.append('mkdir History_Data/seedfiles')
        self.pre_run.append("source $UMDIR/ancils")
        self.pre_run.append('ulimit -s unlimited')

        self.pre_run.append('beg_secs=$(date +%s)')

        self.executable = "$ATMOS_EXEC"

        um_dir = os.path.join(self.sourcesdir,'../source/um_ukca_10.4/build-atmos/bin/')
        self.variables = {'UM_BASE_DIR': base_dir, 
                          'UM_ATM_NPROCX': str(s_x),
                          'UM_ATM_NPROCY': str(s_y),
                          'OMP_NUM_THREADS': '2',
                          'OMP_PLACES': 'threads',
                          'OMP_PROC_BIND': 'spread',
                          'OMP_STACKSIZE': '1000M',
                          'OMP_WAIT_POLICY': 'PASSIVE',

                          'MPICH_MAX_THREAD_SAFETY': 'multiple',

                          'ATMOS_EXEC': os.path.join(um_dir,'um-atmos.exe'),
                          'UM_INSTALL_DIR': um_dir,
			  'UMDIR': os.path.join(self.sourcesdir,'../input'),
                          'SPECTRAL_FILE_DIR': '$UMDIR/vn10.4/ctldata/spectral/ga7',
                          'DATAM': 'History_Data',
                          'HISTORY': 'History_Data/ad317.xhist',
                          'MODELBASIS': '"1981,09,01,00,00,00"',
                          'RUNID': '"ad317"',
                          'BYEAR': '"1981"',
                          'FLUME_IOS_NPROC': '0',
                          'TASKEND': '"0,0,5,0,0,0"',
                          'ATMOS_KEEP_MPP_STDOUT': 'true',
                          'ATMOS_STDOUT_FILE': 'pe_output/ad317.fort6.pe',
                          'COUPLER': 'none',
                          'DR_HOOK': 'false',
                          'ENS_MEMBER': '0',
                          'PRINT_STATUS': 'PrStatus_Normal',
                          'RCF_PRINTSTATUS': 'PrStatus_Normal',
                          'RCF_TIMER': 'false',
                          'UM_THREAD_LEVEL': 'MULTIPLE',
                          'VN': '10.4',
        }

        self.post_run.append('end_secs=$(date +%s)')
        self.post_run.append('let wallsecs=$end_secs-$beg_secs; echo "Time taken by GA7-UKCA in seconds is " $wallsecs')

        self.sanity_patterns = sn.all([sn.assert_found(r'End of UM RUN Job', 'pe_output/ad317.fort6.pe000')])

        p_name = "perf_%s"%self.num_tasks
        self.perf_patterns = {
            p_name: sn.extractsingle(r'^Time taken by GA7-UKCA in seconds is \s+(?P<'+p_name+'>\S+)',
                                     self.stdout, p_name, float)
        }

        self.maintainers = ['Man']
        self.strict_check = True

class GA7UKCA_BM(GA7UKCAcheck):
    def __init__(self, s_x, s_y, **kwargs):
        super().__init__('GA7_UKCA_{}c_BM'.format(s_x*s_y*2), s_x, s_y, **kwargs)

        self.reference = {
            'kupe:compute': {
                'perf_512':  (2061, None, 0.10), #TODO still need to calculate the 2*standard deviation, which PDT should not outreach
                'perf_1024': (1219, None, 0.10)
            },
        }
        self.tags |= {'BM'}

class GA7UKCA_PDT(GA7UKCAcheck):
    def __init__(self, s_x, s_y, **kwargs):
        super().__init__('GA7_UKCA_{}c_PDT'.format(s_x*s_y*2), s_x, s_y, **kwargs)

        self.reference = {
            'kupe:compute': {
                'perf_1024': (580.6, None, (580.6+(2*3.1))/580.6)  # cray provided 580.6+(2*3.1)
            },
        }
        self.pre_run.append("cp SHARED_PDT SHARED")
        self.tags |= {'PDT'}


def _get_checks(**kwargs):
    return [GA7UKCA_BM(16, 32, **kwargs), 
            GA7UKCA_BM(32, 32, **kwargs),

            GA7UKCA_PDT(32,32, **kwargs)
           ]
