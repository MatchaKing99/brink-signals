"""What to watch. Edit this file to add a county or source."""

# The seven counties in the Charlotte-region market. `jobs_where` anchors the
# job-board search; `areas` are the county names job boards return, used to
# keep only postings inside the market.
COUNTIES = {
    "Mecklenburg": {"state": "NC", "jobs_where": "Charlotte, NC"},
    "Gaston":      {"state": "NC", "jobs_where": "Gastonia, NC"},
    "Cabarrus":    {"state": "NC", "jobs_where": "Concord, NC"},
    "Union":       {"state": "NC", "jobs_where": "Monroe, NC"},
    "Iredell":     {"state": "NC", "jobs_where": "Statesville, NC"},
    "Rowan":       {"state": "NC", "jobs_where": "Salisbury, NC"},
    "York":        {"state": "SC", "jobs_where": "Rock Hill, SC"},
}

# Live ArcGIS sources pulled every week.
#   kind "permits":  building permits, scored by signals/permits.py
#   kind "planning": development / site-plan filings (earlier than permits)
# `discover` finds the newest yearly layer by name when a county publishes
# one layer per year.
ARCGIS_SOURCES = [
    {
        "county": "Mecklenburg", "kind": "permits", "days": 30,
        # FeatureServer (not MapServer) is the endpoint that serves records; see
        # github.com/AnthonyMutt/charlotte-development-analysis
        "url": "https://meckgis.mecklenburgcountync.gov/server/rest/services/BuildingPermits/FeatureServer/0",
    },
    {
        "county": "Gaston", "kind": "planning", "days": 3650,
        "url": "https://gis.gastoncountync.gov/publicgis/rest/services/PublicGIS/Developments/FeatureServer/2",
    },
    {
        "county": "Cabarrus", "kind": "permits", "days": 30,
        "discover": {
            "service": "https://location.cabarruscounty.us/arcgisservices/rest/services/opendata/MapServer",
            "name": r"^permits\b",
        },
    },
]

# Counties whose permit systems have no open feed. Their weekly exports can be
# dropped into inbox/ as <county>_<anything>.csv and get scored the same way.
PORTAL_ONLY = {
    "Gaston":  "Tyler EnerGov Citizen Self Service (see docs/gaston-county.md)",
    "Union":   "Evolve portal — ucinspect.unioncountync.gov/EvolvePublic (Monroe & Waxhaw permit separately)",
    "Iredell": "eTRAKiT (Mooresville permits separately at mooresvillepermits.com)",
    "Rowan":   "No public online search found — Salisbury zoning, county building permits",
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

# Thresholds for the weekly digest.
PERMIT_MIN_SCORE = 5
PLANNING_MIN_SCORE = 2
JOB_CLUSTER_MIN = 3        # operator-type postings at one company+city to flag
JOB_GROWTH_FLAG = 3        # flag again if a known cluster grows by this many
