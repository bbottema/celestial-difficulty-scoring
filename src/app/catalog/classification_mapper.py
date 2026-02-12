"""
Classification mapper - enriches and corrects object classifications.

Handles research-identified issues:
1. SIMBAD type corrections (M31 AGN→Galaxy, NGC 7000 Cluster→Emission Nebula)
2. OpenNGC type code mapping
3. Galaxy morphology parsing
4. Classification confidence scoring
"""
from typing import Optional

from app.domain.model.celestial_object import CelestialObject
from app.domain.model.object_classification import ObjectClassification


class ClassificationMapper:
    """
    Enriches and corrects celestial object classifications.

    Uses heuristics and cross-validation to fix known catalog issues.
    """

    def enrich_classification(self, obj: CelestialObject) -> CelestialObject:
        """
        Enrich or correct object classification.

        CORRECTION STRATEGIES:
        1. If SIMBAD source, validate against known issues
        2. Cross-validate type with size/magnitude heuristics
        3. Add confidence scoring
        4. Flag ambiguous classifications

        Args:
            obj: Object with initial classification

        Returns:
            Object with enriched/corrected classification
        """
        # TODO: Implement classification enrichment
        # Step 1: Check provenance source
        # if not obj.provenance:
        #     return obj
        #
        # source = obj.provenance[0].source
        #
        # Step 2: Apply source-specific corrections
        # if source == "simbad":
        #     obj = self._correct_simbad_classification(obj)
        # elif source == "openngc":
        #     obj = self._validate_openngc_classification(obj)
        #
        # Step 3: Heuristic validation
        # obj = self._validate_with_heuristics(obj)
        #
        # return obj
        raise NotImplementedError("Classification enrichment not yet implemented")

    def _correct_simbad_classification(self, obj: CelestialObject) -> CelestialObject:
        """
        Apply corrections for known SIMBAD classification issues.

        KNOWN ISSUES (from research):
        - M31: May be classified as "AGN" instead of "Galaxy"
        - NGC 7000: May be "Cluster of Stars" instead of "Emission Nebula"

        Strategy: Check raw_data from provenance for other_types
        """
        # TODO: Implement SIMBAD corrections
        # Check if raw_data available in provenance
        # if obj.provenance and hasattr(obj.provenance[0], 'raw_data'):
        #     raw = obj.provenance[0].raw_data
        #     other_types = raw.get('OTYPE_LIST', [])
        #
        #     # Priority: Check other_types for observing-relevant classes
        #     if 'HII' in other_types and not obj.classification.is_emission_nebula():
        #         obj.classification = ObjectClassification('nebula', 'emission', None)
        #     elif 'PN' in other_types and not obj.classification.is_planetary_nebula():
        #         obj.classification = ObjectClassification('nebula', 'planetary', None)
        #     # ... more corrections
        #
        # return obj
        raise NotImplementedError("SIMBAD corrections not yet implemented")

    def _validate_openngc_classification(self, obj: CelestialObject) -> CelestialObject:
        """
        Validate OpenNGC classifications.

        OpenNGC types are generally reliable, but check for:
        - Dup, NonEx flags
        - Missing morphology for galaxies
        """
        # TODO: Implement OpenNGC validation
        raise NotImplementedError("OpenNGC validation not yet implemented")

    def _validate_with_heuristics(self, obj: CelestialObject) -> CelestialObject:
        """
        Cross-validate classification with physical properties.

        HEURISTICS:
        - Very large size (>60 arcmin) + faint → likely emission nebula or galaxy
        - Small size (<1 arcmin) + high surface brightness → likely planetary nebula
        - Mag < 10 + size > 30 arcmin → likely open cluster or emission nebula
        - Mag > 15 + size < 5 arcmin → likely galaxy or globular cluster

        These don't override catalog data, but flag confidence issues.
        """
        # TODO: Implement heuristic validation
        # if obj.size.major_arcmin > 60 and obj.magnitude > 6:
        #     # Very large, faint → emission nebula or galaxy
        #     if not (obj.classification.is_emission_nebula() or obj.classification.is_galaxy()):
        #         # Flag low confidence
        #         if obj.provenance:
        #             obj.provenance[0].confidence = 0.7
        #
        # elif obj.size.major_arcmin < 1 and obj.surface_brightness and obj.surface_brightness.value < 10:
        #     # Small, high SB → planetary nebula
        #     if not obj.classification.is_planetary_nebula():
        #         if obj.provenance:
        #             obj.provenance[0].confidence = 0.7
        #
        # # ... more heuristics
        # return obj
        raise NotImplementedError("Heuristic validation not yet implemented")

    def map_legacy_type(self, classification: ObjectClassification) -> str:
        """
        Map enhanced classification to legacy object_type string.

        For backward compatibility with existing scoring code.

        Args:
            classification: Enhanced classification

        Returns:
            Legacy type string ("DeepSky", "SolarSystem", etc.)
        """
        # TODO: Implement legacy mapping
        # if classification.is_solar_system():
        #     return "SolarSystem"
        # elif classification.is_double_star():
        #     return "DoubleStar"
        # else:
        #     return "DeepSky"  # Catch-all for nebulae, galaxies, clusters
        raise NotImplementedError("Legacy type mapping not yet implemented")


class SurfaceBrightnessCalculator:
    """
    Computes surface brightness when not available from catalogs.

    Uses formula: SB = mag + 2.5 * log10(area_arcsec²)
    """

    def compute_surface_brightness(self, obj: CelestialObject) -> CelestialObject:
        """
        Compute average surface brightness from magnitude and size.

        Formula: SB ≈ mag + 2.5 × log₁₀(A) where A = area in arcsec²

        This is an AVERAGE surface brightness, not isophotal SB like
        OpenNGC's surf_br_B. Treat as estimate with lower confidence.

        Args:
            obj: Object with magnitude and size

        Returns:
            Object with computed surface_brightness field
        """
        # TODO: Implement SB computation
        # import math
        #
        # # Skip if already has surface brightness
        # if obj.surface_brightness is not None:
        #     return obj
        #
        # # Need magnitude and size
        # if obj.magnitude is None or obj.size is None:
        #     return obj
        #
        # # Compute area in arcsec²
        # area_sq_arcsec = obj.size.area_sq_arcsec()
        #
        # if area_sq_arcsec <= 0:
        #     return obj
        #
        # # Compute average SB
        # sb_value = obj.magnitude + 2.5 * math.log10(area_sq_arcsec)
        #
        # # Create SurfaceBrightness with provenance
        # from app.domain.model.object_classification import SurfaceBrightness
        # from app.domain.model.data_provenance import DataProvenance
        # from datetime import datetime
        #
        # obj.surface_brightness = SurfaceBrightness(
        #     value=sb_value,
        #     source="computed_mag_size",
        #     band="V"
        # )
        #
        # # Add provenance with lower confidence (0.7)
        # obj.provenance.append(DataProvenance(
        #     source="computed",
        #     fetched_at=datetime.now(),
        #     confidence=0.7
        # ))
        #
        # return obj
        raise NotImplementedError("Surface brightness computation not yet implemented")
