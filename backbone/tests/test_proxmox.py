import unittest
from unittest.mock import patch

from backbone.ansible import AnsibleProvisioner
from backbone.proxmox import ProxmoxManager


class TestProxmoxManager(unittest.TestCase):
	@patch("backbone.proxmox.requests.post")
	def test_create_private_bridge_success(self, post):
		post.return_value.status_code = 200
		mgr = ProxmoxManager("host", "id", "secret")
		self.assertIsNone(mgr.create_private_bridge("node1", "vmbr0", "10.0.0.0/24"))
		post.assert_called()

	@patch("backbone.proxmox.requests.post")
	def test_create_private_bridge_fail(self, post):
		post.return_value.status_code = 400
		mgr = ProxmoxManager("host", "id", "secret")
		with self.assertRaisesRegex(Exception, "Failed to create bridge"):
			mgr.create_private_bridge("node1", "vmbr0", "10.0.0.0/24")

	@patch("backbone.proxmox.requests.post")
	def test_create_vm_fail(self, post):
		post.return_value.status_code = 500
		mgr = ProxmoxManager("host", "id", "secret")
		with self.assertRaisesRegex(Exception, "Failed to create VM"):
			mgr.create_vm("node1", 101, "test", "vmbr0")

	@patch.object(ProxmoxManager, "create_private_bridge")
	@patch.object(ProxmoxManager, "create_vm")
	def test_create_cluster_skip_private_network(self, create_vm, create_bridge):
		mgr = ProxmoxManager("host", "id", "secret")
		mgr.create_cluster("node1", "vmbr0", "10.0.0.0/24", [], create_private_network=False)
		create_bridge.assert_not_called()


class TestAnsibleProvisioner(unittest.TestCase):
	@patch("backbone.ansible.subprocess.run")
	def test_provision_fail(self, run):
		run.return_value.returncode = 1
		prov = AnsibleProvisioner("playbook.yml", "id_rsa")
		with self.assertRaisesRegex(Exception, "Ansible provisioning failed"):
			prov.provision(["10.0.0.2"], "pub.key")
