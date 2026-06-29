# Exordos CLI - Agent Guide

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```text
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## Project Structure and Module Organization

```text
exordos/
├── cmd/               # CLI entry point (cli.py)
├── builder/           # Build system modules
├── repo/              # Repository drivers (nginx.py, etc.)
├── packer/            # Image packaging logic
├── templates/         # Jinja2 templates for provisioning
├── tests/
│   ├── unit/         # Unit tests
│   └── functional/   # Functional tests
└── spec/              # OpenAPI specifications
```

**Key paths:**

- Source code: `exordos/`
- Tests: `exordos/tests/`
- Configuration: `pyproject.toml`, `tox.ini`, `Makefile`

## Build, Test, and Development Commands

### Testing

```bash
# Run all tests with coverage
tox

# Run specific test environment
tox -e py312          # Run tests on Python 3.12
tox -e ruff           # Run linter
tox -e mypy           # Run type checking

# Run pytest directly
pytest exordos/tests/unit/
pytest exordos/tests/functional/
```

### Development

```bash
# Install in development mode
pip install -e ".[dev,test]"

# Run documentation server
tox -e docs

# Build standalone binary
tox -e bin
```

## Code Style and Naming Conventions

### Style Guidelines

- **Indentation**: 4 spaces (Python standard)
- **Line length**: 88 characters (Ruff default)
- **Imports**: Grouped and sorted via Ruff (I rule)
- **Type hints**: Required for all function signatures

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `NginxRepoDriver`)
- **Functions/variables**: `snake_case` (e.g., `root_dir`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `PACKAGE_NAME`)
- **Private members**: Leading underscore (e.g., `_internal_method`)
- **Comments for code**: write on english

### Testing Requirements

- **Unit tests**: Located in `exordos/tests/unit/`
- **Functional tests**: Located in `exordos/tests/functional/`
- **Test naming**: `test_<method_name>_<scenario>`
- **Coverage**: Measured via `coverage.py`, HTML report in `cover/`

## VCS Recommendations

### Commit Message Format

```text
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`  
**Scopes**: `cli`, `builder`, `repo`, `packer`, `tests`

**Example:**

```text
feat(repo): add HTTP server proxy driver

- Implement SimplePythonRepoDriver for file serving
- Add port configuration and error handling
- Include unit tests for driver lifecycle

Closes #123
```

### Pull Request Requirements

- **Title**: Use imperative, present tense: "Add feature", not "Added feature"
- **Description**: Clear summary of changes

## Verification

When verifying changes, follow these rules:

- **Linting**: Run `tox -e ruff`. Do not invoke `ruff` directly — always go through tox.
- **Type checking**: Do NOT run `tox -e mypy` (or mypy in any form). Skip type checking entirely.
- **Tests**: Prefer `tox -e py312` or `pytest exordos/tests/unit/` for the relevant test scope.

## Additional Guidelines

### License

All source files must include Apache 2.0 license header:

```python
#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")
```

### Dependencies

- Manage via `pyproject.toml` and `uv.lock`
- Specify version constraints (e.g., `>=8.1.7,<9.0.0`)
- Include license information in comments

### Documentation

- Update `docs/` for CLI changes
- Run `tox -e cli_docs` to regenerate CLI docs
- Run `make mdlint` for Markdown linting
- Keep `README.md` synchronized with new features
