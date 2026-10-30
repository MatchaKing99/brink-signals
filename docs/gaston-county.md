# Gaston County: How to Pull Permits

> **In brink-signals:** the developments layer is pulled automatically every Monday. For permits, save the Citizen Self Service export as `gaston_<date>.csv` and upload it to `inbox/`. The `pull_permits.py` commands below are from the standalone version and still work the same way.

Gaston works differently from Mecklenburg. There's no open permit dataset to pull from. There are **two sources**, and together they give you an earlier and a later signal.

| Source | What it shows | Timing | How it gets in |
|---|---|---|---|
| **A. Developments map layer** (county GIS) | Proposed and approved developments | **Early**: site plans, months before a building permit | Pulled live by the script |
| **B. Citizen Self Service permit search** | Actual building permits | Later: the build-out or upfit | You export a CSV and the script scores it |

**Good news on coverage:** Gaston County does building plan review and permits for most of the county, including towns like Belmont, and Gastonia sends its permits to the county ([Jaspector](https://www.jaspector.com/permits/north-carolina/gaston/gastonia), [Gastonia](https://gastonianc.gov/doing-business/permits-inspections)). So one portal covers nearly the whole county. Zoning approvals still happen at each town, and those are an even earlier signal if you ever want to go further.

---

## A. Developments (early signal) — run monthly

The county publishes a GIS layer of **"Proposed and Approved Developments within Gaston County"** with data from each municipality. A new industrial park or warehouse showing up here means a building is coming. That's a landlord rep conversation (who's leasing it?) and a heads-up for your material handling partners.

```bash
python3 pull_permits.py --source gaston-dev --inspect     # first time: check fields
python3 pull_permits.py --source gaston-dev --days 180
```

- If `--inspect` says "No fields returned", it lists the layers on that service. Re-run with `--url` ending in the right layer number. The service root is `https://gis.gastoncountync.gov/publicgis/rest/services/PublicGIS/Developments/FeatureServer`.
- If the layer has no date field, the script pulls every record. That's fine because the development list is small. Sort by Score in Airtable.

**Terms of use:** the county's GIS metadata says the data can't be resold or used for commercial trade under NCGS 132-10. Using it for your own prospecting is normal. **Don't resell it, or package and hand the raw county export to partners as a product.** Share your own researched insights ("I'm seeing X industrial projects in Gaston"), not the data dump.

---

## B. Building permits (via Citizen Self Service) — weekly

Gaston's permit system is **Tyler EnerGov "Citizen Self Service."** Get there from the Gaston County Building Inspections website by clicking the *Citizen Self Service* tab. Applying needs an account. Searching usually doesn't, but if Gaston requires a login, create a free account.

**Weekly, about 5 minutes:**
1. Open Citizen Self Service → **Search** → set the search to **Permit**.
2. Open **Advanced** search. Set **Issued Date** from last Monday to today. If there's a Permit Type filter, choose the commercial types; otherwise leave it on all.
3. Run the search. Click **Export** (most EnerGov portals have an Export to Excel button above the results).
4. Open the file in Excel → **File → Save As → CSV UTF-8**. Name it something like `gaston_2026-11-02.csv`.
5. Score it:
   ```bash
   python3 pull_permits.py --from-file gaston_2026-11-02.csv --county Gaston --days 7
   ```
   The first time, run it with `--inspect` to confirm the columns matched.
6. Import the output `permits_gaston_<date>.csv` into the Airtable **Permits** table, the same as Mecklenburg.

**If there's no Export button:** select the results table, copy it, paste it into Excel, and save as CSV. The script maps the column names automatically (Permit Number, Type, Issued Date, Address, Description, Valuation and so on).

---

## What's verified and what isn't

- ✅ The script's Gaston handling (the developments layer, plus scoring CSV exports with typical EnerGov column names) passed tests on sample data.
- ⚠️ My cloud sandbox **can't reach Gaston's servers**, so I haven't seen the live field names, the developments layer number, or whether the portal has an Export button. Run the `--inspect` commands once on your Mac and send me the output. Any fix should be a single line.
- 🔜 **Fully automatic Gaston permit pulls** (no weekly export) are possible. EnerGov portals have a behind-the-scenes search API, but I need to see the live portal to build it reliably. If you connect your Mac to this session through Remote Control (Claude desktop app → Settings → Claude Code → Remote Control, then add the folder you saved this project in), I can test against Gaston's live site from there and automate it.
