import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RunOnlyRegressionTest


class GA7UKCAcheck(RunOnlyRegressionTest):
    def __init__(self, check_name, check_descr, **kwargs):
        super().__init__(check_name, os.path.dirname(__file__), **kwargs)
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'GA7-UKCA/input')
        self.descr = check_descr
        self.valid_prog_environs = ['PrgEnv-cray']

        self.sanity_patterns = sn.all([sn.assert_found(r'^\s*End of UM RUN Job', 'pe_output/umnsa.fort6.pe000')])


        self.perf_patterns = {
            'perf': sn.extractsingle(r'^ Time taken by run_um-nzcsm_XC.sh in seconds is ',
                                     self.stdout, 'perf', float)
#            'perf': sn.extractsingle(r'^ CP2K(\s+[\d\.]+){4}\s+(?P<perf>\S+)',
#                                     self.stdout, 'perf', float)
        }

        self.maintainers = ['Man']
        self.strict_check = True
        self.modules = ['craype-hugepages8M']
        self.modules = ['craype-broadwell']
        self.modules = ['cray-hdf5/1.10.1.1']
        self.modules = ['cray-netcdf/4.4.1.1.6']

        self.readonly_files = ['ad317.astart']

        base_dir = os.path.join(self.current_system.resourcesdir,'GA7-UKCA')
        prescript = os.path.join(self.sourcesdir, '../scripts/nesi_um-atmos')
        self.pre_run = ["source " + prescript, 'ulimit -s unlimited']

        self.pre_run.append("export UM_BASE_DIR=base_dir")
        self.pre_run.append('mkdir History_Data/')
        self.pre_run.append('mkdir History_Data/seedfiles')
        self.pre_run.append("source $UMDIR/ancils")
        self.pre_run.append('ulimit -s unlimited')

        self.executable = "$ATMOS_EXEC"

#TODO also for bigger cases
class GA7UKCAcheck_small(GA7UKCAcheck):
    def __init__(self, **kwargs):
        super().__init__('GA7_UKCA_check_small', 'GA7 UKCA 512 cores', **kwargs)
#        self.executable_opts = ['16 32 2']
        self.valid_systems = ['kupe:compute', 'maui:compute']
 
        self.num_tasks = 512
        self.num_tasks_per_node = 20
        self.use_multithreading = False

        self.time_limit = (2, 00,0)
        um_dir = os.path.join(self.sourcesdir,'../source/um_ukca_10.4/build-atmos/bin/')
        self.variables = {
                          'OMP_NUM_THREADS': '2',
                          'OMP_PLACES': 'threads',
                          'OMP_PROC_BIND': 'spread',
                          'OMP_STACKSIZE': '1000M',
                          'OMP_WAIT_POLICY': 'PASSIVE',

                          'MPICH_MAX_THREAD_SAFETY': 'multiple',

                          'UM_ATM_NPROCX': '16',
                          'UM_ATM_NPROCY': '32', 
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


        self.reference = {
            'kupe:compute': {
                'perf': (1581, None, 0.10) #TODO still need to calculate the 2*standard deviation, which PDT should not outreach
            },
        }
        self.tags |= {'maintenance', 'production'}

def _get_checks(**kwargs):
    return [GA7UKCAcheck_small(**kwargs)]
