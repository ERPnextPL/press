from __future__ import annotations

import sys
from getpass import getpass
from pathlib import Path

from backbone.ansible import AnsibleProvisioner
from backbone.proxmox import ProxmoxManager


def main(args: list[str] | None = None) -> None:
    """Interactively create a Proxmox cluster."""
    host = input("Proxmox Host: ")
    token_id = input("API Token ID: ")
    token_secret = getpass("API Token Secret: ")
    node = input("Node: ")
    bridge = input("Bridge: ")
    cidr = input("CIDR: ")
    count = int(input("Number of VMs: "))
    private_key = input("SSH Private Key [~/.ssh/id_rsa]: ") or "~/.ssh/id_rsa"
    public_key = input("SSH Public Key [~/.ssh/id_rsa.pub]: ") or "~/.ssh/id_rsa.pub"
    machines = []
    for i in range(count):
        vmid = int(input(f"VM {i + 1} ID: "))
        name = input(f"VM {i + 1} name: ")
        ip = input(f"VM {i + 1} IP: ")
        cores = int(input(f"VM {i + 1} cores [1]: ") or 1)
        memory = int(input(f"VM {i + 1} memory MB [1024]: ") or 1024)
        machines.append({"vmid": vmid, "name": name, "cores": cores, "memory": memory, "ip": ip})
    mgr = ProxmoxManager(host, token_id, token_secret)
    mgr.create_cluster(node=node, bridge=bridge, cidr=cidr, machines=machines)
    playbook = str(Path(__file__).parent.joinpath("playbooks", "setup_ubuntu.yml"))
    provisioner = AnsibleProvisioner(playbook, private_key)
    provisioner.provision([m["ip"] for m in machines], public_key)


if __name__ == "__main__":
	sys.exit(main(sys.argv))
