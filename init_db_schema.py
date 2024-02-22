import os
import subprocess

from sqlalchemy import create_engine, text


def clear_alembic_version_history():
    engine = create_engine("sqlite:///celestial.db")
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


def regenerate_initial_migration(env):
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial schema"], check=True, env=env)
    print("Generated initial migration.")


def apply_migration(env):
    subprocess.run(["alembic", "upgrade", "head"], check=True, env=env)
    print("Applied migration to the database.")


if __name__ == "__main__":
    clear_migrations_folder()
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')
    clear_alembic_version_history()
    regenerate_initial_migration(env)
    apply_migration(env)
