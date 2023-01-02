import pytest

from hibernate import types


def test_openshift_cluster_init():
    cluster = types.OpenShiftCluster('my-cluster')
    assert cluster.name == 'my-cluster'
    assert len(cluster.machines) == 0

    machines = [
        types.Machine('machine-1', 'running'),
        types.Machine('machine-2', 'running')
    ]
    cluster_with_machines = types.OpenShiftCluster('my-other-cluster', machines)
    assert cluster_with_machines.name == 'my-other-cluster'
    assert len(cluster_with_machines.machines) == 2


def test_openshift_cluster_add_machine():
    machine_1 = types.Machine('machine-1', 'running')
    machine_2 = types.Machine('machine-2', 'running')
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
    # TODO: Check this out - If I don't explicitly set machines to an empty
    # list, the cluster is created with two machines. It must not be getting
    # cleared from a previous test.
    cluster = types.OpenShiftCluster('my-cluster', [])
    assert len(cluster.machines) == 0
    assert cluster.state == "Unknown"


def test_openshift_cluster_single_state():
    cluster = types.OpenShiftCluster('my-cluster', [])
    cluster.add_machine(types.Machine('machine-1', 'running'))
    assert cluster.state == "running"

    cluster.add_machine(types.Machine('machine-2', 'running'))
    assert cluster.state == "running"


def test_openshift_cluster_mixed_state():
    machines = [
        types.Machine('machine-1', 'running'),
        types.Machine('machine-2', 'stopped')
    ]
    cluster = types.OpenShiftCluster('my-cluster', machines)
    assert cluster.state == "running, stopped"


def test_machine_init():
    machine = types.Machine('my-machine', 'running')
    assert machine.name == 'my-machine'
    assert machine.state == 'running'
