# Permit Tracker: Airtable Setup

One new base (or three new tables in your existing Leads base): **Partners**, **Permits**, **Operators**. Setup takes about 15 minutes.

---

## Step 1: Create the tables from the CSVs

In Airtable: **Add or import → CSV file** for each file:

| Import this file | As table | Then change these field types |
|---|---|---|
| `airtable_partners.csv` | **Partners** | Type, Priority, Stage → *Single select* · Phone → *Phone* · Email → *Email* · Source URL → *URL* |
| `airtable_permits_template.csv` (or your first `permits_*.csv`) | **Permits** | Issued → *Date* · County, Status → *Single select* · Value → *Currency* · Sq Ft, Score → *Number* |

Partners comes pre-loaded with the 11 material handling companies from the outreach kit.

## Step 2: Add the linking fields

**Permits** table, add:
- `Operator` → *Link to Operators*. This is the actual company using the space, which isn't always the permit owner.
- `Shared With` → *Link to Partners*. Tracks which reps got this permit, so you can show what you've given them.
- `Old Address` → *Single line text*. Where the operator is moving from. That's your backfill and landlord lead.
- `Notes` → *Long text*

**Status** single-select options: `New → Researching → Operator ID'd → Contacted → Shared w/ Partner → Dead`

**Operators** table (create blank):
`Company` · `Industry` · `Current Address` · `Previous Address` · `Est. SF` · `Lease Exp (est.)` · `Contact` · `Phone` · `Email` · `Permits` (link) · `Referred By` (link to Partners) · `Next Touch` (date) · `Notes`

**Partners** table, add:
`Referrals Received` (link to Operators) · `Permits Shared` (link to Permits) · `Last Touch` (date) · `Next Touch` (date)

## Step 3: Views that do the work

**Permits**
- **🔥 Hot this week**: Score ≥ 6, Issued in the last 7 days, sort by Score descending.
- **Needs operator**: Status = New or Researching.
- **By county**: grouped by County, for building each partner's territory sheet.

**Partners**
- **Pipeline**: Kanban by Stage. Stages: `Not contacted → Emailed → Meeting set → Swap active → Dormant`.

**Operators**
- **Due to touch**: Next Touch ≤ today. This is your nurture list of companies growing now that will need space again in 2–4 years.

## Step 4: Weekly routine (about 30 minutes, Monday morning)

1. Run `python3 pull_permits.py --days 7` on your laptop.
2. Import the CSV into **Permits** (Import → CSV → *append to existing table*). Sort by Score. Ignore anything under 4 unless the address is one you know.
3. For the top 5–10, identify the operator. Look the address up on Mecklenburg Polaris (parcel owner), check Google Maps signage, and enrich in Apollo. Move them to **Operators**.
4. **Look for the old address.** If the operator was somewhere else before, that building is about to have a vacancy. Call that landlord.
5. Email each active partner their territory's hot list. Tick **Shared With**.

## Step 5 (later): automate with Make

Once the weekly routine is proven, put the script on a schedule and have Make pick up the CSV:
- **Scheduler**: run `pull_permits.py` weekly (cron on your Mac, or a small cloud job).
- **Make**: watch the folder (Google Drive / Dropbox) → parse CSV → *Airtable: Search records* by Permit # (skip duplicates) → *Create record*.
- **Todoist**: for Score ≥ 8, create a P1 task `Research operator: {Address} — {Signals}`.

Build this only after doing it by hand for 3–4 weeks. That's how you'll learn which signals actually produce conversations, and the scoring will need tuning.

---

## Running the script the first time

`pull_permits.py` needs only Python 3, which is already on your Mac. No installs.

```bash
cd ~/Projects/permit-play       # wherever you saved it
python3 pull_permits.py --inspect
```

`--inspect` prints the real field names from the Mecklenburg permit layer and shows which ones the script matched. **Do this first.** I couldn't reach the county's server from my sandbox, so the field matching has only been tested against a mock feed, not the live data. If a line says `NOT FOUND`, paste the output back to me and I'll fix the mapping.

Then:
```bash
python3 pull_permits.py --days 30     # writes permits_2026-10-28.csv
```

**Adding more counties:** Gaston is done; see `3-gaston-county.md`. Cabarrus, Union, Iredell and York each use different systems and need their own small adapter.
