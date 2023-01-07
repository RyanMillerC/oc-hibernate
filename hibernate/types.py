from enum import Enum, auto


class OpenShiftCluster:
    """Represents an OpenShift cluster."""
    def __init__(self, name, machines=[]):
        self.name = name
        # If machines isn't copied, the passed list and self.machines will
        # both point to the same list in memory.
        self.machines = machines.copy()

    def add_machine(self, machine):
        """Add a machine to self.machines

        :param hibernate.types.Machine machine:
            Machine to add.
        """
        if isinstance(machine, Machine):
            self.machines.append(machine)
        else:
            raise TypeError(f"Expected type Machine but received {type(machine)}")

    @property
    def state(self):
        """Dynamically determine value of self.state based by evaluating
        the states of all machines in the cluster.

        Cluster.state is a string, not a State enumerator. This is because a
        Cluster can have a mixed state if the machines in the cluster are in
        different states. If the cluster has a single state, that state as a
        string will be returned: "Running". If the cluster has a mixed state,
        the state will be returned as a CSV: "Running,Stopped".
        """
        if len(self.machines) == 0:
            return str(State.unknown)

        states = []
        for machine in self.machines:
            if machine.state not in states:
                states.append(machine.state)

        return ",".join([str(state) for state in states])


class Machine:
    """Represents a machine in a cluster.

    :param str name:
        Name of the machine
    :param hibernate.types.State state:
        Machine state enum
    """
    def __init__(self, name, state):
        self.name = name
        self.state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        if isinstance(new_state, State):
            self._state = new_state
        else:
            raise TypeError(f"Expected type State but received {type(new_state)}")


class State(Enum):
    """Represents the state of a machine on the cloud provider."""
    running = auto()
    stopped = auto()
    terminated = auto()
    unknown = auto()

    def __str__(self):
        """Print 'Example' instead of 'State.example'."""
        return self.name.title()
