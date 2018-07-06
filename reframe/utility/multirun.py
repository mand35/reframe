import reframe.utility.sanity as sn

def multirun(template_class):

# the MultiRunCheck reqires:
# name as first input parameter
# multirun_san_pat: the single sanity pattern
# multirun_perf_pat: the dict of performance pattern
# multirun_ref: the (single) reference with the target average value
# multirun_pre_run: to be added before each run (e.g. time meassure)
# multirun_post_run: to be added after each run (e.g. time meassure) 
   class MultiRunCheck(template_class):
       multi_rep = 11
       def __init__(self, name, *args, **kwargs):
          if name is not '':
             name += '_'
          super().__init__('{0}{1}runs'.format(name,self.multi_rep), 
                           *args, **kwargs)

          # scale the assumed runtime
          self.time_limit = (self.time_limit[0]*self.multi_rep+
                                int((self.time_limit[1]*self.multi_rep)/60), 
                             (self.time_limit[1]*self.multi_rep) % 60+
                                int((self.time_limit[2]*self.multi_rep) /60), 
                             (self.time_limit[2]*self.multi_rep) % 60)

          # check if we got #multi_rep the the sanity patern
          if hasattr(self, 'multirun_san_pat'):
             self.sanity_patterns = sn.assert_eq(sn.count(
                sn.findall(*self.multirun_san_pat)), self.multi_rep)

          # create the list of result values: first the average and  
          #   then all single elements (to be stored)
          if hasattr(self, 'multirun_perf_pat'):
             self.perf_patterns = {}
             for key in list(self.multirun_perf_pat.keys()):
                self.perf_patterns[key] = sn.avg(
                   sn.extractall(*(self.multirun_perf_pat[key])))
                for run in range(0,self.multi_rep):
                   self.perf_patterns[key+"_{}".format(run)] = sn.extractall(
                      *(self.multirun_perf_pat[key]))[run]
   
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
                    references[key+"_{}".format(run)] = (temp_ref[key][0],
                                                         None, None)
              self.reference = { partition.fullname: references }
   
           # run the executable multiple times also add e.g. time meassure 
           # TODO implement a loop in the job script 
           #   instead of repeating the commands
           if not hasattr(self, 'multirun_pre_run'):
              self.multirun_pre_run = ' '
           if not hasattr(self, 'multirun_post_run'):
              self.multirun_post_run = ' '
           launch_cmd = (' '.join(self.job.launcher.command(self.job)) + ' ' + 
                         ' '.join(self.job.launcher.options))
           opts = ' '.join(self.executable_opts)
           for i in range(0,self.multi_rep-1):
              self.pre_run += [*self.multirun_pre_run , (launch_cmd + ' ' + 
                                  self.executable + ' ' + opts), 
                                  *self.multirun_post_run]
           self.pre_run += self.multirun_pre_run
           self.post_run += self.multirun_post_run
   return MultiRunCheck

