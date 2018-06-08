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
                        'intel/compiler/64/2017/17.0.6', 'intel/mpi/64/2017/6.256',
                        'gcc5/5.5.0']

        self.variables = {'LD_LIBRARY_PATH': "${CRAY_LD_LIBRARY_PATH}:$LD_LIBRARY_PATH",
                          'CRAY_CUDA_MPS': '1',
                          'CUDA_VISIBLE_DEVICES': '1',
                          'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }
        gmx_dir = os.path.join(self.sourcesdir,'../executable')
        self.pre_run('source %/gmx-completion-mdrun_mpi.bash'%gmx_dir)
        self.exclusive = True
        self.use_multithreading=False
        self.num_cpus_per_task = 1
        self.num_tasks = tasks
        self.num_tasks_per_node = tasks
        # cannot be mapped: --mpi=pmi2 --cpu_bind=core --mem_bind=v,local -c ${OMP_NUM_THREADS}
        self.executable = '%/mdrun_mpi'%gmx_dir
        self.executable_opts = ('-v -deffnm 1aki_md1 -dlb no -noconfout').split()
        self.pre_run('beg_secs=$(date +%s)')
        self.post_run.append('end_secs=$(date +%s)')
        self.post_run.append('let wallsecs=$end_secs-$beg_secs; echo "Time taken by GROMACS in seconds is:" $wallsecs')

        self.sanity_patterns = sn.assert_found('Performance:', self.stdout)

        p_name = "perf_{}".format(self.num_tasks)
        self.perf_patterns = {
            p_name: sn.extractsingle(r'^Time taken by GROMACS in seconds is:\s+(?P<'+p_name+'>\S+)',
                                     self.stdout, p_name, float)
        }

        self.modules = ['GROMACS']
        self.maintainers = ['man']
        self.strict_check = True
        self.use_multithreading = False

class GromacsCPU_BM(GromacsBaseCheck):
    def __init__(self, tasks, **kwargs):
       super().__init__('gromacs_CPU_BM', tasks, **kwargs)

       self.valid_systems = ['mahuika:compute']
       self.descr = 'GROMACS CPU BM'

       self.reference = {
           'mahuika:compute': {
                'perf_8':   (389, -0.10, None),
                'perf_10':  (325, -0.10, None),
                'perf_18':  (216, -0.10, None),
                'perf_36':  (136, -0.10, None),
           }
       }
       self.tags = {'BM'}


class GromacsGPU_BM(GromacsBaseCheck):
    def __init__(self, tasks, **kwargs):
       super().__init__('gromacs_gpu_BM', tasks, **kwargs)


       self.num_gpus_per_node = 1
       self.valid_systems = ['mahuika:gpu']
       self.descr = 'GROMACS GPU BM'

       self.reference = {     
           'mahuika:compute': {
                'perf_1':  (198, -0.10, None),
           }
       }
       self.tags = {'BM'}
       self.tags = {'GPU'}


class GromacsGPU_PDT(GromacsBaseCheck):
    def __init__(self, tasks, **kwargs):
       super().__init__('gromacs_gpu_PDT', tasks, **kwargs)

       self.num_gpus_per_node = 1
       self.valid_systems = ['mahuika:gpu']
       self.descr = 'GROMACS GPU PDT'

       self.reference = {     
           'mahuika:compute': {
                'perf_1':  (203, -(2*0.09)/203, None),
           }
       }
       self.tags = {'PDT'}
       self.tags = {'GPU'}

def _get_checks(**kwargs):
    return [GromacsGPU_BM(1, **kwargs),
            GromacsGPU_PDT(1, **kwargs),

            GromacsCPU_PDT(8, **kwargs),
            GromacsCPU_PDT(10, **kwargs),
            GromacsCPU_PDT(18, **kwargs),
            GromacsCPU_PDT(36, **kwargs),
           ]
