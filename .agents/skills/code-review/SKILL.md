---
name: code-review
description: >-
  Conducts structured, thorough code reviews on modified files, git diffs, pull requests,
  or specified modules. Evaluates correctness, edge cases, repository conventions, test coverage,
  code health, and performance.
---

# Code Review Skill

This skill provides a systematic workflow for conducting high-quality, actionable code reviews in this workspace.

---

## When to Use This Skill

Activate this skill when:
- The user requests a review of their current changes, branch, or pull request.
- The user asks for a review of specific files, classes, functions, or commits.
- Validating code before committing, merging, or releasing.

---

## Review Workflow

### Step 1: Identify Review Scope
Determine what code needs review based on user input or git state:
- **Uncommitted / Working changes**:
  ```bash
  git status
  git diff
  git diff --staged
  ```
- **Branch changes against upstream / main**:
  ```bash
  git diff main...HEAD
  # or
  git diff origin/main...HEAD
  ```
- **Explicit target files or directories**:
  Inspect specified files directly.

---

### Step 2: Run Automated Checks
Always verify automated baselines before manual inspection:
1. **Linting & Formatting**:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   ```
2. **Test Suite**:
   ```bash
   uv run pytest
   ```

---

### Step 3: Evaluate Core Review Dimensions

Inspect the changes across the following criteria:

#### 1. Correctness & Logic
- Does the implementation satisfy all requirements without introducing regressions?
- Are edge cases handled (e.g., empty datasets, `None`/null values, zero division, boundary values)?
- Is error handling graceful and descriptive? Are exceptions caught at the right granularity?
- Are data transformations accurate and deterministic?

#### 2. Repository Conventions & Standards
Verify compliance with [.agents/rules/general.md](file:///home/trevor/repos/seinpy/.agents/rules/general.md):
- **Docstrings**:
  - Every module has a top-level module description.
  - Every class, method, and function has a docstring.
  - Docstrings adhere to **Google style guide** conventions (Args, Returns, Raises, Examples).
- **Tooling & Packages**:
  - Code formatted and linted with **Ruff**.
  - **Polars** used instead of Pandas where possible.
  - Package dependencies managed via **UV**.
  - No new external dependencies added without prior user approval.
- **Documentation**:
  - Docstrings and Markdown docs align with MkDocs conventions.
  - API reference documentation kept clean and separate from high-level guides.

#### 3. Test Coverage & Quality
- Are all new or modified functions covered by automated unit tests?
- Test file naming: `tests/xxx_test.py` where `xxx` matches the module under test.
- Test organization: Tests are structured in classes where appropriate (e.g., `class TestFeatureName:`).
- Shared fixtures: Placed in `tests/conftest.py` rather than duplicated across test files.
- Assertions: Check meaningful outcomes and boundary conditions, not just happy paths.

#### 4. Architecture, Maintainability & Performance
- **Type Annotations**: Accurate Python 3.13+ typing used on function signatures.
- **Readability & Complexity**: Functions remain focused with single responsibilities. Avoid excessive nesting or overly dense expressions.
- **Performance**: Efficient Polars operations (avoiding round-trips to Python objects or loops over rows).
- **Security**: No hardcoded credentials, safe file and network handling.

---

## Output Format

Structure code review feedback clearly using the template below:

### 1. Summary & Verdict
Provide a brief summary of the changes and an overall verdict:
- `✅ Approved`: Ready to merge/commit as is.
- `⚠️ Approved with Suggestions`: Minor improvements recommended; non-blocking.
- `❌ Changes Requested`: Critical issues, bugs, or standard violations must be addressed.

### 2. Categorized Findings
Group review comments by severity level:

- 🚨 **Critical / Blocker**
  *Issues that cause crashes, data corruption, security flaws, or broken functionality.*
- ⚠️ **Major / Needs Attention**
  *Logic flaws, missing edge cases, convention violations (e.g., missing docstrings, incorrect test structure), or performance bottlenecks.*
- 💡 **Minor / Suggestion**
  *Readability improvements, idiomatic Python/Polars idioms, naming, or minor cleanup.*
- 🌟 **Positive Highlights**
  *Well-designed logic, thorough tests, or clean patterns worth noting.*

### 3. Actionable Recommendations
For every finding:
1. Link to the exact file and line using clickable markdown links: `[file.py:L10-L15](file:///path/to/file.py#L10-L15)`.
2. Explain the problem and why it matters.
3. Provide a clear code diff or example solution.
