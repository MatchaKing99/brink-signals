#!/usr/bin/env python3
"""
Survey a county's ArcGIS server for anything that looks like permits or
development activity: lists matching services, their layers, fields, record
counts and the newest few records. Run from GitHub Actions (Actions → Probe
county GIS) since many county servers block other networks.

  python3 tools/probe.py <server-root-or-service-url> [...]
  python3 tools/probe.py --search "AWNING,SKATE" <layer-or-service-url> [...]

--search lists every record whose text fields contain any of the terms.
"""
import json
import re
import sys
import urllib.parse
import urllib.request

INTEREST = re.compile(r"permit|plan|develop|energov|zon|site|subdiv|case|project|build|inspect|parcel|tax|land", re.I)
# Code-like fields worth listing every distinct value of (zoning, land use).
CODES = re.compile(r"^(zone|zoning|zonecode|zone_class|landuse|land_use|luc|use_?code|usecode|class|admin)$", re.I)
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
    for f in fields:
        if CODES.match(f["name"]) and f.get("type") == "esriFieldTypeString":
            try:
                rows = get(url + "/query", where="1=1", outFields=f["name"], returnDistinctValues="true",
                           returnGeometry="false").get("features", [])
                vals = sorted({str(r["attributes"].get(f["name"])) for r in rows})
                print(f"    distinct {f['name']} ({len(vals)}): {', '.join(vals[:120])}")
            except Exception as e:
                print(f"    distinct {f['name']} failed: {e}")
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


def search_layer(url, terms):
    try:
        fields = [f["name"] for f in get(url).get("fields") or [] if f.get("type") == "esriFieldTypeString"]
    except Exception as e:
        print(f"    !! {e}")
        return
    if not fields:
        return
    where = " OR ".join(f"UPPER({f}) LIKE '%{t.upper()}%'" for f in fields for t in terms)
    try:
        feats = get(url + "/query", where=where, outFields="*", returnGeometry="false",
                    resultRecordCount=50).get("features", [])
    except Exception as e:
        print(f"    search failed: {e}")
        return
    print(f"    matches: {len(feats)}")
    for feat in feats:
        print("    hit: " + json.dumps(feat.get("attributes"), default=str)[:900])


def probe(target, terms=None):
    print(f"\n######## {target}")
    if re.search(r"/(MapServer|FeatureServer)(/\d+)?/?$", target):
        targets = [(target, None)]
    else:
        targets = [(u, t) for u, t in services(target) if INTEREST.search(u)]
        print(f"matching services: {len(targets)}")
    for svc, _ in targets:
        if re.search(r"/\d+/?$", svc):
            print(f"\n== layer {svc}")
            search_layer(svc, terms) if terms else show_layer(svc)
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
            if terms:
                search_layer(f"{svc}/{l['id']}", terms)
            else:
                show_layer(f"{svc}/{l['id']}")


if __name__ == "__main__":
    args, terms = sys.argv[1:], None
    if args[:1] == ["--search"]:
        terms = [t.strip() for t in args[1].split(",") if t.strip()]
        args = args[2:]
    for t in args:
        try:
            probe(t, terms)
        except Exception as e:
            print(f"!! {t}: {e}")
