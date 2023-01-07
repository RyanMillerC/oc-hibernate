import pytest

from hibernate import types


def test_openshift_cluster_init():
    cluster = types.OpenShiftCluster('my-cluster')
    assert cluster.name == 'my-cluster'
    assert len(cluster.machines) == 0

    machines = [
        types.Machine('machine-1', types.State.running),
        types.Machine('machine-2', types.State.running)
    ]
    cluster_with_machines = types.OpenShiftCluster('my-other-cluster', machines)
    assert cluster_with_machines.name == 'my-other-cluster'
    assert len(cluster_with_machines.machines) == 2


def test_openshift_cluster_add_machine():
    machine_1 = types.Machine('machine-1', types.State.running)
    machine_2 = types.Machine('machine-2', types.State.running)
    cluster = types.OpenShiftCluster('my-cluster')
    cluster.add_machine(machine_1)
    cluster.add_machine(machine_2)
    assert len(cluster.machines) == 2
    assert cluster.machines[0].name == 'machine-1'
    assert cluster.machines[1].name == 'machine-2'


def test_openshift_cluster_add_bad_machine():
    cluster = types.OpenShiftCluster('my-cluster')
    with pytest.raises(TypeError):
        cluster.add_machine('Not a machine!')


def test_openshift_cluster_state_no_machines():
    """OpenShiftCluster instance state property should be "Unknown" if
    instance contains 0 machines."""
    cluster = types.OpenShiftCluster('my-cluster')
    assert len(cluster.machines) == 0
    assert cluster.state == "Unknown"


def test_openshift_cluster_single_state():
    cluster = types.OpenShiftCluster('my-cluster')
    cluster.add_machine(types.Machine('machine-1', types.State.running))
    assert cluster.state == "Running"

    cluster.add_machine(types.Machine('machine-2', types.State.running))
    assert cluster.state == "Running"


def test_openshift_cluster_mixed_state():
    machines = [
        types.Machine('machine-1', types.State.running),
        types.Machine('machine-2', types.State.stopped)
    ]
    cluster = types.OpenShiftCluster('my-cluster', machines)
    assert cluster.state == "Running,Stopped"


def test_machine_init():
    machine = types.Machine('my-machine', types.State.running)
    assert machine.name == 'my-machine'
    assert machine.state == types.State.running


def test_machine_set_state_after_init():
    machine = types.Machine('my-machine', types.State.running)
    machine.state = types.State.stopped
    assert machine.state == types.State.stopped


def test_state_to_string():
    """Used as a string, State.running should print "Running"."""
    machine = types.Machine('my-machine', types.State.running)
    assert str(machine.state) == "Running"
