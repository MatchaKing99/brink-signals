"""
Gaston County parcel lookup (sandbox).

EnerGov's MainParcel (e.g. "126071") is the county's AKPAR / PID, not the
dashed PIN, so we match on AKPAR. Layer fields as seen live in Oct 2026.
"""
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from sandbox.energov import UA

GASTON_PARCELS = "https://gis.gastoncountync.gov/publicgis/rest/services/PublicGIS/Parcels/FeatureServer/11"
FIELDS = ["AKPAR", "PIN", "WHOLE_ADDRESS", "POSTAL", "CURR_NAME1", "CURR_NAME2", "CURR_ADDR1", "CURR_ADDR2",
          "CURR_CITY", "CURR_STATE", "CURR_ZIPCODE", "DEED_BOOK", "DEED_PAGE", "DEEDTYPE", "DESC1_DESC",
          "property_use", "CALCAC", "SQFT", "YEARBLT", "FMV_TOTAL", "SALEDATE", "SALESAMT"]

ENTITY = re.compile(r"\b(LLC|L\.L\.C|INC|INCORPORATED|CORP|CORPORATION|LP|LLP|LTD|COMPANY|CO|HOLDINGS|"
                    r"PROPERTIES|PARTNERS|PARTNERSHIP|TRUST|REIT|FUND)\b\.?", re.I)


def _post(url, params, retries=4):
    data = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                out = json.load(r)
            if "error" in out:
                raise RuntimeError(f"ArcGIS error: {out['error']}")
            return out
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            last = e
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError(f"parcel query failed after {retries} tries: {last}")


def lookup(parcel_ids, url=GASTON_PARCELS, batch=50, delay=0.5):
    """{AKPAR: parcel facts} for the given EnerGov MainParcel values."""
    ids = sorted({str(p).strip() for p in parcel_ids if p and str(p).strip().isdigit()})
    out = {}
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        where = "AKPAR IN (" + ",".join(f"'{p}'" for p in chunk) + ")"
        data = _post(url.rstrip("/") + "/query", {"where": where, "outFields": ",".join(FIELDS),
                                                  "returnGeometry": "false", "f": "json"})
        for f in data.get("features", []):
            a = f["attributes"]
            out.setdefault(str(a["AKPAR"]), facts(a))
        time.sleep(delay)
    return out


def facts(a):
    sale = a.get("SALEDATE")
    sale = dt.datetime.fromtimestamp(sale / 1000, dt.timezone.utc).date().isoformat() if sale else ""
    owner = " & ".join(x.strip() for x in (a.get("CURR_NAME1"), a.get("CURR_NAME2")) if x and x.strip())
    mail = ", ".join(x.strip() for x in (a.get("CURR_ADDR1"), a.get("CURR_ADDR2"), a.get("CURR_CITY")) if x and x.strip())
    mail = f"{mail} {(a.get('CURR_STATE') or '').strip()} {(a.get('CURR_ZIPCODE') or '').strip()[:5]}".strip()
    return {"pin": a.get("PIN") or "", "site": f"{a.get('WHOLE_ADDRESS') or ''}, {a.get('POSTAL') or ''}".strip(", "),
            "owner": owner, "owner_mail": mail, "owner_state": (a.get("CURR_STATE") or "").strip(),
            "deed": f"Bk {a.get('DEED_BOOK')} Pg {a.get('DEED_PAGE')} ({a.get('DEEDTYPE') or '?'})"
                    if a.get("DEED_BOOK") else "",
            "land_use": a.get("DESC1_DESC") or "", "use_class": a.get("property_use") or "",
            "acres": a.get("CALCAC"), "bldg_sqft": a.get("SQFT"), "year_built": a.get("YEARBLT"),
            "market_value": a.get("FMV_TOTAL"), "sale_date": sale, "sale_amount": a.get("SALESAMT")}


def entities(*names):
    """Names that look like companies (LLC, Inc, ...) to look up at the NC Secretary of State."""
    seen, keys = [], set()
    for n in names:
        n = (n or "").strip()
        key = re.sub(r"[^A-Z0-9]", "", n.upper())
        if n and ENTITY.search(n) and key not in keys:
            seen.append(n)
            keys.add(key)
    return seen
