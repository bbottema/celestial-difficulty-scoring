"""
Generate pre-curated object list JSON files from OpenNGC catalog data.

This script reads the OpenNGC CSV files and generates JSON files for:
- messier_110.json - Messier Catalog (110 objects)
- caldwell_109.json - Caldwell Catalog (109 objects)
- solar_system.json - Solar System objects (9 objects)

Usage:
    python scripts/generate_object_lists.py

Output:
    data/object_lists/*.json
"""
import csv
import json
from pathlib import Path
from typing import Optional


def sex_to_deg_ra(ra_str: str) -> Optional[float]:
    """Convert RA from HH:MM:SS.SS to decimal degrees"""
    if not ra_str:
        return None
    try:
        parts = ra_str.split(':')
        h, m, s = float(parts[0]), float(parts[1]), float(parts[2])
        return (h + m / 60 + s / 3600) * 15  # Hours to degrees
    except:
        return None


def sex_to_deg_dec(dec_str: str) -> Optional[float]:
    """Convert Dec from ±DD:MM:SS.S to decimal degrees"""
    if not dec_str:
        return None
    try:
        sign = -1 if dec_str.startswith('-') else 1
        dec_str = dec_str.lstrip('+-')
        parts = dec_str.split(':')
        d, m, s = float(parts[0]), float(parts[1]), float(parts[2])
        return sign * (d + m / 60 + s / 3600)
    except:
        return None


def parse_float(value: str) -> Optional[float]:
    """Parse float, returning None for empty/invalid"""
    if not value or value.strip() == '':
        return None
    try:
        return float(value)
    except ValueError:
        return None


def map_object_type(ngc_type: str) -> str:
    """Map OpenNGC type codes to readable types"""
    type_map = {
        'G': 'galaxy',
        'GGroup': 'galaxy_group',
        'GPair': 'galaxy_pair',
        'GTrpl': 'galaxy_triplet',
        'OCl': 'open_cluster',
        'GCl': 'globular_cluster',
        'Cl+N': 'cluster_nebula',
        'PN': 'planetary_nebula',
        'HII': 'emission_nebula',
        'EmN': 'emission_nebula',
        'RfN': 'reflection_nebula',
        'SNR': 'supernova_remnant',
        'DrkN': 'dark_nebula',
        'NF': 'not_found',
        '*': 'star',
        '**': 'double_star',
        '*Ass': 'asterism',
        'Dup': 'duplicate',
    }
    return type_map.get(ngc_type, 'unknown')


def load_openngc_data(catalog_dir: Path) -> dict:
    """
    Load OpenNGC and addendum CSV files into a lookup dict.
    
    Returns:
        Dict mapping canonical_id (e.g., 'NGC0224') to row data
    """
    objects = {}
    
    # Load main NGC.csv
    ngc_path = catalog_dir / 'NGC.csv'
    if ngc_path.exists():
        with open(ngc_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                name = row.get('Name', '')
                if name:
                    objects[name] = row
    
    # Load addendum.csv (M40, M45, Caldwell, etc.)
    addendum_path = catalog_dir / 'addendum.csv'
    if addendum_path.exists():
        with open(addendum_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                name = row.get('Name', '')
                if name:
                    objects[name] = row
    
    return objects


def build_messier_index(objects: dict) -> dict:
    """
    Build Messier number → canonical_id mapping.
    
    Returns:
        Dict like {'001': 'NGC1952', '031': 'NGC0224', ...}
    """
    messier_map = {}
    for canonical_id, row in objects.items():
        messier_nr = row.get('M', '')
        if messier_nr and messier_nr.strip():
            # Pad to 3 digits
            m_num = messier_nr.strip().zfill(3)
            messier_map[m_num] = canonical_id
    return messier_map


def generate_messier_list(objects: dict, messier_map: dict) -> dict:
    """Generate Messier 110 catalog JSON"""
    messier_objects = []
    
    for m_num in range(1, 111):  # M1 to M110
        m_key = str(m_num).zfill(3)
        canonical_id = messier_map.get(m_key)
        
        if canonical_id and canonical_id in objects:
            row = objects[canonical_id]
            
            ra = sex_to_deg_ra(row.get('RA', ''))
            dec = sex_to_deg_dec(row.get('Dec', ''))
            mag = parse_float(row.get('V-Mag', '')) or parse_float(row.get('B-Mag', ''))
            obj_type = map_object_type(row.get('Type', ''))
            
            messier_objects.append({
                'name': f'M{m_num}',
                'canonical_id': canonical_id,
                'type': obj_type,
                'ra': round(ra, 4) if ra else 0.0,
                'dec': round(dec, 4) if dec else 0.0,
                'magnitude': round(mag, 1) if mag else 99.0
            })
        else:
            print(f"  Warning: M{m_num} not found in catalog (key={m_key})")
    
    return {
        'name': 'Messier Catalog',
        'description': 'The classic 110 deep-sky objects cataloged by Charles Messier (1730-1817). '
                       'These are the most popular targets for amateur astronomers.',
        'category': 'named_catalog',
        'version': '1.0',
        'created_date': '2026-02-13',
        'objects': messier_objects
    }


def generate_caldwell_list(objects: dict) -> dict:
    """
    Generate Caldwell 109 catalog JSON.
    
    Caldwell objects are identified by 'C' prefix in addendum or common names.
    """
    # Caldwell catalog - manually mapped canonical IDs
    # Source: https://en.wikipedia.org/wiki/Caldwell_catalogue
    caldwell_data = [
        ('C1', 'NGC0188', 'open_cluster'),
        ('C2', 'NGC0040', 'planetary_nebula'),
        ('C3', 'NGC4236', 'galaxy'),
        ('C4', 'NGC7023', 'reflection_nebula'),
        ('C5', 'IC0342', 'galaxy'),
        ('C6', 'NGC6543', 'planetary_nebula'),
        ('C7', 'NGC2403', 'galaxy'),
        ('C8', 'NGC0559', 'open_cluster'),
        ('C9', 'C009', 'emission_nebula'),  # Cave Nebula - in addendum
        ('C10', 'NGC0663', 'open_cluster'),
        ('C11', 'NGC7635', 'emission_nebula'),
        ('C12', 'NGC6946', 'galaxy'),
        ('C13', 'NGC0457', 'open_cluster'),
        ('C14', 'C014', 'open_cluster'),  # Double Cluster - in addendum
        ('C15', 'NGC6826', 'planetary_nebula'),
        ('C16', 'NGC7243', 'open_cluster'),
        ('C17', 'NGC0147', 'galaxy'),
        ('C18', 'NGC0185', 'galaxy'),
        ('C19', 'IC5146', 'emission_nebula'),
        ('C20', 'NGC7000', 'emission_nebula'),
        ('C21', 'NGC4449', 'galaxy'),
        ('C22', 'NGC7662', 'planetary_nebula'),
        ('C23', 'NGC0891', 'galaxy'),
        ('C24', 'NGC1275', 'galaxy'),
        ('C25', 'NGC2419', 'globular_cluster'),
        ('C26', 'NGC4244', 'galaxy'),
        ('C27', 'NGC6888', 'emission_nebula'),
        ('C28', 'NGC0752', 'open_cluster'),
        ('C29', 'NGC5005', 'galaxy'),
        ('C30', 'NGC7331', 'galaxy'),
        ('C31', 'IC0405', 'emission_nebula'),
        ('C32', 'NGC4631', 'galaxy'),
        ('C33', 'NGC6992', 'supernova_remnant'),
        ('C34', 'NGC6960', 'supernova_remnant'),
        ('C35', 'NGC4889', 'galaxy'),
        ('C36', 'NGC4559', 'galaxy'),
        ('C37', 'NGC6885', 'open_cluster'),
        ('C38', 'NGC4565', 'galaxy'),
        ('C39', 'NGC2392', 'planetary_nebula'),
        ('C40', 'NGC3626', 'galaxy'),
        ('C41', 'C041', 'open_cluster'),  # Hyades - in addendum
        ('C42', 'NGC7006', 'globular_cluster'),
        ('C43', 'NGC7814', 'galaxy'),
        ('C44', 'NGC7479', 'galaxy'),
        ('C45', 'NGC5248', 'galaxy'),
        ('C46', 'NGC2261', 'reflection_nebula'),
        ('C47', 'NGC6934', 'globular_cluster'),
        ('C48', 'NGC2775', 'galaxy'),
        ('C49', 'NGC2237', 'emission_nebula'),
        ('C50', 'NGC2244', 'open_cluster'),
        ('C51', 'IC1613', 'galaxy'),
        ('C52', 'NGC4697', 'galaxy'),
        ('C53', 'NGC3115', 'galaxy'),
        ('C54', 'NGC2506', 'open_cluster'),
        ('C55', 'NGC7009', 'planetary_nebula'),
        ('C56', 'NGC0246', 'planetary_nebula'),
        ('C57', 'NGC6822', 'galaxy'),
        ('C58', 'NGC2360', 'open_cluster'),
        ('C59', 'NGC3242', 'planetary_nebula'),
        ('C60', 'NGC4038', 'galaxy'),
        ('C61', 'NGC4039', 'galaxy'),
        ('C62', 'NGC0247', 'galaxy'),
        ('C63', 'NGC7293', 'planetary_nebula'),
        ('C64', 'NGC2362', 'open_cluster'),
        ('C65', 'NGC0253', 'galaxy'),
        ('C66', 'NGC5694', 'globular_cluster'),
        ('C67', 'NGC1097', 'galaxy'),
        ('C68', 'NGC6729', 'reflection_nebula'),
        ('C69', 'NGC6302', 'planetary_nebula'),
        ('C70', 'NGC0300', 'galaxy'),
        ('C71', 'NGC2477', 'open_cluster'),
        ('C72', 'NGC0055', 'galaxy'),
        ('C73', 'NGC1851', 'globular_cluster'),
        ('C74', 'NGC3132', 'planetary_nebula'),
        ('C75', 'NGC6124', 'open_cluster'),
        ('C76', 'NGC6231', 'open_cluster'),
        ('C77', 'NGC5128', 'galaxy'),
        ('C78', 'NGC6541', 'globular_cluster'),
        ('C79', 'NGC3201', 'globular_cluster'),
        ('C80', 'NGC5139', 'globular_cluster'),
        ('C81', 'NGC6352', 'globular_cluster'),
        ('C82', 'NGC6193', 'open_cluster'),
        ('C83', 'NGC4945', 'galaxy'),
        ('C84', 'NGC5286', 'globular_cluster'),
        ('C85', 'IC2391', 'open_cluster'),
        ('C86', 'NGC6397', 'globular_cluster'),
        ('C87', 'NGC1261', 'globular_cluster'),
        ('C88', 'NGC5823', 'open_cluster'),
        ('C89', 'NGC6087', 'open_cluster'),
        ('C90', 'NGC2867', 'planetary_nebula'),
        ('C91', 'NGC3532', 'open_cluster'),
        ('C92', 'NGC3372', 'emission_nebula'),
        ('C93', 'NGC6752', 'globular_cluster'),
        ('C94', 'NGC4755', 'open_cluster'),
        ('C95', 'NGC6025', 'open_cluster'),
        ('C96', 'NGC2516', 'open_cluster'),
        ('C97', 'NGC3766', 'open_cluster'),
        ('C98', 'NGC4609', 'open_cluster'),
        ('C99', 'C099', 'dark_nebula'),  # Coalsack - in addendum
        ('C100', 'IC2944', 'open_cluster'),
        ('C101', 'NGC6744', 'galaxy'),
        ('C102', 'IC2602', 'open_cluster'),
        ('C103', 'NGC2070', 'emission_nebula'),
        ('C104', 'NGC0362', 'globular_cluster'),
        ('C105', 'NGC4833', 'globular_cluster'),
        ('C106', 'NGC0104', 'globular_cluster'),
        ('C107', 'NGC6101', 'globular_cluster'),
        ('C108', 'NGC4372', 'globular_cluster'),
        ('C109', 'NGC3195', 'planetary_nebula'),
    ]
    
    caldwell_objects = []
    missing = []
    
    for c_name, canonical_id, obj_type in caldwell_data:
        if canonical_id in objects:
            row = objects[canonical_id]
            ra = sex_to_deg_ra(row.get('RA', ''))
            dec = sex_to_deg_dec(row.get('Dec', ''))
            mag = parse_float(row.get('V-Mag', '')) or parse_float(row.get('B-Mag', ''))
            
            caldwell_objects.append({
                'name': c_name,
                'canonical_id': canonical_id,
                'type': obj_type,
                'ra': round(ra, 4) if ra else 0.0,
                'dec': round(dec, 4) if dec else 0.0,
                'magnitude': round(mag, 1) if mag else 99.0
            })
        else:
            missing.append(f"{c_name} ({canonical_id})")
    
    if missing:
        print(f"  Warning: Missing Caldwell objects: {', '.join(missing)}")
    
    return {
        'name': 'Caldwell Catalog',
        'description': 'The Caldwell catalog of 109 deep-sky objects compiled by Sir Patrick Caldwell-Moore. '
                       'Designed as a supplement to the Messier catalog, featuring southern hemisphere objects.',
        'category': 'named_catalog',
        'version': '1.0',
        'created_date': '2026-02-13',
        'objects': caldwell_objects
    }


def generate_solar_system_list() -> dict:
    """Generate Solar System objects JSON (dynamic resolution via Horizons)"""
    return {
        'name': 'Solar System',
        'description': 'The planets and Moon of our Solar System. '
                       'Positions are calculated dynamically for current date/time.',
        'category': 'named_catalog',
        'version': '1.0',
        'created_date': '2026-02-13',
        'objects': [
            {'name': 'Mercury', 'canonical_id': 'Mercury', 'type': 'planet', 'ra': 0, 'dec': 0, 'magnitude': 0},
            {'name': 'Venus', 'canonical_id': 'Venus', 'type': 'planet', 'ra': 0, 'dec': 0, 'magnitude': -4.0},
            {'name': 'Mars', 'canonical_id': 'Mars', 'type': 'planet', 'ra': 0, 'dec': 0, 'magnitude': 0.5},
            {'name': 'Jupiter', 'canonical_id': 'Jupiter', 'type': 'planet', 'ra': 0, 'dec': 0, 'magnitude': -2.5},
            {'name': 'Saturn', 'canonical_id': 'Saturn', 'type': 'planet', 'ra': 0, 'dec': 0, 'magnitude': 0.5},
            {'name': 'Uranus', 'canonical_id': 'Uranus', 'type': 'planet', 'ra': 0, 'dec': 0, 'magnitude': 5.7},
            {'name': 'Neptune', 'canonical_id': 'Neptune', 'type': 'planet', 'ra': 0, 'dec': 0, 'magnitude': 7.8},
            {'name': 'Moon', 'canonical_id': 'Moon', 'type': 'moon', 'ra': 0, 'dec': 0, 'magnitude': -12.6},
            {'name': 'Sun', 'canonical_id': 'Sun', 'type': 'star', 'ra': 0, 'dec': 0, 'magnitude': -26.7},
        ]
    }


def main():
    # Paths
    project_root = Path(__file__).parent.parent
    catalog_dir = project_root / 'data' / 'catalogs'
    output_dir = project_root / 'data' / 'object_lists'
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading OpenNGC catalog data...")
    objects = load_openngc_data(catalog_dir)
    print(f"  Loaded {len(objects)} objects")
    
    # Build Messier index
    messier_map = build_messier_index(objects)
    print(f"  Found {len(messier_map)} Messier objects")
    
    # Generate Messier catalog
    print("\nGenerating messier_110.json...")
    messier_data = generate_messier_list(objects, messier_map)
    messier_path = output_dir / 'messier_110.json'
    with open(messier_path, 'w', encoding='utf-8') as f:
        json.dump(messier_data, f, indent=2)
    print(f"  Created {messier_path} ({len(messier_data['objects'])} objects)")
    
    # Generate Caldwell catalog
    print("\nGenerating caldwell_109.json...")
    caldwell_data = generate_caldwell_list(objects)
    caldwell_path = output_dir / 'caldwell_109.json'
    with open(caldwell_path, 'w', encoding='utf-8') as f:
        json.dump(caldwell_data, f, indent=2)
    print(f"  Created {caldwell_path} ({len(caldwell_data['objects'])} objects)")
    
    # Generate Solar System
    print("\nGenerating solar_system.json...")
    solar_data = generate_solar_system_list()
    solar_path = output_dir / 'solar_system.json'
    with open(solar_path, 'w', encoding='utf-8') as f:
        json.dump(solar_data, f, indent=2)
    print(f"  Created {solar_path} ({len(solar_data['objects'])} objects)")
    
    print("\nDone! Generated 3 object list files.")


if __name__ == '__main__':
    main()
