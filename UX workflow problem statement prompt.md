# Research Prompt: Object Selection & Observing List Management in Astronomy Software

## Problem Statement

We are developing an astronomical observability scoring tool that helps amateur astronomers identify optimal targets based on their equipment, location, and observing conditions. We need to design a user workflow for selecting celestial objects to observe.

**Current Challenge:**
- We have transitioned from Excel-based imports (AstroPlanner exports) to API-based catalog access
- Our APIs are primarily lookup-based (query by name) rather than search/browse-based
- We need to understand how other astronomy software solves the "what should I observe tonight?" problem

**Our Data Sources:**
- OpenNGC: Local catalog with ~14,000 deep-sky objects (NGC/IC/Messier) - fully browsable
- SIMBAD: Online database with 11M objects - query-only, rate-limited
- JPL Horizons: Solar System ephemerides - not a browsable catalog

**User Scenarios We Need to Support:**
- "What can I observe tonight with my equipment?"
- "I want to observe planets - which are visible?"
- "Show me emission nebulae suitable for my telescope"
- "I'm working through the Messier catalog"
- "What are challenging targets for my large aperture scope?"
- "Plan a photography session for specific object types"
- "When is the best time to observe the Moon this month?"

## Research Questions

### 1. How do leading astronomy applications handle object selection?

**Software to Research:**
- **AstroPlanner** (desktop, macOS/Windows) - our previous workflow source
- **SkySafari** (mobile/desktop) - popular planning app
- **Stellarium** (open source) - widely used planetarium software
- **Cartes du Ciel (Skychart)** (open source) - comprehensive sky atlas
- **TheSkyX** (professional) - high-end planning software
- **KStars** (open source, Linux) - full-featured planetarium
- **Deep-Sky Planner** - specialized for deep-sky observing
- **Telescopius** (web-based) - modern astrophotography planning
- **AstroHopper** (iOS) - observing list management

**For each application, investigate:**
- How do users discover/select objects to observe?
- What pre-curated lists or catalogs are available?
- What search/filter capabilities exist?
- How are custom observing lists created and managed?
- Can users import/export object lists?
- Are there "smart" recommendations or suggestions?
- How do they handle different object types (DSO vs planets vs stars)?

### 2. What catalog browsing patterns are common?

- **By Object Type**: Galaxies, nebulae, clusters, planets, stars, etc.
- **By Named Catalogs**: Messier, Caldwell, NGC, IC, Herschel 400, etc.
- **By Observable Properties**: Magnitude range, size, surface brightness
- **By Sky Location**: Constellation, RA/Dec range, altitude/azimuth
- **By Observability**: "What's up tonight?", "Rising soon", "Best this season"
- **By Difficulty**: Beginner friendly, intermediate, advanced/challenge objects
- **By Equipment Suitability**: "Good for binoculars", "Requires large aperture"

### 3. What pre-curated object lists do astronomy apps typically provide?

Look for:
- Standard astronomical catalogs (Messier, Caldwell, etc.)
- Curated themed lists ("Winter showpieces", "Double stars", etc.)
- Observing programs (Astronomical League programs, certification lists)
- Equipment-specific lists ("Best binocular objects", "Large scope targets")
- Seasonal/monthly highlights
- "Tonight's Best" dynamic lists

### 4. How do apps handle the workflow from "browsing" to "observing"?

- Can users create multiple observing lists?
- How are objects added/removed from lists?
- Can lists be shared or imported?
- Do apps support observing sessions (logging what was observed)?
- Integration with equipment profiles?
- Planning features (best time to observe, moon interference, etc.)?

### 5. What are the UX patterns for filtering large catalogs?

- Progressive disclosure (simple → advanced filters)?
- Real-time filtering vs. explicit "search" action?
- Saved searches or filter presets?
- Visual feedback (map view, list view, table view)?
- Sorting options (by magnitude, size, altitude, etc.)?

### 6. How do commercial vs. open-source apps differ?

- Do commercial apps have more sophisticated recommendation engines?
- Are open-source apps more data-driven (full catalog access)?
- Different approaches to mobile vs. desktop?

### 7. Modern web-based astronomy tools - what patterns are emerging?

- How do sites like Telescopius, AstroBin, or Clear Dark Sky handle object discovery?
- Social features (popular targets, community recommendations)?
- Integration with astrophotography workflows?

## Desired Output

Please provide:

1. **Summary comparison table** of how 5-6 major apps handle object selection
2. **Common UX patterns** identified across applications
3. **Typical pre-curated lists** that appear in multiple apps
4. **Workflow diagrams** if found in documentation/reviews
5. **Notable unique features** that stand out as particularly effective
6. **Recommendations** for our implementation based on findings
7. **Links to relevant documentation, reviews, or user guides**

## Context for Implementation

We are building a Python/PySide6 desktop application with:
- Existing equipment management (telescopes, eyepieces, filters)
- Observing site management (lat/lon, light pollution)
- Sophisticated scoring algorithm for observability
- Phase 8 goal: Replace Excel import with API-based catalog access

We need to design a user-friendly way to:
1. Let users select groups of objects to score
2. Support both casual observers and serious enthusiasts
3. Work offline (where possible) given we have local OpenNGC data
4. Scale from "show me the planets tonight" to "score 1000 galaxies for my imaging run"