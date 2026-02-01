import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_project_root(project_root: Optional[str] = None) -> str:
    return project_root or os.path.dirname(os.path.abspath(__file__))


def get_database_path(project_root: Optional[str] = None) -> Path:
    root = Path(get_project_root(project_root))
    return root / "data" / "celestial.db"


def get_database_url(project_root: Optional[str] = None) -> str:
    db_path = get_database_path(project_root)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"


def clear_database(project_root: Optional[str] = None):
    db_path = get_database_path(project_root)
    if db_path.exists():
        db_path.unlink()
        print(f"Deleted existing database: {db_path}")
    else:
        print("No existing database to clear.")


def clear_migrations_folder(project_root: Optional[str] = None):
    root = get_project_root(project_root)
    versions_dir = os.path.join(root, "alembic", "versions")
    os.makedirs(versions_dir, exist_ok=True)

    for file in os.listdir(versions_dir):
        file_path = os.path.join(versions_dir, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    print("Cleared existing migrations.")


def regenerate_initial_migration(env, project_root: Optional[str] = None):
    root = get_project_root(project_root)
    subprocess.run(
        [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", "Initial schema"],
        check=True,
        env=env,
        cwd=root,
    )
    print("Generated initial migration.")


def apply_migration(env, project_root: Optional[str] = None):
    root = get_project_root(project_root)
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
        env=env,
        cwd=root,
    )
    print("Applied migration to the database.")


if __name__ == "__main__":
    project_root = get_project_root()

    clear_migrations_folder(project_root)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(project_root, "src")
    clear_database(project_root)
    regenerate_initial_migration(env, project_root)
    apply_migration(env, project_root)
