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
        # The county's newer Accela permit system (all trades): work
        # descriptions, construction cost, occupancy group, owner.
        "county": "Mecklenburg", "kind": "permits", "days": 60, "name": "Accela",
        "url": "https://meckgis.mecklenburgcountync.gov/server/rest/services/AccelaAllPermits/FeatureServer/0",
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
        # Charlotte rezoning petitions still in process (~80 at a time). Only
        # requests INTO industrial zoning (ML-1/ML-2, old I-1/I-2) or with an
        # industrial proposed use make the digest; rezonings away from
        # industrial don't.
        "county": "Mecklenburg", "kind": "planning", "days": 365, "name": "Charlotte rezonings",
        "url": "https://gis.charlottenc.gov/arcgis/rest/services/PLN/Rezonings/MapServer/0",
        "fields": {"permit_no": "Petition", "issue_date": "Received", "zoning": "ReqZone",
                   "desc": ["Petitioner", "Propluse"], "type": None, "contractor": None},
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

# Rezoning cases from county pages that list them in an HTML table (pending
# plus this year's closed cases, found in the page's navigation). A case is
# reported when filed and again when decided.
CIVIC_TABLE_SOURCES = [
    {"county": "Lincoln", "url": "https://www.lincolncountync.gov/371/Pending-Applications"},
]

# Town agendas published through CivicPlus AgendaCenter: industrial zoning,
# annexation, site-plan and conditional-use items from each board's agendas
# over the last `days` (the agenda PDF's first pages; needs pdftotext).
AGENDA_SOURCES = [
    {"county": "York", "town": "Fort Mill", "base": "https://www.fortmillsc.gov", "days": 30,
     "boards": ["Planning Commission", "Town Council"]},
]

# Live permits from Tyler EnerGov Citizen Self Service portals (public search,
# no login). Only commercial/industrial permit types are fetched in detail;
# owners come from the parcel layer since portal contacts are private. 21 days
# overlaps last week's run; seen.json keeps each permit to one report.
ENERGOV_SOURCES = [
    {"county": "Gaston", "days": 21, "tenant_id": 1, "tenant_name": "Gaston County, NC",
     "api": "https://selfservice.gastongov.com/energov_prod/selfservice/api/energov",
     "parcels": {"url": "https://gis.gastoncountync.gov/publicgis/rest/services/PublicGIS/Parcels/FeatureServer/11",
                 "fields": "gaston"}},
    # Iredell's portal covers the county, Statesville, Troutman and Harmony
    # (Mooresville permits separately).
    {"county": "Iredell", "days": 21, "tenant_id": 1, "tenant_name": "Iredell County, NC",
     "api": "https://selfservice.iredellcountync.gov/energov_prod/selfservice/api/energov",
     "types_rx": r"commercial|industrial|shell|upfit|erosion control - major|change (of|in) use",
     "parcels": {"url": "https://maps.iredellcountync.gov/server/rest/services/Data/TaxSQL_Parcels/FeatureServer/0",
                 "fields": "iredell"}},
]

# Live permits from Accela Citizen Access portals (public search, no login).
# Only commercial permit types are searched; each record's public detail page
# adds contractor, applicant, owner, occupancy, estimated cost and square feet.
ACCELA_SOURCES = [
    {"county": "Cabarrus", "days": 21, "base": "https://aca-prod.accela.com/CABARRUS",
     "types": ["Permits/Building/Commercial/New", "Permits/Building/Commercial/Shell",
               "Permits/Building/Commercial/Upfit", "Permits/Building/Commercial/Addition",
               "Permits/Building/Commercial/Footing Foundation", "Permits/Building/Commercial/Existing CO",
               "Permits/Kannapolis/Change in Use/NA", "Permits/Kannapolis/NonResidential Zoning Permit/NA"]},
    # Planning module: rezonings (county, Kannapolis) and site-plan reviews (county,
    # Concord, Harrisburg, Kannapolis), months ahead of building permits.
    {"county": "Cabarrus", "kind": "planning", "name": "rezonings & site plans", "days": 30,
     "base": "https://aca-prod.accela.com/CABARRUS", "module": "Planning",
     "types": ["Planning/Rezoning/Conventional/NA", "Planning/Kannapolis/Zoning Map Amendment/NA",
               "Planning/Kannapolis/Cond Zoning Map Amendment/NA", "Planning/Plan Review/Site/NA",
               "Planning/Kannapolis/Plan Review/Minor Site", "Planning/Special Use Permit/NA/NA"]},
]

# Live permits from Evolve Public portals (public date-range search, no login).
# Union's commercial report codes are 6xx; York tags each permit with a letter
# (C commercial, S signs and land disturbance), and its detail adds contract
# price and occupancy. Covers unincorporated areas plus the towns these
# counties inspect for (Monroe and Waxhaw, and Rock Hill / Fort Mill, permit
# separately).
EVOLVE_SOURCES = [
    {"county": "Union", "days": 21, "url": "https://ucinspect.unioncountync.gov/EvolvePublic/",
     "search_menu": ["BL_Menu1", "1"], "types_rx": r"^6\d\d - (?!.*(trailer|alcoholic|pv\b))"},
    {"county": "York", "days": 21, "url": "https://evolvepublic.yorkcountygov.com/",
     "search_menu": ["BL_Menu", "2"], "types_rx": r"^[CS]$", "skip_rx": r"- Sign\b"},
]

# Counties whose permit systems have no open feed. Their weekly exports can be
# dropped into inbox/ as <county>_<anything>.csv and get scored the same way.
PORTAL_ONLY = {
    "Lincoln": "eTRAKiT (linc.csqrcloud.com) requires a login to search permits; rezonings come from the weekly sweep",
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
