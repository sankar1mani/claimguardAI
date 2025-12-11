# Kestra Workflow Setup Guide

## 📋 Overview

This directory contains the **Kestra orchestration workflow** for ClaimGuard AI's automated insurance claim adjudication pipeline.

**Flow ID**: `claim-adjudication-flow`  
**Namespace**: `claimguard.insurance`

---

## 🚀 Quick Start with Kestra

### Option 1: Run with Kestra Server (Recommended for Demo)

1. **Install Kestra** (if not already installed)
   ```bash
   # Using Docker (recommended)
   docker run --pull=always --rm -it -p 8080:8080 kestra/kestra:latest server local
   
   # OR using Java
   wget https://github.com/kestra-io/kestra/releases/latest/download/kestra-standalone.jar
   java -jar kestra-standalone.jar server local
   ```

2. **Access Kestra UI**
   - Open browser: http://localhost:8080
   - You should see the Kestra dashboard

3. **Import the Workflow**
   - Click on **"Flows"** in the left sidebar
   - Click **"Create"** button
   - Copy the contents of `insurance_flow.yaml`
   - Paste into the editor
   - Click **"Save"**

4. **Execute a Claim**
   - Go to the flow: `claimguard.insurance` > `claim-adjudication-flow`
   - Click **"Execute"** button
   - Set inputs:
     - `receipt_file`: Upload a receipt image (or use test JSON files)
     - `api_provider`: Select **"mock"** (for testing without API keys)
     - `sum_insured`: 500000 (or your test amount)
   - Click **"Execute"**
   - Watch the pipeline run in real-time!

5. **View Results**
   - Click on the execution in the **"Executions"** tab
   - View logs for each task (Vision Agent, Policy Engine, Final Decision)
   - Download output files:
     - `extracted_claim.json`
     - `adjudication_result.json`
     - `final_decision.json`

---

## 🎯 Workflow Architecture

```
┌─────────────────────────────────────────────────────┐
│              INPUT: Receipt File Upload              │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  TASK 1: Vision Agent                               │
│  ├─ Analyzes receipt image                          │
│  ├─ Detects fraud (tampering, duplicates)           │
│  └─ Extracts structured data                        │
│  Output: extracted_claim.json                       │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  TASK 2: Policy Engine                              │
│  ├─ Validates exclusions (supplements, cosmetics)   │
│  ├─ Applies room rent capping (1% rule)             │
│  └─ Calculates approved amount                      │
│  Output: adjudication_result.json                   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  TASK 3: Final Decision                             │
│  ├─ Combines Vision + Policy results                │
│  ├─ Determines: APPROVED / PARTIAL / REJECTED       │
│  └─ Generates detailed report                       │
│  Output: final_decision.json                        │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  TASK 4: Log Summary                                │
│  └─ Displays results in Kestra UI                   │
└─────────────────────────────────────────────────────┘
```

---

## 🧪 Testing the Workflow

### Test with Sample Claims

You can test the workflow with the pre-built test claims:

1. **Valid Claim** (Should Approve)
   ```
   File: ../data/claim_valid.json
   Expected: PARTIAL_APPROVAL - ₹495 approved
   ```

2. **Exclusion Fraud** (Should Partially Reject)
   ```
   File: ../data/claim_fraud_exclusion.json
   Expected: PARTIAL_APPROVAL - ₹570 approved (Whey Protein & Moisturizer rejected)
   ```

3. **Room Rent Limit** (Should Apply Deduction)
   ```
   File: ../data/claim_fraud_limit.json
   Expected: PARTIAL_APPROVAL - ₹78,437.50 approved (62.5% ratio applied)
   ```

### Using Mock Mode

The workflow defaults to **mock mode** which:
- ✅ Doesn't require API keys
- ✅ Returns sample data for testing
- ✅ Perfect for hackathon demos

To enable real AI vision:
1. Set environment variable: `GEMINI_API_KEY` or `TOGETHER_API_KEY`
2. Change `api_provider` input to `gemini` or `together` when executing

---

## 📊 Inputs & Outputs

### Inputs

| Input | Type | Description | Default |
|-------|------|-------------|---------|
| `receipt_file` | FILE | Receipt image (JPG/PNG) or JSON for testing | Required |
| `api_provider` | SELECT | Vision provider: `mock`, `gemini`, `together` | `mock` |
| `sum_insured` | FLOAT | Patient's insurance sum (INR) | 500000 |

### Outputs

Each task produces output files accessible in Kestra UI:

1. **extracted_claim.json**
   - Vision Agent output
   - Contains: merchant info, line items, fraud detection

2. **adjudication_result.json**
   - Policy Engine output
   - Contains: approval status, deductions, line-item decisions

3. **final_decision.json**
   - Final decision combining both agents
   - Contains: status, financial summary, reasoning

---

## 🔧 Configuration

### Project Path Configuration

The workflow uses absolute paths configured in the `variables` section:

```yaml
variables:
  project_root: "c:/Users/ACER/OneDrive/Documents/Manee/ClaimguardAI"
  backend_path: "{{vars.project_root}}/backend"
  data_path: "{{vars.project_root}}/data"
```

**Important**: Update `project_root` if you clone this project to a different location!

### Environment Variables

Optional environment variables for AI vision:

```bash
# For Google Gemini Vision
set GEMINI_API_KEY=your_gemini_api_key_here

# For Together AI Vision
set TOGETHER_API_KEY=your_together_api_key_here
```

---

## 🎬 Demo Script for Hackathon

### Scenario 1: Valid Pharmacy Claim ✅

**Story**: Patient Rajesh had a respiratory infection, got prescribed medicines

1. Upload `claim_valid.json` as receipt
2. Set `api_provider` = `mock`
3. Execute workflow
4. **Expected Result**: 
   - Status: PARTIAL_APPROVAL
   - Approved: ₹495.00 (medicines only, GST excluded)
   - All items are legitimate medicines

### Scenario 2: Fraud Detection - Hidden Supplements 🚫

**Story**: Patient Amit tried to claim Whey Protein and Moisturizer as medicines

1. Upload `claim_fraud_exclusion.json`
2. Execute workflow
3. **Expected Result**:
   - Status: PARTIAL_APPROVAL
   - Rejected: ₹2,949 (Whey Protein + Moisturizer)
   - Approved: ₹570 (legitimate medicines only)
   - System catches the fraud!

### Scenario 3: Room Rent Capping - Complex Math 📐

**Story**: Patient Priya stayed in deluxe room (₹8,000/day) exceeding policy limit

1. Upload `claim_fraud_limit.json`
2. Set `sum_insured` = 500000
3. Execute workflow
4. **Expected Result**:
   - Status: PARTIAL_APPROVAL
   - Proportionate ratio: 62.5% (5000/8000)
   - Approved: ₹78,437.50 instead of ₹1,31,775
   - Complex calculation done automatically!

---

## 🛠️ Troubleshooting

### Common Issues

1. **"Backend scripts not found"**
   - Check `project_root` path in `insurance_flow.yaml`
   - Ensure backend folder exists with `.py` files

2. **"Policy rules file not found"**
   - Verify `data/policy_rules.json` exists
   - Check path configuration in workflow

3. **"Python dependencies missing"**
   - Run: `cd backend && pip install -r requirements.txt`

4. **"Kestra can't execute Python scripts"**
   - Ensure Python 3.9+ is installed
   - Check Docker container has Python (if using Docker)

### Debug Mode

To see detailed logs:
1. Check each task's **"Logs"** tab in Kestra UI
2. Look for print statements with emoji indicators
3. Download output JSON files for inspection

---

## 🚀 Production Deployment

For production use (beyond hackathon):

1. **Use Docker for Kestra**
   ```bash
   docker-compose up -d
   ```

2. **Add Database Backend**
   - Configure PostgreSQL for Kestra
   - Store claim history

3. **Enable Monitoring**
   - Set up alerts for failed executions
   - Track processing times

4. **Scale Workers**
   - Add more Kestra workers for parallel processing
   - Queue management for high volume

5. **Secure API Keys**
   - Use Kestra secrets management
   - Never hardcode keys in YAML

---

## 📚 Additional Resources

- **Kestra Documentation**: https://kestra.io/docs
- **Python Script Task**: https://kestra.io/plugins/plugin-script-python
- **ClaimGuard AI Backend**: See `../backend/README.md`

---

## 🤝 Support

For issues or questions:
- Check the main `README.md` in project root
- Review backend test results: `python backend/test_full_pipeline.py`
- Kestra community: https://kestra.io/slack

---

**Built with ❤️ for Assemble Hack 2025**
