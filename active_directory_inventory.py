# File: inventory_plugins/active_directory_inventory.py

from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.errors import AnsibleParserError
from ansible.module_utils._text import to_native
from ansible.template import Templar

DOCUMENTATION = r'''
---
name: active_directory_inventory
plugin_type: inventory
short_description: Dynamic inventory plugin to pull servers from Active Directory OUs
description:
  - Connects to Active Directory and fetches server names from specified Organizational Units (OUs).
options:
  plugin:
    description: Name of the plugin.
    required: true
    type: str
  server_uri:
    description: LDAP URI to connect to Active Directory (e.g., ldaps://ad.example.com).
    required: true
    type: str
  bind_user:
    description: User to bind to Active Directory (e.g., user@example.com).
    required: true
    type: str
  bind_password:
    description: Password for the bind user.
    required: true
    type: str
  base_dns:
    description: List of base DNs (OUs) to search for servers.
    required: true
    type: list
    elements: str
'''

# Safe import of ldap3
try:
    from ldap3 import Server, Connection, ALL
except ImportError:
    raise AnsibleParserError("Missing required Python package 'ldap3'. Install it with: pip install ldap3")

class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = 'active_directory_inventory'

    def verify_file(self, path):
        ''' Only accept YAML or YML files named active_directory_inventory.yml or yaml '''
        valid = False
        if super().verify_file(path):
            if path.endswith(('active_directory_inventory.yml', 'active_directory_inventory.yaml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):
        ''' Main entry point to parse inventory and connect to Active Directory '''
        super().parse(inventory, loader, path, cache)

        self.loader = loader
        self.inventory = inventory
        self.templar = Templar(loader=loader)

        # 🛠 Manually read and parse the YAML inventory file
        config_data = self._read_config_data(path)

        # 🛠 Manually extract options (no set_options used)
        try:
            self.server_uri = config_data['server_uri']
            self.bind_user = config_data['bind_user']
            self.bind_password = config_data['bind_password']
            self.base_dns = config_data['base_dns']
        except KeyError as e:
            raise AnsibleParserError(f"Missing required setting in inventory source: {e}")

        # Debug output
        self.display.v(f"Connecting to Active Directory server: {self.server_uri}")
        self.display.v(f"Binding user: {self.bind_user}")
        self.display.v(f"Base DNs to search: {self.base_dns}")

        # Connect to AD
        try:
            server = Server(self.server_uri, get_info=ALL)
            conn = Connection(server, user=self.bind_user, password=self.bind_password, auto_bind=True)
            self.display.v("✅ Successfully connected and authenticated to Active Directory.")
        except Exception as e:
            raise AnsibleParserError(f"Failed to connect to Active Directory server: {to_native(e)}")

        # Search each provided OU (base_dn)
        for base_dn in self.base_dns:
            self.display.v(f"🔎 Searching for computers under base DN: {base_dn}")

            try:
                conn.search(
                    search_base=base_dn,
                    search_filter='(objectClass=computer)',
                    attributes=['name', 'dNSHostName']
                )

                if not conn.entries:
                    self.display.v(f"⚠️ No computers found under base DN: {base_dn}")

                for entry in conn.entries:
                    hostname = str(entry.name)
                    fqdn = str(entry.dNSHostName) if 'dNSHostName' in entry else hostname

                    # Add host to dynamic inventory
                    self.inventory.add_host(hostname)
                    self.inventory.set_variable(hostname, 'ansible_host', fqdn)

                    # Debug output per server
                    self.display.v(f"✅ Added server {hostname} (ansible_host={fqdn})")

            except Exception as e:
                raise AnsibleParserError(f"LDAP search failed for base_dn {base_dn}: {to_native(e)}")

        # Close the LDAP connection
        conn.unbind()
        self.display.v("🔒 LDAP connection closed.")
