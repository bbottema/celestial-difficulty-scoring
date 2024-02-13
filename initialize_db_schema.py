import os
import subprocess

from sqlalchemy import create_engine, text

# Configure your database URL
DATABASE_URL = "sqlite:///celestial.db"  # Adjust for your database


def clear_alembic_version_history():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        print("Cleared Alembic version history.")


def clear_migrations_folder():
    versions_dir = os.path.join("alembic", "versions")
    for file in os.listdir(versions_dir):
        file_path = os.path.join(versions_dir, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    print("Cleared existing migrations.")


def regenerate_initial_migration():
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial schema"], check=True)
    print("Generated initial migration.")


def apply_migration():
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    print("Applied migration to the database.")


if __name__ == "__main__":
    clear_alembic_version_history()
    clear_migrations_folder()
    regenerate_initial_migration()
    apply_migration()
