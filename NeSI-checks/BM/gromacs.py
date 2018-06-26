import itertools
import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RunOnlyRegressionTest
from reframe.utility.multirun import multirun


class GromacsBaseCheck(RunOnlyRegressionTest):
    def __init__(self, name, tasks, **kwargs):
        super().__init__(name, os.path.dirname(__file__), **kwargs)
 
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'GROMACS/input')
        self.valid_prog_environs = ['intel']

        self.modules = ['cray-fftw/3.3.6.3', 'cuda90/toolkit/9.0.176', 
                        'intel/compiler/64/2017/17.0.6', 
                        'intel/mpi/64/2017/6.256',
                        'gcc5/5.5.0']

        self.variables = {'LD_LIBRARY_PATH': ('${CRAY_LD_LIBRARY_PATH}:'
                                              '$LD_LIBRARY_PATH'),
                          'CRAY_CUDA_MPS': '1',
                          'CUDA_VISIBLE_DEVICES': '1',
                          'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }
        gmx_dir = os.path.join(self.sourcesdir,'../executable')

        self.exclusive = True
        self.use_multithreading=False
        self.num_cpus_per_task = 1
        self.num_tasks = tasks
        self.num_tasks_per_node = tasks

        self.pre_run = ['module load cray-fftw/3.3.6.3 cuda90/toolkit/9.0.176',
           'module load intel/compiler/64/2017/17.0.6 intel/mpi/64/2017/6.256',
           'module load gcc/6.3.0',
           'module swap gcc gcc5/5.5.0',
           'source {}/gmx-completion-mdrun_mpi.bash'.format(gmx_dir)]

        self.executable = '{}/mdrun_mpi'.format(gmx_dir)
        self.executable_opts = ('-v -deffnm 1aki_md1 -dlb no ' 
                                '-noconfout').split()
        # time meassure for performance
        ref_desc = 'Time taken by GROMACS in seconds is:'
        self.multirun_pre_run = ['beg_secs=$(date +%s)']
        self.multirun_post_run = ['end_secs=$(date +%s)',
                ('let wallsecs=$end_secs-$beg_secs; '
                 'echo "{}" $wallsecs'.format(ref_desc))]

        self.multirun_san_pat = ['Performance:', self.stderr]
        self.sanity_patterns = sn.assert_found(*self.multirun_san_pat)

        p_name = "perf_{}".format(self.num_tasks)
        self.multirun_perf_pat = {}
        self.multirun_perf_pat[p_name] = [
                               r'^{}\s+(?P<perf>\S+)'.format(ref_desc),
                               self.stdout, 'perf', float]
        self.perf_patterns = {
            p_name: sn.extractsingle(*(self.multirun_perf_pat[p_name]))
        }

        self.modules = ['GROMACS']
        self.maintainers = ['man']
        self.strict_check = True
        self.use_multithreading = False

    def setup(self, partition, environ, **job_opts):
        super().setup(partition, environ, **job_opts)
        self.job.launcher.options += ['--mpi=pmi2 --cpu_bind=core '
                                      '--mem_bind=v,local']

class GromacsBM_Base(GromacsBaseCheck):
    def __init__(self, name, tasks, **kwargs):
       super().__init__(name, tasks, **kwargs)
       self.pre_run += self.multirun_pre_run
       self.post_run += self.multirun_post_run
       self.tags = {'BM'}

class GromacsCPU_BM(GromacsBM_Base):
    def __init__(self, tasks, **kwargs):
       super().__init__('gromacs_CPU_BM_{}'.format(tasks), tasks, **kwargs)

       self.valid_systems = ['mahuika:compute']
       self.descr = 'GROMACS CPU BM'

       self.reference = {
           'mahuika:compute': {
                'perf_8':   (389, None, 0.10),
                'perf_10':  (325, None, 0.10),
                'perf_18':  (216, None, 0.10),
                'perf_36':  (136, None, 0.10),
           }
       }


class GromacsGPU_BM(GromacsBM_Base):
    def __init__(self, tasks, **kwargs):
       super().__init__('gromacs_gpu_BM_{}'.format(tasks), tasks, **kwargs)


       self.num_gpus_per_node = 1
       self.valid_systems = ['mahuika:gpu']
       self.descr = 'GROMACS GPU BM'

       self.reference = {     
           'mahuika:gpu': {
                'perf_1':  (198, None, 0.10),
           }
       }
       self.tags |= {'GPU'}


class GromacsGPU_PDT(GromacsBaseCheck):
    def __init__(self, name, tasks, **kwargs):
       super().__init__('gromacs_gpu_PDT_{0}_{1}'.format(tasks, name), 
                        tasks, **kwargs)

       self.num_gpus_per_node = 1
       self.valid_systems = ['mahuika:gpu']
       self.descr = 'GROMACS GPU PDT {}'.format(name)
       self.multirun_ref = {     
           'mahuika:gpu': {
                'perf_1':  (203, None, (2*0.09)/203),
           }
       }
       self.tags = {'PDT', 'GPU'}

def _get_checks(**kwargs):
    return [GromacsGPU_BM(1, **kwargs),
            multirun(GromacsGPU_PDT)('',1, **kwargs),

            GromacsCPU_BM(8, **kwargs),
            GromacsCPU_BM(10, **kwargs),
            GromacsCPU_BM(18, **kwargs),
            GromacsCPU_BM(36, **kwargs),
           ]
