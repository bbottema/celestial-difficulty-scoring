"""
OpenNGC catalog provider (offline, local CSV).

OpenNGC provides high-quality DSO data (NGC/IC/Messier) with:
- Clean object type codes (G, EmN, HII, RfN, DrkN, PN, OCl, GCl)
- Galaxy surface brightness (B-band, 25 mag isophote)
- Hubble morphological types
- Cross-references to other catalogs

Research findings: OpenNGC is the PRIMARY source for DSO classification
because its type system is designed for amateur astronomy observing.
"""
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
import pandas as pd

from app.domain.model.celestial_object import CelestialObject
from app.domain.model.object_classification import ObjectClassification, SurfaceBrightness, AngularSize
from app.domain.model.data_provenance import DataProvenance
from app.catalog.interfaces import ProviderDTO

logger = logging.getLogger(__name__)


class OpenNGCProvider:
    """
    Local CSV catalog provider for NGC/IC/Messier objects.

    Data source: https://github.com/mattiaverga/OpenNGC
    License: CC-BY-SA-4.0
    """

    def __init__(self, csv_path: Path):
        """
        Initialize provider with local OpenNGC CSV.

        Args:
            csv_path: Path to OpenNGC.csv file
        """
        self.df = self._load_csv(csv_path)
        logger.info(f"Loaded {len(self.df)} objects from NGC.csv")

        # Load OpenNGC addendum (M40, M45, Caldwell objects, named DSOs)
        # M40 and M45 are not NGC/IC objects, so they're in the official addendum.csv
        addendum_path = csv_path.parent / 'addendum.csv'
        if addendum_path.exists():
            addendum_df = self._load_csv(addendum_path)
            self.df = pd.concat([self.df, addendum_df], ignore_index=True)
            logger.info(f"Added {len(addendum_df)} addendum objects, total: {len(self.df)}")

        self.adapter = OpenNGCAdapter()

    def _load_csv(self, path: Path) -> pd.DataFrame:
        """
        Load and normalize OpenNGC CSV.

        Real OpenNGC columns:
        - Name (NGC/IC identifier)
        - Type (G, HII, PN, OCl, GCl, etc.)
        - RA, Dec (sexagesimal format)
        - MajAx, MinAx (arcmin)
        - V-Mag, B-Mag
        - SurfBr (mag/arcsec²)
        - Hubble (galaxy morphology)
        - M (Messier number)
        - Common names, Identifiers

        Returns:
            Normalized DataFrame
        """
        df = pd.read_csv(path, sep=';', dtype=str, na_values=['', 'null', 'NaN'])

        # Rename columns to internal format
        column_mapping = {
            'Name': 'name',
            'Type': 'obj_type',
            'RA': 'ra_sex',
            'Dec': 'dec_sex',
            'MajAx': 'maj_arcmin',
            'MinAx': 'min_arcmin',
            'PosAng': 'pos_ang',
            'V-Mag': 'mag_v',
            'B-Mag': 'mag_b',
            'SurfBr': 'surf_br',
            'Hubble': 'hubble_type',
            'M': 'messier_nr',
            'Common names': 'comname',
            'Identifiers': 'other_id'
        }
        df = df.rename(columns=column_mapping)

        # Convert RA/Dec from sexagesimal to decimal degrees
        if 'ra_sex' in df.columns and 'dec_sex' in df.columns:
            ra_values = []
            dec_values = []
            for idx, row in df.iterrows():
                ra_values.append(self._sex_to_deg_ra(row['ra_sex']))
                dec_values.append(self._sex_to_deg_dec(row['dec_sex']))
            df['ra'] = ra_values
            df['dec'] = dec_values

        # Convert numeric fields
        numeric_fields = ['maj_arcmin', 'min_arcmin', 'pos_ang', 'mag_v', 'mag_b', 'surf_br', 'ra', 'dec']
        for col in numeric_fields:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Fill missing string values
        string_cols = ['name', 'obj_type', 'messier_nr', 'comname', 'other_id', 'hubble_type']
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].fillna('')

        return df

    def _sex_to_deg_ra(self, ra_str: str) -> Optional[float]:
        """Convert RA from HH:MM:SS.SS to decimal degrees"""
        if pd.isna(ra_str) or not ra_str:
            return None
        try:
            parts = ra_str.split(':')
            h, m, s = float(parts[0]), float(parts[1]), float(parts[2])
            return (h + m/60 + s/3600) * 15  # Hours to degrees
        except:
            return None

    def _sex_to_deg_dec(self, dec_str: str) -> Optional[float]:
        """Convert Dec from ±DD:MM:SS.S to decimal degrees"""
        if pd.isna(dec_str) or not dec_str:
            return None
        try:
            sign = -1 if dec_str.startswith('-') else 1
            dec_str = dec_str.lstrip('+-')
            parts = dec_str.split(':')
            d, m, s = float(parts[0]), float(parts[1]), float(parts[2])
            return sign * (d + m/60 + s/3600)
        except:
            return None

    def resolve_name(self, name: str) -> Optional[str]:
        """
        Resolve Messier/NGC/IC/common name to canonical NGC/IC identifier.

        Decision tree:
        1. Try Messier number (M31 → NGC 224)
        2. Try NGC/IC direct (NGC 224 → NGC 224)
        3. Try common name (Andromeda → NGC 224)
        4. Try other_id field cross-references

        Args:
            name: User input (e.g., "M31", "NGC 7000", "Andromeda")

        Returns:
            Canonical NGC/IC name or None
        """
        name_upper = name.upper().strip()

        # Try Messier number (M31 → find messier_nr=031)
        if name_upper.startswith('M') and name_upper[1:].strip().isdigit():
            messier_num = name_upper[1:].strip().zfill(3)  # Pad to 3 digits: 31 → 031
            row = self.df[self.df['messier_nr'] == messier_num]
            if not row.empty:
                return row.iloc[0]['name']

        # Try NGC/IC direct (handles both "NGC 224" and "NGC0224")
        if name_upper.startswith('NGC') or name_upper.startswith('IC'):
            # Normalize to NGC0224 format (what OpenNGC uses)
            if ' ' in name_upper:
                # "NGC 224" → "NGC0224"
                prefix, number = name_upper.split(maxsplit=1)
                name_normalized = f"{prefix}{number.zfill(4)}"
            elif name_upper.startswith('NGC') and len(name_upper) > 3:
                # "NGC224" → "NGC0224"
                number = name_upper[3:]
                name_normalized = f"NGC{number.zfill(4)}"
            elif name_upper.startswith('IC') and len(name_upper) > 2:
                # "IC1396" → "IC1396" (IC numbers are different)
                name_normalized = name_upper
            else:
                name_normalized = name_upper

            row = self.df[self.df['name'] == name_normalized]
            if not row.empty:
                return name_normalized

        # Try common name
        row = self.df[self.df['comname'].str.upper() == name_upper]
        if not row.empty:
            return row.iloc[0]['name']

        # Try other_id (contains semicolon-separated aliases)
        for other_id in self.df['other_id']:
            if other_id and name_upper in other_id.upper():
                # Find the row with this other_id value
                row = self.df[self.df['other_id'] == other_id]
                if not row.empty:
                    return row.iloc[0]['name']

        return None

    def get_object(self, identifier: str) -> Optional[CelestialObject]:
        """
        Fetch DSO by NGC/IC identifier or Messier number.

        Args:
            identifier: NGC, IC, or Messier identifier (e.g., "NGC 224", "IC 1396", "M31", "Mel022")

        Returns:
            CelestialObject with all OpenNGC fields populated
        """
        identifier_stripped = identifier.strip()

        # First, try to resolve Messier/common names to canonical NGC/IC identifier
        canonical_id = self.resolve_name(identifier_stripped)
        if canonical_id:
            identifier_stripped = canonical_id

        # Try exact match first (for addendum objects like "Mel022")
        row = self.df[self.df['name'] == identifier_stripped]

        # If not found, try uppercase (for NGC/IC objects)
        if row.empty:
            identifier_upper = identifier_stripped.upper()
            row = self.df[self.df['name'] == identifier_upper]

        if row.empty:
            return None

        # Convert DataFrame row to DTO
        dto = ProviderDTO(
            raw_data=row.iloc[0].to_dict(),
            source="openngc"
        )

        # Use adapter to convert to domain model
        return self.adapter.to_domain(dto)

    def batch_get_objects(self, identifiers: list[str]) -> list[CelestialObject]:
        """Batch retrieval (efficient for local CSV)"""
        identifiers_upper = [id.upper().strip() for id in identifiers]
        rows = self.df[self.df['name'].isin(identifiers_upper)]

        objects = []
        for _, row in rows.iterrows():
            dto = ProviderDTO(
                raw_data=row.to_dict(),
                source="openngc"
            )
            obj = self.adapter.to_domain(dto)
            if obj:
                objects.append(obj)

        return objects


class OpenNGCAdapter:
    """
    Converts OpenNGC DTOs to domain model.

    Handles type mapping, unit conversions, and provenance tracking.
    """

    def to_domain(self, dto: ProviderDTO) -> CelestialObject:
        """
        Convert OpenNGC DTO to CelestialObject.

        Mappings:
        - obj_type → ObjectClassification (see _map_type)
        - maj_arcmin, min_arcmin → AngularSize
        - surf_br_B → SurfaceBrightness (galaxies only)
        - messier_nr, comname, other_id → aliases

        Args:
            dto: OpenNGC data transfer object

        Returns:
            Fully populated CelestialObject
        """
        data = dto.raw_data

        # Build classification
        classification = self._map_type(data.get('obj_type', ''), data.get('hubble_type'))

        # Build size
        maj = data.get('maj_arcmin', 0.0)
        if pd.isna(maj) or maj == 0.0:
            maj = 1.0  # Default for point sources
        size = AngularSize(
            major_arcmin=maj,
            minor_arcmin=data.get('min_arcmin') if not pd.isna(data.get('min_arcmin')) else None,
            position_angle_deg=data.get('pos_ang') if not pd.isna(data.get('pos_ang')) else None
        )

        # Surface brightness (galaxies only)
        sb = None
        surf_br_val = data.get('surf_br')
        if surf_br_val is not None:
            try:
                import math
                float_val = float(surf_br_val)
                if not math.isnan(float_val):
                    sb = SurfaceBrightness(
                        value=float_val,
                        source="openngc_surf_br",
                        band="B"
                    )
            except (ValueError, TypeError):
                pass  # Invalid value, skip surface brightness

        # Build aliases
        aliases = []
        if data.get('messier_nr'):
            aliases.append(f"M{data['messier_nr']}")
        if data.get('comname'):
            aliases.append(data['comname'])
        if data.get('other_id'):
            # other_id is semicolon-separated
            aliases.extend([a.strip() for a in data['other_id'].split(';') if a.strip()])

        # Build provenance
        provenance = [DataProvenance(
            source="OpenNGC",
            fetched_at=datetime.now(),
            catalog_version="2023-12-13",
            confidence=1.0
        )]

        # Build CelestialObject
        ra_val = data.get('ra')
        dec_val = data.get('dec')
        obj = CelestialObject(
            name=data.get('comname') or data['name'],
            canonical_id=data['name'],
            aliases=aliases,
            ra=float(ra_val) if ra_val and not pd.isna(ra_val) else 0.0,
            dec=float(dec_val) if dec_val and not pd.isna(dec_val) else 0.0,
            classification=classification,
            magnitude=float(data.get('mag_v', 99.0)) if not pd.isna(data.get('mag_v')) else 99.0,
            size=size,
            surface_brightness=sb,
            provenance=provenance
        )

        return obj

    def _map_type(self, obj_type: str, hubble_type: Optional[str]) -> ObjectClassification:
        """
        Map OpenNGC type codes to domain classification.

        Research-validated mappings:
        - G → galaxy (check hubble_type for spiral/elliptical/lenticular)
        - EmN, HII → nebula.emission
        - RfN → nebula.reflection
        - DrkN → nebula.dark
        - PN → nebula.planetary
        - OCl → cluster.open
        - GCl → cluster.globular
        - SNR → nebula.supernova_remnant
        - Dup, NonEx, Other → special handling

        Args:
            obj_type: OpenNGC type code
            hubble_type: Galaxy morphology (e.g., "SA(s)b")

        Returns:
            ObjectClassification with primary_type + subtype
        """
        obj_type_upper = obj_type.upper().strip() if obj_type else ''

        # Galaxy
        if obj_type_upper == 'G':
            subtype = self._parse_galaxy_subtype(hubble_type)
            return ObjectClassification('galaxy', subtype, hubble_type)

        # Emission nebulae
        if obj_type_upper in ['EMN', 'HII']:
            return ObjectClassification('nebula', 'emission', None)

        # Reflection nebula
        if obj_type_upper == 'RFN':
            return ObjectClassification('nebula', 'reflection', None)

        # Dark nebula
        if obj_type_upper == 'DRKN':
            return ObjectClassification('nebula', 'dark', None)

        # Planetary nebula
        if obj_type_upper == 'PN':
            return ObjectClassification('nebula', 'planetary', None)

        # Supernova remnant
        if obj_type_upper == 'SNR':
            return ObjectClassification('nebula', 'supernova_remnant', None)

        # Open cluster
        if obj_type_upper == 'OCL':
            return ObjectClassification('cluster', 'open', None)

        # Globular cluster
        if obj_type_upper == 'GCL':
            return ObjectClassification('cluster', 'globular', None)

        # Special cases (Dup, NonEx, etc.) - default to unknown
        return ObjectClassification('unknown', None, None)

    def _parse_galaxy_subtype(self, hubble_type: Optional[str]) -> Optional[str]:
        """
        Parse Hubble type to galaxy subtype.

        Rules:
        - E0-E7 → elliptical
        - S0, SA0, SB0 → lenticular
        - SA, SB, SAB, S → spiral (SA=unbarred, SB=barred, SAB=weakly barred)
        - I, Irr → irregular

        Args:
            hubble_type: Hubble classification string

        Returns:
            "spiral", "elliptical", "lenticular", "irregular", or None
        """
        if not hubble_type:
            return None

        ht = hubble_type.upper().strip()

        # Elliptical
        if ht.startswith('E'):
            return 'elliptical'

        # Lenticular (S0, SA0, SB0, etc. - must check for '0' after S or SA/SB)
        if ht.startswith('S0') or ht.startswith('SA0') or ht.startswith('SB0'):
            return 'lenticular'

        # Spiral (check for SA, SB, SAB)
        if any(x in ht for x in ['SA', 'SB', 'SAB']) or ht.startswith('S'):
            return 'spiral'

        # Irregular
        if ht.startswith('I') or 'IRR' in ht:
            return 'irregular'

        return None
