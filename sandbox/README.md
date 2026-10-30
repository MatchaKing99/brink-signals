# Sandbox: live Gaston permits

A test of the permit-aggregator method on one county before anything touches
the weekly bot. **Not wired into `run_weekly.py`**; nothing here writes to
`data/seen.json` or the weekly digest.

| Step | How |
|---|---|
| Collect | Gaston's public Tyler EnerGov Citizen Self Service API (`selfservice.gastongov.com`). The search ignores date filters, so the script sorts by issue date and pages back to the cutoff. |
| Filter | Commercial / industrial / shell permit types; trade-only, sign and cell-site permits dropped |
| Detail | Each permit's public detail record (full description, valuation) |
| Enrich | Gaston parcel layer by parcel ID: owner and mailing address, land use, building SF, year built, acres, last sale |
| Flag | Shared keyword scoring plus "industrial property" from the parcel's land use |

Contacts (applicant, contractor) are private on this portal, so owners come
from the public parcel records. The run rate-limits itself (1s between calls).

```bash
python3 sandbox/gaston_permits.py 30     # last 30 days -> sandbox/output/report.md
```

Or Actions → **Sandbox – Gaston permits** → Run workflow; the report is
attached to the run as an artifact.
