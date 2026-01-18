# Rapid Prototype Workflow

This project uses **pipenv** (Pipfile / Pipfile.lock) to manage dependencies and the virtual environment.

The goal of this workflow is to get the database up and running quickly without relying on Alembic historical migrations.
Instead, we regenerate the schema via `init_db_schema.py` (destructive: it may drop data).

---

## Quick start (recommended)

If you’re coming back after a long time, use the bootstrap script to avoid re-learning the steps.

### 1) Run the bootstrap script
From the project root:

```bash
python init_project.py
```

What it does:

* Ensures `pipenv` is available (installs it if missing)
* Creates/uses the project’s pipenv environment
* Installs dependencies from **Pipfile.lock** (`pipenv sync`)
* Optionally runs the DB initialization script

> Tip (Windows): if `python` points to the wrong install, use `py`:
>
> ```bash
> py init_project.py
> ```

---

## Manual setup (step-by-step)

### 1) Install pipenv (one-time on your machine)

If `pipenv` is not available:

```bash
python -m pip install --user pipenv
```

Verify:

```bash
pipenv --version
```

### 2) Install dependencies (from the lockfile)

From the project root:

```bash
pipenv sync
```

If you want dev tools (tests/linters/etc.) as well:

```bash
pipenv sync --dev
```

**Difference**

* `pipenv sync` installs only `[packages]`
* `pipenv sync --dev` installs `[packages]` + `[dev-packages]`

### 3) Initialize / reset the database schema (destructive)

This regenerates the schema and may drop existing data:

```bash
pipenv run python init_db_schema.py
```

### 4) Run the application

Run your entrypoint using pipenv:

```bash
pipenv run python main.py
```

(Or run your configured “Main” in the IDE once the interpreter is set correctly.)

---

## IDE setup (PyCharm / IntelliJ)

If the IDE lost interpreter settings:

1. Go to **Project Interpreter**
2. Add interpreter → **Pipenv**
3. Point it at a valid `pipenv.exe` (Windows) or `pipenv` (macOS/Linux)
4. Use the project’s Pipfile folder as the working directory

Sanity-check from the IDE terminal:

```bash
pipenv --venv
pipenv run python --version
```

The Python version shown here is the one the project actually runs with.

---

## Notes / gotchas

* `pipenv sync` is the most reproducible option because it follows **Pipfile.lock** exactly.
* If you intentionally want to update dependency versions, use:

  ```bash
  pipenv install
  ```

  and commit the updated `Pipfile.lock`.
* If your environment ever gets into a weird state:

  ```bash
  pipenv --rm
  pipenv sync --dev
  ```