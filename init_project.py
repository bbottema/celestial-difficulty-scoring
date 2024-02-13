import subprocess
import sys
import os


def is_pipenv_installed():
    """Check if pipenv is installed."""
    try:
        subprocess.run(["pipenv", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_pipenv():
    """Install pipenv using pip."""
    print("Installing pipenv...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pipenv"], check=True)


def find_python_executable():
    """Attempt to find the Python executable path."""
    try:
        cmd = ["where", "python"] if os.name == 'nt' else ["which", "python"]
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        paths = result.stdout.decode().replace('\r\n', '\n').split('\n')
        return paths[0] if paths else None
    except subprocess.CalledProcessError:
        return None


def run_pipenv_sync(python_path):
    """Run pipenv sync to install project dependencies, specifying Python path if provided."""
    print("Running pipenv sync...")
    subprocess.run(["pipenv", "sync", "--python", python_path], check=True)


def init_db_schema(python_path):
    """Run the init_db_schema.py script."""
    print("Initializing database schema...")
    subprocess.run(["pipenv", "run", "python", "init_db_schema.py"], check=True)


def main():
    if not is_pipenv_installed():
        install_pipenv()

    python_executable_path = find_python_executable()
    if python_executable_path:
        print(f"Python executable found: {python_executable_path}")
    else:
        print("Python executable not found. Exiting...")
        exit(1)

    run_pipenv_sync(python_executable_path)

    init_db = input("Do you want to initialize the database schema? (y/n): ").strip().lower()
    if init_db == 'y':
        init_db_schema(python_executable_path)


if __name__ == "__main__":
    main()
