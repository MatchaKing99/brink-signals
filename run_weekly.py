#!/usr/bin/env python3
"""
Weekly expansion-signal run. Pulls every source in signals/config.py, keeps
only what's new since the last run, and writes:

  output/<date>/permits.csv, planning.csv, jobs.csv   (Airtable-ready)
  output/<date>/digest.md                             (the weekly email)
  output/latest-digest.md

Usage:
  python3 run_weekly.py                 # everything
  python3 run_weekly.py --no-jobs       # skip the job-board pull (no Adzuna key yet)
  python3 run_weekly.py --all           # list everything, not just new signals
"""
import argparse
import csv
import datetime as dt
import json
import os
import shutil
import sys
import traceback
from pathlib import Path

from signals import config, jobs, permits

ROOT = Path(__file__).parent
STATE = ROOT / "data" / "seen.json"
INBOX = ROOT / "inbox"
TODAY = dt.date.today().isoformat()


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"permits": {}, "planning": {}, "jobs": {}}


def save_state(state):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1, sort_keys=True))


def permit_key(county, rec):
    return f"{county}|{rec.get('permit_no') or ''}|{(rec.get('address') or '').strip()}|{rec.get('desc', '')[:40]}"


def run_arcgis(state, show_all, status):
    found = {"permits": [], "planning": []}
    for src in config.ARCGIS_SOURCES:
        county, kind = src["county"], src["kind"]
        label = f"{county} {kind}"
        try:
            url = src.get("url")
            note = ""
            if "discover" in src:
                hit = permits.discover_layer(src["discover"]["service"], src["discover"]["name"])
                if not hit:
                    status.append((label, "⚪ no matching layer published"))
                    continue
                url, layer_name, year = hit
                if year and year < dt.date.today().year - 1:
                    status.append((label, f"⚪ newest published layer is \"{layer_name}\" — nothing current"))
                    continue
                note = f" (layer: {layer_name})"
            records, _ = permits.pull_arcgis(url, src["days"])
            min_score = config.PERMIT_MIN_SCORE if kind == "permits" else config.PLANNING_MIN_SCORE
            scored = permits.score_records(records, min_score)
            new = []
            for r in scored:
                k = permit_key(county, r)
                if show_all or k not in state[kind]:
                    state[kind].setdefault(k, TODAY)
                    r["county"] = county
                    new.append(r)
            found[kind] += new
            status.append((label, f"🟢 {len(records)} records, {len(scored)} scored, {len(new)} new{note}"))
        except Exception as e:
            traceback.print_exc()
            status.append((label, f"🔴 failed: {str(e)[:120]}"))
    return found


def run_inbox(state, show_all, status):
    """Score permit exports dropped in inbox/ (portal-only counties)."""
    out = []
    files = sorted(INBOX.glob("*.csv"))
    for f in files:
        county = f.stem.split("_")[0].title()
        try:
            scored = permits.score_csv(f, days=120, min_score=config.PERMIT_MIN_SCORE)
            new = 0
            for r in scored:
                k = permit_key(county, r)
                if show_all or k not in state["permits"]:
                    state["permits"].setdefault(k, TODAY)
                    r["county"] = county
                    out.append(r)
                    new += 1
            status.append((f"{county} permits (inbox: {f.name})", f"🟢 {len(scored)} scored, {new} new"))
            done = ROOT / "data" / "inbox-processed"
            done.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), done / f"{TODAY}_{f.name}")
        except Exception as e:
            traceback.print_exc()
            status.append((f"{county} inbox {f.name}", f"🔴 failed: {str(e)[:120]}"))
    return out


def run_jobs(state, show_all, status):
    try:
        if jobs.provider() == "serpapi":
            postings = jobs.fetch_postings_serpapi(config.COUNTIES, config.SERPAPI_QUERIES,
                                                   config.JOB_TITLE_RX)
        else:
            postings = jobs.fetch_postings(config.COUNTIES, config.JOB_WORDS, config.JOB_TITLE_RX)
    except Exception as e:
        traceback.print_exc()
        status.append(("Job postings (all 7 counties)", f"🔴 {str(e)[:120]}"))
        return []
    groups = jobs.clusters(postings, config.JOB_CLUSTER_MIN)
    out = []
    for g in groups:
        prev = state["jobs"].get(g["key"])
        if prev is None:
            g["why"] = "new cluster"
        elif g["count"] - prev["count"] >= config.JOB_GROWTH_FLAG:
            g["why"] = f"grew {prev['count']}→{g['count']}"
        elif show_all:
            g["why"] = "seen before"
        else:
            state["jobs"][g["key"]]["count"] = max(prev["count"], g["count"])
            continue
        state["jobs"][g["key"]] = {"first_seen": (prev or {}).get("first_seen", TODAY),
                                   "count": g["count"]}
        out.append(g)
    status.append(("Job postings (all 7 counties)",
                   f"🟢 {len(postings)} postings, {len(groups)} clusters, {len(out)} new/growing"))
    return out


# ---- output -----------------------------------------------------------------

PERMIT_COLS = ["Permit #", "Issued", "County", "Address", "Type", "Occupancy", "Description",
               "Value", "Sq Ft", "Zoning", "Contractor", "Owner", "Permit Status", "Score",
               "Signals", "Status"]


def write_permits_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(PERMIT_COLS)
        for r in rows:
            w.writerow([r["permit_no"], r["issue_date"], r["county"], (r["address"] or "").strip(),
                        r["type"], r["occupancy"], r["desc"], permits.fmt_num(r["value"]),
                        permits.fmt_num(r["sqft"]), r["zoning"], r["contractor"], r["owner"],
                        r["status"], r["score"], r["signals"], "New"])


def write_jobs_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Company", "City", "County", "Postings", "Why", "Flags", "Staffing agency",
                    "Retail", "Latest posting", "Sample titles", "Link", "Score"])
        for g in rows:
            w.writerow([g["company"], g["city"], g["county"], g["count"], g["why"],
                        ", ".join(g["flags"]), g["staffing"], g["retail"], g["latest"],
                        " / ".join(g["titles"]), g["link"], g["score"]])


def _money(v):
    return f"${v:,.0f}" if v else "—"


def digest(permit_rows, planning_rows, job_rows, status):
    L = [f"# Brink Signals — week of {TODAY}", ""]
    n = len(permit_rows) + len(planning_rows) + len(job_rows)
    L.append(f"**{n} new signals.** Earliest-stage first: hiring → planning → permits.\n")

    L.append("## 🔥 Hiring clusters (12–18 months ahead of a move)")
    if job_rows:
        L.append("| Company | Where | Open roles | Why it's here | Flags |")
        L.append("|---|---|---|---|---|")
        for g in job_rows[:25]:
            name = g["company"] + (" *(staffing — find the employer)*" if g["staffing"] else "") \
                + (" *(retail — likely store roles)*" if g["retail"] else "")
            flags = ", ".join(g["flags"]) or "—"
            link = f"[{g['count']}]({g['link']})" if g.get("link") else str(g["count"])
            L.append(f"| {name} | {g['city']}, {g['county']} | {link} | {g['why']} | {flags} |")
        L.append("\n*You:* ask whether the current building still fits. "
                 "*Material handling partner:* more operators = more trucks, racking, dock time.\n")
    else:
        L.append("_None new this week._\n")

    L.append("## 📐 Planning & development filings (6–9 months ahead)")
    if planning_rows:
        for r in planning_rows[:20]:
            L.append(f"- **{r['desc'] or 'Unnamed'}** — {r['county']} · {r['type'] or ''} · "
                     f"{r['status'] or ''} · {r['issue_date'] or ''} · _{r['signals']}_")
        L.append("\n*You:* who's developing it, and is it spec or build-to-suit? "
                 "*Partner:* future tenants need fit-out.\n")
    else:
        L.append("_None new this week._\n")

    L.append("## 🏗️ Permits (work is happening now)")
    if permit_rows:
        L.append("| Score | County | Address | Owner | Value | What | Signals |")
        L.append("|---|---|---|---|---|---|---|")
        for r in permit_rows[:30]:
            what = (r["desc"] or "").split(" | ")[0][:70]
            L.append(f"| {r['score']} | {r['county']} | {(r['address'] or '').strip()} | "
                     f"{r['owner'] or '—'} | {_money(r['value'])} | {what} | {r['signals']} |")
        L.append("\n*You:* if this is a new address, what building did they leave? That's a "
                 "backfill or sublease lead. *Partner:* racking, dock and forklift needs at this address.\n")
    else:
        L.append("_None new this week._\n")

    L.append("## Coverage")
    L.append("| Source | Status |")
    L.append("|---|---|")
    for label, s in status:
        L.append(f"| {label} | {s} |")
    for county, how in config.PORTAL_ONLY.items():
        L.append(f"| {county} permits (portal) | ⚪ no open feed — drop exports in `inbox/` · {how} |")
    L.append("\n_CSV files for Airtable are in this week's `output/` folder._")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-jobs", action="store_true")
    ap.add_argument("--all", action="store_true", help="include signals already reported")
    args = ap.parse_args()

    state = load_state()
    status = []
    found = run_arcgis(state, args.all, status)
    permit_rows = found["permits"] + run_inbox(state, args.all, status)
    permit_rows.sort(key=lambda r: r["score"], reverse=True)
    planning_rows = found["planning"]
    if args.no_jobs or not jobs.provider():
        status.append(("Job postings (all 7 counties)", "⚪ skipped — add the SERPAPI_API_KEY secret (free)"))
        job_rows = []
    else:
        job_rows = run_jobs(state, args.all, status)

    out = ROOT / "output" / TODAY
    out.mkdir(parents=True, exist_ok=True)
    write_permits_csv(out / "permits.csv", permit_rows)
    write_permits_csv(out / "planning.csv", planning_rows)
    write_jobs_csv(out / "jobs.csv", job_rows)
    text = digest(permit_rows, planning_rows, job_rows, status)
    (out / "digest.md").write_text(text)
    (ROOT / "output" / "latest-digest.md").write_text(text)
    save_state(state)
    print(text)


if __name__ == "__main__":
    sys.exit(main())
