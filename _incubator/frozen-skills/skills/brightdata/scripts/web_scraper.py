#!/usr/bin/env python3
"""Bounded Web Scraper API client for URL collection and discovery.

Safety defaults:
- Discovery is async/manual only.
- Discovery requires both per-input and total result limits.
- No automatic reruns.
- Raw output can be written to --output.
Requires BRIGHTDATA_API_KEY and scripts/common.py.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from common import print_json,request

ACTIVE={"starting","building","running","processing","scheduled"}

def parse_json_or_file(value:str):
    p=Path(value)
    return json.loads(p.read_text()) if p.exists() else json.loads(value)

def write_or_print(payload,output):
    if output: Path(output).write_text(json.dumps(payload,indent=2,ensure_ascii=False,default=str))
    else: print_json(payload)

def main()->int:
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd",required=True)
    inv=sub.add_parser("inventory"); inv.add_argument("--match")
    for cmd in ("scrape","trigger","discover"):
        q=sub.add_parser(cmd); q.add_argument("dataset_id"); q.add_argument("--input",required=True); q.add_argument("--format",default="json",choices=["json","ndjson","jsonl","csv"]); q.add_argument("--custom-output-fields"); q.add_argument("--include-errors",action="store_true"); q.add_argument("--output"); q.add_argument("--wait",action="store_true"); q.add_argument("--timeout",type=int,default=900)
        if cmd=="discover":
            q.add_argument("--discover-by",required=True); q.add_argument("--limit-per-input",required=True,type=int); q.add_argument("--limit-total",required=True,type=int)
    st=sub.add_parser("status"); st.add_argument("snapshot_id"); st.add_argument("--format",default="json"); st.add_argument("--output")
    ca=sub.add_parser("cancel"); ca.add_argument("snapshot_id")
    a=p.parse_args()
    if a.cmd=="inventory":
        s,_,data=request("GET","/datasets/v3/scrapers",timeout=120)
        if a.match and isinstance(data,list):
            import re; rx=re.compile(a.match,re.I); data=[r for r in data if rx.search(json.dumps(r,default=str))]
        print_json({"status":s,"scrapers":data}); return 0 if s==200 else 1
    if a.cmd=="cancel":
        s,_,data=request("POST",f"/datasets/v3/snapshot/{a.snapshot_id}/cancel",timeout=60); print_json({"status":s,"data":data}); return 0 if s==200 else 1
    if a.cmd=="status":
        s,_,data=request("GET",f"/datasets/v3/snapshot/{a.snapshot_id}",params={"format":a.format},timeout=120); write_or_print({"status":s,"snapshot_id":a.snapshot_id,"data":data},a.output); return 0 if s==200 else 1
    inputs=parse_json_or_file(a.input)
    if isinstance(inputs,dict): inputs=[inputs]
    if not isinstance(inputs,list) or not all(isinstance(x,dict) for x in inputs): raise SystemExit("--input must be a JSON object/array or JSON file")
    path="/datasets/v3/scrape" if a.cmd=="scrape" else "/datasets/v3/trigger"
    params={"dataset_id":a.dataset_id,"format":a.format,"custom_output_fields":a.custom_output_fields,"include_errors":str(a.include_errors).lower()}
    if a.cmd=="discover":
        path="/datasets/v3/trigger"; params.update({"type":"discover_new","discover_by":a.discover_by,"limit_per_input":a.limit_per_input,"limit_multiple_results":a.limit_total})
    s,_,data=request("POST",path,params=params,body=inputs,timeout=120)
    if s not in (200,202): write_or_print({"status":s,"data":data},a.output); return 1
    if isinstance(data,list): write_or_print({"status":s,"data":data},a.output); return 0
    snapshot=data.get("snapshot_id") if isinstance(data,dict) else None
    if not snapshot: write_or_print({"status":s,"data":data},a.output); return 0
    if not a.wait: write_or_print({"status":s,"snapshot_id":snapshot,"data":data},a.output); return 0
    deadline=time.time()+a.timeout
    while time.time()<deadline:
        fs,_,result=request("GET",f"/datasets/v3/snapshot/{snapshot}",params={"format":a.format},timeout=120)
        if fs==200 and (isinstance(result,list) or not (isinstance(result,dict) and result.get("status") in ACTIVE)):
            write_or_print({"status":fs,"snapshot_id":snapshot,"data":result},a.output); return 0
        if fs not in (200,202): write_or_print({"status":fs,"snapshot_id":snapshot,"data":result},a.output); return 1
        time.sleep(5)
    write_or_print({"status":408,"snapshot_id":snapshot,"error":"timeout"},a.output); return 1

if __name__=="__main__": raise SystemExit(main())
