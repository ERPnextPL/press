from __future__ import annotations

import sys
from argparse import ArgumentParser
from getpass import getpass
from pathlib import Path

from backbone.ansible import AnsibleProvisioner
from backbone.proxmox import ProxmoxManager


def main(args: list[str] | None = None) -> None:
        """Create a Proxmox cluster."""
        parser = ArgumentParser()
        parser.add_argument("--insecure", action="store_true", help="Disable SSL certificate verification")
        parser.add_argument("--skip-private-network", action="store_true", help="Skip creating private network")
        parser.add_argument("--host")
        parser.add_argument("--token-id")
        parser.add_argument("--token-secret")
        parser.add_argument("--node")
        parser.add_argument("--bridge")
        parser.add_argument("--cidr")
        parser.add_argument("--count", type=int, default=1)
        parser.add_argument("--machine", dest="machines_data", action="append", help="vmid|name|ip|cores|memory")
        parser.add_argument("--private-key", default="~/.ssh/id_rsa")
        parser.add_argument("--public-key", default="~/.ssh/id_rsa.pub")
        opts = parser.parse_args(args)

        host = opts.host or input("Proxmox Host: ")
        token_id = opts.token_id or input("API Token ID: ")
        token_secret = opts.token_secret or getpass("API Token Secret: ")
        node = opts.node or input("Node: ")
        bridge = opts.bridge or input("Bridge: ")
        cidr = opts.cidr or input("CIDR: ")
        count = opts.count
        private_key = opts.private_key or "~/.ssh/id_rsa"
        public_key = opts.public_key or "~/.ssh/id_rsa.pub"
        machines = []
        if opts.machines_data:
                for data in opts.machines_data:
                        parts = data.split("|")
                        if len(parts) < 3:
                                raise ValueError("machine must be 'vmid|name|ip|cores|memory'")
                        vmid = int(parts[0])
                        name = parts[1]
                        ip = parts[2]
                        cores = int(parts[3]) if len(parts) > 3 and parts[3] else 1
                        memory = int(parts[4]) if len(parts) > 4 and parts[4] else 1024
                        machines.append({"vmid": vmid, "name": name, "cores": cores, "memory": memory, "ip": ip})
        else:
                for i in range(count):
                        vmid = int(input(f"VM {i + 1} ID: "))
                        name = input(f"VM {i + 1} name: ")
                        ip = input(f"VM {i + 1} IP: ")
                        cores = int(input(f"VM {i + 1} cores [1]: ") or 1)
                        memory = int(input(f"VM {i + 1} memory MB [1024]: ") or 1024)
                        machines.append({"vmid": vmid, "name": name, "cores": cores, "memory": memory, "ip": ip})
        mgr = ProxmoxManager(host, token_id, token_secret, verify_ssl=not opts.insecure)
        mgr.create_cluster(
                node=node,
                bridge=bridge,
                cidr=cidr,
                machines=machines,
                create_private_network=not opts.skip_private_network,
        )
        playbook = str(Path(__file__).parent.joinpath("playbooks", "setup_ubuntu.yml"))
        provisioner = AnsibleProvisioner(playbook, private_key)
        provisioner.provision([m["ip"] for m in machines], public_key)


if __name__ == "__main__":
	sys.exit(main(sys.argv))
