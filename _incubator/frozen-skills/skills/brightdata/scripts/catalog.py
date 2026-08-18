#!/usr/bin/env python3
"""Live Bright Data catalog inventory.

Never use a stale platform list when a live catalog is available.
Requires BRIGHTDATA_API_KEY and scripts/common.py.
"""
from __future__ import annotations
import argparse, json, re
from common import print_json, request


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["zones","scrapers","collectors"])
    p.add_argument("--match")
    a=p.parse_args()
    routes={"zones":"/zone/get_all_zones","scrapers":"/datasets/v3/scrapers","collectors":"/dca/collectors_list"}
    status,_,data=request("GET",routes[a.mode],timeout=120)
    if a.match and isinstance(data,list):
        expr=re.compile(a.match,re.I)
        data=[row for row in data if expr.search(json.dumps(row,default=str))]
    print_json({"status":status,a.mode:data})
    return 0 if status==200 else 1

if __name__=="__main__": raise SystemExit(main())
