# Kestra Workflow Setup Guide

## 📋 Overview

This directory contains the **Kestra orchestration workflow** for ClaimGuard AI's automated insurance claim adjudication pipeline.

**Flow ID**: `claim-adjudication-flow`  
**Namespace**: `claimguard.insurance`

---

## 🚀 Quick Start with Kestra

### Option 1: Run with Docker Compose (Recommended)

The easiest way to run the full stack (Frontend, Backend, and Kestra) is using Docker Compose:

```bash
cd docker
docker compose up
```

Access Kestra UI:
- Open browser: http://localhost:8080
- You should see the Kestra dashboard

### Option 2: Run with Kestra Server (Standalone)

1. **Install Kestra** (if not already installed)
   ```bash
   # Using Docker (recommended)
   docker run --pull=always --rm -it -p 8080:8080 kestra/kestra:latest server local
   ```

2. **Access Kestra UI**
   - Open browser: http://localhost:8080

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
     - `sum_insured`: 500000 (or your test amount)
   - Click **"Execute"**
   - Watch the pipeline run in real-time!

5. **View Results**
   - Click on the execution in the **"Executions"** tab
   - View logs for each task (Vision Agent, Policy Engine, Final Decision)
   - Download output files:
     - `vision_result.json`
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
│  TASK 1: Vision Agent API Call                      │
│  ├─ Calls Backend API Endpoint                      │
│  ├─ Detects fraud (tampering, duplicates)           │
│  └─ Extracts structured data (OpenAI GPT-4o)        │
│  Output: vision_result.json                         │
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
│  TASK 4: Email Notification (Mock)                  │
│  └─ Displays formatted email in Kestra logs         │
└─────────────────────────────────────────────────────┘
```

---

## 🧪 Testing the Workflow

### Test with Sample Claims

You can test the workflow with the pre-built test claims found in the `data/` folder.

1. **Valid Claim** (Should Approve)
   - File: `data/claim_valid.json` (as mock receipt)
   - Expected: **PARTIAL_APPROVAL** - ₹495 approved

2. **Exclusion Fraud** (Should Partially Reject)
   - File: `data/claim_fraud_exclusion.json` (as mock receipt)
   - Expected: **PARTIAL_APPROVAL** - ₹570 approved (Whey Protein & Moisturizer rejected)

3. **Room Rent Limit** (Should Apply Deduction)
   - File: `data/claim_fraud_limit.json` (as mock receipt)
   - Expected: **PARTIAL_APPROVAL** - ₹78,437.50 approved (62.5% ratio applied)

### Using Mock Mode

The workflow defaults to **mock mode** if no API key is set, which:
- ✅ Doesn't require API keys
- ✅ Returns sample data for testing
- ✅ Perfect for hackathon demos

To enable real AI vision:
1. Set environment variable: `OPENAI_API_KEY` in the backend service (in `docker/docker-compose.yml` or `.env` file).

---

## 📊 Inputs & Outputs

### Inputs

| Input | Type | Description | Default |
|-------|------|-------------|---------|
| `receipt_file` | FILE | Receipt image (JPG/PNG) or JSON for testing | Required |
| `patient_name` | STRING | Patient Name | "Policy Holder" |
| `sum_insured` | FLOAT | Patient's insurance sum (INR) | 500000 |

### Outputs

Each task produces output files accessible in Kestra UI:

1. **vision_result.json**
   - Vision Agent output
   - Contains: merchant info, line items, fraud detection

2. **final_decision.json**
   - Final decision combining both agents
   - Contains: status, financial summary, reasoning

---

## 🔧 Configuration

### Environment Variables

For AI vision capabilities:

```bash
# OpenAI GPT-4 Vision
OPENAI_API_KEY=sk-your-openai-api-key-here
```

---

## 🎬 Demo Script for Hackathon

### Scenario 1: Valid Pharmacy Claim ✅

**Story**: Patient Rajesh had a respiratory infection, got prescribed medicines

1. Upload `claim_valid.json` as receipt
2. Use default Sum Insured
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

**Built with ❤️ for Assemble Hack 2025**
