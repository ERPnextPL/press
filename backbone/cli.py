# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt
from pathlib import Path

import click

from backbone.hypervisor import Hypervisor, Shell
from backbone.proxmox import ProxmoxManager
from backbone.tests import run_tests


@click.group()
def cli():
	pass


@cli.group()
def hypervisor():
	pass


@hypervisor.command()
def setup():
	shell = Shell()
	hypervisor = Hypervisor(shell=shell)
	hypervisor.setup()


@hypervisor.command()
@click.option("--size", default=16384, type=int)
@click.option("--scaleway", is_flag=True)
def build(size, scaleway):
	shell = Shell()
	hypervisor = Hypervisor(shell=shell)
	if scaleway:
		hypervisor.build_scaleway(size=size)
	else:
		hypervisor.build(size=size)


@hypervisor.command()
def up():
	shell = Shell()
	hypervisor = Hypervisor(shell=shell)
	hypervisor.up()


@hypervisor.command()
@click.option("-c", "--command")
def ssh(command):
	shell = Shell()
	hypervisor = Hypervisor(shell=shell)
	hypervisor.ssh(command=command)


@cli.command()
def tests():
	run_tests()


@cli.group()
def proxmox():
	"""Manage Proxmox VMs"""


@proxmox.command()
@click.option("--node", prompt=True)
@click.option("--bridge", prompt=True)
@click.option("--cidr", prompt=True)
@click.option("--count", type=int, default=1, show_default=True)
@click.option("--private-key", default="~/.ssh/id_rsa", show_default=True)
@click.option("--public-key", default="~/.ssh/id_rsa.pub", show_default=True)
@click.option("--insecure", is_flag=True, help="Disable SSL certificate verification")
@click.option("--skip-private-network", is_flag=True, help="Skip creating private network")
@click.option("--host")
@click.option("--token-id")
@click.option("--token-secret")
@click.option("--machine", "machines_data", multiple=True, help="VM parameters as 'vmid|name|ip|cores|memory'")
def provision(node, bridge, cidr, count, private_key, public_key, insecure, skip_private_network, host, token_id, token_secret, machines_data):
	"""Provision VMs on Proxmox"""
	if host is None:
	host = click.prompt("Proxmox Host")
	if token_id is None:
	token_id = click.prompt("API Token ID")
	if token_secret is None:
	token_secret = click.prompt("API Token Secret", hide_input=True)
	mgr = ProxmoxManager(host, token_id, token_secret, verify_ssl=not insecure)
	machines = []
	if machines_data:
	for data in machines_data:
	parts = data.split("|")
	if len(parts) < 3:
	raise click.BadParameter("machine must be 'vmid|name|ip|cores|memory'")
	vmid = int(parts[0])
	name = parts[1]
	ip = parts[2]
	cores = int(parts[3]) if len(parts) > 3 and parts[3] else 1
	memory = int(parts[4]) if len(parts) > 4 and parts[4] else 1024
	machines.append({"vmid": vmid, "name": name, "cores": cores, "memory": memory, "ip": ip})
	else:
	for i in range(count):
	vmid = click.prompt(f"VM {i + 1} ID", type=int)
	name = click.prompt(f"VM {i + 1} name")
	ip = click.prompt(f"VM {i + 1} IP")
	cores = click.prompt(f"VM {i + 1} cores", type=int, default=1, show_default=True)
	memory = click.prompt(
	f"VM {i + 1} memory (MB)", type=int, default=1024, show_default=True
	)
	machines.append({"vmid": vmid, "name": name, "cores": cores, "memory": memory, "ip": ip})
	mgr.create_cluster(
	node=node,
	bridge=bridge,
	cidr=cidr,
	machines=machines,
	create_private_network=not skip_private_network,
	)
	from backbone.ansible import AnsibleProvisioner

	playbook = str(Path(__file__).parent.joinpath("playbooks", "setup_ubuntu.yml"))
	provisioner = AnsibleProvisioner(playbook, private_key)
	provisioner.provision([m["ip"] for m in machines], public_key)
