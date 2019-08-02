import time
import json


processes = {}
subprocess_hooks = {}


def register_process(name, process):
    processes[name] = process


def insert_global_hook(name, process):
    processes[name] = process


def insert_global_processor_hook(old_path, new_path):
    subprocess_hooks[old_path] = new_path


class ProcessorGenerator(object):
    INITIAL_PROCESS = "initial_process"
    INHERIT = "inherit"
    OVERRIDE = "override"
    TRANSITIONS = "transitions"
    SUB_PROCESSORS = "sub_processors"

    @staticmethod
    def generate(file_path):
        # Load processor file
        try:
            p = subprocess_hooks[file_path]
        except KeyError:
            p = file_path

        file = ProcessorGenerator._open_file(p)
        transitions = {}

        #
        sub_processors = {}

        for sub_processor_key in file[ProcessorGenerator.SUB_PROCESSORS]:
            sub_processor = ProcessorGenerator.generate(file[ProcessorGenerator.SUB_PROCESSORS][sub_processor_key])

            if not sub_processor:
                print(file["name"], "1: Sub-Processor Generation Error")
                return None

            sub_processors[sub_processor_key] = sub_processor

        if not file:
            print(file["name"], "2: File Error")
            return None

        # Create blank processor instance
        processor = Processor()

        # Set initial process
        try:
            processor.initial_process = processes[file[ProcessorGenerator.INITIAL_PROCESS]]
        except KeyError:
            try:
                processor.initial_process = sub_processors[file[ProcessorGenerator.INITIAL_PROCESS]]
            except KeyError:
                print(file["name"], "3: [KeyError] Unable to set initial process")
                return None

        # Copy all transitions from inherited processor (single inheritance only)
        if file[ProcessorGenerator.INHERIT]:
            inherit_file = ProcessorGenerator._open_file(file[ProcessorGenerator.INHERIT])

            if not inherit_file:
                print(file["name"], "4")
                return None

            transitions = inherit_file[ProcessorGenerator.TRANSITIONS]

        # Set/override with all local transitions
        for transition in file[ProcessorGenerator.TRANSITIONS]:
            transitions[transition] = file[ProcessorGenerator.TRANSITIONS][transition]

        # Add transitions to processor
        for process_key in transitions:
            for signal in transitions[process_key]:
                signal_location = signal.split(".")[0]
                signal_value = signal.split(".")[1]

                # Define Transition
                try:
                    t_process = processes[process_key]
                except KeyError:
                    try:
                        t_process = sub_processors[process_key]
                    except KeyError:
                        print(file["name"], "5")
                        return None

                try:
                    t_signal = processes[signal_location].signals[signal_value]
                except KeyError:
                    try:
                        t_signal = sub_processors[signal_location].signals[signal_value]
                    except KeyError:
                        print(file["name"], "6")
                        return None

                try:
                    t_next = processes[transitions[process_key][signal]]
                except KeyError:
                    try:
                        t_next = sub_processors[transitions[process_key][signal]]
                    except KeyError:
                        print(file["name"], "7")
                        return None

                t = Transition(t_process, t_signal, t_next)

                # Add Transition
                processor.add_transition(t)

        return processor

    @staticmethod
    def _open_file(file_path):
        try:
            with open(file_path) as file:
                data = json.load(file)
        except FileNotFoundError:
            return None
        except PermissionError:
            return None

        return data


def generate_processor(file_path):
    with open(file_path) as file:
        data = json.load(file)

    # Create Processor Instance
    processor = Processor()

    # Set initial process
    processor.initial_process = processes[data["initial_process"]]

    # Create Transitions
    for proc in data["transitions"]:
        for signal in data["transitions"][proc]:
            processor.add_transition(Transition(processes[proc], processes[proc].signals[signal], processes[data["transitions"][proc][signal]]))

    return processor


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
        self.signals = {"LOOP": Signal()}
        self._transition_time = time.time()

    def execute(self):
        return self.signals["LOOP"]

    def on_transition(self):
        self._transition_time = time.time()

    def relinquish(self):
        return True

    def loop_time(self):
        return time.time() - self._transition_time

    def register_signal(self, name):
        self.signals[name] = Signal()


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
            print("Transition:", type(self._current_process).__name__)

        # Execute current process
        result = self._current_process.execute()

        next_process = None

        # Process LOOP signals, setting the next process to be the current process, otherwise check for transitions
        if result == self._current_process.signals["LOOP"]:
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
            return self.signals["LOOP"]

    def on_transition(self):
        """ On transition ensure processor is started from its initial process. """
        self._prev_process = None
        self._current_process = self._initial_process

    def add_transition(self, t):
        self._transitions.append(t)

    def relinquish(self):
        try:
            return self._current_process.relinquish()
        except AttributeError:
            return True


class ProcessorSwitch(object):
    def __init__(self):
        self._processors = {}
        self._current_processor = ""
        self._prev_processor = ""

    def execute(self, process_name):
        try:
            if process_name != self._current_processor:
                if self._processors[self._current_processor].relinquish():
                    self._current_processor = process_name

            if process_name != self._prev_processor:
                self._processors[process_name].on_transition()

            self._processors[self._current_processor].execute()

            self._prev_processor = process_name
        except (KeyError, AttributeError):
            pass

    def register_processor(self, name, processor):
        self._processors[name] = processor
