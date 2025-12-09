# Risk Configuration

The dynamic approvals bot uses a JSON configuration file to map Terraform resource types to risk levels using regular expression patterns.

## Configuration File Format

The risk configuration is a JSON file with the following structure:

```json
{
  "default_risk_level": "LOW",
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
    }
  ]
}
```

### Configuration Fields

- **`default_risk_level`** (string, required): The default risk level assigned to resources that don't match any pattern. Must be one of: `LOW`, `MEDIUM`, `HIGH`.

- **`resource_risk_patterns`** (array, optional): List of pattern objects that define how resource types are mapped to risk levels.

### Pattern Object Fields

Each pattern object in `resource_risk_patterns` contains:

- **`pattern`** (string, required): A regular expression pattern that matches against Terraform resource types (e.g., `aws_s3_bucket`, `google_compute_instance`). The pattern is matched using Python's `re.match()` function.

- **risk_level** (string, required): The risk level to assign when this pattern matches. Must be one of: `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.

- **reason** (string, optional): A human-readable explanation for why this resource type has this risk level. Used in risk assessment output.

## Pattern Matching Behavior

1. Patterns are evaluated in order
2. All matching patterns are considered
3. The **highest** risk level from all matches is selected
4. If no patterns match, the `default_risk_level` is used

## Risk Levels

The tool supports the following risk levels (in order of severity):

- **LOW**: Minimal risk changes
- **MEDIUM**: Moderate risk requiring review
- **HIGH**: High risk requiring manual approval
- **CRITICAL**: Critical risk (treated as HIGH in final assessment)

Note: While `CRITICAL` can be used in configuration patterns, the final risk assessment only outputs `LOW`, `MEDIUM`, or `HIGH`. `CRITICAL` resources are counted separately and contribute to raising the overall risk level.

## Example Configuration

Here's a comprehensive example covering multiple cloud providers:

```json
{
  "default_risk_level": "LOW",
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
    },
    {
      "pattern": "^google_compute_firewall$",
      "risk_level": "HIGH",
      "reason": "GCP network access control."
    },
    {
      "pattern": "^azurerm_network_security_group$",
      "risk_level": "HIGH",
      "reason": "Azure network access control."
    },
    {
      "pattern": "^aws_vpc$",
      "risk_level": "MEDIUM",
      "reason": "VPC/Network changes impact connectivity."
    },
    {
      "pattern": ".*null_resource.*",
      "risk_level": "LOW",
      "reason": "Generally benign resource."
    }
  ]
}
```

## Pattern Examples

### Match All IAM Resources

```json
{
  "pattern": "^aws_iam_.*",
  "risk_level": "CRITICAL",
  "reason": "All IAM resources are critical"
}
```

### Match Specific Resource Type

```json
{
  "pattern": "^aws_s3_bucket$",
  "risk_level": "HIGH",
  "reason": "S3 buckets store data"
}
```

### Match Multiple Providers

```json
{
  "pattern": ".*_firewall$",
  "risk_level": "HIGH",
  "reason": "Firewall rules across all providers"
}
```

### Match Resources with Specific Prefix

```json
{
  "pattern": "^aws_rds_.*",
  "risk_level": "HIGH",
  "reason": "RDS database resources"
}
```

## Using Custom Configuration

### Command-Line

```bash
tguard plan.json --risk-config-path ./custom-risk-config.json
```

### Environment Variable

```bash
export RISK_CONFIG_PATH=./custom-risk-config.json
tguard plan.json
```

### Default Location

If no configuration path is provided, the tool uses the built-in configuration at:
`src/terraguard/risk/risk_config.json`

## Best Practices

1. **Order patterns from most specific to least specific**: More specific patterns should come first to avoid unintended matches.

2. **Use anchors appropriately**:
   - `^pattern$` - Exact match
   - `^pattern.*` - Starts with pattern
   - `.*pattern$` - Ends with pattern
   - `.*pattern.*` - Contains pattern

3. **Document reasons**: Always include a clear `reason` field to help reviewers understand why a resource type has a particular risk level.

4. **Test patterns**: Use a regex tester to verify your patterns match the intended resource types.

5. **Start conservative**: Begin with a `LOW` default and explicitly mark high-risk resources. You can always adjust later.
