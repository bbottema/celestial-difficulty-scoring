import argparse
import subprocess
import sys
import os
import shutil


def strip_inline_comment(line: str) -> str:
    """Remove TOML-style inline comments (# ...) unless inside quotes."""
    in_single = False
    in_double = False
    escaped = False

    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue

        if ch == "\\":
            escaped = True
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            continue

        if ch == "#" and not in_single and not in_double:
            return line[:i].rstrip()

    return line.rstrip()


def find_python_executable():
    """Best-effort lookup of a usable Python executable path.

    This is primarily a fallback for cases where `sys.executable` is empty or
    points to a non-existent path.
    """

    def looks_like_python_exe(path: str) -> bool:
        return bool(path) and os.path.isfile(path) and path.lower().endswith(".exe")

    if os.name == "nt":
        try:
            completed = subprocess.run(["where", "python"], check=True, capture_output=True, text=True)
            paths = [p.strip() for p in completed.stdout.splitlines() if p.strip()]
        except (subprocess.CalledProcessError, FileNotFoundError):
            paths = []

        paths = [p for p in paths if looks_like_python_exe(p)]
        non_store_paths = [p for p in paths if "WindowsApps" not in p]
        if non_store_paths:
            return non_store_paths[0]
        if paths:
            return paths[0]

        py_launcher = shutil.which("py")
        if py_launcher:
            try:
                completed = subprocess.run([py_launcher, "-0p"], check=True, capture_output=True, text=True)
                for line in completed.stdout.splitlines():
                    line = line.strip()
                    if not line:
                        continue

                    if ":" in line and line.lower().endswith(".exe") and looks_like_python_exe(line):
                        return line

                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        candidate = parts[1].strip()
                        if looks_like_python_exe(candidate):
                            return candidate
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        python_on_path = shutil.which("python")
        if python_on_path and looks_like_python_exe(python_on_path):
            return python_on_path

        return None

    return shutil.which("python3") or shutil.which("python")


def parse_required_python_version(pipfile_path: str):
    """Parse Pipfile [requires] and return a required Python version tuple.

    Returns:
        (major,) or (major, minor) or (major, minor, micro) if specified, else None.

    Notes:
        We intentionally avoid external TOML dependencies in this bootstrap script.
    """

    def parse_version_string(value):
        value = (value or "").strip().strip('"').strip("'")
        if not value:
            return None
        parts = [p for p in value.split(".") if p]
        try:
            return tuple(int(p) for p in parts)
        except ValueError:
            return None

    if not pipfile_path or not os.path.isfile(pipfile_path):
        return None

    in_requires = False
    python_version = None
    python_full_version = None
    try:
        with open(pipfile_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                line = strip_inline_comment(line).strip()
                if not line:
                    continue

                if line.startswith("[") and line.endswith("]"):
                    in_requires = (line == "[requires]")
                    continue

                if not in_requires or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key == "python_full_version":
                    python_full_version = value
                elif key == "python_version":
                    python_version = value
    except OSError:
        return None

    parsed = parse_version_string(python_full_version) or parse_version_string(python_version)
    if not parsed:
        return None

    # Normalize / validate: require at least major, and only care about first 3 parts.
    parsed = parsed[:3]
    if parsed[0] < 2:
        return None
    return parsed


def get_python_version_info(python_path: str):
    """Return (major, minor, micro) for the given interpreter, best-effort."""
    try:
        completed = subprocess.run(
            [
                python_path,
                "-c",
                "import sys; v=sys.version_info; print(f'{v[0]}.{v[1]}.{v[2]}')",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    out = (completed.stdout or "").strip()
    parts = out.split(".")
    if len(parts) < 2:
        return None
    try:
        nums = tuple(int(p) for p in parts[:3])
    except ValueError:
        return None
    if len(nums) == 2:
        return nums[0], nums[1], 0
    return nums


def python_satisfies_required(python_path: str, required_version):
    version_info = get_python_version_info(python_path)
    if not version_info:
        return False

    if len(required_version) >= 1 and version_info[0] != required_version[0]:
        return False
    if len(required_version) >= 2 and version_info[1] != required_version[1]:
        return False
    if len(required_version) >= 3 and version_info[2] != required_version[2]:
        return False
    return True


def find_python_for_version(required_version):
    """Best-effort lookup of an interpreter matching required_version."""
    if not required_version:
        return None

    major = required_version[0]
    minor = required_version[1] if len(required_version) >= 2 else None

    if os.name == "nt":
        py_launcher = shutil.which("py")
        if py_launcher:
            selector = f"-{major}" if minor is None else f"-{major}.{minor}"
            try:
                completed = subprocess.run(
                    [py_launcher, selector, "-c", "import sys; print(sys.executable)"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                candidate = (completed.stdout or "").strip()
                if candidate and os.path.isfile(candidate):
                    return candidate
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        # Fall back to earlier heuristics.
        return find_python_executable()

    if minor is not None:
        return shutil.which(f"python{major}.{minor}")
    return shutil.which(f"python{major}") or shutil.which("python3") or shutil.which("python")


def is_pipenv_installed(python_path: str) -> bool:
    """Check if pipenv is installed for the given Python interpreter."""
    try:
        subprocess.run([python_path, "-m", "pipenv", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_pipenv(python_path: str):
    """Install pipenv using pip."""
    print("Installing pipenv...")
    try:
        subprocess.run([python_path, "-m", "pip", "install", "--user", "pipenv"], check=True)
    except subprocess.CalledProcessError:
        subprocess.run([python_path, "-m", "pip", "install", "pipenv"], check=True)


def get_pipenv_env_python_major_minor(python_path: str, project_root: str):
    """Return (major, minor) for the project's Pipenv environment, best-effort."""
    try:
        completed = subprocess.run(
            [
                python_path,
                "-m",
                "pipenv",
                "run",
                "python",
                "-c",
                "import sys; v=sys.version_info; print(f'{v[0]}.{v[1]}')",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=project_root,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    out = (completed.stdout or "").strip()
    parts = out.split(".")
    if len(parts) < 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def run_pipenv_sync(python_path: str, project_root: str):
    """Create/select the pipenv environment for the given Python and sync dependencies from Pipfile.lock."""
    print(f"Using Python interpreter: {python_path}")

    required = parse_required_python_version(os.path.join(project_root, "Pipfile"))
    required_major_minor = required[:2] if required and len(required) >= 2 else None

    # Avoid forcing pipenv to recreate/retarget the environment if it already exists.
    env_exists = False
    try:
        completed = subprocess.run(
            [python_path, "-m", "pipenv", "--venv"],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
        )
        venv_path = (completed.stdout or "").strip()
        env_exists = (completed.returncode == 0 and bool(venv_path))
        if env_exists and required_major_minor:
            env_mm = get_pipenv_env_python_major_minor(python_path, project_root)
            if env_mm == tuple(required_major_minor):
                print("Existing Pipenv environment detected, skipping --python selection.")
            else:
                req_str = f"{required_major_minor[0]}.{required_major_minor[1]}"
                env_str = f"{env_mm[0]}.{env_mm[1]}" if env_mm else "unknown"
                print(
                    "Existing Pipenv environment detected but Python version does not match Pipfile "
                    f"(env: {env_str}, required: {req_str}); running --python selection."
                )
                env_exists = False
        elif env_exists:
            print("Existing Pipenv environment detected, skipping --python selection.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        env_exists = False

    if not env_exists:
        subprocess.run([python_path, "-m", "pipenv", "--python", python_path], check=True, cwd=project_root)

    # Best-effort: show what Python Pipenv will actually run inside the environment.
    try:
        completed = subprocess.run(
            [python_path, "-m", "pipenv", "run", "python", "--version"],
            check=True,
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        version_line = (completed.stdout or completed.stderr or "").strip()
        if version_line:
            print(f"Pipenv environment Python: {version_line}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    print("Running pipenv sync...")
    subprocess.run([python_path, "-m", "pipenv", "sync", "--dev"], check=True, cwd=project_root)


def init_db_schema(python_path: str, project_root: str):
    """Run the init_db_schema.py script."""
    print("Initializing database schema...")
    subprocess.run(
        [python_path, "-m", "pipenv", "run", "python", "init_db_schema.py"],
        check=True,
        cwd=project_root,
    )


def resolve_python_executable(project_root: str, argv=None, environ=None) -> str:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--python",
        dest="python_path",
        help="Explicit path to the Python interpreter to use for this project.",
    )
    # Be tolerant of unknown CLI args (e.g., when run from IDE wrappers).
    args, _unknown = parser.parse_known_args(argv)

    environ = os.environ if environ is None else environ
    override = args.python_path or environ.get("PROJECT_PYTHON")
    if override:
        if not os.path.isfile(override):
            raise RuntimeError(f"Provided Python path does not exist: {override}")
        return override

    required = parse_required_python_version(os.path.join(project_root, "Pipfile"))
    if required and len(required) >= 1:
        print(f"Pipfile requires Python {'.'.join(str(p) for p in required)}")

    python_executable_path = sys.executable
    if not python_executable_path or not os.path.isfile(python_executable_path):
        python_executable_path = find_python_executable()

    if not python_executable_path:
        raise RuntimeError(
            "Could not locate a Python interpreter. "
            "Please run this script with a valid Python (e.g., `py init_project.py`)."
        )

    if required and len(required) >= 1:
        required_for_check = required[:2] if len(required) >= 2 else required[:1]
        if not python_satisfies_required(python_executable_path, required_for_check):
            resolved = find_python_for_version(required_for_check)
            if resolved and os.path.isfile(resolved):
                print(f"Switching to required Python interpreter: {resolved}")
                return resolved
            print(
                "Warning: Could not locate the Pipfile-required Python version. "
                f"Proceeding with: {python_executable_path}"
            )

    return python_executable_path


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    python_executable_path = resolve_python_executable(project_root)

    if not is_pipenv_installed(python_executable_path):
        install_pipenv(python_executable_path)

    run_pipenv_sync(python_executable_path, project_root)

    init_db = input("Do you want to initialize the database schema? (y/n): ").strip().lower()
    if init_db == 'y':
        init_db_schema(python_executable_path, project_root)


if __name__ == "__main__":
    main()
