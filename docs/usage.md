# Usage Guide

## Basic Usage

The dynamic approvals bot analyzes Terraform plan JSON files and assesses risk levels.

### Generate Terraform Plan JSON

First, generate a Terraform plan and convert it to JSON:

```bash
terraform plan -out=plan.out
terraform show -json plan.out > plan.json
```

### Run Risk Assessment

```bash
tguard plan.json
```

The tool will:

- Analyze the plan and assess risk
- Print a markdown summary to stdout
- Optionally post a comment to GitHub (if running in GitHub Actions)
- Exit with code 1 if risk exceeds threshold

## Command-Line Options

### Required Arguments

- `plan_json`: Path to Terraform plan JSON file (from `terraform show -json plan.out > plan.json`)

### Optional Arguments

- `--risk-config-path PATH`: Path to the risk configuration JSON file. Overrides `RISK_CONFIG_PATH` environment variable. If not provided, defaults to the built-in configuration.

- `--fail-on {LOW,MEDIUM,HIGH}`: Fail (exit code 1) if risk level is at or above this threshold. Defaults to `FAIL_ON_RISK_LEVEL` environment variable or `HIGH` if not set.

- `--no-github-comment`: Do not attempt to post a comment to GitHub, even if running in GitHub Actions.

## Environment Variables

- `RISK_CONFIG_PATH`: Path to custom risk configuration JSON file
- `FAIL_ON_RISK_LEVEL`: Risk level threshold for failing the build (`LOW`, `MEDIUM`, or `HIGH`)
- `GITHUB_TOKEN`: GitHub personal access token (required for GitHub Actions integration)
- `GITHUB_EVENT_PATH`: Path to GitHub Actions event JSON (automatically set in GitHub Actions)

## Exit Codes

- `0`: Risk level is below the fail-on threshold
- `1`: Risk level meets or exceeds the fail-on threshold (requires manual review)

## Examples

### Basic Assessment

```bash
tguard plan.json
```

### Custom Risk Configuration

```bash
tguard plan.json --risk-config-path ./custom-risk-config.json
```

### Fail on Medium Risk

```bash
tguard plan.json --fail-on MEDIUM
```

### Disable GitHub Comments

```bash
tguard plan.json --no-github-comment
```

### Using Environment Variables

```bash
export FAIL_ON_RISK_LEVEL=MEDIUM
export RISK_CONFIG_PATH=./my-config.json
tguard plan.json
```

## GitHub Actions Integration

The bot automatically detects when running in GitHub Actions and will post comments to pull requests if:

1. The workflow is triggered by a `pull_request` or `pull_request_target` event
2. `GITHUB_TOKEN` environment variable is set (usually automatic in GitHub Actions)
3. `--no-github-comment` flag is not used

### Example GitHub Actions Workflow

```yaml
name: Terraform Risk Assessment

on:
  pull_request:
    paths:
      - "terraform/**"

jobs:
  assess-risk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0

      - name: Terraform Plan
        working-directory: ./terraform
        run: |
          terraform init
          terraform plan -out=plan.out
          terraform show -json plan.out > ../plan.json

      - name: Install Dynamic Approvals Bot
        run: pip install -r requirements.txt

      - name: Assess Risk
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: tguard plan.json --fail-on MEDIUM
```
