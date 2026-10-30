"""
Hiring-cluster signal from the Adzuna job search API (free key:
developer.adzuna.com). A cluster is several operator-type postings from one
employer in one city; a cluster at a new address is the earliest public sign
an operator is adding capacity.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.adzuna.com/v1/api/jobs/us/search/{page}"

# Words in a posting that point at a new or expanding site, not a backfill.
EXPANSION_WORDS = ["new facility", "new distribution center", "new dc", "new warehouse",
                   "new location", "new site", "grand opening", "start-up", "startup",
                   "now opening", "opening soon", "launch team", "expansion", "expanding",
                   "2nd shift", "second shift", "3rd shift", "third shift", "weekend shift"]

# Staffing firms post on behalf of a hidden employer: still a signal, but the
# operator has to be identified before it's actionable.
STAFFING = ["staffmark", "aerotek", "adecco", "peopleready", "people ready", "manpower",
            "express employment", "randstad", "kelly services", "spherion", "prologistix",
            "labor finders", "elwood", "surge staffing", "belflex", "hirequest", "select staffing",
            "employbridge", "advance partners", "staffing", "workforce", "temps", "personnel",
            "recruiting", "talent", "tradesmen international", "integrity trade services"]

# Store-floor roles at national retailers read like warehouse jobs but say
# nothing about industrial space.
RETAIL = ["walmart", "target", "home depot", "lowe's", "lowes", "costco", "sam's club",
          "kroger", "harris teeter", "food lion", "publix", "aldi", "dollar general",
          "dollar tree", "family dollar", "tractor supply", "best buy", "kohl's", "ross",
          "marshalls", "tj maxx", "burlington", "autozone", "o'reilly", "advance auto"]


def _get(params, page, tries=3):
    url = API.format(page=page) + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "brink-signals/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # rate limits and transient 5xx: back off and retry
            if i == tries - 1:
                raise
            print(f"  adzuna retry after {e}", file=sys.stderr)
            time.sleep(5 * (i + 1))


def fetch_postings(counties, terms, days=7, pages=3, app_id=None, app_key=None):
    """Postings from the last `days` for every term in every county, keyed by
    Adzuna job id so the same posting found by two terms counts once."""
    app_id = app_id or os.environ.get("ADZUNA_APP_ID")
    app_key = app_key or os.environ.get("ADZUNA_APP_KEY")
    if not (app_id and app_key):
        raise RuntimeError("ADZUNA_APP_ID / ADZUNA_APP_KEY not set")
    seen = {}
    for county, cfg in counties.items():
        for term in terms:
            for page in range(1, pages + 1):
                data = _get({"app_id": app_id, "app_key": app_key, "what": term,
                             "where": cfg["jobs_where"], "distance": 25, "max_days_old": days,
                             "results_per_page": 50, "sort_by": "date",
                             "content-type": "application/json"}, page)
                results = data.get("results", [])
                for j in results:
                    j["_county"] = in_market(j, counties) or county
                    j["_term"] = term
                    seen.setdefault(str(j.get("id")), j)
                if len(results) < 50:
                    break
                time.sleep(0.5)
    return list(seen.values())


def in_market(job, counties):
    """County name if the posting's location falls inside the market."""
    loc = job.get("location") or {}
    text = " ".join(loc.get("area") or []) + " " + (loc.get("display_name") or "")
    for county in counties:
        if re.search(rf"\b{county}\b", text, re.I):
            return county
    return None


def _company(job):
    return ((job.get("company") or {}).get("display_name") or "Unknown").strip()


def _city(job):
    area = (job.get("location") or {}).get("area") or []
    if len(area) >= 4:
        return area[-1]
    return ((job.get("location") or {}).get("display_name") or "").split(",")[0].strip()


def _key(s):
    s = re.sub(r"\b(inc|llc|l\.l\.c|corp|corporation|co|company|ltd|lp|usa|us)\b\.?", "", s.lower())
    return re.sub(r"[^a-z0-9]", "", s)


def clusters(postings, min_size):
    """Group postings by employer + city and keep groups of `min_size`+."""
    groups = {}
    for j in postings:
        # Adzuna doesn't always name the county; the search radius around the
        # county seat (stored in _county) is the fallback.
        company = _company(j)
        k = f"{_key(company)}|{_city(j).lower()}"
        g = groups.setdefault(k, {"key": k, "company": company, "city": _city(j),
                                  "county": j["_county"], "postings": [], "titles": set(),
                                  "flags": set()})
        g["postings"].append(j)
        g["titles"].add(re.sub(r"\s+", " ", j.get("title", "")).strip())
        text = (j.get("title", "") + " " + j.get("description", "")).lower()
        g["flags"].update(w for w in EXPANSION_WORDS if w in text)

    out = []
    for g in groups.values():
        n = len(g["postings"])
        if n < min_size:
            continue
        name = g["company"].lower()
        g["count"] = n
        g["staffing"] = any(w in name for w in STAFFING)
        g["retail"] = any(re.search(rf"\b{re.escape(w)}\b", name) for w in RETAIL)
        g["latest"] = max((p.get("created") or "")[:10] for p in g["postings"])
        g["link"] = max(g["postings"], key=lambda p: p.get("created") or "").get("redirect_url")
        # Rank: size, plus expansion language, minus noise sources.
        g["score"] = n + 3 * bool(g["flags"]) - 4 * g["retail"] - 2 * g["staffing"]
        g["titles"] = sorted(g["titles"])[:6]
        g["flags"] = sorted(g["flags"])
        del g["postings"]
        out.append(g)
    out.sort(key=lambda g: g["score"], reverse=True)
    return out
