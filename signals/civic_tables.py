"""
Rezoning cases from county web pages that list them in a plain HTML table
(CivicPlus sites such as Lincoln County's Pending Applications and yearly
Closed Applications pages). Standard library only.

Rows read: case number | applicant | description | hearing date [| decision].
A case is reported when it first appears and again when it's decided.
"""
import datetime as dt
import html
import re
import time
import urllib.request

from signals import permits

# Rezonings that mention industrial zoning but aren't an operator taking space.
NOT_A_USER = re.compile(r"dog boarding|kennel|vehicle sales|funeral|church|apartment|short.term rental|greenspace|"
                        r"residential single family\)\.|cell tower|telecommunication|billboard", re.I)


def fetch(url, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "brink-signals/1.0 (weekly rezoning check)"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except OSError:
            if attempt == tries - 1:
                raise
            time.sleep(2 ** attempt * 2)


def _cell(c):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<br\s*/?>", " ", re.sub(r"<(?!br)[^>]+>", " ", c)))).strip()


def rows(page):
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = [_cell(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(cells) >= 4 and re.match(r"(ZMA|CZ|PD|SUP|UDO|TA|CUP|REZ)\b", cells[0], re.I):
            cells[0] = re.sub(r"\s*Map Link\s*", "", cells[0]).strip()
            out.append(cells)
    return out


def to_record(cells, county):
    case, applicant, desc, hearing = cells[:4]
    decision = cells[4] if len(cells) > 4 else ""
    status = decision or ("Postponed" if "Postponed" in hearing else "Pending")
    when = re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", hearing)
    d = permits.to_date(when.group(0)) if when else None
    to_zone = re.search(r"\bto ((?:CZ |Conditional Zoning )?[A-Z]{1,3}(?:-[A-Z0-9]{1,3})?)\b", desc)
    where = (re.search(r"located (?:at|on) (.+?) in [A-Z][A-Za-z ]+? Township", desc)
             or re.search(r"located (?:at|on) (.+?)\.(?:\s+[A-Z][a-z]|$)", desc))
    acres = re.search(r"([\d.,]+)[- ]acre", desc)
    rec = {"permit_no": case + ("" if status.lower().startswith(("pending", "post")) else f" ({status.lower()})"),
           "issue_date": d.isoformat() if d else "", "type": "Rezoning", "desc": desc,
           "address": where.group(1) if where else "", "value": 0, "sqft": 0, "status": status,
           "occupancy": None, "zoning": to_zone.group(1) if to_zone else None, "contractor": applicant,
           "owner": "", "acres": acres.group(1) if acres else ""}
    # Score the request without the zoning it's leaving, so "from I-G to B-G" isn't industrial.
    scored = dict(rec, desc=re.sub(r"\bfrom .*? to ", "to ", desc))
    score, hits = permits.score(scored)
    rec["score"], rec["signals"] = max(score, 0), ", ".join(hits)
    rec["industrial"] = (score >= 0 and not NOT_A_USER.search(desc)
                         and any(h in permits.INDUSTRIAL_HITS for h in hits))
    rec["county"] = county
    return rec


def pull(src):
    """Returns (cases listed, records) from the pending page plus this year's
    closed page, found by name in the pending page's navigation."""
    pending = fetch(src["url"])
    pages = [pending]
    year = dt.date.today().year
    link = re.search(rf'href="(/\d+/{year}-Closed-Applications)"', pending)
    if link:
        base = re.match(r"https?://[^/]+", src["url"]).group(0)
        time.sleep(1)
        pages.append(fetch(base + link.group(1)))
    seen, items = set(), []
    for page in pages:
        for cells in rows(page):
            rec = to_record(cells, src["county"])
            if rec["permit_no"] not in seen:
                seen.add(rec["permit_no"])
                items.append(rec)
    return len(items), items
