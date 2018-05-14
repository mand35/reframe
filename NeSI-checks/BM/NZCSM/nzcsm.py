import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RunOnlyRegressionTest


class NZCSMcheck(RunOnlyRegressionTest):
    def __init__(self, name, s_x, s_y, **kwargs):
        super().__init__(name, os.path.dirname(__file__), **kwargs)

        self.descr = 'NZCSM check {}'.format(s_x, s_y, 2)
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'NZCSM/input')
        self.valid_systems = ['kupe:compute']
        self.valid_prog_environs = ['PrgEnv-intel']

        self.num_tasks = s_x*s_y
        self.num_cpus_per_task = 2
        self.num_tasks_per_node = 20
        self.time_limit = (0, 59, 0)

        prescript = os.path.join(self.sourcesdir, '../scripts/nesi_um-atmos')
        self.pre_run = ['mkdir um_output/', "source " + prescript, 'ulimit -s unlimited']
        self.pre_run.append("cp MPICH_RANK_ORDER.{} MPICH_RANK_ORDER".format(s_x*s_y))
        self.pre_run.append('beg_secs=$(date +%s)')

        self.modules = ['craype-hugepages8M']
        self.readonly_files = ['OS36_alabc', 'OS36_alabc_000', 'OS36_astart']
        
        self.use_multithreading = False
        um_dir = os.path.join(self.sourcesdir,'../source/um_nzcsm_10.4_XC_8Mhugepage_intel_opt/build-atmos/bin')
        
        self.variables = {
                          'OMP_NUM_THREADS': '2',
                          'OMP_STACKSIZE': '512M',
                          'OMP_PLACES': 'threads',
                          'OMP_WAIT_POLICY': 'PASSIVE',

                          'MPICH_MAX_THREAD_SAFETY': 'multiple',
                          'MPICH_RANK_REORDER_METHOD': '3',
                          'MPICH_RANK_REORDER_DISPLAY': '1',
                          'FORT_BUFFERED': 'TRUE',
                          'FORT_FMT_NO_WRAP_MARGIN': 'TRUE',
                          'MALLOC_MMAP_MAX_': '0',
                          'MALLOC_TRIM_THRESHOLD_': '$(( 128 * 1024 * 1024 ))',
                          'MPICH_GNI_MAX_EAGER_MSG_SIZE': '65535',
                          'MPICH_SMP_SINGLE_COPY_SIZE': '65535',

                          'UM_ATM_NPROCX': str(s_x),
                          'UM_ATM_NPROCY': str(s_y),
                          'UM_INSTALL_DIR': um_dir,
                          'ATMOS_EXEC': '${UM_INSTALL_DIR}/um-atmos.exe',
                          'ATMOS_KEEP_MPP_STDOUT': 'true',
                          'UMDIR': self.sourcesdir,
			  'SPECTRAL_FILE_DIR': os.path.join(self.sourcesdir,'vn10.4/ctldata/spectral/ga3_1'),
			  'VN': '10.4',
                          'DATADIR': 'um_output',
                          'DATAM': 'um_output',
                          'DATAW': 'um_output',
                          'HISTORY': 'um_output/umnsa.xhist',
                          'CRUN_LEN': '"12"',
                          'DEL_Y': '"0.0135"',
                          'DEL_X': '"0.0135"',
                          'FIRST_LAT': '"-9.11925"',
                          'FIRST_LON': '"171.89325"',
                          'CB_FREQ': '"1"',
                          'LBC_FIELD_FREQ': '"60"',
                          'NUM_HEADERS': '"710"',
                          'LBC_RAIN': '"True"',
                          'NLANDPTS': '"$NLANDPTS"',
                          'NLBC_TIMES': '"13"',
                          'NL_BL_LEVS': '"42"',
                          'NLEVS': '"70"',
                          'NLEVSP1': '"71"',
                          'NLEVSM1': '"69"',
                          'NLEVSM2': '"68"',
                          'NPTS_Y': '"1350"',
                          'NPTS_X': '"1200"',
                          'NTSTEPS': '"1440"',
                          'OROG_BLEND_WEIGHTS': '"1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1"',
                          'POLE_LAT': '"49.5"',
                          'POLE_LON': '"171.5"',
                          'RADSTEP_DIAG': '"288"',
                          'RADSTEP_PROG': '"96"',
                          'RHCRIT': '"0.96,0.94,0.92,0.9,0.89,0.88,0.87,0.86,0.85,0.84,0.84,0.83,0.82,0.81,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8"',
                          'RIM_WEIGHTS': '"1,1,1,1,1,0.95,0.9,0.85,0.8,0.75,0.7,0.65,0.6,0.55,0.5,0.45,0.4,0.35,0.3,0.25,0.2,0.15,0.1,0.05,0,0,0,0,0,0"',
                          'TOP': '"40000"',
                          'CONTINUE': '"false"',
                          'RUN_END': '"0,0,0,12,0,0"',
                          'ATMOS_KEEP_MPP_STDOUT': 'true',
                          'ATMOS_STDOUT_FILE': 'pe_output/umnsa.fort6.pe',
                          'COUPLER': 'none',
                          'DR_HOOK': 'false',
                          'ENS_MEMBER': '0',
                          'FASTRUN': 'false',
                          'FLUME_IOS_NPROC': '0',
                          'PRINT_STATUS': 'PrStatus_Normal',
                          'RCF_PRINTSTATUS': 'PrStatus_Normal',
                          'RCF_TIMER': 'false',
                          'RUNID': 'umnsa',
                          'UM_THREAD_LEVEL': 'MULTIPLE',
                          'STAGE_DIR': '$PWD'
        }

        self.executable = "$ATMOS_EXEC"

        self.post_run.append('end_secs=$(date +%s)')
        self.post_run.append('let wallsecs=$end_secs-$beg_secs; echo "Time taken by NZCSM in seconds is " $wallsecs')

        self.sanity_patterns = sn.all([sn.assert_found(r'^\s*END OF RUN - TIMER OUTPUT', 'pe_output/umnsa.fort6.pe0000')])

        p_name = "perf_{}".format(self.num_tasks)
        self.perf_patterns = {
            p_name: sn.extractsingle(r'^Time taken by NZCSM in seconds is\s+(?P<'+p_name+'>\S+)',
                                     self.stdout, p_name, float)
        }

        self.maintainers = ['Man']
        self.strict_check = True

class NZCSM_BM(NZCSMcheck):
    def __init__(self, s_x, s_y, **kwargs):
        super().__init__('nzcsm_check_{}c_BM'.format(s_x*s_y*2), s_x, s_y, **kwargs)

        self.reference = {
            'kupe:compute': {
                'perf_512':  (1581, None, 0.10), #TODO still need to calculate the 2*standard deviation, which PDT should not outreach
                'perf_1024': ( 878, None, 0.10),
                'perf_1440': ( 653, None, 0.10)
            },
        }
        self.tags |= {'BM'}

class NZCSM_PDT(NZCSMcheck):
    def __init__(self, s_x, s_y, **kwargs):
        super().__init__('nzcsm_check_{}c_PDT'.format(s_x*s_y*2), s_x, s_y, **kwargs)

        self.reference = {
            'kupe:compute': {
               'perf_1024': ( 446.6, None, 1.0125),  ## cray provided  446.6+(2*2.8) = 452.2
               'perf_512':  (   805, None, 1.0124), ## not measures, just estimated  805+(2*5)
            },
        }
        self.pre_run.append("cp SHARED_PDT SHARED")

        self.tags |= {'PDT'}

def _get_checks(**kwargs):
    return [
            NZCSM_BM(16,32, **kwargs),
            NZCSM_BM(32,32, **kwargs),
            NZCSM_BM(36,40, **kwargs), 

            #NZCSM_PDT(16,32, **kwargs) 
            NZCSM_PDT(32,32, **kwargs) ## cray provided PDT ref, but job could be too big for production
            ]
