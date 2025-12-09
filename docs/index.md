# 🛡️ Terraguard

A lightweight, multi-cloud Terraform plan risk assessor designed for Continuous Integration (CI) environments, specifically GitHub Actions. It analyzes resource changes in a Terraform plan and determines a risk level, optionally failing the CI build for required manual review.

## 🚀 Features

- **Risk Scoring:** Assigns a risk level (LOW, MEDIUM, HIGH) and a numeric score to the entire Terraform plan.
- **Configurable Sensitivity:** Uses external configuration (e.g., `risk_config.json`) with Regular Expressions to identify high-risk resources across any provider (AWS, GCP, Azure, Kubernetes, etc.).
- **CI Gating:** Fails the CI/CD pipeline if the assessed risk exceeds a configured threshold (e.g., fail on `MEDIUM` or `HIGH`).
- **GitHub Integration:** Automatically posts a formatted summary of the risk assessment as a comment on the associated Pull Request.

## ⚙️ Installation

The best practice is to install the package in an isolated virtual environment (`.venv`) or directly within your CI environment.

### Requirements

- Python 3.8+
- A generated Terraform plan JSON file (from `terraform show -json ...`).

### Install from Source

Navigate to the project root directory and run:

```bash
# Install the package in editable mode for development
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

## 📖 Quick Start

1. **Generate a Terraform plan JSON file:**

   ```bash
   terraform plan -out=plan.out
   terraform show -json plan.out > plan.json
   ```

2. **Run the risk assessment:**

   ```bash
   tguard plan.json
   ```

3. **The tool will:**
   - Analyze the plan and assess risk
   - Print a markdown summary to stdout
   - Optionally post a comment to GitHub (if running in GitHub Actions)
   - Exit with code 1 if risk exceeds threshold (default: HIGH)

## 🔧 How It Works

1. **Plan Loading:** Reads and parses the Terraform plan JSON file
2. **Change Summarization:** Analyzes resource changes and categorizes them by action type (create/update/delete)
3. **Risk Mapping:** Maps each resource type to a risk level using regex patterns from the configuration
4. **Risk Assessment:** Evaluates overall risk based on:
   - Critical and high-risk resource changes
   - Deletion of sensitive resources
   - Blast radius (total number of changes)
5. **Output:** Formats results as markdown and optionally posts to GitHub

## 🎯 Risk Levels

The tool uses three risk levels:

- **LOW** (score: 10): Minimal risk changes
- **MEDIUM** (score: 50): Moderate risk requiring review
- **HIGH** (score: 90): High risk requiring manual approval

The risk assessment considers:

- Resource type sensitivity (IAM, security groups, databases, etc.)
- Action type (deletions are higher risk than updates)
- Total change count (blast radius)

## 📚 Documentation

Explore the documentation to learn more:

- **[Usage Guide](usage.md)** - Detailed usage examples, CLI options, and GitHub Actions integration
- **[Configuration](configuration.md)** - Risk configuration file format, examples, and best practices
- **[API Reference](api/index.md)** - Complete API documentation for all modules

## 💡 Example Output

The tool generates a markdown summary like this:

```markdown
### Terraform Plan Risk Assessment

**Risk Level:** `MEDIUM` (score: 50)

**Change Summary:**

- Total resources with changes: `5`
- Creates: `2`
- Updates: `2`
- Deletes: `1`
- High risk changes: `1`
- Critical changes: `0`
- High risk deletes: `0`
- Critical deletes: `0`

**Reasons / Signals:**

- 5 resource(s) will be changed (create/update/delete).
- 1 resource(s) will be deleted.
- 1 HIGH risk resource(s) will be changed.
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
