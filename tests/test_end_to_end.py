"""
End-to-end run against local fake county + job-board servers shaped like the
real ones (Mecklenburg field names and occupancy codes as seen live in Oct 2026).

  python3 -m unittest discover tests
"""
import datetime as dt
import http.server
import json
import os
import re
import shutil
import tempfile
import threading
import unittest
import urllib.parse
from pathlib import Path

import run_weekly
from signals import accela, config, energov, jobs, permits

NOW = int(dt.datetime.now().timestamp() * 1000)
DAY = 86_400_000


def meck(i, days_ago, occ, desc, cost, zone="ML-1", ptype="Commercial"):
    return {"objectid": i, "permitnum": f"B{i}", "issuedate": NOW - days_ago * DAY,
            "permittype": ptype, "occupancy": occ, "projname": desc, "projadd": f"{i} Test Rd  ",
            "bldgcost": cost, "zonecode": zone, "ownname": f"Owner {i}", "permitstat": "Issued",
            "usdcdesc": "437 - Commercial - Plan Review (Upfits, Additions, Repair)", "totalsqft": 5000}


MECK = [
    meck(1, 3, "S1     * STORAGE - MODERATE HAZARD", "High pile racking install", 420000),
    meck(2, 5, "F1     * FACTORY INDUSTRIAL - MODERATE", "Building addition", 1800000),
    meck(3, 6, "S1     * STORAGE - MODERATE HAZARD", "Detached Garage #12 apartments", 200000),
    meck(4, 8, "U      * UTILITY", "Primary clarifier distribution", 5000000),
    meck(5, 9, "R3     * RESIDENTIAL - SINGLE FAMILY", "Dock replacement", 39000, "R-3", "One/Two Family"),
    meck(6, 90, "S1     * STORAGE - MODERATE HAZARD", "Warehouse racking (old)", 900000),
]
GASTON = [{"OBJECTID": 1, "NAME": "FAIRVIEW INDUSTRIAL", "DATE": NOW - 400 * DAY, "STATUS": "PROPOSED",
           "DEV_TYPE": "Commercial", "created_date": NOW - 300 * DAY},
          {"OBJECTID": 2, "NAME": "LOWELL WOODS", "DATE": NOW - 400 * DAY, "STATUS": "APPROVED",
           "DEV_TYPE": "Single Family Residential", "created_date": NOW - 300 * DAY}]
CABARRUS_2026 = [meck(10, 4, "S2     * STORAGE - LOW HAZARD", "Warehouse upfit with dock levelers", 300000, "I-1")]


def insp(i, pid, name, days_ago, addr):
    return {"objectid": i, "permit_id": pid, "address": addr, "parcel": f"P{pid}",
            "inspection_name": name, "inspection_status": "Approved",
            "inspection_date": NOW - days_ago * DAY, "created_date": NOW}


UNION_OK = [insp(1, 501, "Comm Building Footing", 20, "100 Industrial Dr  Monroe"),
            insp(2, 502, "Comm Building Final", 10, "9509 Morgan Mill Rd  Monroe"),
            insp(3, 502, "Comm Electrical Final", 12, "9509 Morgan Mill Rd  Monroe"),
            insp(4, 503, "Res Building Framing", 5, "4755 Dusty Ln  Marshville"),
            insp(5, 504, "Comm Building Final", 300, "Old Job Rd  Monroe")]
UNION_NOT = [insp(9, 501, "Comm Plumbing Rough In", 8, "100 Industrial Dr  Monroe")]


def rowan(i, num, ptype, work, sqft, days_ago, company):
    return {"OBJECTID": i, "TypeName": "Permit", "dIssued": NOW - days_ago * DAY, "sPermitNum": num,
            "sCompanyName_Parc": company, "sAddress1": str(100 + i), "sPreDirection": "",
            "sAddress2": "UNITY CHURCH", "sStreetT": "RD", "sName_Workclass": work, "sSqFeet": sqft,
            "sName": "Active", "PermitType": ptype}


ROWAN = [rowan(1, "COM-10-26-1", "Commercial", "New Warehouse", 120000, 3, "Big GC Inc"),
         rowan(2, "COM-10-26-2", "Commercial", "Upfit", 1200, 4, "Small GC"),
         rowan(3, "ELEC-10-26-3", "Electrical", "Conditional Power", 0, 2, "Sparky"),
         rowan(4, "COM-10-47-4", "Commercial", "New Warehouse", 90000, -7000, "Typo Date"),
         rowan(5, "COM-10-26-5", "Commercial", "Re Roof", 30000, 3, "Roofer Co")]
ROWAN_ZONING = [{"OBJECTID": 1, "CASE_": "Z 07-26", "ZONING": "IND", "COMMENTS": "Rezone for distribution center",
                 "APPROVAL": "October 1, 2026", "created_date": NOW - 10 * DAY},
                {"OBJECTID": 2, "CASE_": "Z 07-26", "ZONING": "IND", "COMMENTS": "Rezone for distribution center",
                 "APPROVAL": "October 1, 2026", "created_date": NOW - 10 * DAY},
                {"OBJECTID": 3, "CASE_": "Z 08-26", "ZONING": "RS", "COMMENTS": "Single family subdivision",
                 "APPROVAL": "October 1, 2026", "created_date": NOW - 10 * DAY},
                {"OBJECTID": 4, "CASE_": "Z 05-26", "ZONING": "IND", "COMMENTS": "Kannapolis ETJ Relinquishment",
                 "APPROVAL": "September 21, 2026", "created_date": NOW - 10 * DAY}]
GASTON_REZ = [{"OBJECTID": 1, "ZRNO": "REZ-26-01", "DATE": NOW - 30 * DAY, "LOCATION": "1 Logistics Pkwy",
               "PROPSDZONE": "CD/I-2", "REZONEAC": 40.0},
              {"OBJECTID": 2, "ZRNO": "REZ-26-02", "DATE": NOW - 30 * DAY, "LOCATION": "315 W Chestnut St",
               "PROPSDZONE": "R-8", "REZONEAC": 1.6}]
_meet = (dt.date.today() - dt.timedelta(days=20)).strftime("%B %d, %Y") + " at 6:00"
IREDELL_HEARINGS = [{"OBJECTID": 1, "Case_": "Case: 2610-1", "Meeting_Time": _meet,
                     "Location_Site": "195 Ostwalt Amity", "Applicant": "Encased Power, LLC",
                     "Request": "This is a request to rezone from RA to Heavy Industrial (HI) for manufacturing."},
                    {"OBJECTID": 2, "Case_": "Case: 2102-1", "Meeting_Time": "February 3, 2021 at 7:00",
                     "Location_Site": "1 Old Rd", "Applicant": "Old Co",
                     "Request": "Rezone to Heavy Industrial for a warehouse."}]

# Charlotte's PLN/Rezonings layer (field names as seen live Oct 2026).
CLT_REZ = [{"OBJECTID": 1, "Petition": "2026-081", "Petitioner": "Crossroads Logistics LLC",
            "ExistZone": "N1-A", "ReqZone": "ML-1(CD)", "Type": "CD", "PetAcres": 42.5,
            "Propluse": "Warehouse distribution", "Status": "Pending", "Received": NOW - 20 * DAY},
           {"OBJECTID": 2, "Petition": "2026-076", "Petitioner": "Greg Smith", "ExistZone": "ML-2",
            "ReqZone": "N1-C", "Type": "CV", "PetAcres": 0.28, "Propluse": None, "Status": "Pending",
            "Received": NOW - 20 * DAY},
           {"OBJECTID": 3, "Petition": "2026-077", "Petitioner": "Keen Homecrafters LLC",
            "ExistZone": "N1-A", "ReqZone": "N1-B(CD)", "Type": "CD", "PetAcres": 0.79, "Propluse": None,
            "Status": "Pending", "Received": NOW - 20 * DAY}]

# Gaston EnerGov portal: real records saved from the live search (Oct 2026).
EG = json.loads((Path(__file__).parent / "fixtures" / "gaston_energov.json").read_text())
EG_ROWS = [dict(r, IssueDate=f"{dt.date.today()}T00:00:00") for r in EG["rows"]]


def energov_route(handler, path, q, body):
    if path.endswith("/search/criteria"):
        return handler._send({"Result": EG["criteria"]})
    if path.endswith("/search/search"):
        assert body["SortBy"] == "IssueDate" and body["FilterModule"] == 2
        return handler._send({"Result": {"EntityResults": EG_ROWS if body["PageNumber"] == 1 else []}})
    if "/permits/" in path:
        cid = path.rsplit("/", 1)[1]
        return handler._send({"Result": EG["kyle_detail"] if cid == EG["kyle_detail"]["PermitId"] else {"Value": 0}})
    if path.endswith("/query"):   # parcel layer
        hit = EG["kyle_parcel"] if str(EG["kyle_parcel"]["PID"]) in q.get("where", "") else None
        return handler._send({"features": [{"attributes": hit}] if hit else []})

# Cabarrus Accela Citizen Access: real pages saved from the live portal (Oct 2026),
# trimmed of scripts and view state.
FIX = Path(__file__).parent / "fixtures"
ACA_SEARCH = (FIX / "cabarrus_search.html").read_text()
ACA_RESULTS = (FIX / "cabarrus_results.html").read_text()
ACA_DETAIL = (FIX / "cabarrus_detail.html").read_text()   # BU2026-03307, Shallow Bay flex warehouse
ACA_LAST = re.sub(r"<a[^>]*>Next &gt;</a>", "", ACA_RESULTS)


def accela_route(handler, path, q, form):
    handler.send_response(200)
    handler.end_headers()
    if "CapDetail" in path:
        page = ACA_DETAIL if q.get("capID3") == "02802" else "<html>Project Description: Small job More Details</html>"
    elif form is None:
        page = ACA_SEARCH
    else:
        assert handler.headers.get("Referer") and handler.headers.get("Origin"), "portal's CSRF check"
        target = form.get("__EVENTTARGET", "")
        if target.endswith("btnNewSearch"):
            assert form["ctl00$PlaceHolderMain$ddlSearchType"] == "0"
            # Only one permit type has results here, so the 10-row page isn't counted twice.
            page = ACA_RESULTS if form["ctl00$PlaceHolderMain$generalSearchForm$ddlGSPermitType"].endswith("/New") \
                else ACA_LAST.replace("ACA_TabRow_", "x_")
        else:
            page = ACA_LAST.replace("ACA_TabRow_", "x_")   # page 2: no further rows
    handler.wfile.write(page.encode())


def fields(rows, date_field):
    return [{"name": k, "type": "esriFieldTypeDate" if k == date_field else
             ("esriFieldTypeOID" if k.lower() == "objectid" else "esriFieldTypeString")} for k in rows[0]]


LAYERS = {
    "/meck/0": (MECK, "issuedate"),
    "/gaston/2": (GASTON, "DATE"),
    "/cab/MapServer/33": ([meck(99, 3000, "S1", "old", 1)], "issuedate"),
    "/cab/MapServer/41": (CABARRUS_2026, "issuedate"),
    "/union/ok/0": (UNION_OK, "inspection_date"),
    "/rowan/6": (ROWAN, "dIssued"),
    "/gaston/rez/0": (GASTON_REZ, "DATE"),
    "/rowan/zoning/18": (ROWAN_ZONING, "created_date"),
    "/iredell/hearings/0": (IREDELL_HEARINGS, "no-date-field"),
    "/clt/rez/0": (CLT_REZ, "Received"),
    "/union/not/6": (UNION_NOT, "inspection_date"),
    "/stale/MapServer/33": ([meck(98, 3000, "S1", "old", 1)], "issuedate"),
}


def adzuna_results(where, what):
    if "forklift" not in what:
        return []
    base = lambda i, co, city, county, title, desc="": {
        "id": f"{co}-{i}", "title": title, "description": desc, "created": "2026-10-28T10:00:00Z",
        "redirect_url": f"https://example.test/{co}/{i}", "company": {"display_name": co},
        "location": {"display_name": f"{city}, NC", "area": ["US", "North Carolina", f"{county} County", city]}}
    if where.startswith("Gastonia"):
        return [base(i, "Acme Packaging LLC", "Gastonia", "Gaston", "Forklift Operator - 2nd shift",
                     "Join the launch team at our new facility") for i in range(5)]
    if where.startswith("Charlotte"):
        return ([base(i, "Staffmark", "Charlotte", "Mecklenburg", "Forklift Operator") for i in range(4)] +
                [base(i, "Walmart", "Charlotte", "Mecklenburg", "Forklift Associate") for i in range(3)] +
                [base(9, "Solo Co", "Charlotte", "Mecklenburg", "Forklift Operator")] +
                [base(i, "Bank Co", "Charlotte", "Mecklenburg", "Distribution Analyst") for i in range(5)])
    return []


def serp_results(q):
    """Two pages for Gastonia warehouse searches, nothing elsewhere."""
    if not (q["location"].startswith("Gastonia") and "warehouse" in q["q"]):
        return {"error": "Google hasn't returned any results for this query."}
    job = lambda i, co, title, posted, loc="Gastonia, NC": {
        "job_id": f"{co}{i}", "title": title, "company_name": co, "location": loc,
        "via": "Indeed", "description": "Now hiring for our new facility, 2nd shift",
        "detected_extensions": {"posted_at": posted},
        "share_link": f"https://example.test/{co}/{i}"}
    if "next_page_token" not in q:
        return {"jobs_results": [job(i, "Acme Packaging", "Forklift Operator", "2 days ago") for i in range(3)]
                + [job(9, "Old Co", "Forklift Operator", "3 weeks ago")],
                "serpapi_pagination": {"next_page_token": "p2"}}
    return {"jobs_results": [job(3, "Acme Packaging", "Order Picker", "5 days ago",
                                 "Gastonia, NC (+2 others)"),
                             job(4, "Acme Packaging", "HR Generalist", "1 day ago")]}


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body):
        b = json.dumps(body).encode()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path.startswith("/energov/"):
            return energov_route(self, u.path, dict(urllib.parse.parse_qsl(u.query)), None)
        if u.path.startswith("/aca/") or "CapDetail" in u.path:
            return accela_route(self, u.path, dict(urllib.parse.parse_qsl(u.query)), None)
        self.route(u.path, dict(urllib.parse.parse_qsl(u.query)))

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"])).decode()
        if self.path.startswith("/energov/"):
            return energov_route(self, self.path, {}, json.loads(body))
        if self.path.startswith("/aca/"):
            return accela_route(self, urllib.parse.urlparse(self.path).path, {}, dict(urllib.parse.parse_qsl(body)))
        self.route(self.path, dict(urllib.parse.parse_qsl(body)))

    def route(self, path, q):
        if path == "/serp":
            assert q["engine"] == "google_jobs"
            return self._send(serp_results(q))
        if path.startswith("/adzuna/"):
            assert "what" not in q, "one combined what_or search per county"
            return self._send({"results": adzuna_results(q["where"], q["what_or"])})
        if path == "/stale/MapServer":
            return self._send({"layers": [{"id": 33, "name": "Permits 2015"}]})
        if path == "/cab/MapServer":
            return self._send({"layers": [{"id": 33, "name": "Permits 2015"},
                                          {"id": 41, "name": "Permits 2026"},
                                          {"id": 5, "name": "Parcels"}]})
        layer = path[:-len("/query")] if path.endswith("/query") else path
        rows, date_f = LAYERS[layer]
        oid = next(k for k in rows[0] if k.lower() == "objectid")
        if not path.endswith("/query"):
            # Mecklenburg's real FeatureServer pages with resultOffset; the
            # others exercise pyesridump's object-ID-range path.
            return self._send({"name": layer, "maxRecordCount": 2, "fields": fields(rows, date_f),
                               "supportsPagination": layer == "/meck/0"})
        if "objectIds" in q:  # our fallback batch fetch
            want = set(map(int, q["objectIds"].split(",")))
            return self._send({"features": [{"attributes": r} for r in rows if r[oid] in want]})
        hits = rows
        where = q.get("where", "1=1")
        m = re.search(r"DATE '(\d{4}-\d\d-\d\d)'", where)
        if m:
            cut = dt.datetime.strptime(m.group(1), "%Y-%m-%d").timestamp() * 1000
            hits = [r for r in hits if r[date_f] >= cut]
        elif where not in ("1=1",) and not re.search(rf"{oid} >= \d+", where):
            return self._send({"error": {"code": 400, "message": "Unable to complete operation."}})
        m = re.search(rf"{oid} >= (\d+) AND {oid} <= (\d+)", where)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            hits = [r for r in hits if lo <= r[oid] <= hi]
        if q.get("returnCountOnly") == "true":
            return self._send({"count": len(hits)})
        if q.get("returnIdsOnly") == "true":
            return self._send({"objectIdFieldName": oid, "objectIds": [r[oid] for r in hits]})
        if "resultOffset" in q:
            off, n = int(q["resultOffset"]), int(q["resultRecordCount"])
            hits = hits[off:off + n]
        return self._send({"features": [{"attributes": r} for r in hits]})


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{cls.srv.server_port}"
        config.ARCGIS_SOURCES = [
            {"county": "Mecklenburg", "kind": "permits", "days": 30, "url": base + "/meck/0"},
            {"county": "Gaston", "kind": "planning", "days": 3650, "url": base + "/gaston/2"},
            {"county": "Cabarrus", "kind": "permits", "days": 30,
             "discover": {"service": base + "/cab/MapServer", "name": r"^permits\b"}},
            {"county": "Rowan", "kind": "permits", "days": 45, "url": base + "/rowan/6",
             "type_rx": r"commercial|\bCOM-", "min_score": 2},
            {"county": "Rowan", "kind": "planning", "days": 120, "url": base + "/rowan/zoning/18"},
            {"county": "Gaston", "kind": "planning", "days": 3650, "url": base + "/gaston/rez/0"},
            {"county": "Iredell", "kind": "planning", "days": 365, "url": base + "/iredell/hearings/0"},
            {"county": "Mecklenburg", "kind": "planning", "days": 365, "url": base + "/clt/rez/0",
             "fields": {"permit_no": "Petition", "issue_date": "Received", "zoning": "ReqZone",
                        "desc": ["Petitioner", "Propluse"], "type": None, "contractor": None}},
            {"county": "Stale", "kind": "permits", "days": 30,
             "discover": {"service": base + "/stale/MapServer", "name": r"^permits\b"}},
        ]
        config.ENERGOV_SOURCES = [{"county": "Gaston", "days": 21, "tenant_id": 1, "tenant_name": "Gaston County, NC",
                                   "api": base + "/energov/api",
                                   "parcels": {"url": base + "/energov/parcels/11", "fields": "gaston"}}]
        energov.PAUSE = accela.PAUSE = 0
        config.ACCELA_SOURCES = [{"county": "Cabarrus", "days": 21, "base": base + "/aca/CABARRUS",
                                  "types": ["Permits/Building/Commercial/New", "Permits/Building/Commercial/Upfit"]}]
        config.INSPECTION_SOURCES = [{"county": "Union", "days": 120,
                                      "urls": [base + "/union/ok/0", base + "/union/not/6"]}]
        jobs.API = base + "/adzuna/{page}"
        os.environ["ADZUNA_APP_ID"] = os.environ["ADZUNA_APP_KEY"] = "test"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "inbox").mkdir()
        run_weekly.ROOT, run_weekly.STATE, run_weekly.INBOX = (
            self.tmp, self.tmp / "data" / "seen.json", self.tmp / "inbox")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_once(self):
        import sys
        sys.argv = ["run_weekly.py"]
        run_weekly.main()
        return (self.tmp / "output" / "latest-digest.md").read_text()

    def test_first_run_finds_real_signals_only(self):
        d = self.run_once()
        # Permits: the two real industrial ones plus Cabarrus' newest yearly layer.
        for good in ("Owner 1", "Owner 2", "Owner 10"):
            self.assertIn(good, d)
        for junk in ("Owner 3", "Owner 4", "Owner 5", "Owner 6", "Owner 99"):
            self.assertNotIn(junk, d)
        self.assertIn("Permits 2026", d)
        self.assertIn('newest published layer is "Permits 2015"', d)
        # Planning: industrial yes, subdivision no.
        self.assertIn("FAIRVIEW INDUSTRIAL", d)
        self.assertNotIn("LOWELL WOODS", d)
        # Rowan: big commercial job, split address joined; small upfit, trades, typo dates dropped.
        self.assertIn("| Rowan | 101 UNITY CHURCH RD | ", d)
        self.assertIn("120000", (self.tmp / "output" / dt.date.today().isoformat() / "permits.csv").read_text())
        for junk in ("Small GC", "Sparky", "Typo Date", "Roofer Co", "102 UNITY", "103 UNITY", "104 UNITY"):
            self.assertNotIn(junk, d)
        self.assertIn("types seen: Commercial 3, Electrical 1", d)
        # Rowan rezonings: industrial case once (not once per parcel); residential dropped.
        self.assertEqual(d.count("Z 07-26"), 1)
        self.assertNotIn("Z 08-26", d)
        self.assertNotIn("Z 05-26", d)   # administrative boundary change
        # Gaston rezonings: conditional industrial zoning recognized, residential dropped.
        self.assertIn("REZ-26-01", d)
        self.assertNotIn("REZ-26-02", d)
        # Iredell hearings: recent industrial rezoning in, 2021 hearing out (text dates parsed).
        self.assertIn("Case: 2610-1", d)
        self.assertIn("Encased Power", d)
        self.assertNotIn("Case: 2102-1", d)
        # Charlotte rezonings: only requests into industrial zoning; away-from-industrial
        # and residential petitions dropped. Requested zoning shown.
        self.assertIn("2026-081: Crossroads Logistics LLC", d)
        self.assertIn("→ ML-1(CD)", d)
        self.assertNotIn("2026-076", d)
        self.assertNotIn("2026-077", d)
        # Gaston live permits: spec warehouse upfit in, with parcel owner and building facts;
        # drone docks, cell sites and residential out.
        self.assertIn("| Gaston | 1910 KYLE COURT GASTONIA NC 28052 | KYLE COURT LLC | $250,000 |", d)
        self.assertIn("Distribution Warehouse; 54,000 SF; built 1999", d)
        self.assertIn("sold 11/2016 $1,495,000", d)
        for junk in ("BLDC-26-10-05-03160", "MARTIN LUTHER KING", "4920 YORK", "840 MYRTLE"):
            self.assertNotIn(junk, d)
        self.assertIn("| Gaston permits (live portal) | 🟢 5 permits, 4 commercial, 1 industrial, 1 new |", d)
        self.assertNotIn("Gaston permits (portal)", d)
        self.assertNotIn("Iredell permits (portal)", d)
        # Cabarrus live permits: spec flex warehouse in with owner, contractor, cost and SF from
        # the detail page; Building B (flex warehouse) in too; schools, EV chargers, shelters out.
        self.assertIn("| Cabarrus | 5542 LIPPARD LN, AC, HARRISBURG NC 28075 | LIPPARD LANE OWNER LLC | $4,393,440 |", d)
        self.assertIn("S-1 Storage (Moderate Hazard)", d)
        for junk in ("RICELAND", "GRACES RESERVE", "IRON HORSE", "SUDBURY"):
            self.assertNotIn(junk, d)
        self.assertIn("| Cabarrus permits (live portal) | 🟢 10 permits, 10 commercial, 2 industrial, 2 new |", d)
        # Union inspections: commercial jobs only, merged across layers, final flagged.
        self.assertIn("| 🏁 **final** | Union | 9509 Morgan Mill Rd Monroe |", d)
        self.assertIn("| under construction | Union | 100 Industrial Dr Monroe |", d)
        self.assertIn("Comm Plumbing Rough In", d)        # merged from the second layer
        self.assertNotIn("Dusty Ln", d)                   # residential
        self.assertNotIn("Old Job Rd", d)                 # older than the window
        # Jobs: real cluster ranked first with its flags; staffing flagged; singletons dropped.
        self.assertIn("Acme Packaging", d)
        self.assertIn("new facility", d)
        self.assertIn("staffing — find the employer", d)
        self.assertNotIn("Solo Co", d)
        self.assertNotIn("Bank Co", d)  # office roles dropped by the title filter
        self.assertLess(d.index("Acme Packaging"), d.index("Staffmark"))

    def test_second_run_reports_nothing_new(self):
        self.run_once()
        d = self.run_once()
        self.assertIn("**0 new signals.**", d)

    def test_inbox_export_is_scored_and_archived(self):
        (self.tmp / "inbox" / "union_export.csv").write_text(
            "Permit Number,Type,Issued Date,Address,Description,Valuation,Owner\n"
            f"U-1,Commercial Alteration,{dt.date.today():%m/%d/%Y},9 Industrial Dr Monroe,"
            "Install pallet racking and dock levelers,\"$500,000\",Monroe Mfg\n")
        d = self.run_once()
        self.assertIn("Monroe Mfg", d)
        self.assertIn("| Union | 9 Industrial Dr Monroe |", d)
        self.assertFalse(list((self.tmp / "inbox").glob("*.csv")))


if __name__ == "__main__":
    unittest.main()


class SerpApiProvider(EndToEnd):
    """Same pipeline with the free Google Jobs provider instead of Adzuna."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        jobs.SERPAPI = f"http://127.0.0.1:{cls.srv.server_port}/serp"
        os.environ["SERPAPI_API_KEY"] = "test"

    @classmethod
    def tearDownClass(cls):
        os.environ.pop("SERPAPI_API_KEY", None)
        super().tearDownClass()

    def test_first_run_finds_real_signals_only(self):
        d = self.run_once()
        self.assertIn("Acme Packaging", d)
        self.assertIn("| Gastonia, Gaston | [4]", d)   # 3 + page-2 picker; HR role dropped
        self.assertIn("new facility", d)
        self.assertNotIn("Old Co", d)                  # older than 7 days
        self.assertIn("FAIRVIEW INDUSTRIAL", d)

    test_inbox_export_is_scored_and_archived = None
