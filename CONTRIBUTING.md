# Contributing to copilot-orchestrator

First off, thank you for considering contributing to the Copilot Orchestrator! It's people like you who make this a great tool.

## 🛠 Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for extremely fast Python package management.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-org/copilot-orchestrator.git
    cd copilot-orchestrator
    ```

2.  **Initialize the environment**:
    We provide a `Makefile` to handle all setup steps (installing dependencies and pre-commit hooks):
    ```bash
    make setup
    ```

## 🔄 Workflow

### 📝 Commit Convention
We use [Commitizen](https://commitizen-tools.github.io/commitizen/) and **Conventional Commits**. This is critical because our automated release system (`release.yml`) decides the next version based on these prefixes.

**Format**: `<type>(<scope>): <description>`

Common types:
- `feat`: A new feature (bumps **Minor** version).
- `fix`: A bug fix (bumps **Patch** version).
- `docs`: Documentation changes.
- `refactor`: Code change that neither fixes a bug nor adds a feature.
- `chore`: Updating build tasks, package manager configs, etc.

*Example*: `feat(domain): add user session entity`

### 🛡 Code Quality
Before pushing, ensure all checks pass:

- **Lint & Type Check**: `make lint` (runs Ruff and MyPy)
- **Tests**: `make test` (runs PyTest)
- **Everything**: `make check`

### 🪝 Pre-commit Hooks
We use `pre-commit` to ensure code is formatted and linted before it even hits the repo. These are installed automatically during `make setup`. They will block commits if your code doesn't meet the standards.

## 🚀 Releasing
Versioning is automated. When a PR is merged into `main`, GitHub Actions will:
1.  Analyze your commits.
2.  Bump the version in `pyproject.toml`.
3.  Update `CHANGELOG.md`.
4.  Create a new Git Tag and GitHub Release.

---

*Happy Coding!*
