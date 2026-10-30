# Sandbox: permit-aggregator method on one county (Gaston, Tyler EnerGov)

Proves the chain before it goes into the live bot:

vendor connector → standard record → industrial tagging (`signals.permits.score` / `is_industrial`, imported unchanged) → parcel and owner match → LLC flag → report with a suggested move.

```bash
python3 -m sandbox.run_sandbox                 # last 60 days → sandbox/output/report.md, permits.csv
python3 -m sandbox.run_sandbox --days 14 --max-details 50
```

The GitHub workflow **Sandbox permits (Gaston EnerGov)** runs the same thing manually (Actions tab → Run workflow). It uploads `sandbox/output/` as an artifact and never commits, never writes `data/seen.json`, and never opens issues.

## What the Gaston portal actually does (checked live Oct 30, 2026)

- Portal: `https://selfservice.gastongov.com/energov_prod/selfservice` (linked from gastongov.com as "Citizen's Self Service"). Search and permit detail are public. No login or CAPTCHA.
- Every API call needs the headers `tenantId: 1` and `Tyler-TenantUrl: home`.
- `GET api/energov/search/criteria` returns the blank search model. Fill `PermitCriteria` and `POST api/energov/search/search`.
  - The date filters only work with `SearchModule: 2, FilterModule: 2`.
  - `PermitTypeId` and `PermitStatusId` must be the string `"none"`. A null makes the server return 500.
  - Page size 100 works. The response has `TotalPages`, `PermitsFound` and `EntityResults[]`, where each row has `CaseNumber`, `CaseType`, `CaseWorkclass`, `CaseStatus`, `IssueDate`, `ApplyDate`, `AddressDisplay`, `MainParcel` and `Description`.
- `GET api/energov/permits/permit/{CaseId}` returns `ValuationValue`, `SquareFeet` (usually 0), `Contacts[]` (owner, GC, applicant, trades) and `CustomFields[]`. The custom fields hold Total Building Area, the occupancy group (e.g. "S-1 Storage") and the construction type, plus project name and acreage on erosion permits. Pick-list values are GUIDs that resolve through each field's `PickListItems`.
- `MainParcel` is the county GIS `AKPAR`/`PID`, not the dashed PIN. The parcels layer is `PublicGIS/Parcels/FeatureServer/11`.
- The NC Secretary of State business search (sosnc.gov) answers 403 with a Cloudflare "Just a moment..." bot challenge. LLCs are listed for a manual lookup and are never scraped.
- The proxy or portal sometimes drops a TLS connection mid-request. The client retries with backoff.

## Files

- `energov.py`: the connector. It's generic Tyler EnerGov CSS. Only the base URL, tenant and type-name rules are Gaston-specific.
- `parcels.py`: Gaston parcel lookup and LLC detection.
- `run_sandbox.py`: the pipeline and report.
- `../tests/test_sandbox_energov.py`: replays saved real responses (`tests/fixtures/energov/`) from a local fake server.
