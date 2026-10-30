"""
Hiring-cluster signal. A cluster is several operator-type postings from one
employer in one city; a cluster at a new address is the earliest public sign
an operator is adding capacity.

Two providers, picked by which key is set:
  SERPAPI_API_KEY   Google Jobs via SerpApi — free plan, 250 searches/month
                    (Google Jobs aggregates Indeed, LinkedIn, ZipRecruiter and
                    company career sites)
  ADZUNA_APP_ID/KEY Adzuna — 25 test calls, then paid
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.adzuna.com/v1/api/jobs/us/search/{page}"
SERPAPI = "https://serpapi.com/search.json"

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


def _get(params, page=None, tries=3, base=None):
    url = (base or API.format(page=page)) + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "brink-signals/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # rate limits and transient 5xx: back off and retry
            if i == tries - 1:
                raise
            print(f"  job search retry after {e}", file=sys.stderr)
            time.sleep(5 * (i + 1))


def fetch_postings(counties, words, title_rx, days=7, pages=4, app_id=None, app_key=None):
    """Postings from the last `days` matching any of `words`, one combined
    search per county (Adzuna bills per call, so ~7-28 calls a run). Titles
    are then filtered to operator-type roles with `title_rx`."""
    app_id = app_id or os.environ.get("ADZUNA_APP_ID")
    app_key = app_key or os.environ.get("ADZUNA_APP_KEY")
    if not (app_id and app_key):
        raise RuntimeError("ADZUNA_APP_ID / ADZUNA_APP_KEY not set")
    keep = re.compile(title_rx, re.I)
    seen, calls = {}, 0
    for county, cfg in counties.items():
        for page in range(1, pages + 1):
            data = _get({"app_id": app_id, "app_key": app_key, "what_or": " ".join(words),
                         "where": cfg["jobs_where"], "distance": 25, "max_days_old": days,
                         "results_per_page": 50, "sort_by": "date",
                         "content-type": "application/json"}, page)
            calls += 1
            results = data.get("results", [])
            for j in results:
                if not keep.search(j.get("title", "")):
                    continue
                j["_county"] = in_market(j, counties) or county
                seen.setdefault(str(j.get("id")), j)
            if len(results) < 50:
                break
            time.sleep(0.5)
    print(f"  adzuna: {calls} calls", file=sys.stderr)
    return list(seen.values())


def provider():
    if os.environ.get("SERPAPI_API_KEY"):
        return "serpapi"
    if os.environ.get("ADZUNA_APP_ID") and os.environ.get("ADZUNA_APP_KEY"):
        return "adzuna"
    return None


def _days_ago(text):
    """'3 days ago' / '1 week ago' / '20 hours ago' -> days; None if unknown."""
    m = re.search(r"(\d+)\+?\s*(hour|day|week|month)", text or "", re.I)
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2).lower()
    return {"hour": 0, "day": n, "week": 7 * n, "month": 30 * n}[unit]


def fetch_postings_serpapi(counties, queries, title_rx, days=7, pages=2, api_key=None):
    """Google Jobs results for each query in each county. One call per page,
    10 jobs per page: 7 counties x 2 queries x 2 pages = 28 calls/week,
    ~120/month, inside SerpApi's 250 free searches."""
    api_key = api_key or os.environ.get("SERPAPI_API_KEY")
    keep = re.compile(title_rx, re.I)
    today = time.strftime("%Y-%m-%d")
    seen, calls = {}, 0
    for county, cfg in counties.items():
        loc = cfg["serpapi_location"]
        for q in queries:
            token = None
            for _ in range(pages):
                params = {"engine": "google_jobs", "q": q, "location": loc, "hl": "en",
                          "gl": "us", "api_key": api_key}
                if token:
                    params["next_page_token"] = token
                data = _get(params, base=SERPAPI)
                calls += 1
                if data.get("error"):
                    # "hasn't returned any results" is a normal empty page
                    if "any results" not in data["error"]:
                        raise RuntimeError(f"SerpApi: {data['error']}")
                    break
                for r in data.get("jobs_results", []):
                    ext = r.get("detected_extensions") or {}
                    age = _days_ago(ext.get("posted_at"))
                    if age is not None and age > days:
                        continue
                    if not keep.search(r.get("title", "")):
                        continue
                    link = r.get("share_link") or next(
                        (o.get("link") for o in r.get("apply_options") or []), None)
                    job = {"id": r.get("job_id") or f"{r.get('company_name')}|{r.get('title')}|{r.get('location')}",
                           "title": r.get("title", ""), "description": r.get("description", ""),
                           "created": today if age is None else time.strftime(
                               "%Y-%m-%d", time.localtime(time.time() - age * 86400)),
                           "redirect_url": link, "company": {"display_name": r.get("company_name")},
                           "location": {"display_name": r.get("location", ""), "area": []},
                           "via": r.get("via")}
                    job["_county"] = in_market(job, counties) or county
                    seen.setdefault(str(job["id"]), job)
                token = (data.get("serpapi_pagination") or {}).get("next_page_token")
                if not token:
                    break
    print(f"  serpapi: {calls} searches", file=sys.stderr)
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
    # Google Jobs writes multi-site postings as "Charlotte, NC (+2 others)".
    name = (job.get("location") or {}).get("display_name") or ""
    return re.sub(r"\s*\(.*\)", "", name).split(",")[0].strip()


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
