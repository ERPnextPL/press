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
def provision(node, bridge, cidr, count, private_key, public_key):
       """Interactively provision VMs on Proxmox"""
       host = click.prompt("Proxmox Host")
       token_id = click.prompt("API Token ID")
       token_secret = click.prompt("API Token Secret", hide_input=True)
       mgr = ProxmoxManager(host, token_id, token_secret)
       machines = []
       for i in range(count):
               vmid = click.prompt(f"VM {i + 1} ID", type=int)
               name = click.prompt(f"VM {i + 1} name")
               ip = click.prompt(f"VM {i + 1} IP")
               cores = click.prompt(
                       f"VM {i + 1} cores", type=int, default=1, show_default=True
               )
               memory = click.prompt(
                       f"VM {i + 1} memory (MB)", type=int, default=1024, show_default=True
               )
               machines.append({"vmid": vmid, "name": name, "cores": cores, "memory": memory, "ip": ip})
       mgr.create_cluster(node=node, bridge=bridge, cidr=cidr, machines=machines)
       from backbone.ansible import AnsibleProvisioner
       playbook = str(Path(__file__).parent.joinpath("playbooks", "setup_ubuntu.yml"))
       provisioner = AnsibleProvisioner(playbook, private_key)
       provisioner.provision([m["ip"] for m in machines], public_key)
