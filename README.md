# oc-hibernate

**Start and stop OpenShift clusters running in AWS.**

#### **Q: Why shut down an OpenShift cluster?**
**A:** Cost. Testing failover. I'm sure there are other reasons.

#### **Q: Is this stable?**
**A:** No! This is a work in progress. If you're a Red Hat employee, this
should work on RHPDS open environments pre-provisioned with OpenShift
installed.

#### **Q: What about certificates?**
**A:** OpenShift runs an internal certificate authority (CA) that issues
certificates for every node in a cluster. These node certificates are short
lived. When the cluster is provisioned, the initial certificates are only valid
for 24 hours. After the initial rotation, any issued node certificates are
valid for 30 days. OpenShift will automatically handle certificate rotation of
node certificates shortly before they expire.

The consideration here is, if the nodes are powered off, OpenShift can’t
automatically rotate the certificates. When the cluster boots after
certificates have expired, the cluster will not function properly.

oc-hibernate offers a subcommand `fix-certs` to address this issue. See Usage
below.

## Prerequisites

`aws`, `ansible-playbook`, and `oc` need to be in your PATH. Install those
through your package manager.

`anisble-playbook` is provided by the `ansible` package.

Additionally, you must configure your AWS credentials/region with `aws
configure`.

## Installation

Building from source is the only installation path until this project is more
stable.

1. Build a binary with `make build`. It will create the binary under `./dist/oc-hibernate`.
2. Run `make install` or manually copy the binary into a directory in your PATH.

**Do not rename the binary.** `oc`/`kubectl` plugins must be prefixed with
`oc-` for `oc SUBCOMMAND` (e.g. `oc hibernate`) to work.

## Usage

### Check status of all clusters

```bash
$ oc hibernate list
```

### Check status of specific cluster

This will return individual machine statuses.

```bash
$ oc hibernate list CLUSTER_NAME
```

### Stop a cluster

```
$ oc hibernate stop CLUSTER_NAME
```

### Resume a cluster

```
$ oc hibernate start CLUSTER_NAME
```

### Approve Pending CertificateSigningRequests (CSRs)

**NOTE:** This will run against the current `oc/kubectl` context.

```
$ oc fix-certs
```
