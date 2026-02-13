# Object Lists

This directory contains pre-curated celestial object lists in JSON format.

## Available Lists

| File | Description | Objects |
|------|-------------|---------|
| `messier_110.json` | The Messier Catalog | 110 |
| `caldwell_109.json` | The Caldwell Catalog | 109 |
| `solar_system.json` | Planets and Moon | 9 |

## JSON Schema

```json
{
  "name": "Catalog Name",
  "description": "Description of the catalog",
  "category": "named_catalog",
  "version": "1.0",
  "created_date": "2026-02-13",
  "objects": [
    {
      "name": "M31",
      "canonical_id": "NGC0224",
      "type": "galaxy",
      "ra": 10.6847,
      "dec": 41.2689,
      "magnitude": 3.4
    }
  ]
}
```

## Canonical ID Format

- **NGC/IC objects:** `NGC0224` (zero-padded to 4 digits, no space)
- **Solar System:** Object name as-is (`Jupiter`, `Moon`, `Sun`)
- **Addendum objects:** As in addendum.csv (`Mel022`, `C009`, etc.)

## Regenerating Lists

Run the generation script:

```bash
python scripts/generate_object_lists.py
```

This reads from `data/catalogs/NGC.csv` and `data/catalogs/addendum.csv`.
