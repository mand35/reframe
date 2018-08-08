#
# Scheduler implementations
#

import abc
import os

import reframe.core.debug as debug
import reframe.core.fields as fields
import reframe.core.shell as shell
from reframe.core.exceptions import JobNotStartedError
from reframe.core.launchers import JobLauncher


class JobState:
    def __init__(self, state):
        self._state = state

    def __repr__(self):
        return debug.repr(self)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        return self._state == other._state

    def __str__(self):
        return self._state


class Job(abc.ABC):
    """A job descriptor.

    .. caution::
       This is an abstract class.
       Users may not create jobs directly.
    """

    #: Options to be passed to the backend job scheduler.
    #:
    #: :type: :class:`list` of :class:`str`
    #: :default: ``[]``
    options = fields.TypedListField('options', str)

    #: The parallel program launcher that will be used to launch the parallel
    #: executable of this job.
    #:
    #: :type: :class:`reframe.core.launchers.JobLauncher`
    launcher = fields.TypedField('launcher', JobLauncher)

    _jobid = fields.IntegerField('_jobid', allow_none=True)
    _exitcode = fields.IntegerField('_exitcode', allow_none=True)
    _state = fields.TypedField('_state', JobState, allow_none=True)

    # The sched_* arguments are exposed also to the frontend
    def __init__(self,
                 name,
                 launcher,
                 workdir='.',
                 num_tasks=1,
                 num_tasks_per_node=None,
                 num_tasks_per_core=None,
                 num_tasks_per_socket=None,
                 num_cpus_per_task=None,
                 use_smt=None,
                 time_limit=(0, 10, 0),
                 script_filename=None,
                 stdout=None,
                 stderr=None,
                 pre_run=[],
                 post_run=[],
                 sched_account=None,
                 sched_partition=None,
                 sched_reservation=None,
                 sched_nodelist=None,
                 sched_exclude_nodelist=None,
                 sched_exclusive_access=None,
                 sched_options=[]):

        # Mutable fields
        self.options = list(sched_options)
        self.launcher = launcher

        self._name = name
        self._workdir = workdir
        self._num_tasks = num_tasks
        self._num_tasks_per_node = num_tasks_per_node
        self._num_tasks_per_core = num_tasks_per_core
        self._num_tasks_per_socket = num_tasks_per_socket
        self._num_cpus_per_task = num_cpus_per_task
        self._use_smt = use_smt
        self._script_filename = script_filename or '%s.sh' % name
        self._stdout = stdout or os.path.join(workdir, '%s.out' % name)
        self._stderr = stderr or os.path.join(workdir, '%s.err' % name)
        self._time_limit = time_limit

        # Backend scheduler related information
        self._sched_nodelist = sched_nodelist
        self._sched_exclude_nodelist = sched_exclude_nodelist
        self._sched_partition = sched_partition
        self._sched_reservation = sched_reservation
        self._sched_account = sched_account
        self._sched_exclusive_access = sched_exclusive_access

        # Live job information; to be filled during job's lifetime by the
        # scheduler
        self._jobid = None
        self._exitcode = None
        self._state = None

    def __repr__(self):
        return debug.repr(self)

    # Read-only properties
    @property
    def exitcode(self):
        return self._exitcode

    @property
    def jobid(self):
        return self._jobid

    @property
    def state(self):
        return self._state

    @property
    def name(self):
        return self._name

    @property
    def workdir(self):
        return self._workdir

    @property
    def num_tasks(self):
        return self._num_tasks

    @property
    def script_filename(self):
        return self._script_filename

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr

    @property
    def time_limit(self):
        return self._time_limit

    @property
    def num_cpus_per_task(self):
        return self._num_cpus_per_task

    @property
    def num_tasks_per_core(self):
        return self._num_tasks_per_core

    @property
    def num_tasks_per_node(self):
        return self._num_tasks_per_node

    @property
    def num_tasks_per_socket(self):
        return self._num_tasks_per_socket

    @property
    def use_smt(self):
        return self._use_smt

    @property
    def sched_nodelist(self):
        return self._sched_nodelist

    @property
    def sched_exclude_nodelist(self):
        return self._sched_exclude_nodelist

    @property
    def sched_partition(self):
        return self._sched_partition

    @property
    def sched_reservation(self):
        return self._sched_reservation

    @property
    def sched_account(self):
        return self._sched_account

    @property
    def sched_exclusive_access(self):
        return self._sched_exclusive_access

    def prepare(self, commands, environs=None, **gen_opts):
        environs = environs or []
        with shell.generate_script(self.script_filename,
                                   **gen_opts) as builder:
            builder.write_prolog(self.emit_preamble())
            for e in environs:
                builder.write(e.emit_load_commands())

            for c in commands:
                builder.write_body(c)

    @abc.abstractmethod
    def emit_preamble(self):
        pass

    @abc.abstractmethod
    def submit(self):
        pass

    @abc.abstractmethod
    def wait(self):
        if self._jobid is None:
            raise JobNotStartedError('cannot wait an unstarted job')

    @abc.abstractmethod
    def cancel(self):
        if self._jobid is None:
            raise JobNotStartedError('cannot cancel an unstarted job')

    @abc.abstractmethod
    def finished(self):
        if self._jobid is None:
            raise JobNotStartedError('cannot poll an unstarted job')
