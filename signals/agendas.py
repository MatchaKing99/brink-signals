"""
Industrial zoning items from town agendas published through CivicPlus
AgendaCenter (e.g. Fort Mill SC). Standard library plus the `pdftotext`
command (poppler-utils), which the weekly workflow installs.

For each configured board, read agendas posted in the last N days, keep the
agenda page itself (up to ADJOURN), split it into numbered items and keep the
zoning / annexation / site-plan / conditional-use items with an industrial hit.
"""
import datetime as dt
import html
import re
import subprocess
import tempfile
import time
import urllib.request

from signals import permits

PAUSE = 1.0
ZONING_ITEM = re.compile(r"rezon|zoning map|map amendment|annex|conditional (use|zoning)|special (use|exception)|"
                         r"site plan|planned development|master plan|land development", re.I)
NOT_A_USER = re.compile(r"residential \(R-|single.family|townhome|apartment|multi.family|church|school|"
                        r"short.term rental|text amendment|moratorium|master plan|comprehensive plan", re.I)


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
        if re.sub(r"<[^>]+>|\s+", " ", html.unescape(m.group(1))).strip().lower() != board.lower():
            continue
        for path, mdy in dict.fromkeys(re.findall(r'href="(/AgendaCenter/ViewFile/Agenda/_(\d{8})-\d+)"', m.group(2))):
            d = dt.date(int(mdy[4:]), int(mdy[:2]), int(mdy[2:4]))
            if d >= cutoff:
                out.append((d, path))
    return out


def items(text):
    """Agenda items (title + description) from the agenda page. Handles numbered
    items ("1. Annexation/Zoning Map Amendment Request: ...") and ITEM blocks with
    lettered sub-items ("ITEM 4 New Business / A. Consideration of ...")."""
    head = re.split(r"\n[^\n]*\bAdjourn|\n[^\n]*press was notified|\n\s*(?:Present|Members present):",
                    text, maxsplit=1, flags=re.I)[0]
    parts = re.split(r"\n\s*(?:ITEM\s+\d+\s+[^\n]*|\d{1,2}\.|[A-H]\.)\s+", head)
    out = []
    for n, body in enumerate(parts[1:], 1):
        body = re.sub(r"\[Pages? [\d\-– ]+\]", "", body)
        body = re.sub(r"\s+", " ", body).strip()
        if len(body) > 25:
            out.append((str(n), body))
    return out


def to_record(src, board, date, url, num, body):
    to_zone = re.search(r"(?:zoning designation of|to)\s+[^()]*?\(([A-Z]{1,3}(?:-[A-Z0-9]{1,3})?)\)", body)
    where = re.search(r"Request:\s*([^.]+?)(?:\s{2,}|\s+An\b|\s+A\b|$)", body)
    acres = re.search(r"([\d.,]+)\s*(?:\+/-\s*)?acres", body)
    rec = {"permit_no": f"{src['town']} {board} {date:%m/%d/%Y} item {num}", "issue_date": date.isoformat(),
           "type": board, "desc": body, "address": where.group(1).strip() if where else "", "value": 0, "sqft": 0,
           "status": "On agenda", "occupancy": None, "zoning": to_zone.group(1) if to_zone else None,
           "contractor": "", "owner": "", "acres": acres.group(1) if acres else "",
           "property": f"agenda: {url}"}
    scored = dict(rec, desc=re.sub(r"\bfrom .*? to ", "to ", body))
    score, hits = permits.score(scored)
    rec["score"], rec["signals"] = max(score, 0), ", ".join(hits)
    rec["industrial"] = (score >= 0 and bool(ZONING_ITEM.search(body)) and not NOT_A_USER.search(body)
                         and any(h in permits.INDUSTRIAL_HITS for h in hits))
    rec["county"] = src["county"]
    return rec


def pull(src):
    """Returns (agenda items read, records)."""
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
