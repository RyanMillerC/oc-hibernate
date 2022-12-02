# oc-hibernate

**Start and stop OpenShift clusters running in AWS.**

* **Q:** Why shut down an OpenShift cluster?
* **A:** Cost. Testing failover. I'm sure there are other reasons.

* **Q:** Is this stable?
* **A:** No! This is a work in progress. If you're a Red Hat employee, this
  should work on RHPDS open environments pre-provisioned with OpenShift
  installed.

* **Q:** How do I install this plugin?
* **A:** At the moment there is no workflow to generate binary releases. To
  install, run `make build`. It will create a binary under
  `./dist/oc-hibernate`. Copy that binary into your PATH.

## How to Use

### Check status of a cluster

```
$ oc hibernate status CLUSTER_NAME
```

### Stop a cluster

```
$ oc hibernate stop CLUSTER_NAME
```

### Resume a cluster

```
$ oc hibernate start CLUSTER_NAME
```
