
class OpenShiftCluster():
    """Represents an OpenShift cluster."""
    def __init__(self, name, machines=[]):
        self.name = name
        self.machines = machines

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
        the states of all machines in the cluster."""
        if len(self.machines) == 0:
            return "Unknown"
        states = []
        for machine in self.machines:
            if machine.state not in states:
                states.append(machine.state)
        # if len(states) == 1:
        #     return states[0]
        return ", ".join(states)


class Machine():
    """Represents a machine in a cluster.

    :param str name:
        Name of the machine
    :param str state:
        Machine state
    """
    def __init__(self, name, state):
        self.name = name
        self.state = state
