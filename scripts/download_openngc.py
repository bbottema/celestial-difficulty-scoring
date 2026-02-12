"""
Download OpenNGC catalog data.

Downloads the official OpenNGC NGC.csv file from GitHub.
"""
from pathlib import Path
import requests


def download_openngc():
    """Download OpenNGC catalog to data/catalogs/"""
    data_dir = Path(__file__).parent.parent / 'data' / 'catalogs'
    data_dir.mkdir(parents=True, exist_ok=True)

    csv_path = data_dir / 'NGC.csv'
    addendum_path = data_dir / 'addendum.csv'

    if csv_path.exists() and addendum_path.exists():
        print(f"OpenNGC catalog already exists: {csv_path}")
        print(f"OpenNGC addendum already exists: {addendum_path}")
        response = input("Re-download? (y/N): ")
        if response.lower() != 'y':
            print("Using existing files.")
            return csv_path

    # Download main NGC.csv
    print("Downloading OpenNGC catalog from GitHub...")
    ngc_url = "https://raw.githubusercontent.com/mattiaverga/OpenNGC/master/database_files/NGC.csv"

    try:
        response = requests.get(ngc_url, timeout=30)
        response.raise_for_status()

        csv_path.write_bytes(response.content)
        print(f"[OK] Downloaded NGC.csv: {csv_path}")
        print(f"  Size: {csv_path.stat().st_size / 1024:.1f} KB")

        # Count lines
        lines = csv_path.read_text(encoding='utf-8').count('\n')
        print(f"  Objects: ~{lines - 1} (excluding header)")

    except Exception as e:
        print(f"[FAIL] Failed to download NGC.csv: {e}")
        return None

    # Download addendum.csv (contains M40, M45)
    print("\nDownloading OpenNGC addendum (M40, M45)...")
    addendum_url = "https://raw.githubusercontent.com/mattiaverga/OpenNGC/master/database_files/addendum.csv"

    try:
        response = requests.get(addendum_url, timeout=30)
        response.raise_for_status()

        addendum_path.write_bytes(response.content)
        print(f"[OK] Downloaded addendum.csv: {addendum_path}")
        print(f"  Size: {addendum_path.stat().st_size / 1024:.1f} KB")

        # Count lines
        lines = addendum_path.read_text(encoding='utf-8').count('\n')
        print(f"  Objects: ~{lines - 1} (excluding header)")

    except Exception as e:
        print(f"[FAIL] Failed to download addendum.csv: {e}")
        print("  Note: Main catalog still downloaded successfully")

    return csv_path


if __name__ == "__main__":
    download_openngc()
