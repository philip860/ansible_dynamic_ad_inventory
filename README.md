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
