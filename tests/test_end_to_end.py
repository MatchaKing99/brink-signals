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
from signals import config, jobs, permits

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


def fields(rows, date_field):
    return [{"name": k, "type": "esriFieldTypeDate" if k == date_field else
             ("esriFieldTypeOID" if k.lower() == "objectid" else "esriFieldTypeString")} for k in rows[0]]


LAYERS = {
    "/meck/0": (MECK, "issuedate"),
    "/gaston/2": (GASTON, "DATE"),
    "/cab/MapServer/33": ([meck(99, 3000, "S1", "old", 1)], "issuedate"),
    "/cab/MapServer/41": (CABARRUS_2026, "issuedate"),
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
                [base(9, "Solo Co", "Charlotte", "Mecklenburg", "Forklift Operator")])
    return []


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
        self.route(u.path, dict(urllib.parse.parse_qsl(u.query)))

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"])).decode()
        self.route(self.path, dict(urllib.parse.parse_qsl(body)))

    def route(self, path, q):
        if path.startswith("/adzuna/"):
            return self._send({"results": adzuna_results(q["where"], q["what"])})
        if path == "/cab/MapServer":
            return self._send({"layers": [{"id": 33, "name": "Permits 2015"},
                                          {"id": 41, "name": "Permits 2026"},
                                          {"id": 5, "name": "Parcels"}]})
        layer = path[:-len("/query")] if path.endswith("/query") else path
        rows, date_f = LAYERS[layer]
        if not path.endswith("/query"):
            return self._send({"name": layer, "maxRecordCount": 2, "fields": fields(rows, date_f)})
        if "objectIds" in q:
            want = set(map(int, q["objectIds"].split(",")))
            assert len(want) <= 2, "batching must respect maxRecordCount"
            oid = next(k for k in rows[0] if k.lower() == "objectid")
            return self._send({"features": [{"attributes": r} for r in rows if r[oid] in want]})
        m = re.search(r"DATE '(\d{4}-\d\d-\d\d)'", q["where"])
        oid = next(k for k in rows[0] if k.lower() == "objectid")
        if m:
            cut = dt.datetime.strptime(m.group(1), "%Y-%m-%d").timestamp() * 1000
            ids = [r[oid] for r in rows if r[date_f] >= cut]
        else:
            ids = [r[oid] for r in rows]
        return self._send({"objectIdFieldName": oid, "objectIds": ids})


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
        ]
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
        # Planning: industrial yes, subdivision no.
        self.assertIn("FAIRVIEW INDUSTRIAL", d)
        self.assertNotIn("LOWELL WOODS", d)
        # Jobs: real cluster ranked first with its flags; staffing flagged; singletons dropped.
        self.assertIn("Acme Packaging", d)
        self.assertIn("new facility", d)
        self.assertIn("staffing — find the employer", d)
        self.assertNotIn("Solo Co", d)
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
