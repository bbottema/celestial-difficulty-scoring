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
from pathlib import Path
from typing import Optional
import pandas as pd

from app.domain.model.celestial_object import CelestialObject
from app.catalog.interfaces import ProviderDTO, ICatalogProvider


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
        self.adapter = OpenNGCAdapter()

    def _load_csv(self, path: Path) -> pd.DataFrame:
        """
        Load and normalize OpenNGC CSV.

        OpenNGC uses semicolon delimiter and provides:
        - raj2000, dej2000 (degrees)
        - maj_ax_deg, min_ax_deg (degrees)
        - mag_v, mag_b
        - surf_br_B (galaxies only)
        - obj_type (G, EmN, HII, RfN, DrkN, PN, OCl, GCl, SNR)
        - hubble_type (galaxy morphology)

        Returns:
            Normalized DataFrame with arcmin conversions
        """
        # TODO: Implement CSV loading
        # - Read with sep=';'
        # - Convert numeric fields (raj2000, dej2000, mag_v, etc.)
        # - Convert axes: degrees → arcmin (multiply by 60)
        # - Handle missing values
        raise NotImplementedError("OpenNGC CSV loading not yet implemented")

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
        # TODO: Implement name resolution logic
        # - Normalize input (uppercase, strip whitespace)
        # - Check messier_nr column
        # - Check name column
        # - Check comname column
        # - Check other_id column
        raise NotImplementedError("OpenNGC name resolution not yet implemented")

    def get_object(self, identifier: str) -> Optional[CelestialObject]:
        """
        Fetch DSO by NGC/IC identifier.

        Args:
            identifier: NGC or IC identifier (e.g., "NGC 224", "IC 1396")

        Returns:
            CelestialObject with all OpenNGC fields populated
        """
        # TODO: Implement object retrieval
        # - Query DataFrame by name column
        # - Convert row to ProviderDTO
        # - Use adapter to convert DTO → CelestialObject
        # - Add provenance (source="openngc", catalog_version="2023-12-13")
        raise NotImplementedError("OpenNGC object retrieval not yet implemented")

    def batch_get_objects(self, identifiers: list[str]) -> list[CelestialObject]:
        """Batch retrieval (efficient for local CSV)"""
        # TODO: Implement batch query
        # - Use DataFrame.isin() for efficient filtering
        # - Convert all rows in single pass
        raise NotImplementedError("OpenNGC batch retrieval not yet implemented")


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
        # TODO: Implement DTO → domain mapping
        # - Extract classification from obj_type + hubble_type
        # - Build AngularSize with major/minor axes
        # - Extract surface brightness if surf_br_B exists
        # - Build aliases list (messier_nr, comname, other_id)
        # - Add provenance (source="openngc", fetched_at=now())
        raise NotImplementedError("OpenNGC adapter not yet implemented")

    def _map_type(self, obj_type: str, hubble_type: Optional[str]) -> 'ObjectClassification':
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
        # TODO: Implement type mapping
        # - Map obj_type to primary_type + subtype
        # - For galaxies, parse hubble_type → spiral/elliptical/lenticular
        # - Handle edge cases (Dup, NonEx, etc.)
        raise NotImplementedError("OpenNGC type mapping not yet implemented")

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
        # TODO: Implement Hubble type parsing
        # - Check for E prefix → elliptical
        # - Check for S0 → lenticular
        # - Check for SA/SB/SAB → spiral
        # - Check for I/Irr → irregular
        raise NotImplementedError("Hubble type parsing not yet implemented")
