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

    if csv_path.exists():
        print(f"OpenNGC catalog already exists: {csv_path}")
        response = input("Re-download? (y/N): ")
        if response.lower() != 'y':
            print("Using existing file.")
            return csv_path

    print("Downloading OpenNGC catalog from GitHub...")
    url = "https://raw.githubusercontent.com/mattiaverga/OpenNGC/master/database_files/NGC.csv"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        csv_path.write_bytes(response.content)
        print(f"[OK] Downloaded successfully: {csv_path}")
        print(f"  Size: {csv_path.stat().st_size / 1024:.1f} KB")

        # Count lines
        lines = csv_path.read_text(encoding='utf-8').count('\n')
        print(f"  Objects: ~{lines - 1} (excluding header)")

        return csv_path

    except Exception as e:
        print(f"[FAIL] Failed to download: {e}")
        return None


if __name__ == "__main__":
    download_openngc()
