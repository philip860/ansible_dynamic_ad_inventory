#!/usr/bin/env python3

import os
import sys
import json
import getpass

# 🛠 Set the plugin path environment variable **before** loading anything Ansible
plugin_path = '/root/python_Scripts/ansible_dynamic_inventory/inventory_plugins'
existing_inventory_plugins = os.getenv('ANSIBLE_INVENTORY_PLUGINS', '')

if existing_inventory_plugins:
    new_plugin_path = f"{plugin_path}:{existing_inventory_plugins}"
else:
    new_plugin_path = plugin_path

os.environ['ANSIBLE_INVENTORY_PLUGINS'] = new_plugin_path

# Now safe to import Ansible stuff
from ansible.plugins.loader import inventory_loader
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar
from ansible.errors import AnsibleParserError
from ansible.cli import CLI
from ansible.utils.display import Display

display = Display()

def main():
    inventory_yaml_path = '/root/python_Scripts/ansible_dynamic_inventory/active_directory_inventory.yml'

    loader = DataLoader()

    # Vault password handling
    vault_password_file = os.getenv('ANSIBLE_VAULT_PASSWORD_FILE', None)

    if vault_password_file:
        display.v("Using Vault password file from environment variable.")
        loader.set_vault_secrets([('default', CLI.setup_vault_secrets(vault_ids=None, vault_password_files=[vault_password_file]))])
    else:
        # Prompt user manually for Vault password
        vault_password = getpass.getpass(prompt="Vault password: ")
        from ansible.parsing.vault import VaultSecret
        loader.set_vault_secrets([('default', VaultSecret(vault_password.encode('utf-8')))])

    # Load inventory source YAML
    try:
        inventory_source_data = loader.load_from_file(inventory_yaml_path)
    except Exception as e:
        raise AnsibleParserError(f"Failed to load inventory source file: {e}")

    # Manually load the plugin
    plugin = inventory_loader.get('active_directory_inventory')

    # Create a dummy inventory object
    inventory = type('inventory', (), {
        'hosts': {},
        'groups': {},
        'add_host': lambda self, host, group=None: self.hosts.setdefault(host, {"groups": []}) if not group else (self.hosts.setdefault(host, {"groups": []})["groups"].append(group)),
        'set_variable': lambda self, host, var, val: self.hosts.setdefault(host, {}).update({var: val}),
        'add_group': lambda self, group: self.groups.setdefault(group, {})
    })()

    # Parse using your plugin
    plugin.parse(inventory, loader, inventory_yaml_path, cache=False)

    # Build JSON output
    output = {
        "_meta": {
            "hostvars": {}
        }
    }

    for host, attrs in inventory.hosts.items():
        output["_meta"]["hostvars"][host] = attrs

    for group, _ in inventory.groups.items():
        if group not in output:
            output[group] = {"hosts": []}
        for host, attrs in inventory.hosts.items():
            if "groups" in attrs and group in attrs["groups"]:
                output[group]["hosts"].append(host)

    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
