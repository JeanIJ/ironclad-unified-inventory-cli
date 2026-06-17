import requests
import os
import json
from typing import Any
from inventory_source import NetboxInventorySource, QualysInventorySource, CrowdstrikeInventorySource
from inventory_manager import InventoryManager
from asset import Asset
import argparse

NETBOX_API_URL = "https://my.api.mockaroo.com/ironclad/netbox/inventory.json"
QUALYS_API_URL = "https://my.api.mockaroo.com/ironclad/qualys/inventory.json"
CROWDSTRIKE_API_URL = "https://my.api.mockaroo.com/ironclad/crowdstrike/inventory.json"

def build_manager() -> InventoryManager:
    sources = {
        "netbox": NetboxInventorySource(NETBOX_API_URL),
        "qualys": QualysInventorySource(QUALYS_API_URL),
        "crowdstrike": CrowdstrikeInventorySource(CROWDSTRIKE_API_URL),
    }
    return InventoryManager(sources)

def print_assets(assets: list[Asset], format_type: str) -> None:
    if format_type == "json":
        output = [a.to_dict() for a in assets]
        print(json.dumps(output, indent=2))
    else:
        for a in assets:
            print(a.summary())

def cmd_pull(args) -> None:
    mgr = build_manager()
    mgr.pull(args.source)
    s = mgr.stats()
    print("Pulled inventory.")
    print("Stats:", s)

def cmd_list(args) -> None:
    mgr = build_manager()
    mgr.pull(args.source)
    assets = mgr.list_assets(
        args.source,
        os_filter=args.os,
        environment_filter=args.environment,
        owner_filter=args.owner,
    )
    print_assets(assets, args.format)

def cmd_search(args) -> None:
    mgr = build_manager()
    mgr.pull(args.source)
    results = mgr.search(args.query, args.source)
    print(f"Results: {len(results)}")
    print_assets(results[: args.limit], args.format)

def cmd_find_ip(args) -> None:
    mgr = build_manager()
    mgr.pull(args.source)
    results = mgr.find_by_ip(args.ip)
    print(f"Results: {len(results)}")
    print_assets(results, args.format)

def cmd_stats(args) -> None:
    mgr = build_manager()
    mgr.pull(args.source)
    print("Stats:", mgr.stats())

def main():
    p = argparse.ArgumentParser(prog="ironclad-inventory", description="Ironclad Unified Inventory CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_pull = sub.add_parser("pull", help="Pull inventory from a source")
    p_pull.add_argument("--source", choices=["netbox", "qualys", "crowdstrike", "all"], default="all")
    p_pull.set_defaults(func=cmd_pull)

    p_list = sub.add_parser("list", help="List assets")
    p_list.add_argument("--source", choices=["netbox", "qualys", "crowdstrike", "all"], default="all")
    p_list.add_argument("--os", default=None, help="Filter by OS (case-insensitive partial match)")
    p_list.add_argument("--environment", default=None, help="Filter by environment (case-insensitive partial match)")
    p_list.add_argument("--owner", default=None, help="Filter by owner (case-insensitive partial match)")
    p_list.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    p_list.set_defaults(func=cmd_list)

    p_search = sub.add_parser("search", help="Search assets by keyword")
    p_search.add_argument("--source", choices=["netbox", "qualys", "crowdstrike", "all"], default="all")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--limit", type=int, default=50)
    p_search.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    p_search.set_defaults(func=cmd_search)

    p_find_ip = sub.add_parser("find-ip", help="Find asset by exact IP address")
    p_find_ip.add_argument("--source", choices=["netbox", "qualys", "crowdstrike", "all"], default="all")
    p_find_ip.add_argument("--ip", required=True, help="IP address to search for")
    p_find_ip.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    p_find_ip.set_defaults(func=cmd_find_ip)

    p_stats = sub.add_parser("stats", help="Show counts by source")
    p_stats.add_argument("--source", choices=["netbox", "qualys", "crowdstrike", "all"], default="all")
    p_stats.set_defaults(func=cmd_stats)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()