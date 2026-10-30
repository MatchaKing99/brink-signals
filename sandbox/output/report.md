# SANDBOX: Gaston County permit pipeline, 2026-10-30

Source: Gaston County Citizen Self Service (Tyler EnerGov), public search API, no login. Window: permits issued or applied in the last 60 days.

| Step | Result |
|---|---|
| Pulled (issued or applied in window) | 2167 |
| Commercial / industrial permit types | 368 (130 building or site work, the rest trade permits) |
| Detail records fetched | 368 |
| Tagged industrial by the bot's scorer | 29 |
| **Industrial at the bot's digest threshold (score ≥ 5)** | **18** |
| Other commercial work on industrial-use parcels | 22 |
| Matched to a county parcel | 360 of 368 |
| API calls to the portal | 460 |
| NC Secretary of State lookups | blocked by a Cloudflare bot challenge (HTTP 403), so look these up by hand |

**Compared with the live bot:** it has 0 Gaston permits on record (Gaston permits currently need a manual export), so every permit below is one it missed.

## Industrial permits

Everything the bot's scorer tags as industrial. ⭐ = score 5+, the bar for the weekly digest.

### ⭐ Lane Seven Expansion - Demo demising wall, modify existing office and expand 716 SF with n | 3145 ABERDEEN BOULEVARD GASTONIA NC 28054
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Documents Needed. Applied 2026-10-23, issued not yet. [BLDC-26-10-23-03187](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/10db333a-d6de-4fa3-ac00-88b7fd8ecf5e)
- **Size:** $354,031, 241,124 SF of work, occupancy S-1 Storage. Score 15 (rack, warehouse, expansion, storage, high pile, industrial occupancy, 50k+ SF, $250k+)
- **Who:** Owner: Noah Cardenas; Superintendent: Ranger Construction Company, Inc.; Other: Ranger Construction Company, Inc.; Contractor (Electrical): Southern Electrical Contractors of Charlotte Inc; Contractor (GC): Ranger Construction Company, Inc; Contractor (Plumbing): Ranger Construction Company, Inc; Applicant: Ranger Construction Company, Inc.; Contractor (Mechanical): Air Charlotte Mechanical Services, Inc
- **Property:** PIN 3565-79-0211, Distribution Warehouse land use, 20.41 ac, 239,559 SF building, built 2022, tax value $17,420,680. Owner NP GASTONIA INDUSTRIAL 4 LLC (3315 NORTH OAK TRAFFICWAY, KANSAS CITY MO 64116). Deed Bk 5348 Pg 0536 (SWD), last sale 2022-06-30.
- **Look up at NC SOS:** NP GASTONIA INDUSTRIAL 4 LLC, Ranger Construction Company, Inc
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. The owner is out of state (MO). Pitch landlord rep or a BOV.

### ⭐ Kyle Spec - scope will include 1,000 SF new office with a 53,141 SF existing storage wareh | 1910 KYLE COURT GASTONIA NC 28052
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Issued. Applied 2026-08-24, issued 2026-10-13. [BLDC-26-08-24-03100](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/0ea4c364-fcd8-42f0-81ca-a76620dc29e5)
- **Size:** $250,000, 54,000 SF of work, occupancy S-1 Storage / B Business. Score 11 (warehouse, storage, industrial occupancy, 50k+ SF, $250k+)
- **Who:** Contractor (GC): Zenith Building Group LLC; Applicant: Tenant Improvement Interior s; Applicant: Tenant Improvement Interiors; Superintendent: Peter Rorie; Contractor (Plumbing): Zenith Building Group LLC; Builder: Zenith Building Group; Contractor (Mechanical): Zenith Building Group LLC; Contractor (Electrical): Zenith Building Group LLC
- **Property:** PIN 3536-13-5985, Distribution Warehouse land use, 3.23 ac, 54,000 SF building, built 1999, tax value $1,614,770. Owner KYLE COURT LLC (805 TRADE ST NW SUITE 101, CONCORD NC 28027). Deed Bk 4879 Pg 2295 (WD), last sale 2016-11-16 for $1,495,000.
- **Look up at NC SOS:** KYLE COURT LLC, Zenith Building Group LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale.

### ⭐ New addition to existing facility - footing and foundation only and underslab utilities | 1 ONE EXBERRY DRIVE DALLAS NC 28034
- **What:** Foundation Only (Commercial) - Foundation Only (Addition). Status: Issued. Applied 2026-09-17, issued 2026-10-28. [BLDC-26-09-17-03139](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/2669314b-6daf-4697-a8d0-4881e0d149b9)
- **Size:** $2,350,000, 155,032 SF of work, occupancy F-1 Factory / B Business. Score 10 (addition, industrial occupancy, 50k+ SF, $1M+)
- **Who:** Owner: GNT USA LLC; Applicant: Merriman Schmitt Architects; Contractor (GC): Edifice, LLC; Contractor (Electrical): Jonathan "Matt" Anderson; Contractor (Mechanical): Herlocker Mechanical Systems, Inc.; Superintendent: Edifice
- **Property:** PIN 3537-69-3563, Industrial land use, 49.66 ac, 76,098 SF building, built 2021, tax value $8,495,540. Owner GNT NORTH AMERICA LLC (1 EXBERRY DR, DALLAS NC 28034). Deed Bk 5164 Pg 0818 (SWD), last sale 2020-10-14.
- **Look up at NC SOS:** GNT NORTH AMERICA LLC, GNT USA LLC, Edifice, LLC
- **Your move:** An owner-user is expanding in place. Ask GNT NORTH AMERICA LLC about overflow warehouse needs or a move if the site maxes out.

### ⭐ FIRE SPRINKLERS | 231 SOUTHRIDGE PARKWAY BESSEMER CITY NC 28016
- **What:** Sprinkler - Plumbing - Plumbing (New). Status: In Review. Applied 2026-10-13, issued not yet. [SPL-26-10-13-0141](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/d45f9cea-c6b4-4f6a-a490-8fce8d10e847)
- **Size:** $870,375, 299,711 SF of work, occupancy S-1 Storage. Score 10 (storage, sprinkler, industrial occupancy, 50k+ SF, $250k+)
- **Who:** Applicant: S.A.COMUNALE CO, INC.
- **Property:** PIN 3526-54-2972, Industrial Land land use, 48.25 ac, tax value $863,430. Owner AMAZON.COM SERVICES LLC (C/O AMAZON PROPERTY TAX, PO BOX 80416, SEATTLE WA 98108). Deed Bk 5267 Pg 1389 (SWD), last sale 2021-09-17 for $3,229,500.
- **Look up at NC SOS:** AMAZON.COM SERVICES LLC, S.A.COMUNALE CO, INC.
- **Your move:** New construction or site work. Call AMAZON.COM SERVICES LLC (and S.A.COMUNALE CO, INC.) now: is it spec or build-to-suit, and is the leasing assignment open? The owner is out of state (WA). Pitch landlord rep or a BOV.

### ⭐ New fire sprinkler system for office/warehouse building | 120 GIBSON COURT DALLAS NC 28034
- **What:** Sprinkler - Plumbing - Plumbing (New). Status: Denied. Applied 2026-09-08, issued not yet. [SPL-26-09-08-0137](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/88e0b985-5a8d-47d6-996e-f241730a6f89)
- **Size:** $125,000, 46,750 SF of work, occupancy F-1 Factory / B Business. Score 9 (warehouse, sprinkler, industrial occupancy, 10k+ SF, $100k+)
- **Who:** Applicant: Wayne Automatic Fire Sprinklers, Inc
- **Property:** PIN 3548-42-7566, Industrial Land land use, 2.23 ac. Owner STACK HOLDINGS LLC (3626 DALLAS HIGH SHOALS HWY, DALLAS NC 28034). Deed .
- **Look up at NC SOS:** STACK HOLDINGS LLC, Wayne Automatic Fire Sprinklers, Inc
- **Your move:** New construction or site work. Call STACK HOLDINGS LLC (and Wayne Automatic Fire Sprinklers, Inc) now: is it spec or build-to-suit, and is the leasing assignment open?

### ⭐ New to Dallas and received a remodel permit from the city for the provided plans attached. | 191 GIBSON COURT DALLAS NC 28034
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Documents Needed. Applied 2026-09-23, issued not yet. [BLDC-26-09-23-03146](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/fae0ba02-e3d2-41ef-b503-15c0e9e188f3)
- **Size:** $65,000, 11,500 SF of work, occupancy F-2 Factory / S-2 Storage. Score 9 (warehouse, addition, storage, industrial occupancy, 10k+ SF)
- **Who:** Applicant: David Kenahan; Contractor (Electrical): D.R. Electric; Owner: David Kenahan
- **Property:** PIN 3548-62-3323, Industrial land use, 3.2 ac, 11,500 SF building, built 1996, tax value $775,420. Owner ROWKEN HOLDINGS LLC (3306 N NC HIGHWAY BUSINESS 16, DENVER NC 28037). Deed Bk 5640 Pg 1007 (SWD), last sale 2026-05-13 for $1,375,000.
- **Look up at NC SOS:** ROWKEN HOLDINGS LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. It sold recently (2026-05-13, $1,375,000). A new owner may be repositioning it, so offer leasing.

### ⭐ CanSource Equipment Additions | 1115 CRAWFORD OAKS DRIVE GASTONIA NC 28056
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Other). Status: Complete. Applied 2026-08-06, issued 2026-08-31. [BLDC-26-08-06-03075](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/afc4c1c7-dc07-4b3e-a9b6-626ee06162e7)
- **Size:** $50,000, 470,000 SF of work, occupancy F-1 Factory / S-1 Storage. Score 8 (addition, storage, industrial occupancy, 50k+ SF)
- **Who:** Contractor (GC): Zenith Building Group LLC; Other: Peter Rorie; Contractor (Plumbing): Zenith Building Group LLC; Superintendent: Zenith Building Group; Applicant: Smith Harris Design; Contractor (Mechanical): Zenith Building Group LLC; Contractor (Electrical): Zenith Building Group LLC
- **Property:** PIN 3585-49-4255, Distribution Warehouse land use, 43.5 ac, 468,712 SF building, built 2023, tax value $34,876,110. Owner CRP/CHI OAKS COMMERCE CENTER OWNER LLC (1001 PENNSYLVANIA AVE NW STE 220S, WASHINGTON DC 20004). Deed Bk 5379 Pg 0600 (SWD), last sale 2022-11-22.
- **Look up at NC SOS:** CRP/CHI OAKS COMMERCE CENTER OWNER LLC, Zenith Building Group LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. The owner is out of state (DC). Pitch landlord rep or a BOV.

### ⭐ Vertical Demolition of plant and removal of slabs and foundations - crush material onsite  | 103 EAST WOODROW AVENUE BELMONT NC 28012
- **What:** Demolition (Commercial) - Commercial (Demolition). Status: Documents Needed. Applied 2026-10-29, issued not yet. [DEMO-26-10-29-00785](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/27f0bdb5-7287-4e6f-8d55-426ebdae67c7)
- **Size:** $178,432, 158,373 SF of work, occupancy F-1 Factory. Score 7 (industrial occupancy, 50k+ SF, $100k+)
- **Who:** Applicant: RCI Demolition Inc.
- **Property:** PIN 3595-21-7000, Industrial land use, 10.14 ac, 5,000 SF building, built 1930, tax value $2,548,790. Owner PARKDALE AMERICA LLC (JENNIFER GIACOBBE, PO BOX 1787, GASTONIA NC 28053). Deed Bk 2739 Pg 42 (SPL), last sale 1997-12-30.
- **Look up at NC SOS:** PARKDALE AMERICA LLC, RCI Demolition Inc.
- **Your move:** New construction or site work. Call PARKDALE AMERICA LLC (and RCI Demolition Inc.) now: is it spec or build-to-suit, and is the leasing assignment open?

### ⭐ Install a 10x 25 cooler on the rear of an existing outdoor work shed on a concrete pad | 1 ONE EXBERRY DRIVE DALLAS NC 28034
- **What:** Building Permit Request: Commercial Accessory Structure - Accessory Structure (Addition). Status: Documents Needed. Applied 2026-09-15, issued not yet. [BLDC-26-09-15-03135](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/673a29ac-ef60-4852-9c05-cf6266fd2926)
- **Size:** $114,380, 250 SF of work, occupancy S-2 Storage. Score 7 (cooler, storage, industrial occupancy, $100k+)
- **Who:** Other: E2 Industrial Refrigeration; Applicant: E2 Industrial Refrigeration; Other: Kim Durham
- **Property:** PIN 3537-69-3563, Industrial land use, 49.66 ac, 76,098 SF building, built 2021, tax value $8,495,540. Owner GNT NORTH AMERICA LLC (1 EXBERRY DR, DALLAS NC 28034). Deed Bk 5164 Pg 0818 (SWD), last sale 2020-10-14.
- **Look up at NC SOS:** GNT NORTH AMERICA LLC
- **Your move:** An owner-user is expanding in place. Ask GNT NORTH AMERICA LLC about overflow warehouse needs or a move if the site maxes out.

### ⭐ adding an equipment room to the existing building | 1230 GASTONIA TECHNOLOGY PARKWAY DALLAS NC 28034
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Other). Status: Documents Needed. Applied 2026-10-07, issued not yet. [BLDC-26-10-07-03168](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/c5a00c52-05a4-4643-813d-9b06cf23eaad)
- **Size:** $60,000, 199,844 SF of work, occupancy F-2 Factory / S-2 Storage. Score 7 (storage, industrial occupancy, 50k+ SF)
- **Who:** Applicant: AngeloArchitects, PLLC
- **Property:** PIN 3547-14-3173, Industrial land use, 44.1 ac, 199,844 SF building, built 2015, tax value $17,736,990. Owner OWENS CORNING COMPOSITE MATERIALS II LLC (ATTN: COMMERCIAL REAL ESTATE, ONE OWENS CORNING PARKWAY, TOLEDO OH 43659). Deed Bk 5585 Pg 0868 (SWD), last sale 2025-09-16.
- **Look up at NC SOS:** OWENS CORNING COMPOSITE MATERIALS II LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. The owner is out of state (OH). Pitch landlord rep or a BOV. It sold recently (2025-09-16). A new owner may be repositioning it, so offer leasing.

### ⭐ Demo 280 LF of demising wall | 3145 ABERDEEN BOULEVARD GASTONIA NC 28054
- **What:** Demolition (Commercial) - Commercial (Demolition). Status: Documents Needed. Applied 2026-09-22, issued not yet. [DEMO-26-09-22-00776](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/049908e9-1c5f-4c5e-9a5d-e69e2e020ada)
- **Size:** $13,000, 114,724 SF of work, occupancy S-1 Storage. Score 7 (storage, industrial occupancy, 50k+ SF)
- **Who:** Contractor (GC): Ranger Construction Company, Inc.; Contractor (GC): Ranger Construction Company, Inc.; Applicant: Ranger Construction Company, Inc.
- **Property:** PIN 3565-79-0211, Distribution Warehouse land use, 20.41 ac, 239,559 SF building, built 2022, tax value $17,420,680. Owner NP GASTONIA INDUSTRIAL 4 LLC (3315 NORTH OAK TRAFFICWAY, KANSAS CITY MO 64116). Deed Bk 5348 Pg 0536 (SWD), last sale 2022-06-30.
- **Look up at NC SOS:** NP GASTONIA INDUSTRIAL 4 LLC, Ranger Construction Company, Inc.
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start. The owner is out of state (MO). Pitch landlord rep or a BOV.

### ⭐ Flute Fill w/1.5" EPS, 1" ISO, 60 mil TPO Rhino. Encapsulate Internal Gutter | 110 KINGS ROAD KINGS MOUNTAIN NC 28086
- **What:** Roof (Commercial) - Roof (Other). Status: Void. Applied 2026-09-11, issued not yet. [BLDC-26-09-11-03130](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/42b9cb21-c299-4058-a0e2-25718cec7577)
- **Size:** $197,304, 31,300 SF of work, occupancy F-1 Factory / F-1 Factory. Score 6 (industrial occupancy, 10k+ SF, $100k+)
- **Who:** Applicant: Radco Construction
- **Property:** PIN 3506-50-7441, Industrial land use, 10.02 ac, 1,500 SF building, built 2003, tax value $4,863,960. Owner BOWER FAMILY REAL ESTATE LLC (110 KINGS RD, KINGS MTN NC 28086). Deed Bk 4769 Pg 1908 (NW), last sale 2015-03-02.
- **Look up at NC SOS:** BOWER FAMILY REAL ESTATE LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### ⭐ New Building per plans | 142 BRICKYARD ROAD MOUNT HOLLY NC 28120
- **What:** New Building (Commercial) - New (New). Status: Issued. Applied 2026-09-23, issued 2026-10-19. [BLDC-26-09-23-03148](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/44d88a62-55fa-48e9-afc3-aad7dfb8da2e)
- **Size:** $191,226, 1,740 SF of work, occupancy S-2 Storage. Score 6 (new building, storage, industrial occupancy, $100k+)
- **Who:** Contractor (GC): RJ Ward Construction Inc; Applicant: RJ Ward Construction Inc; Owner: Flachofsky Storage LLC; Contractor (Electrical): Jerry E. Autry Electric
- **Property:** PIN 3597-22-3767, Industrial Land land use, 0.81 ac. Owner FLACHOFSKY STORAGE LLC (120 BRICKYARD ROAD, MOUNT HOLLY NC 28120). Deed .
- **Look up at NC SOS:** FLACHOFSKY STORAGE LLC, RJ Ward Construction Inc
- **Your move:** New construction or site work. Call FLACHOFSKY STORAGE LLC (and RJ Ward Construction Inc) now: is it spec or build-to-suit, and is the leasing assignment open?

### ⭐ New Storage Building per plans | 134 BRICKYARD ROAD MOUNT HOLLY NC 28120
- **What:** New Building (Commercial) - New (New). Status: Issued. Applied 2026-09-23, issued 2026-10-19. [BLDC-26-09-23-03147](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/f765eb93-dda4-494c-a0d1-d1c4362b3fca)
- **Size:** $191,226, 1,740 SF of work, occupancy S-1 Storage. Score 6 (new building, storage, industrial occupancy, $100k+)
- **Who:** Contractor (GC): RJ Ward Construction Inc; Applicant: RJ Ward Construction Inc; Owner: Flachofsky Storage LLC; Contractor (Electrical): Jerry E. Autry Electric
- **Property:** PIN 3597-22-5584, Industrial Land land use, 0.8 ac. Owner FLACHOFSKY STORAGE LLC (120 BRICKYARD ROAD, MOUNT HOLLY NC 28120). Deed .
- **Look up at NC SOS:** FLACHOFSKY STORAGE LLC, RJ Ward Construction Inc
- **Your move:** New construction or site work. Call FLACHOFSKY STORAGE LLC (and RJ Ward Construction Inc) now: is it spec or build-to-suit, and is the leasing assignment open?

### ⭐ JAK Machine Shop - Adding 2,520 sq feet addition to existing building | 3215 BESSEMER CITY ROAD BESSEMER CITY NC 28016
- **What:** Building Permit Request: Commercial Addition - Addition (Addition). Status: Issued. Applied 2026-09-18, issued 2026-10-06. [BLDC-26-09-18-03140](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/0b5abeaf-5235-4dd4-90f1-4013e4f3b0e9)
- **Size:** $60,000, 2,520 SF of work, occupancy S-2 Storage. Score 5 (addition, storage, industrial occupancy)
- **Who:** Applicant: Jak Machine LLC; Contractor (GC): Home Owner/Homeowner/OWNER; Contractor (Plumbing): Home Owner/Homeowner/OWNER; Contractor (Electrical): Home Owner/Homeowner/OWNER
- **Property:** PIN 3526-67-7008, Service Shop land use, 1.35 ac, 4,012 SF building, built 1964, tax value $159,040. Owner DEATON JOHNNY MACK & DEATON KRISTY BEAM (334 JIM CLARK RD, BESSEMER CITY NC 28016). Deed Bk 4912 Pg 2421 (WD), last sale 2017-05-24 for $48,000.
- **Look up at NC SOS:** Jak Machine LLC
- **Your move:** An owner-user is expanding in place. Ask DEATON JOHNNY MACK & DEATON KRISTY BEAM about overflow warehouse needs or a move if the site maxes out.

### ⭐ installation and integration of the new Addressable Fire Alarm Control Panel, Annunciator, | 920 EAST FIRST STREET CHERRYVILLE NC 28021
- **What:** Fire Alarm (Electrical) - Electrical (Other). Status: Issued. Applied 2026-06-17, issued 2026-10-22. [FA-26-06-17-0227](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/3e85a4cd-f92c-42fe-99fa-c295539270b9)
- **Size:** $33,500, 11,145 SF of work, occupancy F-1 Factory. Score 5 (industrial occupancy, 10k+ SF)
- **Who:** Contractor (Electrical): Pye Barker Fire and Safety LLC; Applicant: Sonitrol Security/ Pye-Barker Fire & Safety
- **Property:** PIN 2690-32-7958, Industrial land use, 10.11 ac, 11,146 SF building, built 1920, tax value $1,114,700. Owner RIDDLEYS PROPERTIES LLC (119 BESS RD, KINGS MTN NC 28086). Deed Bk 4686 Pg 1566 (WD), last sale 2013-07-19.
- **Look up at NC SOS:** RIDDLEYS PROPERTIES LLC, Pye Barker Fire and Safety LLC
- **Your move:** New construction or site work. Call RIDDLEYS PROPERTIES LLC (and Pye Barker Fire and Safety LLC) now: is it spec or build-to-suit, and is the leasing assignment open?

### ⭐ UPDATE FIRE SUPPRESSION SYSTEM IN SPRAY BOOTH. CURRENT SYSTEM OBSOLETE | 1660 PACOLET COURT GASTONIA NC 28052
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (New). Status: Submitted - Online. Applied 2026-10-27, issued not yet. [BLDC-26-10-27-03190](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/b06da196-9fdb-4fbe-8986-8e1928c10ea0)
- **Size:** $25,000, 30,000 SF of work, occupancy H-1 High Hazard. Score 5 (industrial occupancy, 10k+ SF)
- **Who:** Applicant: Reliable Fire & Safety
- **Property:** PIN 3536-56-8554, Service Shop land use, 7.89 ac, 13,500 SF building, built 1992, tax value $771,040. Owner CRAIG BUSINESS PROPERTIES LLC (1660 PACOLET COURT, GASTONIA NC 28052). Deed Bk 5560 Pg 1109 (SWD), last sale 2025-05-28.
- **Look up at NC SOS:** CRAIG BUSINESS PROPERTIES LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. It sold recently (2025-05-28). A new owner may be repositioning it, so offer leasing.

### ⭐ In March/April of 2026 we built two walls in our office to segment off a breakroom for emp | 707 CASON ST BELMONT NC 28012
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Issued. Applied 2026-08-31, issued 2026-09-23. [BLDC-26-08-31-03111](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/bf4ee505-271d-4f1b-97e1-e8c316f0d51f)
- **Size:** $4,900, 10,390 SF of work, occupancy F-1 Factory. Score 5 (industrial occupancy, 10k+ SF)
- **Who:** Contractor (Unlicensed): Waldenwood Group, LLC (dba Steel Tech Inc); Applicant: Waldenwood Group, LLC (dba Steel Tech Inc)
- **Property:** PIN 3596-00-1128, Office Warehouse land use, 1.21 ac, 10,390 SF building, built 1996, tax value $383,670. Owner EHJH PROPERTIES LLC (707 CASON STREET, BELMONT NC 28012). Deed Bk 5594 Pg 2116 (SWD), last sale 2025-10-24 for $1,750,000.
- **Look up at NC SOS:** EHJH PROPERTIES LLC, Waldenwood Group, LLC (dba Steel Tech Inc)
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. It sold recently (2025-10-24, $1,750,000). A new owner may be repositioning it, so offer leasing.

### RDS Lawn Care - Building repairs from vehicle damage (550 sqft area) Scope of work include | 1627 CHARLES RAPER JONAS HIGHWAY MOUNT HOLLY NC 28120
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Issued. Applied 2026-10-28, issued 2026-10-30. [BLDC-26-10-28-03193](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/51fcf9c8-869b-4801-b24e-480f027f1537)
- **Size:** $96,100, 550 SF of work, occupancy S-2 Storage. Score 4 (storage, industrial occupancy)
- **Who:** Contractor (Electrical): Vision Electric Inc.; Contractor (GC): Pinnix General Con; Applicant: Pinnix Inc.
- **Property:** PIN 3587-79-5458, Service Shop land use, 0.21 ac, 2,400 SF building, built 1982, tax value $79,770. Owner MOUNTAIN CANDY PROPERTIES LLC (702 HANNA WOODS, CRAMERTON NC 28032). Deed Bk 5425 Pg 2029 (SWD), last sale 2023-07-31 for $135,000.
- **Look up at NC SOS:** MOUNTAIN CANDY PROPERTIES LLC, Pinnix Inc.
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale.

### First Assembly - 30x40 Accessory Storage Building | 613 SOUTH MYRTLE SCHOOL ROAD GASTONIA NC 28052
- **What:** Building Permit Request: Commercial Accessory Structure - Accessory Structure (New). Status: Documents Needed. Applied 2026-09-15, issued not yet. [BLDC-26-09-15-03134](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/24657fc0-779c-4020-9297-43e08aa5351d)
- **Size:** $33,824, 1,200 SF of work, occupancy S-1 Storage. Score 4 (storage, industrial occupancy)
- **Who:** Contractor (Unlicensed): COOPER INDUSTRIES; Applicant: COOPER INDUSTRIES
- **Property:** PIN 3535-53-6914, Church/Religious land use, 47.92 ac, 44,794 SF building, built 2007. Owner FIRST ASSEMBLY OF GOD OF GAST (N C DISTRICT COUNCIL, P O BOX 459, SELMA NC 27576). Deed Bk 5658 Pg 1245 (AOC), last sale 2026-07-28.
- **Your move:** New construction or site work. Call FIRST ASSEMBLY OF GOD OF GAST (and COOPER INDUSTRIES) now: is it spec or build-to-suit, and is the leasing assignment open? It sold recently (2026-07-28). A new owner may be repositioning it, so offer leasing.

### Remove existing toilet and sink. Make restroom larger to meet Handicap code. Install handi | 101 NORTH WEBB STREET GASTONIA NC 28052
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Documents Needed. Applied 2026-09-28, issued not yet. [BLDC-26-09-28-03152](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/66e873dd-9ea2-46a6-b1df-ab0b6ee4f58b)
- **Size:** $25,000, 4,000 SF of work, occupancy S-1 Storage. Score 4 (storage, industrial occupancy)
- **Who:** Contractor (Plumbing): Dallas Electrical & Plumbing Contractors, Inc.; Contractor (Electrical): Dallas Electrical & Plumbing Contractors, Inc.; Applicant: Pearson Construction and Services LLC; Architect: AngeloArchitects, PLLC
- **Property:** PIN 3545-07-6555, Warehouse land use, 0.37 ac, 4,000 SF building, built 1990, tax value $146,850. Owner YELTON JAMES K (8034 CATAWBA COVE DR, BELMONT NC 28012). Deed Bk 3142 Pg 0476 (WD), last sale 2000-10-12 for $100,000.
- **Look up at NC SOS:** Dallas Electrical & Plumbing Contractors, Inc., Pearson Construction and Services LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale.

### 16' x 22' x 8' Accessory Storage Building | 2529 HICKORY GROVE ROAD GASTONIA NC 28056
- **What:** Building Permit Request: Commercial Accessory Structure - Accessory Structure (New). Status: Void. Applied 2026-10-09, issued not yet. [BLDC-26-10-09-03175](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/118c136a-f46b-4b26-bca8-881fa86fe51c)
- **Size:** $12,500, 352 SF of work, occupancy S-1 Storage. Score 4 (storage, industrial occupancy)
- **Who:** Applicant: Kevin Farmer
- **Property:** PIN 3586-35-6921, Residential 1 Family land use, 0.56 ac, 1,490 SF building, built 1957, tax value $192,700. Owner FARMER KEVIN L & FARMER DONNA T (2529 HICKORY GROVE RD, GASTONIA NC 28056). Deed Bk 2670 Pg 0894 (WD), last sale 1997-06-12.
- **Your move:** New construction or site work. Call FARMER KEVIN L & FARMER DONNA T (and Kevin Farmer) now: is it spec or build-to-suit, and is the leasing assignment open?

### Single trade permit | 6517 WILKINSON BOULEVARD BELMONT NC 28012
- **What:** Building Permit Request: Commercial Accessory Structure - Accessory Structure (Other). Status: Denied. Applied 2026-09-08, issued not yet. [BLDC-26-09-08-03121](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/22e9ffaf-4b7a-42f6-b81e-8738fca14983)
- **Size:** $4,000, 192 SF of work, occupancy S-1 Storage. Score 4 (storage, industrial occupancy)
- **Who:** Applicant: Chun Lin
- **Property:** PIN 3595-03-4666, Shopping Center/Mall land use, 6.09 ac, 52,069 SF building, built 1994, tax value $5,562,660. Owner AC BELMONT LLC (2825 SOUTH BLVD STE 300, CHARLOTTE NC 28209). Deed Bk 5238 Pg 1787 (SWD), last sale 2021-06-18 for $5,000,000.
- **Look up at NC SOS:** AC BELMONT LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### Exisiting RTU to be removed. Place DOAS in place. Redo ductwork down to laboratory space a | 1225 GASTONIA TECHNOLOGY PARKWAY DALLAS NC 28034
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-10-28, issued 2026-10-29. [HCOC-26-10-28-0730](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/1b7b3353-d40b-4ae5-837f-0bc64a8d161d)
- **Size:** $150,633. Score 3 (distribution, $100k+)
- **Who:** Contractor (Mechanical): GSM Services Inc; Applicant: GSM Services Inc; Contractor (Electrical): Southeastern Industrial Inc
- **Property:** PIN 3547-03-5813, Industrial land use, 15.83 ac, 36,300 SF building, built 2015, tax value $5,830,760. Owner LANXESS PERFORMANCE MATERIALS LLC (C/O ENVALIOR PERFORMANCE MATERIAL LLC, 1225 GASTONIA TECHNOLOGY PKWY, DALLAS NC 28034). Deed Bk 5384 Pg 0559 (SWD), last sale 2022-12-21.
- **Look up at NC SOS:** LANXESS PERFORMANCE MATERIALS LLC, GSM Services Inc
- **Your move:** New construction or site work. Call LANXESS PERFORMANCE MATERIALS LLC (and GSM Services Inc) now: is it spec or build-to-suit, and is the leasing assignment open?

### BLDC-26-06-26-03027 New plumbing installation for amenity building. Will go with Building  | 3050 SOUTH NEW HOPE ROAD GASTONIA NC 28056
- **What:** Plumbing Commercial - Plumbing. Status: Void. Applied 2026-09-29, issued not yet. [STC-26-09-29-04516](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/58d7e9ac-c04d-4810-90b1-aad9ad1f7731)
- **Size:** $75,400. Score 2 (cooler)
- **Who:** Applicant: Service Plumbing of Charlotte
- **Property:** PIN 3564-86-1011, Homeowner Association land use, 1.56 ac. Owner AVALON COMMUNITY ASSOCIATION INC (1616 CLEVELAND AVE, CHARLOTTE NC 28203). Deed Bk 5618 Pg 1348 (SWD), last sale 2026-02-12.
- **Look up at NC SOS:** AVALON COMMUNITY ASSOCIATION INC
- **Your move:** New construction or site work. Call AVALON COMMUNITY ASSOCIATION INC (and Service Plumbing of Charlotte) now: is it spec or build-to-suit, and is the leasing assignment open? It sold recently (2026-02-12). A new owner may be repositioning it, so offer leasing.

### BLDC-26-07-16-03048 omplete wiring of new 7-Brew prefabricated building according to plans | 702 WEST TRADE STREET DALLAS NC 28034
- **What:** Electrical - Commercial - Electrical. Status: Denied. Applied 2026-10-22, issued not yet. [STC-26-10-22-04566](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/64ceed56-9d2b-40d4-917f-3c7c1dd7ec93)
- **Size:** $40,450. Score 2 (cooler)
- **Who:** Applicant: Patrick Coble
- **Property:** PIN 3547-87-5453, Commercial Land land use, 1.07 ac. Owner WOODHAVEN DALLAS LLC (6101 CARNEGIE BOULEVARD, SUITE 150, CHARLOTTE NC 28209). Deed .
- **Look up at NC SOS:** WOODHAVEN DALLAS LLC
- **Your move:** New construction or site work. Call WOODHAVEN DALLAS LLC (and Patrick Coble) now: is it spec or build-to-suit, and is the leasing assignment open?

### applicant needs to be added to the master permit for this project, BLDC-26-07-13-03046 Ins | 200 BEATTY DRIVE BELMONT NC 28012
- **What:** Mechanical - Commercial - Mechanical. Status: Denied. Applied 2026-10-21, issued not yet. [STC-26-10-21-04560](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/ea57aa70-383e-4d88-a9cf-40f1d658e34d)
- **Size:** $19,900. Score 2 (cooler)
- **Who:** Applicant: Precision Bevo Llc
- **Property:** PIN 3595-55-1313, Conv Store/Gas Station land use, 2.27 ac, 1,500 SF building, built 1993, tax value $824,110. Owner SOUTHERN BENEDICTINE SOCIETY (C/O BELMONT ABBEY, 100 BELMONT MT HOLLY RD, BELMONT NC 28012). Deed Bk 0265 Pg 0055 (WD), last sale 1966-06-01.
- **Look up at NC SOS:** Precision Bevo Llc
- **Your move:** New construction or site work. Call SOUTHERN BENEDICTINE SOCIETY (and Precision Bevo Llc) now: is it spec or build-to-suit, and is the leasing assignment open?

### replace like for like for one walk in cooler condenser | 1770 OAK HOLLOW ROAD GASTONIA NC 28054
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-10-30, issued 2026-10-30. [HCOC-26-10-30-0732](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/bbc89595-f56d-4534-b8b1-b5d8dc251fa5)
- **Size:** $10,800. Score 2 (cooler)
- **Who:** Contractor (Mechanical): MOORE'S ELECTRICAL & MECHANICAL; Contractor (Mechanical): Moore's Electrical & Mechanical Construction, Inc.; Contractor (Electrical): Moore's Electrical & Mechanical Construction, Inc.; Applicant: Moores Electrical and Mechanical
- **Property:** PIN 3556-66-6528, Retirement/Rest Home land use, 5.0 ac, 33,721 SF building, built 1993, tax value $3,821,410. Owner OHI ASSET GASTONIA LP (C/O OMEGA HEALTHCARE INVESTORS INC, 303 INTERNATIONAL CIRCLE SUITE 200, HUNT VALLEY MD 21030). Deed Bk 5380 Pg 2062 (SWD), last sale 2022-12-02 for $12,605,000.
- **Look up at NC SOS:** OHI ASSET GASTONIA LP
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start. The owner is out of state (MD). Pitch landlord rep or a BOV.

### 408 Brook St Construction Plans | 408 BROOK STREET BELMONT NC 28012
- **What:** NR - Erosion Industrial - NR - Industrial. Status: Issued. Applied 2026-10-23, issued 2026-10-30. [EC-26-10-23-02051](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/263f88aa-df9f-4c85-9760-598ab76abea0)
- **Size:** no valuation, site work 1.2 ac of 8.66 ac disturbed. Score 2 (industrial)
- **Who:** Financial Responsible Party: Lynddahl Telecom America Inc.; Builder: Regional Construction Services, Inc; Applicant: Matthew Graham
- **Property:** PIN 3594-48-2825, Industrial land use, 6.14 ac, 54,600 SF building, built 2002, tax value $3,367,310. Owner SSI 408 BROOK NC PROPERTY LLC (ATTN: PRESIDENT, 71 COMMERCIAL STREET #266, BOSTON MA 02109). Deed Bk 5673 Pg 0337 (NWD), last sale 2026-09-29.
- **Look up at NC SOS:** SSI 408 BROOK NC PROPERTY LLC, Lynddahl Telecom America Inc., Regional Construction Services, Inc
- **Your move:** New construction or site work. Call SSI 408 BROOK NC PROPERTY LLC (and Regional Construction Services, Inc) now: is it spec or build-to-suit, and is the leasing assignment open? The owner is out of state (MA). Pitch landlord rep or a BOV. It sold recently (2026-09-29). A new owner may be repositioning it, so offer leasing.

## Other commercial work on industrial parcels

The keyword scorer didn't tag these, but the county classes the parcel as industrial. That's a sign the operator is investing in the building.

### Avient Intellipak Replacement | 1101 HIGHWAY 27 SOUTH STANLEY NC 28164
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-09-03, issued 2026-09-03. [HCOC-26-09-03-0683](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/c95a1bcd-a2e2-4c7b-a220-611f5b5284a6)
- **Size:** $319,640. Score 2 ($250k+)
- **Who:** Applicant: Climate Systems, LLC.; Contractor (Mechanical): Climate Systems Inc; Contractor (Electrical): Climate Systems Inc; Applicant: Climate Systems LLC
- **Property:** PIN 3588-06-7124, Industrial land use, 26.1 ac, 136,997 SF building, built 1989, tax value $6,308,280. Owner PAPAMANUEL HOLDINGS LLC (1101 S HIGHWAY 27, STANLEY NC 28164). Deed Bk 5013 Pg 0033 (SWD), last sale 2018-11-28 for $6,853,000.
- **Look up at NC SOS:** PAPAMANUEL HOLDINGS LLC, Climate Systems Inc, Climate Systems, LLC.
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### BLDC-26-04-06-02917 Installing new packaged HVAC unit, as well as new ductwork and insulat | 105 WOLFPACK ROAD GASTONIA NC 28056
- **What:** Mechanical - Commercial - Mechanical. Status: Void. Applied 2026-10-07, issued not yet. [STC-26-10-07-04530](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/4280074c-45b0-44cb-8c80-63f6aa353651)
- **Size:** $150,567. Score 1 ($100k+)
- **Who:** Applicant: Nick Chrisco
- **Property:** PIN 3542-37-8623, Industrial land use, 2.52 ac, 30,945 SF building, built 1973, tax value $705,680. Owner BINGHAM PROPERTIES LLC (323 DOVER RD, KINGS MTN NC 28086). Deed Bk 4346 Pg 1032 (WD), last sale 2007-08-17 for $800,000.
- **Look up at NC SOS:** BINGHAM PROPERTIES LLC
- **Your move:** New construction or site work. Call BINGHAM PROPERTIES LLC (and Nick Chrisco) now: is it spec or build-to-suit, and is the leasing assignment open?

### New addition to existing GNT Plant | 1 ONE EXBERRY DRIVE DALLAS NC 28034
- **What:** ZN - Addition (Zoning Commercial) - ZN - Addition. Status: Issued. Applied 2026-10-06, issued 2026-10-27. [ZONC-26-10-06-00245](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/7e5a9619-a0a2-47cb-99b5-40e8aafa827e)
- **Size:** no valuation. Score 1 (addition)
- **Who:** Applicant: Merriman Schmitt Architects; Owner: Storey PM
- **Property:** PIN 3537-69-3563, Industrial land use, 49.66 ac, 76,098 SF building, built 2021, tax value $8,495,540. Owner GNT NORTH AMERICA LLC (1 EXBERRY DR, DALLAS NC 28034). Deed Bk 5164 Pg 0818 (SWD), last sale 2020-10-14.
- **Look up at NC SOS:** GNT NORTH AMERICA LLC
- **Your move:** An owner-user is expanding in place. Ask GNT NORTH AMERICA LLC about overflow warehouse needs or a move if the site maxes out.

### Replacement of three 15-ton systems with three new HP systems Including replacement of lin | 1518 COSTNER SCHOOL ROAD BESSEMER CITY NC 28016
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-09-04, issued 2026-09-04. [HCOC-26-09-04-0686](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/b78b4c74-2a01-4754-b6ec-b3c3710f1906)
- **Size:** $84,091. Score 0 (no keywords)
- **Who:** Contractor (Mechanical): GSM Services Inc; Applicant: GSM Services Inc; Contractor (Electrical): M.D. Bridges Electrical Services Inc
- **Property:** PIN 3538-42-7143, Industrial land use, 3.01 ac, 2,400 SF building, built 1959, tax value $491,250. Owner PACOR INC (PROPERTY TAX DEPT, 333 RISING SUN RD, BORDENTOWN NJ 08505). Deed Bk CORP Pg MERG (CB), last sale 2011-02-01.
- **Look up at NC SOS:** PACOR INC, GSM Services Inc
- **Your move:** New construction or site work. Call PACOR INC (and GSM Services Inc) now: is it spec or build-to-suit, and is the leasing assignment open? The owner is out of state (NJ). Pitch landlord rep or a BOV.

### Change out package units for qty.6 -5 ton split systems | 170 TARHEEL DRIVE GASTONIA NC 28056
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-09-21, issued 2026-09-24. [HCOC-26-09-21-0701](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/c3f914d0-f9d5-418d-811e-42cfcbc43d23)
- **Size:** $58,000. Score 0 (no keywords)
- **Who:** Contractor (Mechanical): AIRTECHS MECHANICAL services Inc; Applicant: AIRTECHS MECHANICAL services Inc; Contractor (Electrical): *Zapp Electric; Applicant: Airtechs Mechanical Services, Inc
- **Property:** PIN 3542-46-0492, Industrial land use, 1.61 ac, 34,660 SF building, built 1996, tax value $781,620. Owner AMERICAN FORMS MANUFACTURING (170 TARHEEL DRIVE, GASTONIA NC 28056). Deed Bk 2455 Pg 0649 (WD), last sale 1995-05-18 for $27,500.
- **Look up at NC SOS:** AIRTECHS MECHANICAL services Inc
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### Install (2) Cook 25000 CFM Roof mount exhaust fans | 2408 FORBES ROAD GASTONIA NC 28056
- **What:** Mechanical - Commercial - Mechanical. Status: Issued. Applied 2026-10-22, issued 2026-10-22. [STC-26-10-22-04567](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/2fdbdc3c-1b95-4103-b71a-d30b31cef1b3)
- **Size:** $30,618. Score 0 (no keywords)
- **Who:** Contractor (Mechanical): Hoffman Mechanical Solutions; Applicant: Jose Morales
- **Property:** PIN 3543-10-5190, Industrial land use, 24.48 ac, 199,200 SF building, built 1994, tax value $8,967,570. Owner IFAB PROPERTIES LLC (5301 NW 74TH AVENUE, SUITE 200, MIAMI FL 33166). Deed Bk 5458 Pg 1178 (NWD), last sale 2024-02-01.
- **Look up at NC SOS:** IFAB PROPERTIES LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start. The owner is out of state (FL). Pitch landlord rep or a BOV.

### Please resubmit for a Commercial HVAC Change Out permit for this project. change out from  | 1236 INDUSTRIAL AVENUE GASTONIA NC 28054
- **What:** Mechanical - Commercial - Mechanical. Status: Denied. Applied 2026-10-13, issued not yet. [STC-26-10-13-04542](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/8b4fb11c-fe73-4e6e-8d86-e89d8663bfd4)
- **Size:** $30,000. Score 0 (no keywords)
- **Who:** Contractor (Mechanical): Spearman Heat and Cooling, Inc; Applicant: Spearman Heat and Cooling, Inc
- **Property:** PIN 3556-50-2226, Industrial land use, 2.32 ac, 64,670 SF building, built 1961, tax value $1,396,320. Owner 1236 INDUSTRIAL AVE LLC (605 LEXINGTON AVENUE, SUITE 100, CHARLOTTE NC 28203). Deed Bk 5478 Pg 0650 (SWD), last sale 2024-05-14 for $3,350,000.
- **Look up at NC SOS:** 1236 INDUSTRIAL AVE LLC, Spearman Heat and Cooling, Inc
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### Temporary Electrical Service to Jobsite trailers | 1 ONE EXBERRY DRIVE DALLAS NC 28034
- **What:** Electrical - Commercial - Electrical. Status: Issued. Applied 2026-10-21, issued 2026-10-29. [STC-26-10-21-04564](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/ddd753af-28f4-429f-bde0-e0803849c31b)
- **Size:** $15,000. Score 0 (no keywords)
- **Who:** Applicant: Jonathan "Matt" Anderson; Contractor (Electrical): Jonathan "Matt" Anderson
- **Property:** PIN 3537-69-3563, Industrial land use, 49.66 ac, 76,098 SF building, built 2021, tax value $8,495,540. Owner GNT NORTH AMERICA LLC (1 EXBERRY DR, DALLAS NC 28034). Deed Bk 5164 Pg 0818 (SWD), last sale 2020-10-14.
- **Look up at NC SOS:** GNT NORTH AMERICA LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### installation of 24K BTU Daikin Mini split | 100 BRICKYARD ROAD MOUNT HOLLY NC 28120
- **What:** Mechanical - Commercial - Mechanical. Status: Complete. Applied 2026-10-07, issued 2026-10-08. [STC-26-10-07-04532](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/ca1c3562-155b-44cc-a10a-06407b68cee1)
- **Size:** $9,500. Score 0 (no keywords)
- **Who:** Contractor (Mechanical): Roland Black Services; Applicant: Roland Black Services
- **Property:** PIN 3597-31-3630, Industrial land use, 2.73 ac, 23,848 SF building, built 2004, tax value $907,630. Owner CARA LLC (P O BOX 505, MT HOLLY NC 28120). Deed Bk SECOF Pg STATE (CB), last sale 2006-12-19.
- **Look up at NC SOS:** CARA LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### installation of 24K BTU Daikin Mini split | 100 BRICKYARD ROAD MOUNT HOLLY NC 28120
- **What:** Electrical - Commercial - Electrical. Status: Issued. Applied 2026-10-07, issued 2026-10-08. [STC-26-10-07-04531](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/2fb181d7-798d-43aa-97e2-a62939f55856)
- **Size:** $9,500. Score 0 (no keywords)
- **Who:** Applicant: Roland Black Services; Contractor (Electrical): Jacob Sain
- **Property:** PIN 3597-31-3630, Industrial land use, 2.73 ac, 23,848 SF building, built 2004, tax value $907,630. Owner CARA LLC (P O BOX 505, MT HOLLY NC 28120). Deed Bk SECOF Pg STATE (CB), last sale 2006-12-19.
- **Look up at NC SOS:** CARA LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### LIKE FOR LIKE CHANGEOUT-REPLACE 1.5 TON SPLIT HEAT PUMP SERVING SHIPPING OFFICE | 141 ROBINS STREET LOWELL NC 28098
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-10-01, issued 2026-10-01. [HCOC-26-10-01-0707](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/542f0912-aea8-4c37-a1e5-5c57cab3cf46)
- **Size:** $6,370. Score 0 (no keywords)
- **Who:** Contractor (Mechanical): NATIVE AIR INC.; Applicant: NATIVE AIR INC.; Contractor (Electrical): Deaver Electric
- **Property:** PIN 3575-15-2941, Industrial land use, 3.94 ac, 76,362 SF building, built 1984, tax value $2,564,680. Owner ROBINS STREET LLC (2190 W BATES AVENUE, ENGLEWOOD CO 80110). Deed Bk 5606 Pg 2232 (WAR), last sale 2025-12-16 for $6,270,000.
- **Look up at NC SOS:** ROBINS STREET LLC, NATIVE AIR INC.
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start. The owner is out of state (CO). Pitch landlord rep or a BOV. It sold recently (2025-12-16, $6,270,000). A new owner may be repositioning it, so offer leasing.

### 4 ton gas Pak change out - like for like | 3626 DALLAS HIGH SHOALS HIGHWAY DALLAS NC 28034
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-09-24, issued 2026-09-25. [HCOC-26-09-24-0703](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/f4066360-a229-4952-93b6-d53385b0a156)
- **Size:** $5,800. Score 0 (no keywords)
- **Who:** Contractor (Electrical): ElectriComm Solutions Inc; Contractor (Mechanical): C & C Heating, Cooling & Insulation, LLC; Applicant: C & C Heating, Cooling & Insulation, LLC
- **Property:** PIN 3548-42-4309, Industrial land use, 2.77 ac, 52,880 SF building, built 1955. Owner STACK HOLDINGS LLC (3626 DALLAS HIGH SHOALS HWY, DALLAS NC 28034). Deed .
- **Look up at NC SOS:** STACK HOLDINGS LLC, ElectriComm Solutions Inc, C & C Heating, Cooling & Insulation, LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### BLDC-26-04-29-02953 Installation of electrical for accessory building. | 130 MARIPOSA ROAD STANLEY NC 28164
- **What:** Electrical - Commercial - Electrical. Status: Denied. Applied 2026-10-14, issued not yet. [STC-26-10-14-04548](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/63a36417-ae28-429a-b916-ae848e6f24ad)
- **Size:** $5,000. Score 0 (no keywords)
- **Who:** Applicant: Haley Cannon; Applicant: E AND G LANDSCAPING
- **Property:** PIN 3579-56-1310, Industrial Land land use, 7.91 ac, tax value $158,800. Owner CATAWBA GROUP PROPERTIES LLC (156 SMITH CLEMMER RD, MT HOLLY NC 28120). Deed Bk 5618 Pg 0698 (WAR), last sale 2026-02-11 for $540,000.
- **Look up at NC SOS:** CATAWBA GROUP PROPERTIES LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start. It sold recently (2026-02-11, $540,000). A new owner may be repositioning it, so offer leasing.

### relocating 100 AMP service to new customer supplied pole- all new grounding. Includes runn | 2088 WEST DAVIDSON AVENUE GASTONIA NC 28052
- **What:** Electrical - Commercial - Electrical. Status: Issued. Applied 2026-09-14, issued 2026-09-15. [STC-26-09-14-04501](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/f31fb512-c10a-4aef-a427-f6dfdbc301e3)
- **Size:** $4,400. Score 0 (no keywords)
- **Who:** Applicant: J & E Electric of South Carolina Inc; Contractor (Electrical): J & E Electric of South Carolina Inc
- **Property:** PIN 3546-15-4388, Industrial land use, 7.33 ac, 4,000 SF building, built 1989, tax value $454,750. Owner BRADLEY FAMILY TRUST (137 BRADLEY TRAIL, GASTONIA NC 28056). Deed Bk 5643 Pg 2561 (WAR), last sale 2026-05-28.
- **Look up at NC SOS:** BRADLEY FAMILY TRUST, J & E Electric of South Carolina Inc
- **Your move:** New construction or site work. Call BRADLEY FAMILY TRUST (and J & E Electric of South Carolina Inc) now: is it spec or build-to-suit, and is the leasing assignment open? It sold recently (2026-05-28). A new owner may be repositioning it, so offer leasing.

### Replace 100 amp service for billboard | 5015 YORK HIGHWAY GASTONIA NC 28052
- **What:** Electrical - Commercial - Electrical. Status: Complete. Applied 2026-09-03, issued 2026-09-03. [STC-26-09-03-04478](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/c847a8a0-0ec4-45e8-92d7-d5c5b92b2086)
- **Size:** $3,750. Score 0 (no keywords)
- **Who:** Contractor (Electrical): On Time Electrical LLC; Applicant: One Hour Heating and Air(DBA)
- **Property:** PIN 3542-18-5712, Industrial land use, 6.86 ac, 31,625 SF building, built 1981, tax value $634,700. Owner BUCKNER PROPERTIES LLC (2054 KENDRICK RD, GASTONIA NC 28056). Deed Bk 5438 Pg 0569 (NDT), last sale 2023-10-03.
- **Look up at NC SOS:** BUCKNER PROPERTIES LLC, On Time Electrical LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

...and 7 more in permits.csv.

## Problems

- None.
