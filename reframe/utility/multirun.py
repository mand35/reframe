import reframe.utility.sanity as sn

def multirun(template_class):

# the MultiRunCheck reqires:
# name as first input parameter
# multirun_san_pat: the single sanity pattern
# multirun_perf_pat: the dict of performance pattern
# multirun_pre_run: to be added before each run (e.g. time meassure)
# multirun_post_run: to be added after each run (e.g. time meassure) 
   class MultiRunCheck(template_class):
       multi_rep = 3
       def __init__(self, name, **kwargs):
          super().__init__('{0}_{1}runs'.format(name,self.multi_rep), **kwargs)

          # check if we got #multi_rep the the sanity patern
          if hasattr(self, 'multirun_san_pat'):
             self.sanity_patterns = sn.assert_eq(sn.count(
                sn.findall(*self.multirun_san_pat)), self.multi_rep)

          # create the list of result values: first the average and  
          #   then all single elements (to be stored)
          if hasattr(self, 'multirun_perf_pat'):
             key = list(self.multirun_perf_pat.keys())[0]
             perf_list = sn.extractall(*self.multirun_perf_pat[key])
             self.perf_patterns = {}
             self.perf_patterns[key] = sn.avg(perf_list)
             for run in range(0,self.multi_rep):
                self.perf_patterns[key+"_{}".format(run)] = perf_list[run]
   
       # run the test #multi_rep times
       def setup(self, partition, environ, **job_opts):
           super().setup(partition, environ, **job_opts)

           # create the REFERENCE values (1 with the average and the limit
           #   and multi_rep times the average value without limits)
           if hasattr(self, 'multirun_ref'):
              temp_ref = {}
              temp_ref = self.multirun_ref[partition.fullname]
              references = {}
              for key in temp_ref.keys():
                 references[key] = temp_ref[key]
                 for run in range(0,self.multi_rep):
                    references[key+"_{}".format(run)] = (temp_ref[key],
                                                         None, None)
              self.reference = { partition.fullname: references }
   
           # run the executable multiple times also add e.g. time meassure 
           if not hasattr(self, 'multirun_pre_run'):
              self.multirun_pre_run = ' '
           if not hasattr(self, 'multirun_post_run'):
              self.multirun_post_run = ' '
           launch_cmd = ' '.join(self.job.launcher.command(self.job))
           opts = ' '.join(self.executable_opts)
           for i in range(0,self.multi_rep-1):
              self.pre_run += (self.multirun_pre_run + 
                  [launch_cmd + " " + self.executable + opts] + 
                  self.multirun_post_run)
           self.pre_run += self.multirun_pre_run
           self.post_run += self.multirun_post_run
   return MultiRunCheck

