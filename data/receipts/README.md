# Test Receipts for ClaimGuard AI

This folder contains sample receipt images for testing the ClaimGuard AI claim adjudication system.

## Available Test Receipts

### Valid Receipts ✅
- **Validreceipt1.jpg** - A valid receipt that should pass policy checks
- **Validreceipt2.png** - Another valid receipt for testing

### Invalid Receipts ❌
- **Invalidreceipt.jpg** - Receipt that violates policy rules
- **Invalidreceipt1.jpg** - Another invalid receipt example
- **Invalidreceipt2.jpg** - Additional invalid receipt test case

### Edge Cases 🔍
- **Edgecase.jpg** - Receipt designed to test edge case scenarios

## How to Use

1. **Upload via Frontend**: Use the ClaimGuard AI web interface to upload these receipts
2. **API Testing**: Send these images to the `/api/adjudicate` endpoint
3. **Kestra Workflow**: Place receipts in the appropriate input folder for automated processing

## Testing Different Scenarios

You can test various claim scenarios using the JSON files in the `../claims/` folder:
- `claim_valid.json` - Standard valid claim
- `claim_clean_authentic.json` - Clean, authentic claim
- `claim_fraud_duplicate.json` - Duplicate claim fraud detection
- `claim_fraud_exclusion.json` - Excluded item fraud
- `claim_fraud_limit.json` - Claim limit violation
- `claim_fraud_missing_gst.json` - Missing GST fraud
- `claim_fraud_tampering.json` - Receipt tampering detection

## Policy Rules

The system validates claims against the policy rules defined in `../policy_rules.json`.

---

**Happy Testing! 🚀**
