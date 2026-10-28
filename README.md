# Ironclad Unified Inventory CLI

**CodeYou SecOps Assignment 9** — a command-line inventory that pulls assets from NetBox, Qualys, and CrowdStrike into one list.

## Description

Ironclad Analytics tracks assets in three systems. Their fields do not match:

- **NetBox** — network and infrastructure devices
- **Qualys** — vulnerability-scanner asset records
- **CrowdStrike** — endpoint and EDR sensor records

Each adapter maps its records to one `Asset` model. You can pull, list, filter, search, and summarize inventory from one place.

## Tech

| Piece | Detail |
| --- | --- |
| Language | Python 3.10+ (`list[...]` and `str \| None` type hints) |
| CLI | `argparse` (standard library) |
| HTTP | `requests` |
| Auth | `IRONCLAD_API_KEY` environment variable, sent as the `X-API-Key` header |
| Sources | Mockaroo JSON endpoints for NetBox, Qualys, and CrowdStrike |

Modules:

- `main.py` — CLI entry point
- `asset.py` — shared `Asset` model
- `inventory_source.py` — base client and the three source adapters
- `inventory_manager.py` — pull, list, search, find-by-IP, and stats

## Setup

Python 3.10 or newer is required. Commands that fetch inventory need network access to the Mockaroo endpoints.

```bash
git clone https://github.com/JeanIJ/ironclad-unified-inventory-cli.git
cd ironclad-unified-inventory-cli
python3 -m venv venv
source venv/bin/activate
pip install requests
```

Set the API key in the environment before running a command. Use your own key. Do not commit a real key.

```bash
export IRONCLAD_API_KEY=your_key_here
```

## Usage

Run these commands from the repository root with the virtual environment activated. `--source` accepts `netbox`, `qualys`, `crowdstrike`, or `all` (the default).

### Pull

Download inventory and print counts.

```bash
python main.py pull --source all
python main.py pull --source netbox
python main.py pull --source qualys
python main.py pull --source crowdstrike
```

### List

Print assets. Optional filters are case-insensitive partial matches.

```bash
python main.py list --source all
python main.py list --source netbox --os Windows
python main.py list --source all --environment prod --owner HR
```

| Flag | Effect |
| --- | --- |
| `--os` | Operating system contains this text |
| `--environment` | Environment contains this text |
| `--owner` | Owner context contains this text |

### Search

Match a keyword against asset id, hostname, IP, OS, environment, owner, and source.

```bash
python main.py search --query windows --source all
python main.py search --query "Windows 11" --source all --limit 500
```

`--limit` defaults to 50. The `Results:` line is the full match count. Only the first `--limit` rows are printed.

### Find by IP

Exact match on `ip_address` for the sources you pass with `--source`.

```bash
python main.py find-ip --ip 147.149.196.21
python main.py find-ip --ip 147.149.196.21 --source all
```

### Stats

```bash
python main.py stats --source all
python main.py stats --source netbox
```

### Output format

`list`, `search`, and `find-ip` accept `--format table` (default) or `--format json`.

```bash
python main.py list --source netbox --format json
python main.py search --query windows --source all --format json
python main.py find-ip --ip 147.149.196.21 --format json
```

A table row looks like this:

```text
[netbox] web-752 ip=147.149.196.21 os=Windows env=dev owner=HR
```

## Status

This CLI can:

- Pull from one source or all three, then print per-source counts
- List filters: `--os`, `--environment`, and `--owner`
- Keyword search with `--limit`
- Table and JSON output
- Find by exact IP

Inventory comes from the course Mockaroo endpoints. It does not connect to production NetBox, Qualys, or CrowdStrike. Qualys records have no owner field, and CrowdStrike records have no environment field, so those `Asset` values stay empty for those sources.

## Project structure

```text
ironclad-unified-inventory-cli/
├── main.py                 # CLI entry point (argparse)
├── asset.py                # shared Asset model
├── inventory_source.py     # Base class and three source adapters
├── inventory_manager.py    # Pull, list, search, find-by-IP, and stats
└── README.md
```

## Schema field mapping

### NetBox → Asset

| NetBox field | Asset field | Notes |
| --- | --- | --- |
| `id` | `asset_id` | Device identifier |
| `device_name` | `hostname` | Device name |
| `primary_ip` | `ip_address` | Primary IP |
| `platform` | `os` | OS or network platform |
| `environment` | `environment` | Dev, staging, or prod |
| `tenant` | `owner_context` | Owning team or tenant |

### Qualys → Asset

| Qualys field | Asset field | Notes |
| --- | --- | --- |
| `asset_id` | `asset_id` | Scanner asset id |
| `hostname` | `hostname` | Reported hostname |
| `ip_address` | `ip_address` | IP seen in the scan |
| `operating_system` | `os` | OS fingerprint |
| `asset_group` | `environment` | Asset group used as environment |
| *(none)* | `owner_context` | No owner field in the Qualys payload |

### CrowdStrike → Asset

| CrowdStrike field | Asset field | Notes |
| --- | --- | --- |
| `sensor_id` | `asset_id` | EDR sensor id |
| `hostname` | `hostname` | Endpoint hostname |
| `local_ip` | `ip_address` | Local IP, not the external IP |
| `os_version` | `os` | OS version reported by the sensor |
| *(none)* | `environment` | No environment field in the payload |
| `logged_in_user` | `owner_context` | Signed-in user as the owner proxy |

## Example output

Counts below are from sample runs on the mock inventory. Totals change when that data changes.

Pull:

```text
$ python main.py pull --source all
Pulled inventory.
Stats: {'total': 1343, 'netbox': 408, 'qualys': 384, 'crowdstrike': 551}
```

Filtered list:

```text
$ python main.py list --source netbox --os Windows --format table
[netbox] web-752 ip=147.149.196.21 os=Windows env=dev owner=HR
[netbox] fw-782 ip=108.34.31.144 os=Windows env=dev owner=Engineering
[netbox] switch-517 ip=51.160.209.219 os=Windows env=prod owner=Finance
```

Search:

```text
$ python main.py search --query windows --source all --limit 10
Results: 572
[netbox] web-752 ip=147.149.196.21 os=Windows env=dev owner=HR
[netbox] fw-782 ip=108.34.31.144 os=Windows env=dev owner=Engineering
[netbox] switch-517 ip=51.160.209.219 os=Windows env=prod owner=Finance
```

Stats:

```text
$ python main.py stats --source all
Stats: {'total': 1343, 'netbox': 408, 'qualys': 384, 'crowdstrike': 551}
```

Find by IP (JSON):

```text
$ python main.py find-ip --ip 147.149.196.21 --format json
Results: 1
```

```json
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
