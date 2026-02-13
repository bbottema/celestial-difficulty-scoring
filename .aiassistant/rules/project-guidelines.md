---
apply: always
---

## Testing Principles

1. **Tests Before Implementation (TDD)**: Always write the test cases before implementing the feature or fix
2. **Relative Assertions**: Tests should use relative assertions, never arbitrary threshold assertions
3. **Meaningful Test Cases**: Tests should validate behavior and relationships, not magic numbers

## Event Architecture

The project uses different event handling patterns depending on the context:

### UI Events

**Direct wiring is allowed** for UI-related events (button clicks, widget signals, etc.) as long as:
- The code remains maintainable and readable
- It doesn't create spaghetti code with excessive coupling
- The control flow is clear and traceable

### Application Events (Non-UI)

**Use the event bus** for non-UI application events:
- Located in `src/app/config/event_bus_config.py`
- Provides decoupled communication between components
- Maintains clean separation of concerns

## Clean Code Principles

Follow the principles from "Clean Code" by Robert C. Martin (Uncle Bob), with pragmatic application:

### Self-Describing Code

1. **Variables**: Use descriptive, intention-revealing names
2. **Functions**: Names should clearly indicate what the function does

### Function and Class Design

- **Prefer small, focused functions and classes**
- **Avoid god-functions and classes**: Break down large functions into smaller, well-named helper functions. Each class should have one reason to change.
- **Pragmatic approach**: not every function needs to be a single-line operation

### Class Design

- **Dependency Injection**: Use the autowiring system in `src/app/config/autowire.py`

### Code Organization

- Follow the existing project structure:
  - `src/app/domain/`: Domain models and business logic (services)
  - `src/app/orm/`: ORM models and database interaction
  - `src/app/catalog/`: Catalog services and providers
  - `src/app/ui/`: UI components
  - `src/app/config/`: Configuration and dependency injection
  - `tests/`: Mirror the source structure

## Code Documentation

- **Don't document what you can self-describe**
- **Document the "why" not the "what"**

### Type Hints

- Use type hints consistently (project uses mypy for type checking)
- Configuration in `mypy.ini`
- Run tests with `python run_tests.py` before committing

## Additional Notes

- The project uses:
  - **Pipenv** for dependency management
  - **Alembic** for database migrations
  - **PyQt/PySide** for the UI layer
  - **SQLAlchemy** for ORM

- Follow existing patterns in the codebase when implementing new features
- Run tests with `python run_tests.py` before committing
