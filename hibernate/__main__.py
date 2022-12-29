"""Main module for hibernate. Hibernate uses the click CLI package. The main
command `oc-hibernate` does nothing except perform preflight checks. The
subcommands `oc-hibernate COMMAND` actually perform functions.
"""

import json
import sys

import click
import sh

from hibernate import helper


@click.group()
def cli():
    """Stop and resume OpenShift clusters in AWS."""
    helper.run_preflight_checks()


@cli.command()
def fix_certs():
    """Approve pending certificate signing requests."""
    try:
        oc_cmd_output = sh.oc("get", "csr", "-o", "json")
    except sh.ErrorReturnCode as exception:
        print(exception.stdout.decode('utf-8'), end="")
        helper.print_error(exception.stderr.decode('utf-8'), end="")
        sys.exit(1)

    oc_response = json.loads(oc_cmd_output.stdout)

    # Check each CSR for Pending status
    pending_csr_names = []
    for csr in oc_response["items"]:
        name = csr["metadata"]["name"]
        conditions = []
        if csr["status"] and csr["status"]["conditions"]:
            for condition in csr["status"]["conditions"]:
                conditions.append(condition["type"])
        else:
            # CSRs without a status/condition are assumed to be pending
            conditions.append("Pending")
        if "Pending" in conditions:
            pending_csr_names.append(name)

    if len(pending_csr_names) == 0:
        print('No CSRs to approve!')
        sys.exit()

    # Approve all pending CSRs
    try:
        oc_cmd_output = sh.oc(
            "adm",
            "certificate",
            "approve",
            *pending_csr_names,
            _in=sys.stdin,
            _out=sys.stdout
        )
    except sh.ErrorReturnCode as exception:
        print(exception.stdout.decode('utf-8'), end="")
        helper.print_error(exception.stderr.decode('utf-8'), end="")
        sys.exit(1)


@cli.command(name="list")
@click.argument("CLUSTER_ID", required=False)
@click.option(
    "--profile",
    default="default",
    help="Use specific AWS profile instead of default."
)
def list_clusters(cluster_id, profile):
    """List status of available clusters."""
    clusters = helper.get_availible_cluster_ids(profile)

    # If cluster_id was passed, print machine statuses for that cluster
    if cluster_id:
        for cluster in clusters:
            if cluster['cluster_id'] == cluster_id:
                template = "{instance:50}{state:10}"
                print(template.format(instance="INSTANCE", state="STATE"))
                for instance in cluster['machines']:
                    print(
                        template.format(
                            instance=instance['name'],
                            state=instance['state']
                        )
                    )
        sys.exit()

    # Default - if no cluster_id was passed, print all cluster statuses
    template = "{cluster_id:30}{state:10}"
    print(template.format(cluster_id="CLUSTER", state="STATE"))
    for cluster in clusters:
        print(
            template.format(
                cluster_id=cluster['cluster_id'],
                state=cluster['state']
            )
        )


@cli.command()
@click.argument("CLUSTER_ID")
@click.option(
    "--profile",
    default="default",
    help="Use specific AWS profile instead of default."
)
def start(cluster_id, profile):
    """Resume (start up) a cluster."""
    playbook_path = helper.get_resource_path('playbooks/start.yml')
    sh.ansible_playbook(
        playbook_path,
        "--extra-vars", f'cluster_id="{cluster_id}"',
        "--extra-vars", f'aws_profile="{profile}"',
        _in=sys.stdin,
        _out=sys.stdout
    )


@cli.command()
@click.argument("CLUSTER_ID", required=False)
@click.option(
    "--current-context",
    help="Stop the cluster in your current context.",
    is_flag=True
)
@click.option(
    "--profile",
    default="default",
    help="Use specific AWS profile instead of default."
)
def stop(cluster_id, current_context, profile):
    """Stop (shut down) a cluster."""
    if current_context:
        cluster_id = helper.get_cluster_id()

    if not cluster_id:
        helper.print_error("ERROR: Must provide cluster_id or use --current_context")
        sys.exit(1)

    playbook_path = helper.get_resource_path('playbooks/stop.yml')
    sh.ansible_playbook(
        playbook_path,
        "--extra-vars", f'cluster_id="{cluster_id}"',
        "--extra-vars", f'aws_profile="{profile}"',
        _in=sys.stdin,
        _out=sys.stdout
    )
