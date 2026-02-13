---
apply: by model decision
instructions: Apply when changing code
---

## Testing

- TDD: write tests first.
- Use relative assertions; avoid arbitrary thresholds.
- Prefer behavior/relationships over magic numbers.

## Events

- UI: direct wiring is fine if it stays readable/maintainable.
- Non-UI: use the event bus (`src/app/config/event_bus_config.py`).

## Clean Code

- Self-describing names for variables and functions.
- Prefer small, focused functions/classes; avoid god-classes.
- Keep pragmatism: not everything must be one-liner simple.
- DI via `src/app/config/autowire.py`.

## Code Organization

- Follow existing structure under `src/app/` and mirror in `tests/`.

## Code Docs

- Don’t comment what the name can say; comment the “why.”

## Type Hints

- Use type hints consistently; mypy config in `mypy.ini`.

## Notes

- Stick to existing patterns and project tooling.
- Run tests with `python run_tests.py` before committing
- The project uses:
  - **Pipenv** for dependency management
  - **Alembic** for database migrations
  - **PyQt/PySide** for the UI layer
  - **SQLAlchemy** for ORM