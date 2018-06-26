import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RunOnlyRegressionTest
from reframe.utility.multirun import multirun

class ANSYScheck(RunOnlyRegressionTest):
    def __init__(self, name, tasks, **kwargs):
        super().__init__(name, os.path.dirname(__file__), **kwargs)

        self.descr = 'ANSYS check'
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'ANSYS')
        self.valid_systems = ['mahuika:compute']
        self.valid_prog_environs = ['PrgEnv-cray']

        self.num_tasks = tasks
        self.num_cpus_per_task = 1
        self.time_limit = (0, 59, 0)

        self.variables = {
                          'ANSYSLMD_LICENSE_FILE': '1055@130.216.8.193',
			  'ANSYSLI_SERVERS': '2325@130.216.8.193',
                          'TIME_EXECUTABLE': '1',
                          'FLUENT_LM_CHECK_DISABLE': '1',

        }
        self.readonly_files = ['AC33aoa60coarse4URANSE.out3.cas', 
                               'AC33aoa60coarse4URANSE.out3.dat']
        self.exclusive = True

        self.pre_run = ['module load fluent/17.0']
        self.multirun_pre_run = ['beg_secs=$(date +%s)']
        
        self.executable =  ('/bin/hostname | sort -n | '
                           'head -%d > ./hosts'%self.num_tasks )

        # the actual task 'fluent' need to be started without srun
        # manual time meassure
        ref_desc = 'Time taken by ANSYS in seconds is:'
        self.multirun_post_run = [('fluent -v3ddp -g -mpi=intel '
                   '-i fluent_commands.txt '
                   '-t{} -cnf=./hosts '.format(self.num_tasks)),
                   'end_secs=$(date +%s)',
                   'let wallsecs=$end_secs-$beg_secs; ',
                   'echo "{}" $wallsecs 1>&2'.format(ref_desc), 
                   'rm AC33aoa60coarse4LESavg.out.cas '
                      'AC33aoa60coarse4LESavg.out.dat']

        self.multirun_san_pat = [
           r'^\s*Writing "AC33aoa60coarse4LESavg.out.dat"',self.stdout]
        self.sanity_patterns = sn.all([
           sn.assert_not_found(r'^\sANSYS LICENSE MANAGER ERROR',self.stdout),
           sn.assert_found(*self.multirun_san_pat)])

        p_name = "perf_{}".format(self.num_tasks)
        self.multirun_perf_pat = {}
        self.multirun_perf_pat[p_name] = [
            r'^{}\s+(?P<'+p_name+'>\S+)'.format(ref_desc), 
            self.stderr, p_name, float]

        self.perf_patterns = {
            p_name: sn.extractsingle(*(self.multirun_perf_pat[p_name]))
        }

        self.maintainers = ['Man']
        self.strict_check = True

class ANSYS_BM(ANSYScheck):
     def __init__(self, tasks, **kwargs):
        super().__init__('ANSYS_check_{}c_BM'.format(tasks), tasks, **kwargs)

        self.pre_run += self.multirun_pre_run
        self.post_run += self.multirun_post_run

        self.reference = {
            'mahuika:compute': {
                'perf_24':  (467, None, 0.10), 
                'perf_10':  (801, None, 0.10), 
                'perf_18':  (538, None, 0.10), 
                'perf_36':  (390, None, 0.10), 
                'perf_72':  (262, None, 0.10), 
            },
        }
        self.tags |= {'BM'}


class ANSYS_PDT(ANSYScheck):
    def __init__(self, name, tasks, **kwargs):
        super().__init__('ANSYS_check_{0}c_PDT_{1}'.format(tasks,name), 
                         tasks, **kwargs)

        self.multirun_ref = {
            'mahuika:compute': {
                'perf_24':  (467.0, None, (2*1.78)/465.0), 
            },
        }
        self.tags |= {'PDT'}

def _get_checks(**kwargs):
    return [
            multirun(ANSYS_PDT)('', 24, **kwargs),

            ANSYS_BM(24, **kwargs),
            ANSYS_BM(10, **kwargs),
            ANSYS_BM(18, **kwargs),
            ANSYS_BM(36, **kwargs),
            ANSYS_BM(72, **kwargs),
            ]
