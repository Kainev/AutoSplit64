import time


class Signal(object):
    """
    Object used to define transition relationships between processes
    """
    def __init__(self, name=""):
        self._name = name

    def name(self):
        return self._name


class Transition(object):
    """
    Define state transition behaviour between two processes given a Signal object
    """
    def __init__(self, process, signal, next_process):
        self.process = process
        self.signal = signal
        self.next_process = next_process

    def valid(self, process, signal):
        return self.process == process and self.signal == signal


class Process(object):
    LOOP = Signal()

    def __init__(self):
        self._transition_time = time.time()

    def execute(self):
        return Process.LOOP

    def on_transition(self):
        self._transition_time = time.time()

    def loop_time(self):
        return time.time() - self._transition_time


class Processor(Process):
    def __init__(self):
        super().__init__()

        # Processor
        self._initial_process = None
        self._prev_process = None
        self._current_process = None
        self._transitions = []

    @property
    def initial_process(self):
        return self._initial_process

    @initial_process.setter
    def initial_process(self, process):
        self._initial_process = process
        self._current_process = process

    def execute(self):
        if not self._current_process:
            return

        # If transitioning from a different process, call on_transition
        if self._current_process != self._prev_process:
            self._current_process.on_transition()

        # Execute current process
        result = self._current_process.execute()

        if result.name():
            print(result.name())

        next_process = None

        # Automatically process LOOP signal transitions, setting the next process to be the current process, otherwise check for transitions
        if result == Process.LOOP:
            next_process = self._current_process
        else:
            for transition in self._transitions:
                if transition.valid(self._current_process, result):
                    next_process = transition.next_process
                    break

        # Set processes for next execution
        self._prev_process = self._current_process
        self._current_process = next_process

        # If no valid transition is found, return result up processor chain
        if not next_process:
            return result
        else:
            return Process.LOOP

    def on_transition(self):
        """ On transition ensure processor is started from its initial process. """
        self._prev_process = None
        self._current_process = self._initial_process

    def add_transition(self, t):
        self._transitions.append(t)

    def relinquish(self):
        return True


class ProcessorSwitch(object):
    def __init__(self):
        self._processors = {}
        self._current_processor = ""
        self._prev_processor = ""

    def execute(self, process_name):
        try:
            if process_name != self._current_processor:
                print("!=")
                if self._processors[self._current_processor].relinquish():
                    print("relinquish")
                    self._current_processor = process_name

            if process_name != self._prev_processor:
                self._processors[process_name].on_transition()

            self._processors[self._current_processor].execute()

            self._prev_processor = process_name
        except (KeyError, AttributeError):
            pass

    def register_processor(self, name, processor):
        self._processors[name] = processor
