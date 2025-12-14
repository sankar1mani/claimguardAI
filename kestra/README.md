# Kestra Workflow Guide 🔄

> **Orchestration engine for ClaimGuard AI's automated claim adjudication pipeline**

---

## 📋 Overview

This directory contains the Kestra workflow that orchestrates the entire claim processing pipeline.

- **Flow ID**: `claim-adjudication-flow`
- **Namespace**: `claimguard.insurance`
- **Stages**: 6 automated stages
- **Runtime**: ~10-30 seconds per claim

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

The easiest way to run Kestra with the full stack:

```bash
cd docker
docker compose up
```

Access Kestra UI: **http://localhost:8080**

The workflow is automatically loaded from the `kestra/` directory.

### Option 2: Standalone Kestra

If you want to run only Kestra:

```bash
docker run -p 8080:8080 \
  -v $(pwd)/kestra:/app/flows \
  kestra/kestra:latest server local --flow-path=/app/flows
```

---

## 🎯 Workflow Stages

The workflow processes claims through 6 automated stages:

```
1. File Validation
   ↓
2. AI Vision Agent (OpenAI GPT-4o)
   ├─ Extract receipt data
   ├─ Detect fraud
   └─ Medical necessity check
   ↓
3. Fraud Evaluation
   └─ Analyze fraud risk level
   ↓
4. Policy Engine
   ├─ Apply exclusion rules
   ├─ Calculate room rent capping
   └─ Determine approved amount
   ↓
5. Generate Report
   └─ Create detailed claim summary
   ↓
6. Send Notification (Mock Email)
   └─ Display formatted decision
```

---

## 🎮 How to Execute a Claim

### Via Kestra UI

1. Open http://localhost:8080
2. Navigate to **Flows** → `claimguard.insurance` → `claim-adjudication-flow`
3. Click **Execute** button
4. Fill in the inputs:
   - **receipt_file**: Upload a receipt image or JSON file
   - **patient_name**: Patient name (default: "Policy Holder")
   - **sum_insured**: Insurance coverage amount (default: ₹500,000)
5. Click **Execute**
6. Watch the pipeline run in real-time!

### Via API

You can also trigger the workflow via the Kestra API:

```bash
curl -X POST http://localhost:8080/api/v1/executions/claimguard.insurance/claim-adjudication-flow \
  -H "Content-Type: multipart/form-data" \
  -F "receipt_file=@path/to/receipt.jpg" \
  -F "sum_insured=500000"
```

---

## 📊 Viewing Results

After execution completes:

1. Go to **Executions** tab in Kestra UI
2. Click on your execution
3. View logs for each stage
4. Download output files:
   - `vision_result.json` - AI vision analysis
   - `fraud_decision.txt` - Fraud risk assessment
   - `final_decision.json` - Final adjudication decision

---

## 🧪 Test Scenarios

Use the test files in the `data/` folder to test different scenarios:

### ✅ Valid Claim
```bash
# Upload: data/claims/claim_valid.json
# Expected: PARTIAL_APPROVAL
# Approved: ₹495 (all valid medicines)
```

### ⚠️ Exclusion Fraud
```bash
# Upload: data/claims/claim_fraud_exclusion.json
# Expected: PARTIAL_APPROVAL
# Approved: ₹570 (medicines only)
# Rejected: ₹2,949 (Whey Protein + Moisturizer)
```

### ✂️ Room Rent Capping
```bash
# Upload: data/claims/claim_fraud_limit.json
# Expected: PARTIAL_APPROVAL
# Approved: ₹78,437.50 (62.5% ratio applied)
# Deducted: ₹53,337.50 (due to room rent limit)
```

---

## 🔧 Workflow Configuration

### Inputs

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `receipt_file` | FILE | Receipt image (JPG/PNG) or JSON | Required |
| `patient_name` | STRING | Patient name | "Policy Holder" |
| `sum_insured` | FLOAT | Insurance sum (INR) | 500,000 |

### Outputs

| File | Description |
|------|-------------|
| `vision_result.json` | AI vision analysis with extracted data |
| `fraud_decision.txt` | Fraud risk level (APPROVE/REJECT) |
| `final_decision.json` | Final decision with amounts |

---

## 🛠️ Customization

### Modifying the Workflow

Edit `insurance_flow.yaml` to customize:

1. **Add new stages**: Add tasks under the `tasks:` section
2. **Change AI provider**: Modify the backend API endpoint
3. **Adjust policy rules**: Edit `data/policy_rules.json`
4. **Add notifications**: Configure real email integration

After making changes:
```bash
# Restart Kestra to reload the workflow
docker compose restart kestra
```

### Environment Variables

The workflow can access these environment variables:

```yaml
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}
```

---

## 📈 Monitoring

### Real-time Execution

- View live logs in the Kestra UI
- Track execution progress through each stage
- See task duration and status

### Execution History

- All executions are stored in Kestra's database
- View past executions in the **Executions** tab
- Filter by status, date, or flow

---

## 🐛 Troubleshooting

### Workflow not loading?

Check Kestra logs:
```bash
docker compose logs kestra
```

Common issues:
- YAML syntax error in `insurance_flow.yaml`
- Backend service not running
- Missing environment variables

### Execution failing?

1. Check backend is running: http://localhost:8000/docs
2. Verify OpenAI API key is set
3. Check logs for each failed task
4. Ensure test files are in `data/` folder

---

## 📚 Learn More

- [Kestra Documentation](https://kestra.io/docs)
- [Kestra Flow Syntax](https://kestra.io/docs/developer-guide/flows)
- [Main Project README](../README.md)

---

**Built with ❤️ for Assemble Hack 2025**
