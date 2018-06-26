import itertools
import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RunOnlyRegressionTest
from reframe.core.launchers import JobLauncher
from reframe.utility.multirun import multirun

class NAMDBaseCheck(RunOnlyRegressionTest):
    def __init__(self, name, tasks, **kwargs):
        super().__init__(name, os.path.dirname(__file__), **kwargs)
 
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'NAMD')
        self.valid_prog_environs = ['intel']

        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'NAMD/input')
        self.time_limit = (0, 30,0)
        self.exclusive = True
        self.use_multithreading=False
        self.num_tasks = tasks
        self.num_tasks_per_node = tasks
        self.num_tasks_per_socket = int(tasks/2)
        self.num_cpus_per_task = 1
        
        self.variables = {
           'OMP_NUM_THREADS': str(self.num_cpus_per_task),
           'I_MPI_FABRICS': '"shm:ofa"'
        }

        self.readonly_files = [
                               'FFTW_NAMD_2.11_Linux-x86_64-MPI_FFTW3.txt', 
                               'open_core_wb_ion.pdb', 'open_core_wb_ion.psf',
                               'open_core_eq_31.restart.xsc', 
                               'open_core_eq_31.restart.vel',
                               'open_core_eq_31.restart.coor', 
                               'par_all27_prot_na.prm',
                               'open_target_1.pdb', 'open_target_2.pdb',  
                               'RMSD_open.in', 
                               'benchmark.conf', 'open_core_meta_01.dcd']

        self.executable = os.path.join(self.sourcesdir, '../executable/namd2')
        self.executable_opts = ['benchmark.conf']

        self.pre_run = [
                        'module load cray-fftw/3.3.6.3',
                        'export LD_LIBRARY_PATH=$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH',
                        'module load gcc/6.3.0', 
                        'module load intel/compiler/64/2017/17.0.6',
                        'module load intel/mpi/64/2018/1.163']

        ref_desc = 'Time taken by NAMD in seconds is:'
        self.multirun_pre_run = ['beg_secs=$(date +%s)']
        self.multirun_post_run = ['end_secs=$(date +%s)',
           'let wallsecs=$end_secs-$beg_secs' ,
           'echo "{}" $wallsecs'.format(ref_desc)]

        self.multirun_san_pat = ['End of program', self.stdout]
        self.sanity_patterns = sn.assert_found(*self.multirun_san_pat)

        p_name = "perf_{}".format(self.num_tasks)
        self.multirun_perf_pat = {} 
        self.multirun_perf_pat[p_name] = [
           r'^{0}\s+(?P<{1}>\S+)'.format(ref_desc,p_name), 
           self.stdout, p_name, float]
        self.perf_patterns = {
            p_name: sn.extractsingle(*(self.multirun_perf_pat[p_name]))
        }

        self.maintainers = ['man']
        self.strict_check = True
        self.use_multithreading = False

    def setup(self, partition, environ, **job_opts):
        super().setup(partition, environ, **job_opts)
        self.job.launcher.options += ['--mpi=pmi2']  # we need to run it with PMI2

class NAMD_BM(NAMDBaseCheck):
    def __init__(self, tasks, **kwargs):
       super().__init__('NAMD_BM_%s'%tasks, tasks, **kwargs)

       self.pre_run += self.multirun_pre_run
       self.post_run += self.multirun_post_run

       self.valid_systems = ['mahuika:compute']
       self.descr = 'NAMD BM'

       self.reference = {     
           'mahuika:compute': {
                'perf_12':  (750, None, 0.10), 
                'perf_10':  (851, None, 0.10), # 25%
                'perf_18':  (549, None, 0.10), # 50%
                'perf_36':  (334, None, 0.10), #100%
                'perf_72':  (117, None, 0.10), #200%
                'perf_108': (134, None, 0.10), #300%
                'perf_144': (114, None, 0.10), #400%
           }
       }
       self.tags = {'BM'}

class NAMD_PDT(NAMDBaseCheck):
    def __init__(self, name, tasks, **kwargs):
       super().__init__('namd_PDT_{0}_{1}'.format(tasks,name), tasks, **kwargs)

       self.valid_systems = ['mahuika:compute']
       self.descr = 'NAMD PDT'

       self.multirun_ref = {     
           'mahuika:compute': {
                'perf_12':  (740, None, (2*5.58)/740),
           }
       }
       self.tags = {'PDT'}

def _get_checks(**kwargs):
    return [NAMD_BM(12, **kwargs),
            NAMD_BM(10, **kwargs),
            NAMD_BM(18, **kwargs),
            NAMD_BM(36, **kwargs),
            multirun(NAMD_PDT)('', 12, **kwargs)
           ]
