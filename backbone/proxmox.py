from __future__ import annotations

import requests


class ProxmoxManager:
	def __init__(self, host: str, token_id: str, token_secret: str, verify_ssl: bool = True):
		self.base_url = f"https://{host}:8006/api2/json"
		self.token_id = token_id
		self.token_secret = token_secret
		self.verify_ssl = verify_ssl

	def _headers(self) -> dict[str, str]:
		return {"Authorization": f"PVEAPIToken={self.token_id}={self.token_secret}"}

	def _post(self, path: str, data: dict[str, str]):
		url = f"{self.base_url}/{path.lstrip('/')}"
		return requests.post(url, headers=self._headers(), verify=self.verify_ssl, data=data)

	def create_private_bridge(self, node: str, bridge: str, cidr: str) -> None:
		payload = {"iface": bridge, "type": "bridge", "cidr": cidr, "comments": "Press private network"}
		resp = self._post(f"nodes/{node}/network", payload)
		if resp.status_code >= 400:
			raise Exception(f"Failed to create bridge: {resp.text}")

	def create_vm(
		self,
		node: str,
		vmid: int,
		name: str,
		bridge: str,
		cores: int = 1,
		memory: int = 1024,
		storage: str = "local-lvm",
	) -> None:
		payload = {
			"vmid": vmid,
			"name": name,
			"cores": cores,
			"memory": memory,
			"net0": f"virtio,bridge={bridge}",
			"scsi0": f"{storage}:8",
			"ide2": f"{storage}:cloudinit",
			"scsihw": "virtio-scsi-pci",
			"ostype": "l26",
		}
		resp = self._post(f"nodes/{node}/qemu", payload)
		if resp.status_code >= 400:
			raise Exception(f"Failed to create VM {name}: {resp.text}")

	def create_cluster(
		self,
		node: str,
		bridge: str,
		cidr: str,
		machines: list[dict[str, any]],
		create_private_network: bool = True,
	) -> None:
		if create_private_network:
			self.create_private_bridge(node, bridge, cidr)
		for machine in machines:
			self.create_vm(node=node, bridge=bridge, **machine)
