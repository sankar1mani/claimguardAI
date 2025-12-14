# Test Claims for ClaimGuard AI

This folder contains sample claim JSON files for testing the ClaimGuard AI fraud detection and policy validation system.

## Available Test Claims

### Valid Claims ✅
- **claim_valid.json** - Standard valid claim that passes all checks
- **claim_clean_authentic.json** - Clean, authentic claim with no fraud indicators

### Fraud Detection Test Cases 🚨

#### Duplicate Claims
- **claim_fraud_duplicate.json** - Tests duplicate claim detection

#### Policy Violations
- **claim_fraud_exclusion.json** - Contains excluded items per policy rules
- **claim_fraud_limit.json** - Exceeds claim limits defined in policy

#### Receipt Issues
- **claim_fraud_missing_gst.json** - Missing GST information on receipt
- **claim_fraud_tampering.json** - Receipt tampering detection test

## JSON Structure

Each claim JSON file contains:
- `claimId` - Unique claim identifier
- `policyId` - Associated policy ID
- `claimDate` - Date of claim submission
- `items` - Array of claimed items with details
- `receiptMetadata` - Receipt information and validation data
- `fraudIndicators` - (Optional) Fraud detection markers

## How to Use

1. **API Testing**: POST these JSON files to `/api/adjudicate` endpoint
2. **Frontend Upload**: Use the JSON upload feature in the web interface
3. **Automated Testing**: Reference these files in your test suites

## Policy Validation

All claims are validated against `../policy_rules.json` which defines:
- Coverage limits
- Excluded items
- Required documentation
- Claim processing rules

---

**Test thoroughly! 🔍**
