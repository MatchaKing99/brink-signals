#!/usr/bin/env python3
"""
Sandbox: the permit-aggregator method on one county (Gaston, Tyler EnerGov).

  vendor connector -> standard record -> industrial tagging (signals.permits)
  -> parcel / owner match -> LLC flag -> report with a suggested move

Writes sandbox/output/report.md and permits.csv. Reads data/seen.json only to
compare against the live bot; never writes it.

  python3 -m sandbox.run_sandbox                # live, last 60 days
  python3 -m sandbox.run_sandbox --days 14 --max-details 50
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
import traceback
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from signals import config, permits          # noqa: E402  (reuse the live bot's scoring)
from sandbox import energov, parcels          # noqa: E402

PORTAL = "https://selfservice.gastongov.com/energov_prod/selfservice"
SOS_SEARCH = "https://www.sosnc.gov/online_services/search/by_title/_Business_Registration"
NEW_WORK = re.compile(r"new building|new construction|shell|foundation|erosion|site plan|grading|\bnew\b", re.I)
UPFIT = re.compile(r"alteration|remodel|upfit|up-fit|change in use|tenant|interior", re.I)
DEAD = re.compile(r"void|withdrawn|cancel|denied|expired", re.I)
ADDITION = re.compile(r"addition|expansion", re.I)


def sos_status(url):
    """Can we use the NC SOS business search from here? Checked once, never bypassed."""
    if not url:
        return "skipped"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": energov.UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read(20000).decode("utf-8", "ignore")
        if "Just a moment" in body or "challenge" in body.lower():
            return "blocked by a bot challenge, so look these up by hand"
        return "reachable"
    except urllib.error.HTTPError as e:
        body = e.read(20000).decode("utf-8", "ignore")
        if "Just a moment" in body or "cf-" in body:
            return f"blocked by a Cloudflare bot challenge (HTTP {e.code}), so look these up by hand"
        return f"HTTP {e.code}, so look these up by hand"
    except Exception as e:  # noqa: BLE001
        return f"unreachable ({e}), so look these up by hand"


def money(v):
    return f"${v:,.0f}" if v else ""


def your_move(rec, p):
    """One or two lines an industrial broker could act on this week."""
    # The permit type and work class say what kind of job it is; the free-text
    # description only breaks a tie ("new open office" inside a remodel is still a remodel).
    t = f"{rec['type']} {rec['work']}"
    if not (NEW_WORK.search(t) or UPFIT.search(t) or ADDITION.search(t)):
        t = f"{t} {rec['desc']}"
    who = (p or {}).get("owner") or rec["owner"] or "the owner"
    moves = []
    if ADDITION.search(t):
        moves.append(f"An owner-user is expanding in place. Ask {who} about overflow warehouse needs "
                     "or a move if the site maxes out.")
    elif UPFIT.search(t):
        moves.append("An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; "
                     "the space that user is leaving may come up for sublease or sale.")
    elif NEW_WORK.search(t):
        moves.append(f"New construction or site work. Call {who} now: "
                     "is it spec or build-to-suit, and is the leasing assignment open?")
    else:
        moves.append("The operator is spending money on the building (power, HVAC, fire). Find out when the lease "
                     "runs out and offer tenant rep before renewal talks start.")
    if p:
        if p.get("owner_state") and p["owner_state"] != "NC":
            moves.append(f"The owner is out of state ({p['owner_state']}). Pitch landlord rep or a BOV.")
        if p.get("sale_date") and p["sale_date"] >= (dt.date.today() - dt.timedelta(days=730)).isoformat():
            moves.append(f"It sold recently ({p['sale_date']}{', ' + money(p['sale_amount']) if p.get('sale_amount') else ''}). "
                         "A new owner may be repositioning it, so offer leasing.")
    return " ".join(moves)


def live_bot_keys(seen_path):
    try:
        seen = json.loads(Path(seen_path).read_text())
    except (OSError, ValueError):
        return set(), set()
    gaston_permits = {k for k in seen.get("permits", {}) if k.startswith("Gaston|")}
    gaston_addrs = {k.split("|")[2].upper() for k in seen.get("planning", {}) if k.startswith("Gaston|") and k.split("|")[2]}
    return gaston_permits, gaston_addrs


def run(base=PORTAL, parcels_url=parcels.GASTON_PARCELS, days=60, out_dir=ROOT / "sandbox" / "output",
        max_details=500, delay=1.0, sos_url=SOS_SEARCH, seen_path=ROOT / "data" / "seen.json",
        today=None, log=print):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    today = today or dt.date.today()
    problems = []
    log(f"EnerGov: {base}")
    client = energov.EnerGov(base, delay=delay)
    rows, details, stats, probs = energov.pull(client, days=days, today=today, max_details=max_details, log=log)
    problems += probs

    recs = []
    for cid, row in rows.items():
        if not energov.is_commercial(row):
            continue
        rec = energov.standardize(row, details.get(cid), portal=base)
        s, hits = permits.score(rec)
        rec["score"], rec["signals"] = s, ", ".join(dict.fromkeys(hits))
        recs.append(rec)

    try:
        pmap = parcels.lookup([r["parcel"] for r in recs], url=parcels_url)
    except RuntimeError as e:
        pmap = {}
        problems.append(f"parcel lookup: {e}")
    for r in recs:
        r["parcel_facts"] = pmap.get(r["parcel"])

    live = [r for r in recs if not DEAD.search(r["status"])]
    tagged = [r for r in live if r["score"] >= 0 and permits.is_industrial(r)]
    industrial = [r for r in tagged if r["score"] >= config.PERMIT_MIN_SCORE]
    below = [r for r in tagged if r["score"] < config.PERMIT_MIN_SCORE]
    # Commercial work on parcels the county classes as industrial that the keyword scorer didn't tag.
    tagged_ids = {id(r) for r in tagged}
    on_ind_parcel = [r for r in live if id(r) not in tagged_ids and r["score"] >= 0 and r["parcel_facts"]
                     and "industrial" in (r["parcel_facts"]["land_use"] + r["parcel_facts"]["use_class"]).lower()]
    for group in (industrial, below, on_ind_parcel):
        group.sort(key=lambda r: (r["score"], r["value"] or 0, r["sqft"] or 0), reverse=True)

    sos = sos_status(sos_url)
    seen_permits, seen_addrs = live_bot_keys(seen_path)
    stats.update(scored=len(recs), tagged=len(tagged), industrial=len(industrial),
                 parcels_matched=sum(1 for r in recs if r["parcel_facts"]), on_ind_parcel=len(on_ind_parcel))

    write_csv(out_dir / "permits.csv", recs)
    report = render(stats, industrial, below, on_ind_parcel, problems, sos, seen_permits, seen_addrs, days, today)
    (out_dir / "report.md").write_text(report)
    log(f"pulled {stats['pulled']}, commercial {stats['commercial']}, industrial {stats['industrial']} "
        f"(+{len(below)} tagged below score {config.PERMIT_MIN_SCORE}), on industrial parcels {len(on_ind_parcel)}")
    return stats, industrial, problems


def write_csv(path, recs):
    cols = ["permit_no", "issue_date", "apply_date", "type", "occupancy", "desc", "address", "value", "sqft",
            "status", "score", "signals", "parcel", "parcel_owner", "land_use", "acres", "url"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in sorted(recs, key=lambda r: -r["score"]):
            p = r["parcel_facts"] or {}
            w.writerow({**r, "parcel_owner": p.get("owner", ""), "land_use": p.get("land_use", ""),
                        "acres": p.get("acres", "")})


def card(r, seen_addrs, star=False):
    p = r["parcel_facts"]
    title = (r["desc"] or r["type"])[:90]
    lines = [f"### {'⭐ ' if star else ''}{title} | {r['address']}",
             f"- **What:** {r['type']}{' (' + r['work'] + ')' if r['work'] else ''}. Status: {r['status']}. "
             f"Applied {r['apply_date'] or '?'}, issued {r['issue_date'] or 'not yet'}. "
             f"[{r['permit_no']}]({r['url']})",
             f"- **Size:** {money(r['value']) or 'no valuation'}"
             f"{', ' + format(int(r['sqft']), ',') + ' SF of work' if r['sqft'] else ''}"
             f"{', occupancy ' + r['occupancy'] if r['occupancy'] else ''}"
             f"{', site work ' + r['site_acres'] if r['site_acres'] else ''}. "
             f"Score {r['score']} ({r['signals'] or 'no keywords'})"]
    lines.append(f"- **Who:** owner of record {(p or {}).get('owner') or 'unknown'}. The GC and applicant "
                 "aren't public on this portal, so ask the owner or check the job-site sign.")
    if p:
        lines.append(f"- **Property:** PIN {p['pin']}, {p['land_use'] or '?'} land use, {p['acres']} ac"
                     f"{', ' + format(int(p['bldg_sqft']), ',') + ' SF building' if p['bldg_sqft'] else ''}"
                     f"{', built ' + str(p['year_built']) if p['year_built'] else ''}"
                     f"{', tax value ' + money(p['market_value']) if p['market_value'] else ''}. "
                     f"Owner {p['owner']} ({p['owner_mail']}). Deed {p['deed']}"
                     f"{', last sale ' + p['sale_date'] if p['sale_date'] else ''}"
                     f"{' for ' + money(p['sale_amount']) if p.get('sale_amount') else ''}.")
    else:
        lines.append(f"- **Property:** no parcel match for {r['parcel'] or 'a blank parcel number'}")
    ents = parcels.entities((p or {}).get("owner"))
    if ents:
        lines.append(f"- **Look up at NC SOS:** {', '.join(ents)}")
    if r["address"].split(" NC ")[0].upper() in seen_addrs:
        lines.append("- **Live bot:** this address is already in the Gaston planning signals")
    lines.append(f"- **Your move:** {your_move(r, p)}")
    return "\n".join(lines)


def render(stats, industrial, below, on_ind_parcel, problems, sos, seen_permits, seen_addrs, days, today):
    out = [f"# SANDBOX: Gaston County permit pipeline, {today.isoformat()}", "",
           f"Source: Gaston County Citizen Self Service (Tyler EnerGov), public search API, no login. "
           f"Window: permits issued or applied in the last {days} days.", "",
           "| Step | Result |", "|---|---|",
           f"| Pulled (issued or applied in window) | {stats['pulled']} |",
           f"| Commercial / industrial permit types | {stats['commercial']} ({stats['primary']} building or site work, the rest trade permits) |",
           f"| Detail records fetched | {stats['details']} |",
           f"| Tagged industrial by the bot's scorer | {stats['tagged']} |",
           f"| **Industrial at the bot's digest threshold (score ≥ {config.PERMIT_MIN_SCORE})** | **{stats['industrial']}** |",
           f"| Other commercial work on industrial-use parcels | {stats['on_ind_parcel']} |",
           f"| Matched to a county parcel | {stats['parcels_matched']} of {stats['scored']} |",
           f"| API calls to the portal | {stats['api_calls']} |",
           f"| NC Secretary of State lookups | {sos} |", "",
           f"**Compared with the live bot:** it has {len(seen_permits)} Gaston permits on record "
           "(Gaston permits currently need a manual export), so every permit below is one it missed.", ""]
    out += ["## Industrial permits", "",
            f"Everything the bot's scorer tags as industrial. ⭐ = score {config.PERMIT_MIN_SCORE}+, "
            "the bar for the weekly digest.", ""]
    out += [card(r, seen_addrs, star=True) + "\n" for r in industrial]
    out += [card(r, seen_addrs) + "\n" for r in below]
    if not industrial and not below:
        out += ["None this window.", ""]
    out += ["## Other commercial work on industrial parcels", "",
            "The keyword scorer didn't tag these, but the county classes the parcel as industrial. "
            "That's a sign the operator is investing in the building.", ""]
    out += [card(r, seen_addrs) + "\n" for r in on_ind_parcel[:15]] or ["None.", ""]
    if len(on_ind_parcel) > 15:
        out.append(f"...and {len(on_ind_parcel) - 15} more in permits.csv.")
    out += ["", "## Problems", ""]
    out += [f"- {p}" for p in problems] or ["- None."]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--max-details", type=int, default=500)
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between portal requests")
    ap.add_argument("--out", default=str(ROOT / "sandbox" / "output"))
    ap.add_argument("--no-sos", action="store_true", help="skip the NC SOS reachability check")
    a = ap.parse_args()
    try:
        run(days=a.days, max_details=a.max_details, delay=a.delay, out_dir=a.out,
            sos_url=None if a.no_sos else SOS_SEARCH)
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        Path(a.out).mkdir(parents=True, exist_ok=True)
        (Path(a.out) / "report.md").write_text("# SANDBOX: Gaston permit pipeline FAILED\n\n```\n"
                                               + traceback.format_exc() + "```\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
