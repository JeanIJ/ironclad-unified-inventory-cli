# Ironclad Unified Inventory CLI

## Overview

This tool unifies asset inventory across three security systems at Ironclad
Analytics:

* **NetBox** — network/infrastructure perspective
* **Qualys** — vulnerability/asset risk perspective
* **CrowdStrike** — endpoint/EDR perspective
  Each acquisition brought its own asset-tracking system with different schemas. This
  CLI acts as a translation layer, normalizing all records into a single internal
  `Asset` model and enabling analysts to pull, list, search, and summarize inventory
  without switching platforms.

---

## Project Structure

```text
soc-assignment-9/
├── main.py # CLI entry point (argparse)
├── asset.py # Universal Asset model
├── inventory_source.py # Base class + 3 source adapters
├── inventory_manager.py # Orchestrates pull/list/search/stats
└── README.md # This file
```

---

## Setup

### 1. Create virtual environment and install dependencies

```bash
cd ~/Documents/CodeYou_Projects/soc-assignment-9
python3 -m venv venv
source venv/bin/activate
pip install requests
```

### 2. Set API key

```bash
export IRONCLAD_API_KEY=cf7bbbd0
```

---

## How to Run Each CLI Command

### Pull inventory from one or all sources

```bash
python main.py pull --source all
python main.py pull --source netbox
python main.py pull --source qualys
python main.py pull --source crowdstrike
```

### List assets (with optional filters)

```bash
python main.py list --source all
python main.py list --source netbox
python main.py list --source netbox --os Windows
python main.py list --source all --environment prod --owner HR
```

### Search assets by keyword across all fields

```bash
python main.py search --query windows --source all
python main.py search --query "Windows 11" --source all
python main.py search --query "Windows 11" --source all --limit 500
```

### Find asset by exact IP address

```bash
python main.py find-ip --ip 147.149.196.21
python main.py find-ip --ip 147.149.196.21 --source all
```

### Show inventory statistics

```bash
python main.py stats --source all
python main.py stats --source netbox
```

### Output formats

Add `--format json` to list, search, or find-ip for JSON output:

```bash
python main.py list --source netbox --format json
python main.py search --query windows --source all --format json
python main.py find-ip --ip 147.149.196.21 --format json
```

---

## Schema Field Mapping Notes

### NetBox → Asset

| NetBox Field    | Asset Field       | Rationale                            |
| :-------------- | :---------------- | :----------------------------------- |
| `id`          | `asset_id`      | Unique device identifier in NetBox   |
| `device_name` | `hostname`      | Canonical name of the device         |
| `primary_ip`  | `ip_address`    | Primary IP assigned to the device    |
| `platform`    | `os`            | Operating system or network platform |
| `environment` | `environment`   | Dev/staging/prod context             |
| `tenant`      | `owner_context` | Organizational owner or team         |

### Qualys → Asset

| Qualys Field         | Asset Field       | Rationale                               |
| :------------------- | :---------------- | :-------------------------------------- |
| `asset_id`         | `asset_id`      | UUID assigned by Qualys scanner         |
| `hostname`         | `hostname`      | DNS or reported hostname                |
| `ip_address`       | `ip_address`    | IP detected during scan                 |
| `operating_system` | `os`            | OS fingerprint from scan                |
| `asset_group`      | `environment`   | Logical grouping maps to environment    |
| *(none)*           | `owner_context` | Qualys schema has no direct owner field |

### CrowdStrike → Asset

| CrowdStrike Field  | Asset Field       | Rationale                                  |
| :----------------- | :---------------- | :----------------------------------------- |
| `sensor_id`      | `asset_id`      | EDR sensor UUID                            |
| `hostname`       | `hostname`      | Endpoint hostname                          |
| `local_ip`       | `ip_address`    | Local network IP (chosen over external_ip) |
| `os_version`     | `os`            | OS version reported by sensor              |
| *(none)*         | `environment`   | CrowdStrike schema has no direct env field |
| `logged_in_user` | `owner_context` | Current user as proxy for ownership        |

---

## Completed Challenges

### Challenge B — Filters on list

Added optional flags to the `list` command:

* `--os` — Filter by operating system (case-insensitive partial match)
* `--environment` — Filter by environment (case-insensitive partial match)
* `--owner` — Filter by owner context (case-insensitive partial match)
  **Example:**

```bash
python main.py list --source all --os Windows --environment prod
```

### Challenge C — Output Formats

Added `--format` flag supporting:

* `--format table` (default) — Human-readable text output
* `--format json` — Machine-readable JSON for integration with SIEMs or scripts
  **Example:**

```bash
python main.py search --query windows --source all --format json
```

### Challenge D — Find by IP

Added `find-ip` command with exact IP address matching across all sources.
**Example:**

```bash
python main.py find-ip --ip 147.149.196.21 --format json
```

---

## Terminal Output

### Pull all sources

```bash
$ python main.py pull --source all
Pulled inventory.
Stats: {'total': 1343, 'netbox': 408, 'qualys': 384, 'crowdstrike': 551}
```

### List one source with filters

```bash
$ python main.py list --source netbox --os Windows --format table
[netbox] web-752 ip=147.149.196.21 os=Windows env=dev owner=HR
[netbox] fw-782 ip=108.34.31.144 os=Windows env=dev owner=Engineering
[netbox] switch-517 ip=51.160.209.219 os=Windows env=prod owner=Finance
...
```

### Search across all sources

```bash
$ python main.py search --query windows --source all --limit 10
Results: 572
[netbox] web-752 ip=147.149.196.21 os=Windows env=dev owner=HR
[netbox] fw-782 ip=108.34.31.144 os=Windows env=dev owner=Engineering
[netbox] switch-517 ip=51.160.209.219 os=Windows env=prod owner=Finance
...
```

### Stats

```bash
$ python main.py stats --source all
Stats: {'total': 1343, 'netbox': 408, 'qualys': 384, 'crowdstrike': 551}
```

### Challenge demo — Find by IP (JSON)

```json
$ python main.py find-ip --ip 147.149.196.21 --format json
Results: 1
[
{
"asset_id": "1",
"hostname": "web-752",
"ip_address": "147.149.196.21",
"os": "Windows",
"environment": "dev",
"owner_context": "HR",
"source": "netbox"
}
]
```
