# Backend API 🔧

> **FastAPI backend for ClaimGuard AI - AI vision and policy engine**

---

## 📋 Overview

The backend provides REST APIs for:
- Receipt analysis using OpenAI GPT-4o Vision
- Policy rule validation
- Fraud detection
- Claim adjudication

**Tech Stack**: Python 3.10, FastAPI, PostgreSQL, OpenAI SDK

---

## 🚀 Quick Start

### With Docker (Recommended)

```bash
cd docker
docker compose up backend
```

API will be available at: **http://localhost:8000**

### Without Docker

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📡 API Endpoints

### 1. Analyze Receipt

**POST** `/api/analyze`

Analyzes a receipt image and returns structured data with policy validation.

**Request**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@receipt.jpg" \
  -F "sum_insured=500000"
```

**Response**:
```json
{
  "vision_analysis": {
    "merchant_name": "Apollo Pharmacy",
    "date": "2024-01-15",
    "line_items": [...],
    "fraud_detection": {...}
  },
  "policy_adjudication": {
    "status": "APPROVED",
    "total_claimed": 1500.00,
    "total_approved": 1500.00,
    "items": [...]
  }
}
```

### 2. Health Check

**GET** `/health`

Returns API health status.

### 3. API Documentation

**GET** `/docs`

Interactive Swagger UI documentation.

---

## 🏗️ Project Structure

```
backend/
├── main.py                 # FastAPI app & routes
├── vision_agent.py         # OpenAI integration
├── policy_engine.py        # Policy rules engine
├── database.py             # PostgreSQL connection
├── models.py               # Database models
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set these variables:

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Database
DATABASE_URL=postgresql://claimguard:claimguard_secret@localhost:5432/claimguard

# Optional
KESTRA_URL=http://localhost:8080
```

### Policy Rules

Edit `../data/policy_rules.json` to customize:
- Excluded items list
- Room rent percentage
- Medical necessity criteria

---

## 🧪 Testing

### Manual Testing

Use the Swagger UI at http://localhost:8000/docs to test endpoints interactively.

### With Test Data

```bash
# Test with valid claim
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@../data/claims/claim_valid.json" \
  -F "sum_insured=500000"

# Test with fraud claim
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@../data/claims/claim_fraud_exclusion.json" \
  -F "sum_insured=500000"
```

---

## 📦 Dependencies

Key Python packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai` - OpenAI API client
- `sqlalchemy` - Database ORM
- `psycopg2-binary` - PostgreSQL driver
- `python-multipart` - File upload support

Install all:
```bash
pip install -r requirements.txt
```

---

## 🔍 How It Works

### Vision Agent (`vision_agent.py`)

1. Receives receipt image
2. Sends to OpenAI GPT-4o Vision API
3. Extracts structured data:
   - Merchant name
   - Date
   - Line items (name, quantity, price)
   - GST information
4. Performs fraud detection:
   - Checks for tampering
   - Validates mandatory fields
   - Assesses medical necessity

### Policy Engine (`policy_engine.py`)

1. Receives extracted data
2. Applies policy rules:
   - **Exclusions**: Rejects non-payable items
   - **Room Rent Capping**: Calculates proportionate deduction
   - **Medical Necessity**: Validates treatments
3. Calculates final amounts:
   - Total claimed
   - Total approved
   - Total deducted

---

## 🐛 Troubleshooting

### OpenAI API Errors

```
Error: Invalid API key
```
**Solution**: Check your `OPENAI_API_KEY` in `.env`

### Database Connection Errors

```
Error: Could not connect to database
```
**Solution**: Ensure PostgreSQL is running:
```bash
docker compose up db
```

### Import Errors

```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📚 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Main Project README](../README.md)

---

**Built with ❤️ for Assemble Hack 2025**
