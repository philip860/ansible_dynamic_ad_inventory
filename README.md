# Active Directory Dynamic Inventory for Ansible

This project provides a **custom dynamic inventory** solution for Ansible, pulling computer objects from **Active Directory** Organizational Units (OUs).

It uses:
- A custom Ansible **inventory plugin** (`active_directory_inventory.py`)
- A dynamic **inventory wrapper** script (`active_directory_inventory_wrapper.py`)
- A YAML **inventory configuration file** (`active_directory_inventory.yml`)

---

## 📂 Project Structure

| File | Purpose |
|:---|:---|
| `active_directory_inventory.py` | Custom Ansible Inventory Plugin to query Active Directory |
| `active_directory_inventory_wrapper.py` | Python wrapper script to call the plugin manually, outputting dynamic inventory |
| `active_directory_inventory.yml` | Inventory source configuration with Active Directory connection details |

---

## 🔥 How These Files Work Together

1. `active_directory_inventory.yml` holds your **Active Directory connection settings**.
2. `active_directory_inventory.py` is a **plugin** that reads the YAML, connects to AD via LDAP(S), and pulls server names.
3. `active_directory_inventory_wrapper.py` **loads the plugin**, handles Vault decryption if needed, and **outputs JSON inventory** for Ansible to consume.

---

## 🚀 Manual Usage (Generate Inventory Locally)

### 1. Install Requirements

Ensure you have:
- `python3`
- `ansible-core` 2.16+
- `ldap3` Python library

Install ldap3 if missing:

```bash
pip3 install ldap3
```

### 2. Prepare Files

Ensure the files are placed:

```bash
/root/python_Scripts/
├── active_directory_inventory_wrapper.py
└── ansible_dynamic_inventory/
    ├── active_directory_inventory.yml
    └── inventory_plugins/
        └── active_directory_inventory.py
```

Important:
- `inventory_plugins/` folder must contain `active_directory_inventory.py`.
- The environment variable `ANSIBLE_INVENTORY_PLUGINS` is automatically set by the wrapper script.

---

### 3. Configure Active Directory Settings

Edit `active_directory_inventory.yml`:

```yaml
plugin: active_directory_inventory
server_uri: "ldaps://your-ad-server.domain.com"
bind_user: "your_bind_account@domain.com"
bind_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  (vault encrypted password content)
base_dns:
  - "OU=Servers,OU=Example,DC=domain,DC=com"
```

Use `ansible-vault encrypt_string` to encrypt your bind password:

```bash
ansible-vault encrypt_string 'YourSuperSecretPassword' --name 'bind_password'
```

Then paste the output under `bind_password:`.

---

### 4. Set Vault Password (if using encryption)

If your `bind_password` is encrypted:

```bash
echo 'your-vault-password' > /etc/ansible/.vault_pass
chmod 600 /etc/ansible/.vault_pass
```

Export the environment variable:

```bash
export ANSIBLE_VAULT_PASSWORD_FILE=/etc/ansible/.vault_pass
```

Or the wrapper will prompt manually.

---

### 5. Run the Wrapper Manually

```bash
python3 /root/python_Scripts/active_directory_inventory_wrapper.py
```

The script will:
- Load the YAML config
- Connect to Active Directory
- Decrypt Vault secrets if needed
- Output dynamic inventory in JSON format

---

## 🎯 Using This Dynamic Inventory in AWX / Ansible Automation Platform (AAP)

### Option 1 — Custom Inventory Script (Recommended)

1. **Upload `active_directory_inventory_wrapper.py` into AWX/AAP:**
   - Inventories ➔ Sources ➔ Create New Source
   - Source Type: **Custom Script**
   - Upload `active_directory_inventory_wrapper.py`

2. **Configure the Inventory Source:**
   - Ensure `active_directory_inventory.yml` is accessible.
   - Attach a **Vault Credential** if needed.

3. **Sync Inventory:**
   - Trigger manual sync.

---

### Option 2 — Bundle Into an Execution Environment (Advanced)

Package the plugin and wrapper into a Docker container and register it as an Execution Environment.

---

## 🔋 Troubleshooting Tips

| Problem | Solution |
|:---|:---|
| SASLprep / ASCII control error | Clean `bind_user` and `bind_password` with `.strip()` |
| Vault decryption issues | Ensure Vault password matches encryption password |
| Plugin not found | Ensure `ANSIBLE_INVENTORY_PLUGINS` is set correctly |
| No servers returned | Check `base_dns` values and permissions |

---

## 🛠 Future Enhancements

- Group servers by AD attributes
- Support pagination for large AD environments
- Schedule automatic inventory refreshes

---

## 📋 Example Output

```json
{
  "_meta": {
    "hostvars": {
      "server1": {
        "ansible_host": "server1.domain.com"
      },
      "server2": {
        "ansible_host": "server2.domain.com"
      }
    }
  },
  "servers": {
    "hosts": [
      "server1",
      "server2"
    ]
  }
}
```

---

# ✨ Ready to automate Active Directory inventories in production!
