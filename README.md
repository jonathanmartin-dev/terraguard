# 🛡️ Terraguard

A lightweight, multi-cloud Terraform plan risk assessor designed for Continuous Integration (CI) environments, specifically GitHub Actions. It analyzes resource changes in a Terraform plan and determines a risk level, optionally failing the CI build for required manual review.

## 🚀 Features

- **Risk Scoring:** Assigns a risk level (LOW, MEDIUM, HIGH) and a numeric score to the entire Terraform plan.
- **Configurable Sensitivity:** Uses external configuration (e.g., `risk_config.json`) with Regular Expressions to identify high-risk resources across any provider (AWS, GCP, Azure, Kubernetes, etc.).
- **CI Gating:** Fails the CI/CD pipeline if the assessed risk exceeds a configured threshold (e.g., fail on `MEDIUM` or `HIGH`).
- **GitHub Integration:** Automatically posts a formatted summary of the risk assessment as a comment on the associated Pull Request.

## ⚙️ Installation

The best practice is to install the package in an isolated virtual environment (`.venv`) or directly within your CI environment.

### 1. Requirements

- Python 3.8+
- A generated Terraform plan JSON file (from `terraform show -json ...`).

### 2. Install from Source

Navigate to the project root directory and run:

```bash
# Install the package in editable mode for development
pip install -e .
```

## 🛠️ Development Setup

To set up the project for development:

### 1. Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 2. Activate the Virtual Environment

**On macOS/Linux:**

```bash
source .venv/bin/activate
```

**On Windows:**

```bash
.venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
# Install the package with all development dependencies
pip install -e ".[dev]"
```

This will install:

- **Documentation tools:** mkdocs, mkdocs-material, mkdocstrings, and plugins
- **Code formatting:** black
- **Type checking:** mypy
- **Testing:** pytest, pytest-cov
- **Linting:** ruff
- **Pre-commit hooks:** pre-commit

### 4. Set Up Pre-commit Hooks (Optional)

```bash
pre-commit install
```

This will automatically run code quality checks (formatting, linting) before each commit.
