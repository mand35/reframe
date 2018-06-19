import itertools
import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RunOnlyRegressionTest


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
        self.pre_run = ['module load cray-fftw/3.3.6.3 cuda90/toolkit/9.0.176',
           'module load intel/compiler/64/2017/17.0.6 intel/mpi/64/2017/6.256',
           'module load gcc/6.3.0',
           'module swap gcc gcc5/5.5.0',
           'source {}/gmx-completion-mdrun_mpi.bash'.format(gmx_dir)]
        self.exclusive = True
        self.use_multithreading=False
        self.num_cpus_per_task = 1
        self.num_tasks = tasks
        self.num_tasks_per_node = tasks
        # cannot be mapped: --mpi=pmi2 --cpu_bind=core --mem_bind=v,local -c ${OMP_NUM_THREADS}
        self.executable = '{}/mdrun_mpi'.format(gmx_dir)
        self.executable_opts = ('-v -deffnm 1aki_md1 -dlb no -noconfout').split()
        self.pre_run.append('beg_secs=$(date +%s)')
        self.post_run = ['end_secs=$(date +%s)',
                ('let wallsecs=$end_secs-$beg_secs; '
                 'echo "Time taken by GROMACS in seconds is:" $wallsecs')]

        self.sanity_patterns = sn.assert_found('Performance:', self.stderr)

        p_name = "perf_{}".format(self.num_tasks)
        self.perf_patterns = {
            p_name: sn.extractsingle(r'^Time taken by GROMACS in seconds is:''\s+(?P<'+p_name+'>\S+)',
                                     self.stdout, p_name, float)
        }

        self.modules = ['GROMACS']
        self.maintainers = ['man']
        self.strict_check = True
        self.use_multithreading = False

    def setup(self, partition, environ, **job_opts):
        super().setup(partition, environ, **job_opts)
        self.job.launcher.options += ['--mpi=pmi2']

class GromacsCPU_BM(GromacsBaseCheck):
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
       self.tags = {'BM'}


class GromacsGPU_BM(GromacsBaseCheck):
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
       self.tags = {'BM'}
       self.tags = {'GPU'}


class GromacsGPU_PDT(GromacsBaseCheck):
    def __init__(self, tasks, **kwargs):
       super().__init__('gromacs_gpu_PDT_{}'.format(tasks), tasks, **kwargs)

       self.num_gpus_per_node = 1
       self.valid_systems = ['mahuika:gpu']
       self.descr = 'GROMACS GPU PDT'

       self.reference = {     
           'mahuika:gpu': {
                'perf_1':  (203, None, (2*0.09)/203),
           }
       }
       self.tags = {'PDT'}
       self.tags = {'GPU'}

def _get_checks(**kwargs):
    return [GromacsGPU_BM(1, **kwargs),
            GromacsGPU_PDT(1, **kwargs),

            GromacsCPU_BM(8, **kwargs),
            GromacsCPU_BM(10, **kwargs),
            GromacsCPU_BM(18, **kwargs),
            GromacsCPU_BM(36, **kwargs),
           ]
