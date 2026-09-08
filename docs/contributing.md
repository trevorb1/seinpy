# Contributing

Development and code contributions to **seinpy** are highly welcome. Follow these steps to set up the repository for development and submit your changes.

---

## Code Contributions

### 1. Create a New Branch
Before making changes, create a descriptive branch:
```bash
git checkout -b feature-branch
```

### 2. Make Code Changes
Implement your feature or bug fix. Be sure to add matching unit tests in the `tests/` directory.

### 3. Run the Test Suite
Ensure all existing and new tests pass successfully:
```bash
uv run pytest
```

You can also run pytest with coverage tracking to identify untested code paths:
```bash
uv run pytest --cov=seinpy tests/ --cov-report=term-missing
```

### 4. Install and Run Pre-Commit Hooks
Run pre-commit validation to ensure correct formatting and linting (with `ruff`):
```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

### 5. Submit a Pull Request
Push your branch to your fork:
```bash
git push origin feature-branch
```
Then, launch a pull request on GitHub for review!

---

## Documentation Contributions

If you would like to edit or add documentation:

### 1. Install Documentation Dependencies

Make sure you sync the environment including the `docs` dependency group:

```bash
uv sync --group docs
```

### 2. Serve the Documentation Locally

Launch a local hot-reloading server to preview your changes immediately:

```bash
uv run mkdocs serve
```

Open your browser and navigate to `http://127.0.0.1:8000/`. Any changes you make to markdown files in the `docs/` folder or to `mkdocs.yml` will automatically refresh the browser.

### 3. Verify the Build

Before submitting your pull request, verify that the documentation builds cleanly without warnings or errors:

```bash
uv run mkdocs build
```

This will compile the static site into the `/site` directory. Note that the `/site` directory is ignored by Git.

### 4. Navigating Configuration

If you add new pages inside the `docs/` directory, make sure to add them to the navigation structure under the `nav` key in `mkdocs.yml` so they are accessible from the sidebar.
