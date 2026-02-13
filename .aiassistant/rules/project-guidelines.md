CODE word: moomoo

# Project Guidelines

This document provides baseline instructions for maintaining consistency across the Celestial Difficulty Scoring project.

## Documentation Synchronization

When updating project documentation, ensure consistency across related documents:

### SCORING_IMPROVEMENT_PLAN.md Synchronization

- **Ongoing Work**: Changes to `SCORING_IMPROVEMENT_PLAN.md` must be reflected in the corresponding phase document under `/planning/phase-N_<phase-name>.md`
- **Completed Phases**: When marking work as complete, move the relevant content from `SCORING_IMPROVEMENT_PLAN.md` to `/planning/COMPLETED_PHASES.md` and update the specific phase document accordingly
- Always maintain bidirectional consistency – changes in phase documents should be reflected in the main plan

## Test-Driven Development (TDD)

**Write tests first, then implement.**

### Testing Principles

1. **Tests Before Implementation**: Always write the test cases before implementing the feature or fix
2. **Relative Assertions**: Tests should use relative assertions, never arbitrary threshold assertions
   - ✅ Good: `assert result > baseline` or `assert abs(actual - expected) < tolerance * expected`
   - ❌ Bad: `assert result < 100` or `assert value == 42`
3. **Meaningful Test Cases**: Tests should validate behavior and relationships, not magic numbers
4. Ensure tests **are descriptive and self-documenting**

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

- **Prefer small, focused functions and classes**: Each function should have a clear, single purpose. Classes should be focussed.
- **Avoid god-functions and classes**: Break down large functions into smaller, well-named helper functions. Each class should have one reason to change.
- **Pragmatic approach**: Balance purity with practicality - not every function needs to be a single-line operation

### Class Design

- **Dependency Injection**: Use the autowiring system in `src/app/config/autowire.py`

### Documentation

- **Don't document what you can self-describe**: If a variable or function name clearly expresses intent, additional documentation is unnecessary
- **Document the "why" not the "what"**: Comments should explain reasoning, edge cases, or non-obvious decisions
- **Keep documentation synchronized**: When code changes, update corresponding documentation

### Code Organization

- Follow the existing project structure:
  - `src/app/domain/`: Domain models and business logic (services)
  - `src/app/orm/`: ORM models and database interaction
  - `src/app/catalog/`: Catalog services and providers
  - `src/app/ui/`: UI components
  - `src/app/config/`: Configuration and dependency injection
  - `tests/`: Mirror the source structure

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
