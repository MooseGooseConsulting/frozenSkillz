#!/usr/bin/env python3
"""Intent-ranked open-web Discover API client.

Discover finds/ranks web sources. It does not query ChatGPT/Perplexity/Grok.
Requires BRIGHTDATA_API_KEY and scripts/common.py.
"""
from __future__ import annotations
import argparse,time
from common import print_json,request


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--intent")
    p.add_argument("--num-results",type=int,default=10)
    p.add_argument("--mode","--depth",dest="mode",choices=["standard","zeroRanking","deep","fast"],default="standard")
    p.add_argument("--format",choices=["json","md"],default="json")
    p.add_argument("--include-content",action="store_true")
    p.add_argument("--include-images",action="store_true")
    p.add_argument("--country",default="US")
    p.add_argument("--city")
    p.add_argument("--language",default="en")
    p.add_argument("--start-date")
    p.add_argument("--end-date")
    p.add_argument("--filter-keyword",action="append",default=[])
    p.add_argument("--keep-duplicates",action="store_true")
    p.add_argument("--sync",action="store_true")
    p.add_argument("--timeout",type=int,default=600)
    a=p.parse_args()
    if not 1 <= a.num_results <= 20:
        p.error("--num-results must be between 1 and 20")
    if a.mode=="zeroRanking" and a.include_content:
        p.error("--include-content is not supported with --mode zeroRanking")
    body={"query":a.query,"intent":a.intent,"mode":a.mode,"format":a.format,"num_results":a.num_results,"remove_duplicates":not a.keep_duplicates,"include_content":a.include_content,"include_images":a.include_images,"country":a.country,"city":a.city,"language":a.language,"start_date":a.start_date,"end_date":a.end_date,"filter_keywords":a.filter_keyword or None}
    if a.mode=="zeroRanking": body.pop("num_results",None)
    body={k:v for k,v in body.items() if v is not None}
    if a.sync:
        status,_,data=request("POST","/discover/sync",body=body,timeout=60)
        print_json({"status":status,"data":data}); return 0 if status==200 else 1
    status,_,job=request("POST","/discover",body=body,timeout=120)
    if status!=200 or not isinstance(job,dict) or "task_id" not in job:
        print_json({"status":status,"data":job}); return 1
    task_id=job["task_id"]; deadline=time.time()+a.timeout
    while time.time()<deadline:
        s,_,data=request("GET","/discover",params={"task_id":task_id},timeout=60)
        if s==200 and isinstance(data,dict) and data.get("status") in {"done","failed"}:
            print_json({"task_id":task_id,"status":s,"data":data}); return 0 if data.get("status")=="done" else 1
        if s not in (200,202): print_json({"task_id":task_id,"status":s,"data":data}); return 1
        time.sleep(3)
    print_json({"task_id":task_id,"status":408,"error":"timeout"}); return 1

if __name__=="__main__": raise SystemExit(main())
