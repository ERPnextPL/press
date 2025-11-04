# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

import frappe


def execute():
        for name in frappe.db.get_all("Release Group", pluck="name"):
                if frappe.db.exists(
                        "Release Group Dependency", {"parent": name, "dependency": "PIP_VERSION"}
                ):
                        continue

                release_group = frappe.get_doc("Release Group", name)

                pip_version = None
                if release_group.version:
                        pip_version = frappe.db.get_value(
                                "Frappe Version Dependency",
                                {"parent": release_group.version, "dependency": "PIP_VERSION"},
                                "version",
                        )

                if not pip_version:
                        pip_version = "25.3"

                release_group.append(
                        "dependencies",
                        {"dependency": "PIP_VERSION", "version": pip_version},
                )
                release_group.db_update_all()
