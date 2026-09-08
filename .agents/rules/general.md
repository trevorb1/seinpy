---
trigger: always_on
---

# General Workspace Rules

These are general guidelines for working on the `seinpy` repository.

## Coding Style & Standards
- Use ruff as the formater and linter.
- Ensure all modules have top level descriptions.
- Ensure all functions, methods, and classes have docstrings. 
- Follow Google style guide conventions for docstrings

## Testing
- Place tests in the `tests/` directory.
- Name each test file as "xxx_test.py" where "xxx" is the name of the corresponding python module that is being tested. 
- Use pytest as the testing library 
- Shared test fixtures can be placed in tests/conftest.py
- Tests should be nested in classes where possible. 

## Python packages 
- Use polars where possible instead of pandas 
- Do not add a new dependency without getting permission from me first 
- Use UV for dependency management.

## Documentation 
- Use the MKDocs theme.
- Keep API docs seperate from reference documentation.
- Embed examples where applicable. 