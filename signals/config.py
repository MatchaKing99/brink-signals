"""What to watch. Edit this file to add a county or source."""

# The seven counties in the Charlotte-region market. `jobs_where` anchors the
# job-board search; `areas` are the county names job boards return, used to
# keep only postings inside the market.
COUNTIES = {
    "Mecklenburg": {"state": "NC", "jobs_where": "Charlotte, NC",
                    "serpapi_location": "Charlotte, North Carolina, United States"},
    "Gaston":      {"state": "NC", "jobs_where": "Gastonia, NC",
                    "serpapi_location": "Gastonia, North Carolina, United States"},
    "Cabarrus":    {"state": "NC", "jobs_where": "Concord, NC",
                    "serpapi_location": "Concord, North Carolina, United States"},
    "Union":       {"state": "NC", "jobs_where": "Monroe, NC",
                    "serpapi_location": "Monroe, North Carolina, United States"},
    "Iredell":     {"state": "NC", "jobs_where": "Statesville, NC",
                    "serpapi_location": "Statesville, North Carolina, United States"},
    "Rowan":       {"state": "NC", "jobs_where": "Salisbury, NC",
                    "serpapi_location": "Salisbury, North Carolina, United States"},
    "York":        {"state": "SC", "jobs_where": "Rock Hill, SC",
                    "serpapi_location": "Rock Hill, South Carolina, United States"},
}

# Live ArcGIS sources pulled every week.
#   kind "permits":  building permits, scored by signals/permits.py
#   kind "planning": development / site-plan filings (earlier than permits)
# `discover` finds the newest yearly layer by name when a county publishes
# one layer per year.
ARCGIS_SOURCES = [
    {
        # 60 days: the county's GIS copy runs a few weeks behind, and seen.json
        # stops anything from being reported twice.
        "county": "Mecklenburg", "kind": "permits", "days": 60,
        # FeatureServer (not MapServer) is the endpoint that serves records; see
        # github.com/AnthonyMutt/charlotte-development-analysis
        "url": "https://meckgis.mecklenburgcountync.gov/server/rest/services/BuildingPermits/FeatureServer/0",
    },
    {
        "county": "Gaston", "kind": "planning", "days": 3650,
        "url": "https://gis.gastoncountync.gov/publicgis/rest/services/PublicGIS/Developments/FeatureServer/2",
    },
    {
        # Every trade's permits (141K); commercial building permits carry no
        # description or value, so size (sq ft) does the scoring.
        "county": "Rowan", "kind": "permits", "days": 45, "name": "all permits",
        "url": "https://gis.rowancountync.gov/arcgis/rest/services/Public/Building_Permits/MapServer/6",
        "type_rx": r"commercial|\bCOM-", "min_score": 2,
    },
    {
        # Rezoning cases; one row per parcel, so a case can repeat by parcel.
        "county": "Rowan", "kind": "planning", "days": 120, "name": "rezonings",
        "url": "https://gis.rowancountync.gov/arcgis/rest/services/Energov/Energov_main_10_4_s077/MapServer/18",
    },
    {
        # Planning Board hearings: rezoning and special-use requests with the
        # applicant and the full request text. Small layer, no date filter.
        "county": "Iredell", "kind": "planning", "days": 365, "name": "planning board hearings",
        "url": "https://maps.iredellcountync.gov/server/rest/services/PublicViewer_Planning/Board_Public_Hearings/FeatureServer/0",
    },
    {
        "county": "Iredell", "kind": "planning", "days": 3650, "name": "Mooresville projects under construction",
        "url": "https://maps.iredellcountync.gov/server/rest/services/Planning/Development_Activity_Countywide/MapServer/5",
    },
    {
        # Accela plan reviews (permit applications). Newest filing seen Oct 2026
        # was April 2025, so this may stay quiet until the county refreshes it.
        "county": "Cabarrus", "kind": "permits", "days": 60, "name": "Accela plan reviews",
        "url": "https://location.cabarruscounty.us/arcgisservices/rest/services/Current_Accela_Permits/Plan_Reviews/MapServer/0",
        # Only review types are published (no description), so require an
        # industrial word in the type itself.
        "type_rx": r"commercial|industrial|shell|warehouse|upfit", "min_score": 1,
        "require_industrial": True,
    },
    {
        "county": "Gaston", "kind": "planning", "days": 3650, "name": "county rezonings",
        "url": "https://gis.gastoncountync.gov/publicgis/rest/services/PublicGIS/CountyZoningReviewCases/FeatureServer/0",
    },
    {
        "county": "Gaston", "kind": "planning", "days": 3650, "name": "municipal rezonings",
        "url": "https://gis.gastoncountync.gov/publicgis/rest/services/PublicGIS/MunicipalZoningReviewCases/FeatureServer/1",
    },
    {
        # Rock Hill publishes one commercial-permit layer per year; newest seen
        # was 2023. Reported as "nothing current" until a newer year appears.
        "county": "York", "kind": "permits", "days": 60, "name": "Rock Hill commercial",
        "discover": {
            "service": "https://crh-vmw-gisvdr1.cityofrockhillsc.gov/arcgis/rest/services/permitting_data/permitting/MapServer",
            "name": r"^commercial - \d{4}$",
        },
    },
]

# Counties that publish building-inspection results instead of permits. A
# commercial final inspection means a building is about to be occupied.
INSPECTION_SOURCES = [
    # 120 days: the county refreshes this layer in batches; seen.json keeps
    # each job from being reported more than once per stage.
    {"county": "Union", "days": 120,
     "urls": [
         "https://atlas.unioncountync.gov/server/rest/services/Hosted/Approved_Permits/FeatureServer/0",
         "https://atlas.unioncountync.gov/server/rest/services/Hosted/Not_Approved_Permits/FeatureServer/6",
     ]},
]

# Counties whose permit systems have no open feed. Their weekly exports can be
# dropped into inbox/ as <county>_<anything>.csv and get scored the same way.
PORTAL_ONLY = {
    "Gaston":  "Tyler EnerGov Citizen Self Service (see docs/gaston-county.md)",
    "Union":   "Evolve portal — ucinspect.unioncountync.gov/EvolvePublic (Monroe & Waxhaw permit separately); commercial inspections are pulled live",
    "Iredell": "eTRAKiT (Mooresville permits separately at mooresvillepermits.com); planning hearings and Mooresville projects pulled live",
    "York":    "Evolve Public Portal (unincorporated); Rock Hill / Fort Mill permit separately",
}

# Job-board search. Adzuna bills per call, so each county gets ONE search for
# any of these words (`what_or`), then titles are kept only if they look like
# hourly operations roles.
JOB_WORDS = ["forklift", "warehouse", "picker", "packer", "loader", "handler",
             "shipping", "receiving", "distribution", "production", "assembler"]
JOB_TITLE_RX = (r"forklift|reach truck|order (picker|selector)|picker|packer|loader|"
                r"material handler|warehouse (associate|worker|operator|lead|supervisor)|"
                r"shipping|receiving|distribution center|production (associate|worker|operator)|"
                r"machine operator|assembler|dock")

# Google Jobs (SerpApi) searches per county. 2 queries x 2 pages x 7 counties
# = 28 searches a week, inside the free 250/month.
SERPAPI_QUERIES = ["warehouse forklift jobs", "production machine operator jobs"]

# Thresholds for the weekly digest.
PERMIT_MIN_SCORE = 5
PLANNING_MIN_SCORE = 2
JOB_CLUSTER_MIN = 3        # operator-type postings at one company+city to flag
JOB_GROWTH_FLAG = 3        # flag again if a known cluster grows by this many
