import itertools
import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RunOnlyRegressionTest


class GATKBaseCheck(RunOnlyRegressionTest):
    def __init__(self, name, threads, **kwargs):
        super().__init__(name, os.path.dirname(__file__), **kwargs)
 
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'GATK/input')
        self.exclusive = True
        self.use_multithreading=False
        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = threads

        bam_files = ['Chr26Bam30/Chr26_AUDOPU000000000454_renamed.bam ',
                     'Chr26Bam30/Chr26_AUMERU000000000001_renamed.bam ',
                     'Chr26Bam30/Chr26_AUMERU000000000002_renamed.bam ',
                     'Chr26Bam30/Chr26_AUMERU000000000454_renamed.bam ',
                     'Chr26Bam30/Chr26_AUNAMU000000000011_renamed.bam ',
                     'Chr26Bam30/Chr26_AURONU000000000002_renamed.bam ',
                     'Chr26Bam30/Chr26_AURONU000000000004_renamed.bam ',
                     'Chr26Bam30/Chr26_BDBAGU000000000014_renamed.bam ',
                     'Chr26Bam30/Chr26_BDBANU000000000002_renamed.bam ',
                     'Chr26Bam30/Chr26_BDBANU000000000004_renamed.bam ',
                     'Chr26Bam30/Chr26_BRBRAU000000000001_renamed.bam ',
                     'Chr26Bam30/Chr26_BRBRAU000000000003_renamed.bam ',
                     'Chr26Bam30/Chr26_BRMORU000000000003_renamed.bam ',
                     'Chr26Bam30/Chr26_CHMIRU000000000002_renamed.bam ',
                     'Chr26Bam30/Chr26_CHSWAU000000000003_renamed.bam ',
                     'Chr26Bam30/Chr26_CHSWAU000000000004_renamed.bam ',
                     'Chr26Bam30/Chr26_CHSWAU000000000027_renamed.bam ',
                     'Chr26Bam30/Chr26_CHSWAU000000000029_renamed.bam ',
                     'Chr26Bam30/Chr26_CHVBNU000000000002_renamed.bam ',
                     'Chr26Bam30/Chr26_CNTIBU000000000008_renamed.bam ',
                     'Chr26Bam30/Chr26_CNTIBU000000000011_renamed.bam ',
                     'Chr26Bam30/Chr26_ESCASU000000000001_renamed.bam ',
                     'Chr26Bam30/Chr26_ESCASU000000000003_renamed.bam ',
                     'Chr26Bam30/Chr26_ESCHUU000000000001_renamed.bam ',
                     'Chr26Bam30/Chr26_ESCHUU000000000002_renamed.bam ',
                     'Chr26Bam30/Chr26_ESOJAU000000000004_renamed.bam ',
                     'Chr26Bam30/Chr26_ESOJAU000000000005_renamed.bam ',
                     'Chr26Bam30/Chr26_ESSALU000000000001_renamed.bam ',
                     'Chr26Bam30/Chr26_ESSALU000000000002_renamed.bam ',
                     'Chr26Bam30/Chr26_ETMENU000000000001_renamed.bam ']

        self.readonly_files = bam_files

        inp_opts = map(lambda x: '-I '+x, bam_files)
        self.executable = 'java'
        exe = os.path.join(self.sourcesdir,'../source/GenomeAnalysisTK.jar')
        out = output.vcf
        self.executable_opts = '-Xmx8G -jar '+ exe +
                               '-R '+ ref +
                               '-T UnifiedGenotyper '+ ''.join(bam_files) +
                               '-o '+ out +'-out_mode EMIT_VARIANTS_ONLY '+
                               '-stand_call_conf 20 -stand_emit_conf 20 '+
                               '-A FisherStrand -A StrandOddsRatio -A StrandBiasBySample '+
                               '-rf BadCigar --genotype_likelihoods_model BOTH '+
                               '-L 26:1000000-2000000 -nt '+ self.num_cpus_per_task +'-log GATK.log'

        self.pre_run('beg_secs=$(date +%s)')
        self.post_run.append('end_secs=$(date +%s)')
        self.post_run.append('let wallsecs=$end_secs-$beg_secs; echo "Time taken by GATK in seconds is:" $wallsecs')

        self.sanity_patterns = sn.assert_found('End of program', self.stdout)

        p_name = "perf_{}".format(threads)
        self.perf_patterns = {
            p_name: sn.extractsingle(r'^Time taken by GATK in seconds is:\s+(?P<'+p_name+'>\S+)',
                                     self.stdout, p_name, float)
        }

        self.maintainers = ['man']
        self.strict_check = True
        self.use_multithreading = False

class GATK_BM(GATKBaseCheck):
    def __init__(self, threads, **kwargs):
       super().__init__('GATK_BM', threads, **kwargs)

       self.valid_systems = ['mahuika:compute']
       self.descr = 'GATK BM'

       self.reference = {     
           'mahuika:compute': {
                'perf_1':  (279, -0.10, None), 
                'perf_2':  (185, -0.10, None), 
                'perf_4':  (124, -0.10, None), 
                'perf_8':  ( 95, -0.10, None), 
           }
       }
       self.tags = {'BM'}


class GATK_PDT(GATKBaseCheck):
    def __init__(self, threads, **kwargs):
       super().__init__('GATK_PDT', threads, **kwargs)

       self.valid_systems = ['mahuika:compute']
       self.descr = 'GATK PDT'

       self.reference = {     
           'mahuika:compute': {
                'perf_1':  (264, -(2*1.96)/264, None), 
           }
       }
       self.tags = {'PDT'}

def _get_checks(**kwargs):
    return [GATK_BM(1, **kwargs),
            GATK_BM(2, **kwargs),
            GATK_BM(4, **kwargs),
            GATK_BM(8, **kwargs),
            GATK_PDT(1,**kwargs)
           ]
