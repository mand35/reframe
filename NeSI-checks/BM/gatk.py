import itertools
import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RunOnlyRegressionTest
from reframe.utility.multirun import multirun

class GATKBaseCheck(RunOnlyRegressionTest):
    def __init__(self, name, threads, **kwargs):
        super().__init__(name, os.path.dirname(__file__), **kwargs)
 
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'GATK/input')
        self.valid_prog_environs = ['PrgEnv-cray']

        self.exclusive = True
        self.use_multithreading=False
        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = threads

        bam_files = ['Chr26Bam30/Chr26_AUDOPU000000000454_renamed.bam',
                     'Chr26Bam30/Chr26_AUMERU000000000001_renamed.bam',
                     'Chr26Bam30/Chr26_AUMERU000000000002_renamed.bam',
                     'Chr26Bam30/Chr26_AUMERU000000000454_renamed.bam',
                     'Chr26Bam30/Chr26_AUNAMU000000000011_renamed.bam',
                     'Chr26Bam30/Chr26_AURONU000000000002_renamed.bam',
                     'Chr26Bam30/Chr26_AURONU000000000004_renamed.bam',
                     'Chr26Bam30/Chr26_BDBAGU000000000014_renamed.bam',
                     'Chr26Bam30/Chr26_BDBANU000000000002_renamed.bam',
                     'Chr26Bam30/Chr26_BDBANU000000000004_renamed.bam',
                     'Chr26Bam30/Chr26_BRBRAU000000000001_renamed.bam',
                     'Chr26Bam30/Chr26_BRBRAU000000000003_renamed.bam',
                     'Chr26Bam30/Chr26_BRMORU000000000003_renamed.bam',
                     'Chr26Bam30/Chr26_CHMIRU000000000002_renamed.bam',
                     'Chr26Bam30/Chr26_CHSWAU000000000003_renamed.bam',
                     'Chr26Bam30/Chr26_CHSWAU000000000004_renamed.bam',
                     'Chr26Bam30/Chr26_CHSWAU000000000027_renamed.bam',
                     'Chr26Bam30/Chr26_CHSWAU000000000029_renamed.bam',
                     'Chr26Bam30/Chr26_CHVBNU000000000002_renamed.bam',
                     'Chr26Bam30/Chr26_CNTIBU000000000008_renamed.bam',
                     'Chr26Bam30/Chr26_CNTIBU000000000011_renamed.bam',
                     'Chr26Bam30/Chr26_ESCASU000000000001_renamed.bam',
                     'Chr26Bam30/Chr26_ESCASU000000000003_renamed.bam',
                     'Chr26Bam30/Chr26_ESCHUU000000000001_renamed.bam',
                     'Chr26Bam30/Chr26_ESCHUU000000000002_renamed.bam',
                     'Chr26Bam30/Chr26_ESOJAU000000000004_renamed.bam',
                     'Chr26Bam30/Chr26_ESOJAU000000000005_renamed.bam',
                     'Chr26Bam30/Chr26_ESSALU000000000001_renamed.bam',
                     'Chr26Bam30/Chr26_ESSALU000000000002_renamed.bam',
                     'Chr26Bam30/Chr26_ETMENU000000000001_renamed.bam']

        self.readonly_files = bam_files + [
                     'Ovis_aries.Oar_v3.1.dna_sm.toplevel.fa',
                     'Ovis_aries.Oar_v3.1.dna_sm.toplevel.dict',
                     'Ovis_aries.Oar_v3.1.dna_sm.toplevel.fa.fai',
                     'GenomeAnalysisTK.jar']

        self.executable = 'java'
        exe = os.path.join(self.sourcesdir,'GenomeAnalysisTK.jar')
        out = 'output.vcf'
        ref = 'Ovis_aries.Oar_v3.1.dna_sm.toplevel.fa'
        self.executable_opts = ['-Xmx8G -jar ', exe, 
                               '-R ', ref ,
                               '-T UnifiedGenotyper -I  ',
                               ' -I '.join(bam_files),
                               '-o ', out ,'-out_mode EMIT_VARIANTS_ONLY ',
                               '-stand_call_conf 20 -stand_emit_conf 20 ',
                               '-A FisherStrand -A StrandOddsRatio ',
                               '-A StrandBiasBySample ',
                               '-rf BadCigar ',
                               '--genotype_likelihoods_model BOTH ',
                               '-L 26:1000000-2000000 ', 
                               '-nt {}'.format(self.num_cpus_per_task) ,
                               '-log GATK.log']

        ref_desc = 'Time taken by GATK in seconds is:'

        self.multirun_pre_run = ['beg_secs=$(date +%s)']
        self.multirun_post_run = ['end_secs=$(date +%s)',
                         'let wallsecs=$end_secs-$beg_secs',
                         'echo "{}" $wallsecs'.format(ref_desc)]

        self.multirun_san_pat = ['Done.', self.stdout]
        self.sanity_patterns = sn.assert_found(*self.multirun_san_pat)

        p_name = "perf_{}".format(threads)
        self.multirun_perf_pat = {}
        self.multirun_perf_pat[p_name] = [
           r'^{}\s+(?P<perf>\S+)'.format(ref_desc),
           self.stdout, 'perf', float]
        self.perf_patterns = {
            p_name: sn.extractsingle(*(self.multirun_perf_pat[p_name]))
        }

        self.maintainers = ['man']
        self.strict_check = True
        self.use_multithreading = False
    def setup(self, partition, environ, **job_opts):
        super().setup(partition, environ, **job_opts)
        self.job.launcher.options += ['--mem_bind=local']

class GATK_BM(GATKBaseCheck):
    def __init__(self, threads, **kwargs):
       super().__init__('GATK_BM_{}'.format(threads), threads, **kwargs)

       self.pre_run += self.multirun_pre_run
       self.post_run += self.multirun_post_run

       self.valid_systems = ['mahuika:compute']
       self.descr = 'GATK BM'

       self.reference = {     
           'mahuika:compute': {
                'perf_1':  (279, None, 0.10), 
                'perf_2':  (185, None, 0.10), 
                'perf_4':  (124, None, 0.10), 
                'perf_8':  ( 95, None, 0.10), 
           }
       }
       self.tags = {'BM'}


class GATK_PDT(GATKBaseCheck):
    def __init__(self, name, threads, **kwargs):
       super().__init__('GATK_PDT_{0}_{1}'.format(threads, name), 
                        threads, **kwargs)

       self.valid_systems = ['mahuika:compute']
       self.descr = 'GATK PDT'

       self.multirun_ref = {     
           'mahuika:compute': {
                'perf_1':  (264, None, (2*1.96)/264), 
           }
       }
       self.tags = {'PDT'}

def _get_checks(**kwargs):
    return [GATK_BM(1, **kwargs),
            GATK_BM(2, **kwargs),
            GATK_BM(4, **kwargs),
            GATK_BM(8, **kwargs),
            multirun(GATK_PDT)('', 1,**kwargs)
           ]
