# Brink Signals

Every Monday morning this repo checks seven Charlotte-region counties for signs that an industrial operator is about to need space, and emails a digest of **what's new since last week**.

**Counties:** Mecklenburg · Gaston · Cabarrus · Union · Iredell · Rowan · York (SC)

## The signals, earliest first

| Signal | Lead time | Source | Counties |
|---|---|---|---|
| 🔥 **Hiring clusters**: 3+ forklift / warehouse / production postings from one employer in one city | 12–18 months | Adzuna job search API | All 7 |
| 📐 **Planning filings**: proposed and approved developments | 6–9 months | County GIS | Gaston (more as found) |
| 🏗️ **Permits**: industrial upfits, additions, racking, dock work | 0–6 months | County GIS, or exports dropped in `inbox/` | Mecklenburg, Cabarrus (live) · Gaston, Union, Iredell, Rowan, York (inbox) |

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

- **Searches:** one search per county (Adzuna bills per call) for postings in the last 7 days within 25 km of the county seat mentioning forklift, warehouse, picker, packer, loader, handler, shipping, receiving, distribution, production or assembler. Only operations-type titles are kept (forklift, order picker, material handler, warehouse associate, machine operator, shipping/receiving …), so "Distribution Analyst" and similar office roles drop out. About 7–28 calls a week.
- **Grouping:** postings are grouped by employer and city.
- **Ranking:** clusters rank higher for size and for expansion language ("new facility", "launch team", "2nd/3rd shift", "grand opening").
- **Labels:** staffing agencies are marked *find the employer*, and retailers are marked *likely store roles*.
- **Repeats:** a cluster reappears only if it grows by 3+ postings.

## Setup (one time)

1. **Adzuna key:** sign up at <https://developer.adzuna.com>. The free tier is only 25 test calls (one or two runs); weekly use needs the "API Access" plan, £8/month (~$10). Everything except the hiring signal runs without a key. In this repo, go to **Settings → Secrets and variables → Actions → New repository secret** and add `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`.
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
| `signals/permits.py` | County GIS access and permit scoring |
| `signals/jobs.py` | Job-board pull and clustering |
| `output/<date>/` | `digest.md` plus Airtable-ready `permits.csv`, `planning.csv`, `jobs.csv` |
| `data/seen.json` | What's already been reported, so each digest is only new items |
| `docs/` | Material handling outreach kit, Airtable setup, Gaston guide |

Run locally with `python3 run_weekly.py` (add `--no-jobs` without an Adzuna key, `--all` to re-list everything). Tests: `python3 -m unittest discover tests`.
