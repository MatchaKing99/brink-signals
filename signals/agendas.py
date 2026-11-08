"""
Industrial zoning items from town agendas. Two platforms:

- CivicPlus AgendaCenter (e.g. Fort Mill SC, Indian Trail): read agendas
  posted in the last N days, keep the agenda page itself (up to ADJOURN) and
  split it into numbered items. Needs the `pdftotext` command (poppler-utils),
  which the weekly workflow installs.
- CivicClerk (e.g. Monroe, Huntersville, Kannapolis): the public portal's
  JSON API lists meetings and each agenda item's full text, so no PDFs.
- Legistar (Charlotte City Council, Mecklenburg commissioners): the public web
  API lists meetings and item titles, e.g. "Public Hearing and Decision on
  Averitt Express, Inc. Business Investment Grant".

Either way, keep the zoning / annexation / site-plan / conditional-use items
with an industrial hit.
"""
import json
import datetime as dt
import html
import re
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request

from signals import permits

PAUSE = 1.0
ZONING_ITEM = re.compile(r"rezon|zoning map|map amendment|annex|conditional (use|zoning)|special (use|exception)|"
                         r"site plan|planned development|master plan|land development|\b(ZM|CZ|CUP|SUP)[- ]?\d", re.I)
NOT_A_USER = re.compile(r"residential \(R-|single.family|townhome|apartment|multi.family|church|school|"
                        r"short.term rental|text amendment|moratorium|master plan|comprehensive plan|"
                        r"manufactured home|road nam|hotel|restaurant|detention center|employee|staffing", re.I)
# Economic-development incentive hearings: often the first public trace of a
# code-named plant or distribution center ("Incentive Request for Project Tribe").
INCENTIVE = re.compile(r"\bincentive|\bEDC\b|economic development (agreement|grant)|investment grant", re.I)
STATUS = [(re.compile(r"removed from (the )?agenda|withdrawn", re.I), "Withdrawn"),
          (re.compile(r"postponed|continued|tabled|deferred", re.I), "Postponed"),
          (re.compile(r"\b(unanimously )?approved\b(?!.*\bconsider)", re.I), "Approved"),
          (re.compile(r"\bdenied\b", re.I), "Denied")]


def fetch(url, binary=False, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "brink-signals/1.0 (weekly agenda check)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", "replace")
        except OSError:
            if attempt == tries - 1:
                raise
            time.sleep(2 ** attempt * 2)


def pdf_text(data, pages=3):
    """Text of the first few pages: the agenda itself. Packets that follow it
    (staff reports, whole ordinances) would otherwise read as agenda items."""
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(data)
        f.flush()
        return subprocess.run(["pdftotext", "-layout", "-l", str(pages), f.name, "-"], capture_output=True,
                              text=True, check=True, timeout=120).stdout


def agenda_links(page, board, days):
    """[(date, url)] for one board's agendas posted within `days`."""
    cutoff = dt.date.today() - dt.timedelta(days=days)
    out = []
    for m in re.finditer(r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|\Z)", page, re.S):
        # Some sites mark a heading with "*" (e.g. Indian Trail's "* Town Council").
        if re.sub(r"<[^>]+>|\s+", " ", html.unescape(m.group(1))).strip(" *").lower() != board.lower():
            continue
        for path, mdy in dict.fromkeys(re.findall(r'href="(/AgendaCenter/ViewFile/Agenda/_(\d{8})-\d+)"', m.group(2))):
            d = dt.date(int(mdy[4:]), int(mdy[:2]), int(mdy[2:4]))
            if d >= cutoff:
                out.append((d, path))
    return out


CASE_NO = re.compile(r"\b[A-Z]{1,5}[- ]?\d{2,4}-\d{2,5}\b")


def items(text):
    """Agenda items (title + description) from the agenda page. Handles numbered
    items ("1. Annexation/Zoning Map Amendment Request: ..."), ITEM blocks with
    lettered sub-items ("ITEM 4 New Business / A. Consideration of ...") and
    bullets ("• ZM 2026-0101 (3010 W. Unionville Indian Trail Rd.)"). When the
    staff memo follows the agenda in the same PDF, the memo's request sentence
    for that case is appended, since bullet items name only the case."""
    head, *rest = re.split(r"\n[^\n]*\bAdjourn[^\n]*|\n[^\n]*press was notified|\n\s*(?:Present|Members present):",
                           text, maxsplit=1, flags=re.I)
    tail = re.sub(r"\s+", " ", rest[0]) if rest else ""
    parts = re.split(r"\n\s*(?:ITEM\s+\d+\s+[^\n]*|\d{1,2}\.|[A-H]\.|•)\s+", head)
    out = []
    for n, body in enumerate(parts[1:], 1):
        body = re.sub(r"\[Pages? [\d\-– ]+\]", "", body)
        body = re.sub(r"\s+", " ", body).strip()
        case = CASE_NO.search(body)
        at = tail.find(case.group(0)) if case else -1
        memo = re.search(r"The (?:request|applicant|petitioner)\b.*?\.(?:\s+The intent\b.*?\.)?", tail[at:at + 3000]) \
            if at >= 0 else None
        if memo:
            body += " | staff memo: " + memo.group(0)
        if len(body) > 25:
            out.append((str(n), body))
    return out


def to_record(src, board, date, url, num, body):
    # The requested zoning: the last "to <name> (CODE)" once the zoning it's leaving is cut out
    # ("...to rezone the property ... from Mixed-Use (RC-MX) to Light Industrial (LI)").
    to_zone = ([None] + re.findall(r"(?:zoning designation of|\bto)\s+[^()]*?\(([A-Z]{1,3}(?:-[A-Z0-9]{1,3})?)\)",
                                   re.sub(r"\bfrom [^()]*\([^)]*\)(?:,? (?:and|or) [^()]*\([^)]*\))*", "", body)))[-1]
    where = (re.search(r"Request:\s*([^.]+?)(?:\s{2,}|\s+An\b|\s+A\b|$)", body)
             or re.search(r"located (?:at|along|on) (.+?)(?:,? and (?:further )?identified|,? \(?(?:tax )?parcel|"
                          r",? (?:PIN|Tax Map)|,? (?:Gaston |Union |\w+ )?County| from |[;]|(?<!\b[NSEW])(?<!Ave|Hwy)(?<!Rd|St|Dr)(?<!Blvd)\.(?!\w)|$)", body))
    acres = re.search(r"([\d.,]+)\s*(?:\+/-\s*)?acres", body)
    rec = {"permit_no": f"{src['town']} {board} {date:%m/%d/%Y} item {num}", "issue_date": date.isoformat(),
           "type": board, "desc": body, "address": where.group(1).strip() if where else "", "value": 0, "sqft": 0,
           "status": next((name for rx, name in STATUS if rx.search(body)), "On agenda"), "occupancy": None, "zoning": to_zone or ([None] + re.findall(r"\bto ([A-Z]{1,3}-[A-Z0-9]{1,3})\b", body))[-1],
           "contractor": "", "owner": "", "acres": acres.group(1) if acres else "",
           "property": f"agenda: {url}"}
    scored = dict(rec, desc=re.sub(r"\bfrom .*? to ", "to ", body))
    score, hits = permits.score(scored)
    rec["score"], rec["signals"] = max(score, 0), ", ".join(hits)
    if INCENTIVE.search(body):
        hits.append("economic-development incentive")
        rec["signals"] = ", ".join(hits)
    rec["industrial"] = not NOT_A_USER.search(body) and (
        INCENTIVE.search(body) is not None
        or (score >= 0 and bool(ZONING_ITEM.search(body)) and any(h in permits.INDUSTRIAL_HITS for h in hits)))
    rec["county"] = src["county"]
    return rec


def pull(src):
    """Returns (agenda items read, records)."""
    if src.get("civicclerk"):
        return pull_civicclerk(src)
    if src.get("legistar"):
        return pull_legistar(src)
    base = src["base"].rstrip("/")
    page = fetch(base + "/AgendaCenter")
    recs = []
    for board in src["boards"]:
        for date, path in agenda_links(page, board, src.get("days", 60)):
            time.sleep(PAUSE)
            text = pdf_text(fetch(base + path, binary=True))
            for num, body in items(text):
                recs.append(to_record(src, board, date, base + path, num, body))
    return len(recs), recs


# CivicClerk boards worth reading, and meetings that never carry land-use items.
CC_BOARDS = re.compile(r"planning|zoning|council|commissioners|town board|adjustment", re.I)
CC_SKIP = re.compile(r"work session|workshop|retreat|strategic|committee|tourism|parks|sample|budget", re.I)


def _clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def _walk(items):
    for it in items or []:
        yield it
        yield from _walk(it.get("childItems"))


def pull_civicclerk(src):
    """Agenda items from a CivicClerk tenant's public API (meetings since
    `days` ago, upcoming ones included once their agenda is published)."""
    tenant = src["civicclerk"]
    api = src.get("api") or f"https://{tenant}.api.civicclerk.com/v1"
    since = (dt.date.today() - dt.timedelta(days=src.get("days", 30))).isoformat()
    url = f"{api}/Events?" + urllib.parse.urlencode({"$filter": f"startDateTime ge {since}",
                                                       "$orderby": "startDateTime"})
    events = []
    while url and len(events) < 300:
        page = json.loads(fetch(url))
        events += page.get("value", [])
        url = page.get("@odata.nextLink")
        time.sleep(PAUSE)
    recs = []
    for e in events:
        board = e.get("eventName") or ""
        if not e.get("agendaId") or not CC_BOARDS.search(board) or CC_SKIP.search(board):
            continue
        time.sleep(PAUSE)
        meeting = json.loads(fetch(f"{api}/Meetings/{e['agendaId']}"))
        date = dt.date.fromisoformat(e["startDateTime"][:10])
        link = f"https://{tenant}.portal.civicclerk.com/event/{e['id']}/overview"
        for it in _walk(meeting.get("items")):
            body = _clean(f"{it.get('agendaObjectItemName')} {it.get('agendaObjectItemDescription') or ''}")
            if len(body) > 25 and not it.get("childItems"):
                num = it.get("agendaObjectItemOutlineNumberFull") or it.get("agendaObjectItemOutlineNumber") or it["id"]
                recs.append(to_record(src, board, date, link, str(num).strip(". "), body))
    return len(recs), recs


def pull_legistar(src):
    """Agenda item titles from a Legistar client's public web API, for the
    boards matching `bodies` (a regex)."""
    api = src.get("api") or f"https://webapi.legistar.com/v1/{src['legistar']}"
    since = (dt.date.today() - dt.timedelta(days=src.get("days", 30))).isoformat()
    events = json.loads(fetch(f"{api}/events?" + urllib.parse.urlencode(
        {"$filter": f"EventDate ge datetime'{since}'", "$orderby": "EventDate"})))
    recs, seen = [], set()
    for e in events:
        board = e.get("EventBodyName") or ""
        if not re.search(src["bodies"], board, re.I):
            continue
        time.sleep(PAUSE)
        date = dt.date.fromisoformat(e["EventDate"][:10])
        link = e.get("EventInSiteURL") or e.get("EventAgendaFile") or ""
        for it in json.loads(fetch(f"{api}/events/{e['EventId']}/eventitems")):
            body = _clean(it.get("EventItemTitle"))
            if len(body) > 25 and (e["EventId"], body) not in seen:
                seen.add((e["EventId"], body))
                num = it.get("EventItemAgendaNumber") or it.get("EventItemMatterFile") or it["EventItemId"]
                recs.append(to_record(src, board, date, link, str(num).strip(". "), body))
    return len(recs), recs
