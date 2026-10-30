"""
Sandbox EnerGov pipeline against a local fake portal + parcel server that
replays real Gaston County responses saved in Oct 2026 (tests/fixtures/energov,
contact emails and phones removed).

  python3 -m unittest discover tests
"""
import datetime as dt
import http.server
import json
import tempfile
import threading
import unittest
import urllib.parse
from pathlib import Path

from sandbox import energov, run_sandbox

FIX = Path(__file__).parent / "fixtures" / "energov"
CRITERIA = json.loads((FIX / "criteria.json").read_text())
SEARCH = json.loads((FIX / "search.json").read_text())
PERMITS = json.loads((FIX / "permits.json").read_text())
PARCELS = json.loads((FIX / "parcels.json").read_text())
TODAY = dt.date(2026, 10, 30)


class Portal(http.server.BaseHTTPRequestHandler):
    searches = []

    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.headers.get("tenantId") != "1":
            return self._send({"Message": "An error has occurred."}, 500)
        path = urllib.parse.urlparse(self.path).path
        if path.endswith("/api/energov/search/criteria"):
            return self._send(CRITERIA)
        if "/api/energov/permits/permit/" in path:
            cid = path.rsplit("/", 1)[1]
            return self._send(PERMITS[cid]) if cid in PERMITS else self._send({"Success": False}, 404)
        self._send({}, 404)

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"])).decode()
        path = urllib.parse.urlparse(self.path).path
        if path.endswith("/api/energov/search/search"):
            c = json.loads(body)
            Portal.searches.append(c)
            # Like the live server: null type/status ids are a 500.
            if c["PermitCriteria"]["PermitTypeId"] is None or c["SearchModule"] != 2:
                return self._send({"Message": "An error has occurred."}, 500)
            if c["PageNumber"] > 1:
                return self._send({**SEARCH, "Result": {**SEARCH["Result"], "EntityResults": []}})
            return self._send(SEARCH)
        if path.endswith("/FeatureServer/11/query"):
            where = urllib.parse.parse_qs(body)["where"][0]
            ids = set(where[where.index("(") + 1:-1].replace("'", "").split(","))
            feats = [f for f in PARCELS["features"] if f["attributes"]["AKPAR"] in ids]
            return self._send({**PARCELS, "features": feats})
        self._send({}, 404)


class SandboxEnerGovTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Portal)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.srv.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def test_standardize_real_detail(self):
        row = next(r for r in SEARCH["Result"]["EntityResults"] if r["CaseNumber"] == "BLDC-26-10-28-03193")
        rec = energov.standardize(row, PERMITS[row["CaseId"]]["Result"])
        self.assertEqual(rec["value"], 96100.0)
        self.assertEqual(rec["sqft"], 550.0)                 # from the Total Building Area custom field
        self.assertEqual(rec["occupancy"], "S-2 Storage")    # resolved from the pick list
        self.assertEqual(rec["contractor"], "Pinnix General Con")
        self.assertEqual(rec["issue_date"], "2026-10-30")
        self.assertTrue(energov.is_commercial(row) and energov.is_primary(row))

    def test_type_classes(self):
        types = {r["CaseNumber"]: r for r in SEARCH["Result"]["EntityResults"]}
        self.assertFalse(energov.is_commercial(types["BLDR-26-06-23-21519"]))   # single-family home
        self.assertFalse(energov.is_commercial(types["EC-26-10-13-02032"]))     # residential erosion
        self.assertTrue(energov.is_commercial(types["EC-26-10-23-02051"]))      # industrial erosion
        self.assertTrue(energov.is_commercial(types["HCOC-26-10-22-0723"]))

    def test_end_to_end(self):
        Portal.searches.clear()
        with tempfile.TemporaryDirectory() as tmp:
            stats, industrial, problems = run_sandbox.run(
                base=self.base + "/energov_prod/selfservice",
                parcels_url=self.base + "/FeatureServer/11", days=60, out_dir=tmp, delay=0,
                sos_url=None, seen_path=Path(tmp) / "none.json", today=TODAY, log=lambda *a: None)
            report = (Path(tmp) / "report.md").read_text()
            csv_text = (Path(tmp) / "permits.csv").read_text()
        # Two searches (issued + applied), each with the date filter the portal honours.
        self.assertEqual(len(Portal.searches), 2)
        pc = [s["PermitCriteria"] for s in Portal.searches]
        self.assertEqual(pc[0]["IssueDateFrom"], "2026-08-31T00:00:00")
        self.assertEqual(pc[1]["ApplyDateTo"], "2026-10-30T23:59:59")
        self.assertEqual(stats["pulled"], 5)        # same rows from both searches, de-duplicated
        self.assertEqual(stats["commercial"], 3)
        self.assertEqual(stats["details"], 3)
        self.assertEqual(stats["parcels_matched"], 3)
        self.assertEqual(problems, [])
        # The 408 Brook St erosion permit is on an industrial parcel; the S-2 remodel is tagged but small.
        self.assertIn("SSI 408 BROOK NC PROPERTY LLC", report)
        self.assertIn("Industrial land use, 6.14 ac", report)
        self.assertIn("BLDC-26-10-28-03193", report)
        self.assertIn("Your move", report)
        self.assertIn("EC-26-10-23-02051", csv_text)
        self.assertNotIn("BLDR-26-06-23-21519", csv_text)


if __name__ == "__main__":
    unittest.main()
