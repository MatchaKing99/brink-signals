# SANDBOX: Gaston County permit pipeline, 2026-10-30

Source: Gaston County Citizen Self Service (Tyler EnerGov), public search API, no login. Window: permits issued or applied in the last 60 days.

| Step | Result |
|---|---|
| Pulled (issued or applied in window) | 2170 |
| Commercial / industrial permit types | 368 (130 building or site work, the rest trade permits) |
| Detail records fetched | 368 |
| Tagged industrial by the bot's scorer | 22 |
| **Industrial at the bot's digest threshold (score ≥ 5)** | **12** |
| Other commercial work on industrial-use parcels | 19 |
| Matched to a county parcel | 360 of 368 |
| API calls to the portal | 853 |
| NC Secretary of State lookups | blocked by a Cloudflare bot challenge (HTTP 403), so look these up by hand |

**Compared with the live bot:** it has 0 Gaston permits on record (Gaston permits currently need a manual export), so every permit below is one it missed.

## Industrial permits

Everything the bot's scorer tags as industrial. ⭐ = score 5+, the bar for the weekly digest.

### ⭐ Lane Seven Expansion - Demo demising wall, modify existing office and expand 716 SF with n | 3145 ABERDEEN BOULEVARD GASTONIA NC 28054
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Documents Needed. Applied 2026-10-23, issued not yet. [BLDC-26-10-23-03187](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/10db333a-d6de-4fa3-ac00-88b7fd8ecf5e)
- **Size:** $354,031, 6,393 SF of work, occupancy S-1 Storage. Score 12 (rack, warehouse, expansion, storage, high pile, industrial occupancy, $250k+)
- **Who:** owner of record NP GASTONIA INDUSTRIAL 4 LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3565-79-0211, Distribution Warehouse land use, 20.41 ac, 239,559 SF building, built 2022, tax value $17,420,680. Owner NP GASTONIA INDUSTRIAL 4 LLC (3315 NORTH OAK TRAFFICWAY, KANSAS CITY MO 64116). Deed Bk 5348 Pg 0536 (SWD), last sale 2022-06-30.
- **Look up at NC SOS:** NP GASTONIA INDUSTRIAL 4 LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. The owner is out of state (MO). Pitch landlord rep or a BOV.

### ⭐ New addition to existing facility - footing and foundation only and underslab utilities | 1 ONE EXBERRY DRIVE DALLAS NC 28034
- **What:** Foundation Only (Commercial) - Foundation Only (Addition). Status: Issued. Applied 2026-09-17, issued 2026-10-28. [BLDC-26-09-17-03139](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/2669314b-6daf-4697-a8d0-4881e0d149b9)
- **Size:** $2,350,000, 78,497 SF of work, occupancy F-1 Factory / B Business. Score 10 (addition, industrial occupancy, 50k+ SF, $1M+)
- **Who:** owner of record GNT NORTH AMERICA LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3537-69-3563, Industrial land use, 49.66 ac, 76,098 SF building, built 2021, tax value $8,495,540. Owner GNT NORTH AMERICA LLC (1 EXBERRY DR, DALLAS NC 28034). Deed Bk 5164 Pg 0818 (SWD), last sale 2020-10-14.
- **Look up at NC SOS:** GNT NORTH AMERICA LLC
- **Your move:** An owner-user is expanding in place. Ask GNT NORTH AMERICA LLC about overflow warehouse needs or a move if the site maxes out.

### ⭐ FIRE SPRINKLERS | 231 SOUTHRIDGE PARKWAY BESSEMER CITY NC 28016
- **What:** Sprinkler - Plumbing - Plumbing (New). Status: In Review. Applied 2026-10-13, issued not yet. [SPL-26-10-13-0141](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/d45f9cea-c6b4-4f6a-a490-8fce8d10e847)
- **Size:** $870,375, 299,711 SF of work, occupancy S-1 Storage. Score 10 (storage, sprinkler, industrial occupancy, 50k+ SF, $250k+)
- **Who:** owner of record AMAZON.COM SERVICES LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3526-54-2972, Industrial Land land use, 48.25 ac, tax value $863,430. Owner AMAZON.COM SERVICES LLC (C/O AMAZON PROPERTY TAX, PO BOX 80416, SEATTLE WA 98108). Deed Bk 5267 Pg 1389 (SWD), last sale 2021-09-17 for $3,229,500.
- **Look up at NC SOS:** AMAZON.COM SERVICES LLC
- **Your move:** New construction or site work. Call AMAZON.COM SERVICES LLC now: is it spec or build-to-suit, and is the leasing assignment open? The owner is out of state (WA). Pitch landlord rep or a BOV.

### ⭐ New Storage Building per plans | 134 BRICKYARD ROAD MOUNT HOLLY NC 28120
- **What:** New Building (Commercial) - New (New). Status: Issued. Applied 2026-09-23, issued 2026-10-19. [BLDC-26-09-23-03147](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/f765eb93-dda4-494c-a0d1-d1c4362b3fca)
- **Size:** $191,226, 50,272 SF of work, occupancy S-1 Storage. Score 9 (new building, storage, industrial occupancy, 50k+ SF, $100k+)
- **Who:** owner of record FLACHOFSKY STORAGE LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3597-22-5584, Industrial Land land use, 0.8 ac. Owner FLACHOFSKY STORAGE LLC (120 BRICKYARD ROAD, MOUNT HOLLY NC 28120). Deed .
- **Look up at NC SOS:** FLACHOFSKY STORAGE LLC
- **Your move:** New construction or site work. Call FLACHOFSKY STORAGE LLC now: is it spec or build-to-suit, and is the leasing assignment open?

### ⭐ New Building per plans | 142 BRICKYARD ROAD MOUNT HOLLY NC 28120
- **What:** New Building (Commercial) - New (New). Status: Issued. Applied 2026-09-23, issued 2026-10-19. [BLDC-26-09-23-03148](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/44d88a62-55fa-48e9-afc3-aad7dfb8da2e)
- **Size:** $191,226, 50,264 SF of work, occupancy S-2 Storage. Score 9 (new building, storage, industrial occupancy, 50k+ SF, $100k+)
- **Who:** owner of record FLACHOFSKY STORAGE LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3597-22-3767, Industrial Land land use, 0.81 ac. Owner FLACHOFSKY STORAGE LLC (120 BRICKYARD ROAD, MOUNT HOLLY NC 28120). Deed .
- **Look up at NC SOS:** FLACHOFSKY STORAGE LLC
- **Your move:** New construction or site work. Call FLACHOFSKY STORAGE LLC now: is it spec or build-to-suit, and is the leasing assignment open?

### ⭐ Kyle Spec - scope will include 1,000 SF new office with a 53,141 SF existing storage wareh | 1910 KYLE COURT GASTONIA NC 28052
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Issued. Applied 2026-08-24, issued 2026-10-13. [BLDC-26-08-24-03100](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/0ea4c364-fcd8-42f0-81ca-a76620dc29e5)
- **Size:** $250,000, 1,000 SF of work, occupancy S-1 Storage / B Business. Score 8 (warehouse, storage, industrial occupancy, $250k+)
- **Who:** owner of record KYLE COURT LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3536-13-5985, Distribution Warehouse land use, 3.23 ac, 54,000 SF building, built 1999, tax value $1,614,770. Owner KYLE COURT LLC (805 TRADE ST NW SUITE 101, CONCORD NC 28027). Deed Bk 4879 Pg 2295 (WD), last sale 2016-11-16 for $1,495,000.
- **Look up at NC SOS:** KYLE COURT LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale.

### ⭐ CanSource Equipment Additions | 1115 CRAWFORD OAKS DRIVE GASTONIA NC 28056
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Other). Status: Complete. Applied 2026-08-06, issued 2026-08-31. [BLDC-26-08-06-03075](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/afc4c1c7-dc07-4b3e-a9b6-626ee06162e7)
- **Size:** $50,000, 156,052 SF of work, occupancy F-1 Factory / S-1 Storage. Score 8 (addition, storage, industrial occupancy, 50k+ SF)
- **Who:** owner of record CRP/CHI OAKS COMMERCE CENTER OWNER LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3585-49-4255, Distribution Warehouse land use, 43.5 ac, 468,712 SF building, built 2023, tax value $34,876,110. Owner CRP/CHI OAKS COMMERCE CENTER OWNER LLC (1001 PENNSYLVANIA AVE NW STE 220S, WASHINGTON DC 20004). Deed Bk 5379 Pg 0600 (SWD), last sale 2022-11-22.
- **Look up at NC SOS:** CRP/CHI OAKS COMMERCE CENTER OWNER LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. The owner is out of state (DC). Pitch landlord rep or a BOV.

### ⭐ Vertical Demolition of plant and removal of slabs and foundations - crush material onsite  | 103 EAST WOODROW AVENUE BELMONT NC 28012
- **What:** Demolition (Commercial) - Commercial (Demolition). Status: Documents Needed. Applied 2026-10-29, issued not yet. [DEMO-26-10-29-00785](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/27f0bdb5-7287-4e6f-8d55-426ebdae67c7)
- **Size:** $178,432, 158,373 SF of work, occupancy F-1 Factory. Score 7 (industrial occupancy, 50k+ SF, $100k+)
- **Who:** owner of record PARKDALE AMERICA LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3595-21-7000, Industrial land use, 10.14 ac, 5,000 SF building, built 1930, tax value $2,548,790. Owner PARKDALE AMERICA LLC (JENNIFER GIACOBBE, PO BOX 1787, GASTONIA NC 28053). Deed Bk 2739 Pg 42 (SPL), last sale 1997-12-30.
- **Look up at NC SOS:** PARKDALE AMERICA LLC
- **Your move:** New construction or site work. Call PARKDALE AMERICA LLC now: is it spec or build-to-suit, and is the leasing assignment open?

### ⭐ Install a 10x 25 cooler on the rear of an existing outdoor work shed on a concrete pad | 1 ONE EXBERRY DRIVE DALLAS NC 28034
- **What:** Building Permit Request: Commercial Accessory Structure - Accessory Structure (Addition). Status: Documents Needed. Applied 2026-09-15, issued not yet. [BLDC-26-09-15-03135](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/673a29ac-ef60-4852-9c05-cf6266fd2926)
- **Size:** $114,380, 250 SF of work, occupancy S-2 Storage. Score 7 (cooler, storage, industrial occupancy, $100k+)
- **Who:** owner of record GNT NORTH AMERICA LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3537-69-3563, Industrial land use, 49.66 ac, 76,098 SF building, built 2021, tax value $8,495,540. Owner GNT NORTH AMERICA LLC (1 EXBERRY DR, DALLAS NC 28034). Deed Bk 5164 Pg 0818 (SWD), last sale 2020-10-14.
- **Look up at NC SOS:** GNT NORTH AMERICA LLC
- **Your move:** An owner-user is expanding in place. Ask GNT NORTH AMERICA LLC about overflow warehouse needs or a move if the site maxes out.

### ⭐ New to Dallas and received a remodel permit from the city for the provided plans attached. | 191 GIBSON COURT DALLAS NC 28034
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Documents Needed. Applied 2026-09-23, issued not yet. [BLDC-26-09-23-03146](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/fae0ba02-e3d2-41ef-b503-15c0e9e188f3)
- **Size:** $65,000, 3,355 SF of work, occupancy F-2 Factory / S-2 Storage. Score 7 (warehouse, addition, storage, industrial occupancy)
- **Who:** owner of record ROWKEN HOLDINGS LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3548-62-3323, Industrial land use, 3.2 ac, 11,500 SF building, built 1996, tax value $775,420. Owner ROWKEN HOLDINGS LLC (3306 N NC HIGHWAY BUSINESS 16, DENVER NC 28037). Deed Bk 5640 Pg 1007 (SWD), last sale 2026-05-13 for $1,375,000.
- **Look up at NC SOS:** ROWKEN HOLDINGS LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. It sold recently (2026-05-13, $1,375,000). A new owner may be repositioning it, so offer leasing.

### ⭐ JAK Machine Shop - Adding 2,520 sq feet addition to existing building | 3215 BESSEMER CITY ROAD BESSEMER CITY NC 28016
- **What:** Building Permit Request: Commercial Addition - Addition (Addition). Status: Issued. Applied 2026-09-18, issued 2026-10-06. [BLDC-26-09-18-03140](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/0b5abeaf-5235-4dd4-90f1-4013e4f3b0e9)
- **Size:** $60,000, 2,520 SF of work, occupancy S-2 Storage. Score 5 (addition, storage, industrial occupancy)
- **Who:** owner of record DEATON JOHNNY MACK & DEATON KRISTY BEAM. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3526-67-7008, Service Shop land use, 1.35 ac, 4,012 SF building, built 1964, tax value $159,040. Owner DEATON JOHNNY MACK & DEATON KRISTY BEAM (334 JIM CLARK RD, BESSEMER CITY NC 28016). Deed Bk 4912 Pg 2421 (WD), last sale 2017-05-24 for $48,000.
- **Your move:** An owner-user is expanding in place. Ask DEATON JOHNNY MACK & DEATON KRISTY BEAM about overflow warehouse needs or a move if the site maxes out.

### ⭐ installation and integration of the new Addressable Fire Alarm Control Panel, Annunciator, | 920 EAST FIRST STREET CHERRYVILLE NC 28021
- **What:** Fire Alarm (Electrical) - Electrical (Other). Status: Issued. Applied 2026-06-17, issued 2026-10-22. [FA-26-06-17-0227](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/3e85a4cd-f92c-42fe-99fa-c295539270b9)
- **Size:** $33,500, 11,145 SF of work, occupancy F-1 Factory. Score 5 (industrial occupancy, 10k+ SF)
- **Who:** owner of record RIDDLEYS PROPERTIES LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 2690-32-7958, Industrial land use, 10.11 ac, 11,146 SF building, built 1920, tax value $1,114,700. Owner RIDDLEYS PROPERTIES LLC (119 BESS RD, KINGS MTN NC 28086). Deed Bk 4686 Pg 1566 (WD), last sale 2013-07-19.
- **Look up at NC SOS:** RIDDLEYS PROPERTIES LLC
- **Your move:** New construction or site work. Call RIDDLEYS PROPERTIES LLC now: is it spec or build-to-suit, and is the leasing assignment open?

### RDS Lawn Care - Building repairs from vehicle damage (550 sqft area) Scope of work include | 1627 CHARLES RAPER JONAS HIGHWAY MOUNT HOLLY NC 28120
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Issued. Applied 2026-10-28, issued 2026-10-30. [BLDC-26-10-28-03193](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/51fcf9c8-869b-4801-b24e-480f027f1537)
- **Size:** $96,100, 550 SF of work, occupancy S-2 Storage. Score 4 (storage, industrial occupancy)
- **Who:** owner of record MOUNTAIN CANDY PROPERTIES LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3587-79-5458, Service Shop land use, 0.21 ac, 2,400 SF building, built 1982, tax value $79,770. Owner MOUNTAIN CANDY PROPERTIES LLC (702 HANNA WOODS, CRAMERTON NC 28032). Deed Bk 5425 Pg 2029 (SWD), last sale 2023-07-31 for $135,000.
- **Look up at NC SOS:** MOUNTAIN CANDY PROPERTIES LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale.

### adding an equipment room to the existing building | 1230 GASTONIA TECHNOLOGY PARKWAY DALLAS NC 28034
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Other). Status: Documents Needed. Applied 2026-10-07, issued not yet. [BLDC-26-10-07-03168](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/c5a00c52-05a4-4643-813d-9b06cf23eaad)
- **Size:** $60,000, 221 SF of work, occupancy F-2 Factory / S-2 Storage. Score 4 (storage, industrial occupancy)
- **Who:** owner of record OWENS CORNING COMPOSITE MATERIALS II LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3547-14-3173, Industrial land use, 44.1 ac, 199,844 SF building, built 2015, tax value $17,736,990. Owner OWENS CORNING COMPOSITE MATERIALS II LLC (ATTN: COMMERCIAL REAL ESTATE, ONE OWENS CORNING PARKWAY, TOLEDO OH 43659). Deed Bk 5585 Pg 0868 (SWD), last sale 2025-09-16.
- **Look up at NC SOS:** OWENS CORNING COMPOSITE MATERIALS II LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. The owner is out of state (OH). Pitch landlord rep or a BOV. It sold recently (2025-09-16). A new owner may be repositioning it, so offer leasing.

### First Assembly - 30x40 Accessory Storage Building | 613 SOUTH MYRTLE SCHOOL ROAD GASTONIA NC 28052
- **What:** Building Permit Request: Commercial Accessory Structure - Accessory Structure (New). Status: Documents Needed. Applied 2026-09-15, issued not yet. [BLDC-26-09-15-03134](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/24657fc0-779c-4020-9297-43e08aa5351d)
- **Size:** $33,824, 1,200 SF of work, occupancy S-1 Storage. Score 4 (storage, industrial occupancy)
- **Who:** owner of record FIRST ASSEMBLY OF GOD OF GAST. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3535-53-6914, Church/Religious land use, 47.92 ac, 44,794 SF building, built 2007. Owner FIRST ASSEMBLY OF GOD OF GAST (N C DISTRICT COUNCIL, P O BOX 459, SELMA NC 27576). Deed Bk 5658 Pg 1245 (AOC), last sale 2026-07-28.
- **Your move:** New construction or site work. Call FIRST ASSEMBLY OF GOD OF GAST now: is it spec or build-to-suit, and is the leasing assignment open? It sold recently (2026-07-28). A new owner may be repositioning it, so offer leasing.

### Remove existing toilet and sink. Make restroom larger to meet Handicap code. Install handi | 101 NORTH WEBB STREET GASTONIA NC 28052
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Documents Needed. Applied 2026-09-28, issued not yet. [BLDC-26-09-28-03152](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/66e873dd-9ea2-46a6-b1df-ab0b6ee4f58b)
- **Size:** $25,000, 106 SF of work, occupancy S-1 Storage. Score 4 (storage, industrial occupancy)
- **Who:** owner of record YELTON JAMES K. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3545-07-6555, Warehouse land use, 0.37 ac, 4,000 SF building, built 1990, tax value $146,850. Owner YELTON JAMES K (8034 CATAWBA COVE DR, BELMONT NC 28012). Deed Bk 3142 Pg 0476 (WD), last sale 2000-10-12 for $100,000.
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale.

### Demo 280 LF of demising wall | 3145 ABERDEEN BOULEVARD GASTONIA NC 28054
- **What:** Demolition (Commercial) - Commercial (Demolition). Status: Documents Needed. Applied 2026-09-22, issued not yet. [DEMO-26-09-22-00776](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/049908e9-1c5f-4c5e-9a5d-e69e2e020ada)
- **Size:** $13,000, 140 SF of work, occupancy S-1 Storage. Score 4 (storage, industrial occupancy)
- **Who:** owner of record NP GASTONIA INDUSTRIAL 4 LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3565-79-0211, Distribution Warehouse land use, 20.41 ac, 239,559 SF building, built 2022, tax value $17,420,680. Owner NP GASTONIA INDUSTRIAL 4 LLC (3315 NORTH OAK TRAFFICWAY, KANSAS CITY MO 64116). Deed Bk 5348 Pg 0536 (SWD), last sale 2022-06-30.
- **Look up at NC SOS:** NP GASTONIA INDUSTRIAL 4 LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start. The owner is out of state (MO). Pitch landlord rep or a BOV.

### Exisiting RTU to be removed. Place DOAS in place. Redo ductwork down to laboratory space a | 1225 GASTONIA TECHNOLOGY PARKWAY DALLAS NC 28034
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-10-28, issued 2026-10-29. [HCOC-26-10-28-0730](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/1b7b3353-d40b-4ae5-837f-0bc64a8d161d)
- **Size:** $150,633. Score 3 (distribution, $100k+)
- **Who:** owner of record LANXESS PERFORMANCE MATERIALS LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3547-03-5813, Industrial land use, 15.83 ac, 36,300 SF building, built 2015, tax value $5,830,760. Owner LANXESS PERFORMANCE MATERIALS LLC (C/O ENVALIOR PERFORMANCE MATERIAL LLC, 1225 GASTONIA TECHNOLOGY PKWY, DALLAS NC 28034). Deed Bk 5384 Pg 0559 (SWD), last sale 2022-12-21.
- **Look up at NC SOS:** LANXESS PERFORMANCE MATERIALS LLC
- **Your move:** New construction or site work. Call LANXESS PERFORMANCE MATERIALS LLC now: is it spec or build-to-suit, and is the leasing assignment open?

### UPDATE FIRE SUPPRESSION SYSTEM IN SPRAY BOOTH. CURRENT SYSTEM OBSOLETE | 1660 PACOLET COURT GASTONIA NC 28052
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (New). Status: Submitted - Online. Applied 2026-10-27, issued not yet. [BLDC-26-10-27-03190](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/b06da196-9fdb-4fbe-8986-8e1928c10ea0)
- **Size:** $25,000, 1,500 SF of work, occupancy H-1 High Hazard. Score 3 (industrial occupancy)
- **Who:** owner of record CRAIG BUSINESS PROPERTIES LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3536-56-8554, Service Shop land use, 7.89 ac, 13,500 SF building, built 1992, tax value $771,040. Owner CRAIG BUSINESS PROPERTIES LLC (1660 PACOLET COURT, GASTONIA NC 28052). Deed Bk 5560 Pg 1109 (SWD), last sale 2025-05-28.
- **Look up at NC SOS:** CRAIG BUSINESS PROPERTIES LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. It sold recently (2025-05-28). A new owner may be repositioning it, so offer leasing.

### In March/April of 2026 we built two walls in our office to segment off a breakroom for emp | 707 CASON ST BELMONT NC 28012
- **What:** Building Permit Request: Commercial Alteration/Remodel - Alteration/Remodel (Remodel). Status: Issued. Applied 2026-08-31, issued 2026-09-23. [BLDC-26-08-31-03111](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/bf4ee505-271d-4f1b-97e1-e8c316f0d51f)
- **Size:** $4,900, 240 SF of work, occupancy F-1 Factory. Score 3 (industrial occupancy)
- **Who:** owner of record EHJH PROPERTIES LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3596-00-1128, Office Warehouse land use, 1.21 ac, 10,390 SF building, built 1996, tax value $383,670. Owner EHJH PROPERTIES LLC (707 CASON STREET, BELMONT NC 28012). Deed Bk 5594 Pg 2116 (SWD), last sale 2025-10-24 for $1,750,000.
- **Look up at NC SOS:** EHJH PROPERTIES LLC
- **Your move:** An upfit usually means a new occupant or an expansion. Ask the GC or owner who the user is; the space that user is leaving may come up for sublease or sale. It sold recently (2025-10-24, $1,750,000). A new owner may be repositioning it, so offer leasing.

### replace like for like for one walk in cooler condenser | 1770 OAK HOLLOW ROAD GASTONIA NC 28054
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-10-30, issued 2026-10-30. [HCOC-26-10-30-0732](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/bbc89595-f56d-4534-b8b1-b5d8dc251fa5)
- **Size:** $10,800. Score 2 (cooler)
- **Who:** owner of record OHI ASSET GASTONIA LP. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3556-66-6528, Retirement/Rest Home land use, 5.0 ac, 33,721 SF building, built 1993, tax value $3,821,410. Owner OHI ASSET GASTONIA LP (C/O OMEGA HEALTHCARE INVESTORS INC, 303 INTERNATIONAL CIRCLE SUITE 200, HUNT VALLEY MD 21030). Deed Bk 5380 Pg 2062 (SWD), last sale 2022-12-02 for $12,605,000.
- **Look up at NC SOS:** OHI ASSET GASTONIA LP
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start. The owner is out of state (MD). Pitch landlord rep or a BOV.

### 408 Brook St Construction Plans | 408 BROOK STREET BELMONT NC 28012
- **What:** NR - Erosion Industrial - NR - Industrial. Status: Issued. Applied 2026-10-23, issued 2026-10-30. [EC-26-10-23-02051](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/263f88aa-df9f-4c85-9760-598ab76abea0)
- **Size:** no valuation, site work 1.2 ac of 8.66 ac disturbed. Score 2 (industrial)
- **Who:** owner of record SSI 408 BROOK NC PROPERTY LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3594-48-2825, Industrial land use, 6.14 ac, 54,600 SF building, built 2002, tax value $3,367,310. Owner SSI 408 BROOK NC PROPERTY LLC (ATTN: PRESIDENT, 71 COMMERCIAL STREET #266, BOSTON MA 02109). Deed Bk 5673 Pg 0337 (NWD), last sale 2026-09-29.
- **Look up at NC SOS:** SSI 408 BROOK NC PROPERTY LLC
- **Your move:** New construction or site work. Call SSI 408 BROOK NC PROPERTY LLC now: is it spec or build-to-suit, and is the leasing assignment open? The owner is out of state (MA). Pitch landlord rep or a BOV. It sold recently (2026-09-29). A new owner may be repositioning it, so offer leasing.

## Other commercial work on industrial parcels

The keyword scorer didn't tag these, but the county classes the parcel as industrial. That's a sign the operator is investing in the building.

### Avient Intellipak Replacement | 1101 HIGHWAY 27 SOUTH STANLEY NC 28164
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-09-03, issued 2026-09-03. [HCOC-26-09-03-0683](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/c95a1bcd-a2e2-4c7b-a220-611f5b5284a6)
- **Size:** $319,640. Score 2 ($250k+)
- **Who:** owner of record PAPAMANUEL HOLDINGS LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3588-06-7124, Industrial land use, 26.1 ac, 136,997 SF building, built 1989, tax value $6,308,280. Owner PAPAMANUEL HOLDINGS LLC (1101 S HIGHWAY 27, STANLEY NC 28164). Deed Bk 5013 Pg 0033 (SWD), last sale 2018-11-28 for $6,853,000.
- **Look up at NC SOS:** PAPAMANUEL HOLDINGS LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### New addition to existing GNT Plant | 1 ONE EXBERRY DRIVE DALLAS NC 28034
- **What:** ZN - Addition (Zoning Commercial) - ZN - Addition. Status: Issued. Applied 2026-10-06, issued 2026-10-27. [ZONC-26-10-06-00245](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/7e5a9619-a0a2-47cb-99b5-40e8aafa827e)
- **Size:** no valuation. Score 1 (addition)
- **Who:** owner of record GNT NORTH AMERICA LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3537-69-3563, Industrial land use, 49.66 ac, 76,098 SF building, built 2021, tax value $8,495,540. Owner GNT NORTH AMERICA LLC (1 EXBERRY DR, DALLAS NC 28034). Deed Bk 5164 Pg 0818 (SWD), last sale 2020-10-14.
- **Look up at NC SOS:** GNT NORTH AMERICA LLC
- **Your move:** An owner-user is expanding in place. Ask GNT NORTH AMERICA LLC about overflow warehouse needs or a move if the site maxes out.

### Replacement of three 15-ton systems with three new HP systems Including replacement of lin | 1518 COSTNER SCHOOL ROAD BESSEMER CITY NC 28016
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-09-04, issued 2026-09-04. [HCOC-26-09-04-0686](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/b78b4c74-2a01-4754-b6ec-b3c3710f1906)
- **Size:** $84,091. Score 0 (no keywords)
- **Who:** owner of record PACOR INC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3538-42-7143, Industrial land use, 3.01 ac, 2,400 SF building, built 1959, tax value $491,250. Owner PACOR INC (PROPERTY TAX DEPT, 333 RISING SUN RD, BORDENTOWN NJ 08505). Deed Bk CORP Pg MERG (CB), last sale 2011-02-01.
- **Look up at NC SOS:** PACOR INC
- **Your move:** New construction or site work. Call PACOR INC now: is it spec or build-to-suit, and is the leasing assignment open? The owner is out of state (NJ). Pitch landlord rep or a BOV.

### Change out package units for qty.6 -5 ton split systems | 170 TARHEEL DRIVE GASTONIA NC 28056
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-09-21, issued 2026-09-24. [HCOC-26-09-21-0701](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/c3f914d0-f9d5-418d-811e-42cfcbc43d23)
- **Size:** $58,000. Score 0 (no keywords)
- **Who:** owner of record AMERICAN FORMS MANUFACTURING. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3542-46-0492, Industrial land use, 1.61 ac, 34,660 SF building, built 1996, tax value $781,620. Owner AMERICAN FORMS MANUFACTURING (170 TARHEEL DRIVE, GASTONIA NC 28056). Deed Bk 2455 Pg 0649 (WD), last sale 1995-05-18 for $27,500.
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### Install (2) Cook 25000 CFM Roof mount exhaust fans | 2408 FORBES ROAD GASTONIA NC 28056
- **What:** Mechanical - Commercial - Mechanical. Status: Issued. Applied 2026-10-22, issued 2026-10-22. [STC-26-10-22-04567](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/2fdbdc3c-1b95-4103-b71a-d30b31cef1b3)
- **Size:** $30,618. Score 0 (no keywords)
- **Who:** owner of record IFAB PROPERTIES LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3543-10-5190, Industrial land use, 24.48 ac, 199,200 SF building, built 1994, tax value $8,967,570. Owner IFAB PROPERTIES LLC (5301 NW 74TH AVENUE, SUITE 200, MIAMI FL 33166). Deed Bk 5458 Pg 1178 (NWD), last sale 2024-02-01.
- **Look up at NC SOS:** IFAB PROPERTIES LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start. The owner is out of state (FL). Pitch landlord rep or a BOV.

### Temporary Electrical Service to Jobsite trailers | 1 ONE EXBERRY DRIVE DALLAS NC 28034
- **What:** Electrical - Commercial - Electrical. Status: Issued. Applied 2026-10-21, issued 2026-10-29. [STC-26-10-21-04564](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/ddd753af-28f4-429f-bde0-e0803849c31b)
- **Size:** $15,000. Score 0 (no keywords)
- **Who:** owner of record GNT NORTH AMERICA LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3537-69-3563, Industrial land use, 49.66 ac, 76,098 SF building, built 2021, tax value $8,495,540. Owner GNT NORTH AMERICA LLC (1 EXBERRY DR, DALLAS NC 28034). Deed Bk 5164 Pg 0818 (SWD), last sale 2020-10-14.
- **Look up at NC SOS:** GNT NORTH AMERICA LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### installation of 24K BTU Daikin Mini split | 100 BRICKYARD ROAD MOUNT HOLLY NC 28120
- **What:** Mechanical - Commercial - Mechanical. Status: Complete. Applied 2026-10-07, issued 2026-10-08. [STC-26-10-07-04532](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/ca1c3562-155b-44cc-a10a-06407b68cee1)
- **Size:** $9,500. Score 0 (no keywords)
- **Who:** owner of record CARA LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3597-31-3630, Industrial land use, 2.73 ac, 23,848 SF building, built 2004, tax value $907,630. Owner CARA LLC (P O BOX 505, MT HOLLY NC 28120). Deed Bk SECOF Pg STATE (CB), last sale 2006-12-19.
- **Look up at NC SOS:** CARA LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### installation of 24K BTU Daikin Mini split | 100 BRICKYARD ROAD MOUNT HOLLY NC 28120
- **What:** Electrical - Commercial - Electrical. Status: Issued. Applied 2026-10-07, issued 2026-10-08. [STC-26-10-07-04531](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/2fb181d7-798d-43aa-97e2-a62939f55856)
- **Size:** $9,500. Score 0 (no keywords)
- **Who:** owner of record CARA LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3597-31-3630, Industrial land use, 2.73 ac, 23,848 SF building, built 2004, tax value $907,630. Owner CARA LLC (P O BOX 505, MT HOLLY NC 28120). Deed Bk SECOF Pg STATE (CB), last sale 2006-12-19.
- **Look up at NC SOS:** CARA LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### LIKE FOR LIKE CHANGEOUT-REPLACE 1.5 TON SPLIT HEAT PUMP SERVING SHIPPING OFFICE | 141 ROBINS STREET LOWELL NC 28098
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-10-01, issued 2026-10-01. [HCOC-26-10-01-0707](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/542f0912-aea8-4c37-a1e5-5c57cab3cf46)
- **Size:** $6,370. Score 0 (no keywords)
- **Who:** owner of record ROBINS STREET LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3575-15-2941, Industrial land use, 3.94 ac, 76,362 SF building, built 1984, tax value $2,564,680. Owner ROBINS STREET LLC (2190 W BATES AVENUE, ENGLEWOOD CO 80110). Deed Bk 5606 Pg 2232 (WAR), last sale 2025-12-16 for $6,270,000.
- **Look up at NC SOS:** ROBINS STREET LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start. The owner is out of state (CO). Pitch landlord rep or a BOV. It sold recently (2025-12-16, $6,270,000). A new owner may be repositioning it, so offer leasing.

### 4 ton gas Pak change out - like for like | 3626 DALLAS HIGH SHOALS HIGHWAY DALLAS NC 28034
- **What:** HVAC Changeout - Commercial Structure - HVAC Changeout. Status: Issued. Applied 2026-09-24, issued 2026-09-25. [HCOC-26-09-24-0703](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/f4066360-a229-4952-93b6-d53385b0a156)
- **Size:** $5,800. Score 0 (no keywords)
- **Who:** owner of record STACK HOLDINGS LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3548-42-4309, Industrial land use, 2.77 ac, 52,880 SF building, built 1955. Owner STACK HOLDINGS LLC (3626 DALLAS HIGH SHOALS HWY, DALLAS NC 28034). Deed .
- **Look up at NC SOS:** STACK HOLDINGS LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### relocating 100 AMP service to new customer supplied pole- all new grounding. Includes runn | 2088 WEST DAVIDSON AVENUE GASTONIA NC 28052
- **What:** Electrical - Commercial - Electrical. Status: Issued. Applied 2026-09-14, issued 2026-09-15. [STC-26-09-14-04501](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/f31fb512-c10a-4aef-a427-f6dfdbc301e3)
- **Size:** $4,400. Score 0 (no keywords)
- **Who:** owner of record BRADLEY FAMILY TRUST. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3546-15-4388, Industrial land use, 7.33 ac, 4,000 SF building, built 1989, tax value $454,750. Owner BRADLEY FAMILY TRUST (137 BRADLEY TRAIL, GASTONIA NC 28056). Deed Bk 5643 Pg 2561 (WAR), last sale 2026-05-28.
- **Look up at NC SOS:** BRADLEY FAMILY TRUST
- **Your move:** New construction or site work. Call BRADLEY FAMILY TRUST now: is it spec or build-to-suit, and is the leasing assignment open? It sold recently (2026-05-28). A new owner may be repositioning it, so offer leasing.

### Replace 100 amp service for billboard | 5015 YORK HIGHWAY GASTONIA NC 28052
- **What:** Electrical - Commercial - Electrical. Status: Complete. Applied 2026-09-03, issued 2026-09-03. [STC-26-09-03-04478](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/c847a8a0-0ec4-45e8-92d7-d5c5b92b2086)
- **Size:** $3,750. Score 0 (no keywords)
- **Who:** owner of record BUCKNER PROPERTIES LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3542-18-5712, Industrial land use, 6.86 ac, 31,625 SF building, built 1981, tax value $634,700. Owner BUCKNER PROPERTIES LLC (2054 KENDRICK RD, GASTONIA NC 28056). Deed Bk 5438 Pg 0569 (NDT), last sale 2023-10-03.
- **Look up at NC SOS:** BUCKNER PROPERTIES LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### Installing a Backflow Preventer on a domestic line. | 900 DR MARTIN LUTHER KING JR WAY GASTONIA NC 28054
- **What:** Plumbing Commercial - Plumbing. Status: Complete. Applied 2026-09-09, issued 2026-09-10. [STC-26-09-09-04489](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/2e6b2f6f-2187-4438-850b-fb7e6368a158)
- **Size:** $3,000. Score 0 (no keywords)
- **Who:** owner of record HUDSON REAL ESTATE LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3546-82-9781, Industrial land use, 0.68 ac, 8,300 SF building, built 1946, tax value $131,530. Owner HUDSON REAL ESTATE LLC (301 E MAIN ST, DALLAS NC 28034). Deed Bk 5003 Pg 1977 (WAR), last sale 2018-10-04 for $87,000.
- **Look up at NC SOS:** HUDSON REAL ESTATE LLC
- **Your move:** The operator is spending money on the building (power, HVAC, fire). Find out when the lease runs out and offer tenant rep before renewal talks start.

### New gas line for existing hanging heater | 1228 ISLEY DRIVE GASTONIA NC 28052
- **What:** Mechanical - Commercial - Mechanical. Status: Issued. Applied 2026-10-14, issued 2026-10-14. [STC-26-10-14-04551](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/d5c52956-8149-4594-b6b2-2b39bd466458)
- **Size:** $2,657. Score 0 (no keywords)
- **Who:** owner of record GASTONIA 1228 INVESTMENTS LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3536-26-4870, Industrial land use, 12.82 ac, 1,440 SF building, built 2005, tax value $3,582,290. Owner GASTONIA 1228 INVESTMENTS LLC (1139 BOLLING ROAD, CHARLOTTE NC 28207). Deed .
- **Look up at NC SOS:** GASTONIA 1228 INVESTMENTS LLC
- **Your move:** New construction or site work. Call GASTONIA 1228 INVESTMENTS LLC now: is it spec or build-to-suit, and is the leasing assignment open?

### New construction, 225 SF Accessory Building | 130 MARIPOSA ROAD STANLEY NC 28164
- **What:** Electrical - Commercial - Electrical. Status: Issued. Applied 2026-10-19, issued 2026-10-30. [STC-26-10-19-04556](https://selfservice.gastongov.com/energov_prod/selfservice#/permit/51108cc5-bc63-46ff-b761-13314a23ab28)
- **Size:** $1,200. Score 0 (no keywords)
- **Who:** owner of record CATAWBA GROUP PROPERTIES LLC. The GC and applicant aren't public on this portal, so ask the owner or check the job-site sign.
- **Property:** PIN 3579-56-1310, Industrial Land land use, 7.91 ac, tax value $158,800. Owner CATAWBA GROUP PROPERTIES LLC (156 SMITH CLEMMER RD, MT HOLLY NC 28120). Deed Bk 5618 Pg 0698 (WAR), last sale 2026-02-11 for $540,000.
- **Look up at NC SOS:** CATAWBA GROUP PROPERTIES LLC
- **Your move:** New construction or site work. Call CATAWBA GROUP PROPERTIES LLC now: is it spec or build-to-suit, and is the leasing assignment open? It sold recently (2026-02-11, $540,000). A new owner may be repositioning it, so offer leasing.

...and 4 more in permits.csv.

## Problems

- None.
