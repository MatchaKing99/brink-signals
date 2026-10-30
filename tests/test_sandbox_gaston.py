"""
Sandbox Gaston permit pull against a local fake EnerGov + parcel server, using
real records saved from the county's portal (Oct 2026).

  python3 -m unittest discover tests
"""
import datetime as dt
import http.server
import json
import threading
import unittest
import urllib.parse
from pathlib import Path

from sandbox import gaston_permits as g

FIX = json.loads((Path(__file__).parent / "fixtures" / "gaston_energov.json").read_text())
TODAY = dt.date.today().isoformat()
ROWS = [dict(r, IssueDate=f"{TODAY}T00:00:00") for r in FIX["rows"]]
OLD = dict(FIX["rows"][0], CaseNumber="OLD-1", IssueDate="2001-01-01T00:00:00")


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
        if u.path.endswith("/search/criteria"):
            return self._send({"Result": FIX["criteria"]})
        if "/permits/" in u.path:
            cid = u.path.rsplit("/", 1)[1]
            if cid == FIX["kyle_detail"]["PermitId"]:
                return self._send({"Result": FIX["kyle_detail"]})
            return self._send({"Result": {"Value": 0}})
        if u.path.endswith("/query"):
            where = dict(urllib.parse.parse_qsl(u.query))["where"]
            hit = FIX["kyle_parcel"] if str(FIX["kyle_parcel"]["PID"]) in where else None
            return self._send({"features": [{"attributes": hit}] if hit else []})
        self.send_error(404)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        assert self.headers["tenantId"] == "1"
        assert body["SearchModule"] == 1 and body["FilterModule"] == 2 and body["SortBy"] == "IssueDate"
        page = body["PageNumber"]
        self._send({"Result": {"EntityResults": ROWS if page == 1 else [OLD] if page == 2 else []}})


class SandboxGaston(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{cls.srv.server_port}"
        g.API, g.PARCELS, g.PAUSE = base + "/api/energov", base + "/parcels/11", 0

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def test_pull_enrich_and_flag(self):
        rows = g.recent_permits(30)
        self.assertNotIn("OLD-1", [r["CaseNumber"] for r in rows])   # paging stops at the cutoff
        items = {i["permit_no"]: i for i in g.build(rows)}
        self.assertNotIn("BLDR-26-06-23-21519", items)               # residential never considered
        kyle = items["BLDC-26-08-24-03100"]
        self.assertTrue(kyle["industrial"])
        self.assertEqual(kyle["owner"], "KYLE COURT LLC")
        self.assertEqual(kyle["value"], 250000)
        self.assertEqual(kyle["building_sf"], 54000)
        self.assertIn("11/2016 for $1,495,000", kyle["last_sale"])
        self.assertFalse(items["BLDC-26-10-05-03160"]["industrial"])  # drone "docking stations"
        self.assertFalse(items["ZONC-26-08-31-00240"]["industrial"])  # Verizon cell site
        self.assertFalse(items["BLDC-26-10-14-03178"]["industrial"])  # coffee-stand retaining wall
        rep = g.report(list(items.values()), len(rows), 30)
        self.assertIn("## 1910 KYLE COURT GASTONIA NC 28052", rep)
        self.assertIn("Distribution Warehouse, 54,000 SF, built 1999", rep)


if __name__ == "__main__":
    unittest.main()
