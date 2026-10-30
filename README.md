# Brink Signals

Every Monday morning this repo checks seven Charlotte-region counties for signs that an industrial operator is about to need space, and emails a digest of **what's new since last week**.

**Counties:** Mecklenburg · Gaston · Cabarrus · Union · Iredell · Rowan · York (SC)

## The signals, earliest first

| Signal | Lead time | Source | Counties |
|---|---|---|---|
| 🔥 **Hiring clusters**: 3+ forklift / warehouse / production postings from one employer in one city | 12–18 months | Google Jobs via SerpApi (free) | All 7 |
| 📐 **Planning filings**: industrial rezonings (requests into industrial zoning or for an industrial use), developments, Planning Board hearings, projects under construction | 6–9 months | County / city GIS | Mecklenburg (Charlotte rezoning petitions), Gaston, Rowan, Iredell |
| 🔨 **Commercial inspections**: commercial jobs being inspected; a building or fire **final** means someone is about to move in | 0–3 months | County GIS | Union |
| 🏗️ **Permits**: industrial upfits, additions, racking, dock work | 0–6 months | County GIS, or exports dropped in `inbox/` | Mecklenburg, Rowan (county GIS) · Gaston, Iredell incl. Statesville & Troutman (live portals, with parcel owner, zoning, building and last sale) · Cabarrus incl. Kannapolis, Harrisburg, Midland (live portal, with contractor, owner, occupancy, cost, SF) · Union, York (inbox) |

## How a permit gets scored

A permit only makes the digest at **score 5+**.

**Points**
| Signal | Points |
|---|---|
| Strong words: rack, mezzanine, conveyor, dock, leveler, ESFR, cold storage, freezer, crane, warehouse, distribution, manufacturing, industrial, flex, fulfillment, logistics | +2 each |
| Supporting words: upfit, tenant improvement, addition, expansion, shell, new building, storage, sprinkler, high pile | +1 each |
| Building-code use group **F** (factory), **S** (storage/warehouse) or **H** (high hazard) | +3 |
| Industrial zoning (I-1, I-2, ML-1, ML-2, M-, BP …) | +2 |
| Job value $100K+ / $250K+ / $1M+ | +1 / +2 / +3 |

**Thrown out regardless of score**
- Residential permits, or use groups **R, U, A, E, I** (homes, utilities, restaurants and assembly, schools, institutions)
- Self-storage, garages and carports, apartments, trash enclosures, water-plant work, tank farms, auto repair, car washes, retaining walls, boat docks, churches, schools, restaurants
- Mecklenburg's category boilerplate *"Plan Review (Upfits, Additions, Repair)"*, which otherwise gives every commercial permit free points

Tune any of this in `signals/permits.py`. Thresholds live in `signals/config.py`.

## Hiring clusters

- **Searches:** Google Jobs through SerpApi, which pulls in Indeed, LinkedIn, ZipRecruiter and company career sites. Two searches per county ("warehouse forklift jobs", "production machine operator jobs"), 2 pages each: 28 searches a week, about 120 a month, inside SerpApi's **free 250/month**. Only postings from the last 7 days with operations-type titles are kept (forklift, order picker, material handler, warehouse associate, machine operator, shipping/receiving …), so office roles drop out. Adzuna is supported as a fallback if you ever prefer it.
- **Grouping:** postings are grouped by employer and city.
- **Ranking:** clusters rank higher for size and for expansion language ("new facility", "launch team", "2nd/3rd shift", "grand opening").
- **Labels:** staffing agencies are marked *find the employer*, and retailers are marked *likely store roles*.
- **Repeats:** a cluster reappears only if it grows by 3+ postings.

## Setup (one time)

1. **SerpApi key (free):** sign up at <https://serpapi.com> (free plan: 250 searches/month). Copy your API key from the dashboard, then in this repo go to **Settings → Secrets and variables → Actions → New repository secret**. Name: `SERPAPI_API_KEY`, value: the key. Everything except the hiring signal runs without it.
2. **Email:** make sure GitHub emails you for issues. Settings → Notifications → "Participating, @mentions and custom" → Email. The digest issue is assigned to you, so it lands in your inbox.
3. **First run:** **Actions → Weekly signals → Run workflow** to run it now instead of waiting for Monday.

## Adding permits from portal-only counties

Gaston, Union, Iredell, Rowan and York don't publish an open permit feed.

1. Export a search from the county portal as CSV and name it after the county, e.g. `union_2026-11-02.csv`.
2. Upload it to `inbox/` on GitHub: **Add file → Upload files**.
3. The workflow runs on its own, scores the file, and archives it to `data/inbox-processed/`.

Step-by-step for Gaston: [`docs/gaston-county.md`](docs/gaston-county.md).

## What's where

| Path | What |
|---|---|
| `run_weekly.py` | The weekly run |
| `signals/config.py` | Counties, sources, search terms, thresholds |
| `signals/permits.py` | County GIS access (downloads via [pyesridump](https://github.com/openaddresses/pyesridump)) and permit scoring |
| `signals/jobs.py` | Job-board pull and clustering |
| `output/<date>/` | `digest.md` plus Airtable-ready `permits.csv`, `planning.csv`, `jobs.csv` |
| `data/seen.json` | What's already been reported, so each digest is only new items |
| `docs/` | Material handling outreach kit, Airtable setup, Gaston guide |

Run locally with `pip install -r requirements.txt` then `python3 run_weekly.py` (add `--no-jobs` to skip the job search, `--all` to re-list everything). Tests: `python3 -m unittest discover tests`.
