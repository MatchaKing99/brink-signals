#!/usr/bin/env python3
"""
Survey a county's ArcGIS server for anything that looks like permits or
development activity: lists matching services, their layers, fields, record
counts and the newest few records. Run from GitHub Actions (Actions → Probe
county GIS) since many county servers block other networks.

  python3 tools/probe.py <server-root-or-service-url> [...]
"""
import json
import re
import sys
import urllib.parse
import urllib.request

INTEREST = re.compile(r"permit|plan|develop|energov|zon|site|subdiv|case|project|build|inspect", re.I)
DATE_HINT = re.compile(r"date|issued|created|applied|submitted|approved", re.I)


def get(url, **params):
    params.setdefault("f", "json")
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": "brink-signals-probe/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def services(root, depth=0):
    """Yield (url, type) for every service under a REST root, recursing folders."""
    data = get(root)
    for s in data.get("services", []):
        name = s["name"].split("/")[-1]
        yield f"{root.rstrip('/')}/{name}/{s['type']}", s["type"]
    if depth < 2:
        for folder in data.get("folders", []):
            yield from services(f"{root.rstrip('/')}/{folder}", depth + 1)


def show_layer(url):
    try:
        meta = get(url)
    except Exception as e:
        print(f"    !! {e}")
        return
    fields = meta.get("fields") or []
    print(f"    fields: {', '.join(f['name'] + ('(date)' if f.get('type') == 'esriFieldTypeDate' else '') for f in fields)}")
    try:
        n = get(url + "/query", where="1=1", returnCountOnly="true").get("count")
    except Exception as e:
        n = f"count failed: {e}"
    print(f"    records: {n}")
    dates = [f["name"] for f in fields if f.get("type") == "esriFieldTypeDate"] or \
            [f["name"] for f in fields if DATE_HINT.search(f["name"])]
    params = {"where": "1=1", "outFields": "*", "returnGeometry": "false", "resultRecordCount": 3}
    if dates:
        params["orderByFields"] = f"{dates[0]} DESC"
    try:
        for feat in get(url + "/query", **params).get("features", [])[:3]:
            print("    sample: " + json.dumps(feat.get("attributes"), default=str)[:600])
    except Exception as e:
        print(f"    sample failed: {e}")


def probe(target):
    print(f"\n######## {target}")
    if re.search(r"/(MapServer|FeatureServer)(/\d+)?/?$", target):
        targets = [(target, None)]
    else:
        targets = [(u, t) for u, t in services(target) if INTEREST.search(u)]
        print(f"matching services: {len(targets)}")
    for svc, _ in targets:
        if re.search(r"/\d+/?$", svc):
            print(f"\n== layer {svc}")
            show_layer(svc)
            continue
        try:
            meta = get(svc)
        except Exception as e:
            print(f"\n== {svc}\n  !! {e}")
            continue
        layers = meta.get("layers", []) + meta.get("tables", [])
        print(f"\n== {svc}  ({len(layers)} layers)")
        for l in layers:
            print(f"  [{l['id']}] {l['name']}")
            show_layer(f"{svc}/{l['id']}")


if __name__ == "__main__":
    for t in sys.argv[1:]:
        try:
            probe(t)
        except Exception as e:
            print(f"!! {t}: {e}")
