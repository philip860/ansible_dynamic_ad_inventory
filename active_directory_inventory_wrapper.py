#!/usr/bin/env python3

import sys
import json
import os

# Make sure Ansible can find your plugin (set plugin path)
os.environ['ANSIBLE_INVENTORY_PLUGINS'] = '/root/python_Scripts/ansible_dynamic_inventory/inventory_plugins/'

# Now import ansible
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager

# Create Ansible inventory loader objects
loader = DataLoader()
inventory = InventoryManager(loader=loader, sources=['/root/python_Scripts/ansible_dynamic_inventory/active_directory_inventory.yml'])
variable_manager = VariableManager(loader=loader, inventory=inventory)

# Output the dynamic inventory in JSON format
print(json.dumps(inventory.get_groups_dict(), indent=2))
