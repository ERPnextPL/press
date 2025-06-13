from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Sequence


class AnsibleProvisioner:
    def __init__(self, playbook: str, key_path: str, user: str = "root"):
        self.playbook = playbook
        self.key_path = os.path.expanduser(key_path)
        self.user = user

    def provision(self, hosts: Sequence[str], public_key_path: str) -> None:
        inventory_data = "[all]\n" + "\n".join(hosts) + "\n"
        with NamedTemporaryFile("w", delete=False) as inventory:
            inventory.write(inventory_data)
            inventory_path = inventory.name

        with open(os.path.expanduser(public_key_path)) as f:
            pub_key = f.read().strip()

        extra_vars = json.dumps({"pub_key": pub_key})
        cmd = [
            "ansible-playbook",
            "-i",
            inventory_path,
            "-u",
            self.user,
            "--private-key",
            self.key_path,
            self.playbook,
            "-e",
            extra_vars,
        ]
        result = subprocess.run(cmd, text=True)
        Path(inventory_path).unlink(missing_ok=True)
        if result.returncode:
            raise Exception("Ansible provisioning failed")
