# 🛡️ Terraguard

A lightweight, multi-cloud Terraform plan risk assessor designed for Continuous Integration (CI) environments, specifically GitHub Actions. It analyzes resource changes in a Terraform plan and determines a risk level, optionally failing the CI build for required manual review.

## 📚 Documentation

For detailed documentation, including API reference, configuration guides, and more examples, visit the [documentation site](https://jonathanmartin-dev.github.io/terraguard/).

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

## 📖 Usage

After installation, you can use the `tguard` command to assess risk in your Terraform plan JSON files.

### Basic Usage

```bash
tguard <path-to-terraform-plan.json>
```

### Example

```bash
tguard tests/fixtures/vpc.tfplan.json
```

**Example Output:**

```
### Terraform Plan Risk Assessment

**Risk Level:** `HIGH` (score: 90)

**Change Summary:**
- Total resources with changes: `31`
- Creates: `31`
- Updates: `0`
- Deletes: `0`
- High risk changes: `0`
- Critical changes: `0`
- High risk deletes: `0`
- Critical deletes: `0`

**Reasons / Signals:**
- 31 resource(s) will be changed (create/update/delete).
- High count of changes or deletions (Blast Radius).


Risk level `HIGH` is >= fail-on threshold `HIGH`. Failing for manual review.
```

The tool will exit with a non-zero status code if the assessed risk level meets or exceeds the configured threshold (default: `HIGH`), making it suitable for CI/CD pipeline gating.

### Using a Custom Risk Configuration

You can specify your own risk configuration file using the `--risk-config-path` option:

```bash
tguard tests/fixtures/vpc.tfplan.json --risk-config-path ./my-custom-risk-config.json
```

Or set it via environment variable:

```bash
export RISK_CONFIG_PATH=./my-custom-risk-config.json
tguard tests/fixtures/vpc.tfplan.json
```

**Example Risk Configuration (`risk_config.json`):**

```json
{
  "resource_risk_patterns": [
    {
      "pattern": "^aws_iam_.*",
      "risk_level": "CRITICAL",
      "reason": "Identity and Access Management resources are highly sensitive."
    },
    {
      "pattern": "^aws_security_group$",
      "risk_level": "HIGH",
      "reason": "Firewall rules control network access."
    },
    {
      "pattern": "^aws_db_instance$",
      "risk_level": "HIGH",
      "reason": "Database changes risk data integrity/availability."
    }
  ],
  "default_risk_level": "LOW"
}
```

The configuration uses regular expressions to match Terraform resource types and assign risk levels. Patterns are evaluated in order, and the highest matching risk level is used.

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
