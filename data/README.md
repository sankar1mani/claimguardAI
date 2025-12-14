# ClaimGuard AI - Test Data

This directory contains all test data and policy rules for the ClaimGuard AI system.

## Directory Structure

```
data/
├── policy_rules.json          # Policy rules and validation criteria
├── receipts/                  # Sample receipt images for testing
│   ├── README.md
│   ├── Validreceipt1.jpg
│   ├── Validreceipt2.png
│   ├── Invalidreceipt.jpg
│   ├── Invalidreceipt1.jpg
│   ├── Invalidreceipt2.jpg
│   └── Edgecase.jpg
└── claims/                    # Sample claim JSON files
    ├── README.md
    ├── claim_valid.json
    ├── claim_clean_authentic.json
    ├── claim_fraud_duplicate.json
    ├── claim_fraud_exclusion.json
    ├── claim_fraud_limit.json
    ├── claim_fraud_missing_gst.json
    └── claim_fraud_tampering.json
```

## Quick Start

### For Hackathon Participants 🏆

1. **Test with Receipts**: Navigate to `receipts/` folder and upload any image to the ClaimGuard AI interface
2. **Test with JSON Claims**: Use the JSON files in `claims/` folder to test different fraud scenarios
3. **Review Policy Rules**: Check `policy_rules.json` to understand validation criteria

### Testing Scenarios

- **Valid Claims**: Use `claim_valid.json` or `claim_clean_authentic.json`
- **Fraud Detection**: Test with various `claim_fraud_*.json` files
- **Receipt Validation**: Upload receipts from the `receipts/` folder

## Policy Rules

The `policy_rules.json` file defines:
- Coverage limits and thresholds
- Excluded items and categories
- Required documentation standards
- Fraud detection parameters

## Need Help?

Check the README files in each subfolder for detailed information:
- `receipts/README.md` - Receipt testing guide
- `claims/README.md` - Claim JSON structure and usage

---

**Happy Testing! 🚀**
