# Object Selection and Observing List Management Patterns in Modern Astronomy Software

## Why object selection is a separate product problem from catalog lookup

Most astronomy tools treat “find objects” as a two-layer system:

A **browsable selector** (catalog lists, object-type browsing, filters like altitude/airmass and magnitude) produces a working set for “tonight.” This is typically powered by a local catalog shipped with the app or downloaded ahead of time. Examples include:

- “Tonight’s Best” in SkySafari, which is explicitly location/time dependent, requires the object to reach a minimum altitude during the night, and is sorted in an observing-friendly order (transit time). citeturn7view1  
- “What’s up tonight” (WUT) in KStars, plus an “Observing List Wizard” that can filter by object type, region/constellation, and magnitude threshold to build a session plan. citeturn6view0turn0search30  
- “What’s Up?” in TheSkyX, which generates a report based on viewing time and “optical aid” (naked eye/binocular/small telescope), then lets you step through targets while the chart updates. citeturn11view0  

A **lookup + enrichment layer** handles everything outside the shipped catalog: the user enters a name, pastes a list, or imports a file from elsewhere. Many apps then either (a) resolve the name online and add it to the local store or (b) keep it as a session-only target with cached coordinates. KStars documents this explicitly: a Batch Add feature tries to resolve objects via SIMBAD when they are not already in the local database. citeturn6view0  

This split maps well onto your constraints: you already have an offline-browsable base (OpenNGC), and you have online lookup services (SIMBAD, JPL Horizons) that are strong at resolving ad-hoc inputs.

## Application comparison across major tools

The table focuses on how each app answers “what should I observe tonight?” and how it carries the flow from browsing → list → at-the-scope use → logging/sharing.

| App | Discovery and selection | Filters and browsing patterns | List and session management | Import/export and sharing | Notes for your product |
|---|---|---|---|---|---|
| SkySafari | Built-in “common object lists” (Planets, Brightest Stars, Messier, etc.) and a dynamic “Tonight’s Best” list tied to location/date and minimum altitude during darkness. citeturn7view1 | Sort & Filter supports “Visible Tonight,” sorting by transit/rise/set and other fields; list items can be highlighted on the sky chart; can convert search/common lists into observing lists. citeturn7view1 | Observing Lists store targets and observation logs; supports Sessions; supports list-level “observed/unobserved” filtering; batch-download DSS images for list objects. citeturn6view2 | Imports/exports `.skylist` files; supports sharing lists via email and export to plain text or CSV in older docs. citeturn4search2turn4search11 | Strongest evidence that “highlight list on map + next target + session logging” is a sticky workflow for amateurs. citeturn7view1turn6view2 |
| KStars | Observation Planner provides “Find Object” with type filters and name filter; “Observing List Wizard” can generate a plan by object type + region/constellation + magnitude threshold; includes “What’s up tonight.” citeturn6view0 | Region filters (all sky, constellation, rectangular/circular region), magnitude threshold, date and place selection; altitude-vs-time widget is central in the planner. citeturn6view0 | Separates long-term Wish List from Session Plan; Execution Session view includes object info and also an equipment page; designed for stepping through an observing plan. citeturn6view0 | Batch Add accepts many names at once; missing objects can be resolved via SIMBAD (if enabled) and then added to the local database. citeturn6view0 | This is the clearest “local database + online resolver for out-of-catalog” pattern, which matches your OpenNGC + SIMBAD setup. citeturn6view0 |
| Stellarium | Selection is primarily map-first: pick objects visually, then manage favorites/lists. An Observability analysis plug-in provides an observability report for the selected object. citeturn0search1turn7view3 | Observing Lists evolved from Bookmarks; list records can include RA/Dec, magnitude, constellation; entries can optionally store time, location, landscapeID, and FOV for “view replay.” citeturn7view3 | ObservingLists support multiple lists, edit/delete, import/export, and highlighting of list objects on the sky view; format is `observingList(s).json` with a unique list ID (OLUD). citeturn7view3 | Import/export is part of the ObservingLists system; older Bookmarks.json is deprecated and auto-imported at first run. citeturn7view3turn4search21 | Strong pattern for “store view context with the target” (time+place+FOV) for event-driven lists like eclipses. citeturn7view3 |
| Cartes du Ciel (Skychart) | Observing List is a lightweight, list-first tool: prepare a list, filter it, then run a “Tour” that can slew a telescope. citeturn6view1 | Filters include transit-time window (with meridian-side selection for German EQ mounts), minimum altitude or maximum airmass; supports “filter objects that meet criteria during the night” vs “right now.” citeturn6view1 | Objects can be added from chart context menu; list objects get special labels, and an “Always show objects from the list” option helps with faint targets. citeturn6view1 | File format supports object name and optional RA/Dec (J2000, decimal degrees); coordinates can be filled from catalogs on first load. citeturn6view1 | Extremely relevant for your offline base: “text list in → coords filled from local catalog → filter for night vs now.” citeturn6view1 |
| TheSkyX | Offers both “What’s Up?” (report-driven starter list) and “Create Observing List” (advanced queries) to generate observing lists from catalog searches. citeturn11view0 | “What’s Up?” can use optical aid choice; “Create Observing List” can query catalogs like WDS with constraints (example: spectral type in Orion). citeturn11view0 | Observing lists can be shown in vertical/horizontal orientation; stepping through results updates the sky chart. citeturn11view0 | TheSkyX ships many named catalogs (Messier, Caldwell, Herschel 400, WDS) with explicit object counts and includes many photos. citeturn11view0 | Strong evidence for “advanced query builder → reusable list generator,” which is a natural fit if you expose your scoring filters as a query UI. citeturn11view0 |
| Telescopius | Web-first “Targets” browsing with location-based “what’s visible” and equipment-aware target suggestions (telescope/camera/mount), per a detailed third-party guide. citeturn0search7 | Filters by object type, magnitude, apparent size, altitude; community support explicitly points people to size filters for matching framing. citeturn0search19turn0search7 | Uses Target Lists as a primary object-management tool (site navigation shows “Target Lists” as a first-class area). citeturn0search3 | Users commonly download monthly target lists as CSV; issues and fixes are discussed publicly in their forum, suggesting CSV export is a normal workflow. citeturn8search3 | Most aligned with “astrophotography planning” mental model: equipment fit + framing + curated visible targets. citeturn0search7turn0search19 |

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["SkySafari observing list highlight objects screenshot","KStars observation planner wizard screenshot","Stellarium observing lists dialog screenshot","Cartes du Ciel Skychart observing list tour screenshot","Telescopius target list filters screenshot"],"num_per_query":1}

Additional planning/logging tools that strongly influence workflows (even if you don’t mirror them exactly):

- entity["organization","AstroPlanner","observing planner software"] is explicitly built around “plan and execute an observing session,” with manual entry, import from text, lookup in supplied catalogs, use of pre-made observing plans, logging per object, visibility computation, and field-of-view simulation for eyepieces or imaging sensors. citeturn14view0  
- entity["organization","Deep-Sky Planner","observation planning software"] emphasizes “observing plans” and exports them to other apps (including SkySafari and Cartes du Ciel), treating it as a hub that generates lists consumed elsewhere in the field. citeturn1search2turn4search16  

## Common UX patterns for browsing large catalogs

Across desktop, mobile, and web tools, several patterns show up repeatedly and map directly to your “score 1000 objects” requirement.

### A small number of primary entry points

Most apps funnel users into a few clear “doors”:

A dynamic **Tonight** door:
- SkySafari’s “Tonight’s Best” is explicitly framed as “best objects visible between dusk and dawn,” requires a minimum altitude, and sorts by transit time. citeturn7view1  
- KStars includes a “What’s up tonight” tool intended to give ideas for a specified time/place. citeturn6view0  
- TheSkyX offers “What’s Up?” with user-specified viewing time and optical aid. citeturn11view0  

A structured **Catalog/Type browse** door:
- SkySafari’s Search view includes “most commonly-known objects,” explicitly highlighting lists like Planets and Messier Objects. citeturn7view1  
- KStars can filter the “Find Object” list by object types including Stars, Solar System, clusters, nebulae, galaxies, comets, asteroids, satellites, etc. citeturn6view0  

A **Search by name / paste list** door:
- KStars describes Batch Add for many objects at once, using SIMBAD to resolve unknown names into the local database if enabled. citeturn6view0  

Design implication for your app: users expect three top-level modes: “Tonight,” “Browse,” and “Search/Paste/Import.”

### Faceted filters that start simple and can grow

Effective filters tend to start with a few high-signal knobs and then add depth:

- “Visible tonight” as a single toggle (SkySafari) citeturn7view1  
- Magnitude threshold and region selection (KStars wizard) citeturn6view0  
- Minimum altitude / maximum airmass and meridian-side constraints to prevent flips (Cartes du Ciel) citeturn6view1  

Design implication: make one screen usable with 3–4 filters, with an “Advanced” panel for the heavy stuff: transit-time windows, airmass, and “during night” vs “right now.” citeturn6view1  

### Visual feedback that keeps “lists” connected to “the sky”

List-only views become much more usable when the user can see list objects in context:

- SkySafari highlights list objects on the chart and provides “Select Next Object” and “Surprise Me” actions. citeturn7view1  
- Stellarium’s ObservingLists system supports highlighting bookmarked objects for the active list. citeturn7view3  
- Cartes du Ciel can label list objects and optionally force showing them even when faint. citeturn6view1  

Design implication: treat “highlight a list on the sky view” as a first-class feature, not an add-on.

## Pre-curated lists and observing programs that recur across apps

### Built-in named catalogs and starter lists

Several lists appear as defaults because they solve beginner and intermediate needs immediately:

- Planets and bright-star lists (SkySafari “common object lists”). citeturn7view1  
- The Messier catalog appears directly as a list in SkySafari, described as “the most famous 110 star clusters, nebulae, and galaxies.” citeturn7view1  
- TheSkyX explicitly lists built-in catalogs that include Herschel 400, Caldwell, and Messier (with counts) and frames them as part of its object databases. citeturn11view0  

For your OpenNGC base, these named catalogs are easy wins: Messier (110), Caldwell (109), and subsets like “bright NGC showpieces” can be packaged as offline lists.

### Observing programs as pre-made list bundles

A major cross-app theme is “observing programs” (structured checklists) rather than free-form browsing.

SkySafari provides an online Observing List Repository, and it includes a directory of entity["organization","Astronomical League","observing programs organization"] observing program lists (examples visible in the repository index: Carbon Stars, Deep Sky Binocular, Double Star, Globular Clusters, Planetary Nebula, Herschel II, Urban Observing Club, and others). citeturn10view0  

Design implication: this is a proven way to support “I’m working through the Messier catalog” and “give me a binocular program,” without requiring a search engine or a giant database. Your tool can ship local “program packs” and optionally import broader packs (SkySafari `.skylist`, Stellarium JSON, CSV/text).

### Event and calendar driven lists

Some tools treat “time and sky events” as a primary discovery mechanic:

- TheSkyX includes tours for concepts/events such as “Moon Cycle - Size and Phase” and other time-based views. citeturn7view2  
- SkySafari’s product site describes a calendar for meteor showers and eclipses and encourages planning nights around events. citeturn5search30  
- Stellarium ObservingLists entries can optionally store time and location, which the docs describe as useful for lists like solar eclipses with their locations. citeturn7view3  

Design implication: your “Moon this month” scenario fits naturally as “calendar → recommended windows → one-click list creation.”

## Workflow from browsing to observing

Across apps, the flow is highly consistent even when the UI style differs. These are the dominant “objects → list → session” shapes, supported by documentation.

### Long-term list versus session plan

KStars states directly that the Wish List is not the Session Plan, and the user moves objects from Wish List into a Session Plan. citeturn6view0  
SkySafari similarly has Observing Lists plus a Session concept that groups observations for a night. citeturn6view2  

Derived workflow diagram (modeled on KStars + SkySafari docs):

```
Browse/Search → Add to Wish List (long-term)
          ↓
Generate “Tonight” shortlist (filters, scoring)
          ↓
Create Session Plan / Session (date+site)
          ↓
Observe (next target, highlight on chart)
          ↓
Log observation + mark observed
          ↓
Export/share list + logs
```

### “Wizard” creation beats manual building for large lists

Several tools provide “wizards” or query builders that make 100–1000 item selection practical:

- KStars Observing List Wizard: object categories + sky region + date/place + magnitude threshold, then save as `.obslist`. citeturn6view0  
- TheSkyX “Create Observing List” uses advanced search/database queries beyond the simplified “What’s Up” tab. citeturn11view0  
- Cartes du Ciel’s filters explicitly distinguish “during the night” planning from “right now” observing mode, with constraints like airmass, altitude, and meridian side. citeturn6view1  

Design implication: scoring 1000 galaxies for imaging runs needs a wizard-style list generator, not only a search box.

### Import/export as a real workflow, not an edge case

The ecosystem uses list exchange heavily:

- SkySafari supports `.skylist` import/export and multiple transfer mechanisms (iOS file sharing, SD card folder, email). citeturn4search2turn4search11  
- Stellarium supports list import/export and provides a structured JSON format with unique IDs; older bookmark files are auto-imported. citeturn7view3  
- Cartes du Ciel supports “initial file with title line followed by object names,” adds coordinates from catalogs on load, and documents a fixed-width format that can include J2000 RA/Dec. citeturn6view1  
- Deep-Sky Planner explicitly exports plans to other apps (including SkySafari and Cartes du Ciel). citeturn1search2turn4search16  

Design implication: if your tool can import/export in 2–3 common formats, users can keep using pieces of their existing stack.

## Recommendations for your PySide6 implementation

These recommendations are tightly tied to (a) your data constraints (OpenNGC offline; SIMBAD and Horizons lookup) and (b) the proven UX patterns above.

### Provide three top-level selection modes and keep them visible

Mode 1: **Tonight**
- Show “Top targets for tonight” using your scoring as the ranking engine.
- Include a simple “Visible tonight” toggle, a minimum altitude slider, and a “Moon avoidance” control (many users will accept a single “avoid bright Moon” toggle plus a numeric separation threshold).
- Match SkySafari/KStars expectations: show ordering by best time (transit) and provide “Next target.” citeturn7view1turn6view0  

Mode 2: **Browse**
- Powered entirely by OpenNGC when offline.
- Facets: object type (your mapped types), constellation/region, magnitude range, angular size range, computed surface brightness bins, and “imaging fit” (FOV match).
- Provide “Generate plan” (wizard), modeled after KStars’ Observing List Wizard and TheSkyX Create Observing List. citeturn6view0turn11view0  

Mode 3: **Search / Paste / Import**
- Single-name: resolve against local OpenNGC first, then online (SIMBAD) if enabled.
- Batch input: replicate the “Batch Add” idea from KStars (paste 100 names; resolve what you can; show failures in a repair UI). citeturn6view0  

### Separate “List” from “Session,” then allow light coupling

Adopt a structure consistent with SkySafari and KStars:

- **Target List** (long-term): “Messier,” “Planetary Nebula hunt,” “Winter nebulae,” “My imaging backlog.”
- **Session**: a dated plan linked to a site profile and conditions; contains targets copied from lists or generated by scoring for that night.

This matches:
- KStars Wish List versus Session Plan. citeturn6view0  
- SkySafari Observing Lists plus Sessions grouping observations. citeturn6view2  

### Make list ↔ sky map linkage a first-class interaction

Implement the three high-value map/list actions shown in multiple apps:

- **Highlight this list on the sky map** (SkySafari, Stellarium, Cartes du Ciel). citeturn7view1turn7view3turn6view1  
- **Next target** (SkySafari explicitly provides “Select Next Object”). citeturn7view1  
- **At-scope mode**: a large-font “current target” card with altitude, time-to-transit/set, and a “Log observation” quick action (mirrors the “Execution Session” and logging concepts in KStars/SkySafari). citeturn6view0turn6view2  

### Ship pre-made program packs offline and allow optional imports

Ship local packs that do not require SIMBAD-scale catalogs:

- Messier 110, Caldwell 109, and a few “seasonal showpieces.”
- A “Planets” pack that is populated dynamically via ephemerides rather than a static list.

Add optional import/export that mirrors the formats people already use:

- SkySafari `.skylist` import/export. citeturn4search2turn4search11  
- Stellarium ObservingLists JSON import/export. citeturn7view3  
- Cartes du Ciel text list format (title line + object names; optional RA/Dec fields). citeturn6view1  

SkySafari’s repository structure demonstrates that program bundles (including Astronomical League lists) are commonly distributed as `.skylist` files, so supporting `.skylist` becomes a practical way to unlock a wide ecosystem of lists without building a new community portal immediately. citeturn10view0  

### Treat Solar System selection as a separate “Tonight” module

Your browsing constraints are least friendly for planets and the Moon, since these are time-dependent and not a static catalog.

A pattern that matches user expectations:

- A “Planets tonight” list derived from ephemerides (rank by altitude and apparent size).
- A “Moon planner” page derived from a month calendar view, similar in spirit to time-driven tools described in SkySafari/TheSkyX marketing and feature lists. citeturn5search30turn7view2  

## Notable unique features worth copying

A few details seen in existing tools map especially well to an observability scoring system.

- SkySafari allows converting search results and common object lists into observing lists, then highlighting that list on the chart and stepping through targets (“Select Next Object”), which reduces friction from discovery → execution. citeturn7view1turn6view2  
- KStars documents an explicit “resolve missing objects via SIMBAD and add them to the database” approach during batch additions, which is directly aligned with your “lookup APIs rather than browse APIs” challenge. citeturn6view0turn6view2  
- Cartes du Ciel distinguishes “objects that meet criterion during the night” versus “right now,” and includes meridian-side selection for imaging mounts—this is a strong pattern for imaging planning in a desktop UI. citeturn6view1  
- Stellarium’s ObservingLists can store optional time/location/FOV per entry, explicitly justified for event-driven lists like eclipses; this is a clean mechanism for “Moon this month” and similar features to become shareable artifacts. citeturn7view3  
- TheSkyX treats advanced list generation as a query builder, not just browsing; this matches your need to let users express scoring constraints (“show emission nebulae suitable for my telescope”) as reusable saved filters that generate lists. citeturn11view0  
- entity["organization","AstroHopper","sky navigation web app"] focuses on the “at the telescope” navigation step, using phone sensors to guide to targets (a push-to style flow). This is a different kind of tool than list managers, and it suggests a useful boundary: selection/planning can remain list/table driven, and “navigation mode” can become a highly simplified UI for field use. citeturn1search12turn1search24  

