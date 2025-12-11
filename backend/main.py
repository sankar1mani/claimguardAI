"""
ClaimGuard AI - FastAPI Backend Server
Provides REST API endpoints for receipt analysis and claim adjudication
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Fix Windows encoding issue for Unicode characters (like ₹ Rupee symbol)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import our AI agents
from vision_agent import VisionAgent
from policy_engine import PolicyAdjudicator


# Initialize FastAPI app
app = FastAPI(
    title="ClaimGuard AI API",
    description="Automated claim adjudication system for Indian Health Insurance",
    version="1.0.0"
)

# Configure CORS - Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Vite dev server (actual port from vite.config.js)
        "http://localhost:5173",  # Alternative Vite port
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI agents
# Get the absolute path to the data directory
# Support both local development and Docker environments
BASE_DIR = Path(__file__).parent  # Backend directory
DOCKER_DATA_PATH = BASE_DIR / "data" / "policy_rules.json"  # Docker: /app/data/
LOCAL_DATA_PATH = BASE_DIR.parent / "data" / "policy_rules.json"  # Local: ../data/

# Use Docker path if it exists, otherwise use local path
if DOCKER_DATA_PATH.exists():
    POLICY_RULES_PATH = DOCKER_DATA_PATH
else:
    POLICY_RULES_PATH = LOCAL_DATA_PATH

vision_agent = VisionAgent()
policy_adjudicator = PolicyAdjudicator(policy_path=str(POLICY_RULES_PATH))

# Kestra URL - uses Docker internal hostname when running in container
KESTRA_URL = os.getenv("KESTRA_URL", "http://localhost:8080")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "ClaimGuard AI",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check with agent status"""
    return {
        "status": "healthy",
        "vision_agent": {
            "provider": vision_agent.provider,
            "available": True
        },
        "policy_engine": {
            "rules_loaded": len(vision_agent.policy_rules) if hasattr(vision_agent, 'policy_rules') else 0,
            "available": True
        }
    }


@app.post("/api/analyze")
async def analyze_receipt(file: UploadFile = File(...)) -> JSONResponse:
    """
    Analyze a receipt image and adjudicate the claim
    
    Args:
        file: Uploaded receipt image file (JPEG, PNG, etc.)
        
    Returns:
        JSON response with:
        - Vision analysis results (extracted data, fraud detection)
        - Policy adjudication results (approved/rejected items, amounts)
        - Final decision (APPROVED/PARTIAL_APPROVAL/REJECTED)
    """
    temp_image_path = None
    temp_json_path = None
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Expected image, got {file.content_type}"
            )
        
        # Create temporary file for the uploaded image
        suffix = Path(file.filename).suffix if file.filename else '.jpg'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            # Save uploaded file to temporary location
            shutil.copyfileobj(file.file, temp_file)
            temp_image_path = temp_file.name
        
        print(f"\n{'='*80}")
        print("CLAIMGUARD AI - PROCESSING REQUEST")
        print(f"{'='*80}")
        print(f"File: {file.filename}")
        print(f"Size: {os.path.getsize(temp_image_path)} bytes")
        print(f"Type: {file.content_type}")
        print(f"{'='*80}\n")
        
        # STEP 1: Vision Agent - Extract structured data from receipt
        print("STEP 1: Vision Agent Analysis")
        print("-" * 80)
        vision_result = vision_agent.process_receipt(temp_image_path)
        
        if not vision_result:
            raise HTTPException(
                status_code=500,
                detail="Vision agent failed to process the receipt"
            )
        
        print(f"Vision analysis complete")
        print(f"   Merchant: {vision_result.get('merchant_name', 'N/A')}")
        print(f"   Total: Rs.{vision_result.get('total_amount', 0):,.2f}")
        print(f"   Items: {len(vision_result.get('line_items', []))}")
        print(f"   Fraud Risk: {vision_result.get('fraud_detection', {}).get('recommendation', 'N/A')}\n")
        
        # STEP 2: Save vision result to temporary JSON file for policy engine
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_json:
            json.dump(vision_result, temp_json, indent=2)
            temp_json_path = temp_json.name
        
        # STEP 3: Policy Engine - Adjudicate the claim
        print("STEP 2: Policy Engine Adjudication")
        print("-" * 80)
        policy_result = policy_adjudicator.adjudicate_claim(temp_json_path)
        
        if not policy_result:
            raise HTTPException(
                status_code=500,
                detail="Policy engine failed to adjudicate the claim"
            )
        
        print(f"Policy adjudication complete")
        print(f"   Status: {policy_result.get('status', 'N/A')}")
        print(f"   Claimed: Rs.{policy_result.get('total_claimed', 0):,.2f}")
        print(f"   Approved: Rs.{policy_result.get('total_approved', 0):,.2f}")
        print(f"   Deducted: Rs.{policy_result.get('total_deducted', 0):,.2f}")
        print(f"   Excluded Items: {policy_result.get('excluded_items_count', 0)}\n")
        
        # STEP 4: Combine results
        final_result = {
            "success": True,
            "filename": file.filename,
            "vision_analysis": {
                "fraud_detection": vision_result.get('fraud_detection', {}),
                "merchant_name": vision_result.get('merchant_name', ''),
                "merchant_address": vision_result.get('merchant_address', ''),
                "date": vision_result.get('date', ''),
                "total_amount": vision_result.get('total_amount', 0),
                "line_items_count": len(vision_result.get('line_items', []))
            },
            "policy_adjudication": policy_result,
            "final_decision": {
                "status": policy_result.get('status', 'UNKNOWN'),
                "total_claimed": policy_result.get('total_claimed', 0),
                "total_approved": policy_result.get('total_approved', 0),
                "total_deducted": policy_result.get('total_deducted', 0),
                "summary": policy_result.get('summary', '')
            }
        }
        
        print(f"{'='*80}")
        print(f"ANALYSIS COMPLETE - {final_result['final_decision']['status']}")
        print(f"{'='*80}\n")
        
        return JSONResponse(content=final_result)
    
    except HTTPException:
        raise
    
    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    
    finally:
        # Cleanup temporary files
        if temp_image_path and os.path.exists(temp_image_path):
            try:
                os.unlink(temp_image_path)
            except Exception as e:
                print(f"Warning: Failed to delete temporary image: {e}")
        
        if temp_json_path and os.path.exists(temp_json_path):
            try:
                os.unlink(temp_json_path)
            except Exception as e:
                print(f"Warning: Failed to delete temporary JSON: {e}")


@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "ClaimGuard AI API is working!",
        "vision_agent_provider": vision_agent.provider,
        "policy_rules_loaded": True
    }


# Run the server
if __name__ == "__main__":
    print("\n" + "="*80)
    print("CLAIMGUARD AI - STARTING SERVER")
    print("="*80)
    print(f"Server: http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print(f"Vision Provider: {vision_agent.provider}")
    print(f"Policy Rules: Loaded")
    print("="*80 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
