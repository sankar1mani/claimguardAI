"""
ClaimGuard AI - Vision Agent
Extracts structured data from receipt images using AI Vision Models
Supports: OpenAI GPT-4 Vision, Google Gemini, and Together AI
"""

import json
import os
import sys
from pathlib import Path
import base64

# Fix Windows encoding issue for Unicode characters (like ₹ Rupee symbol)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Try importing vision libraries
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class VisionAgent:
    """Vision Agent for receipt analysis and fraud detection"""
    
    def __init__(self):
        """Initialize the Vision Agent with API configuration"""
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.together_api_key = os.environ.get('TOGETHER_API_KEY')
        
        # Configure OpenAI if available (preferred)
        if self.openai_api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.openai_api_key)
            self.provider = "openai"
        # Configure Gemini if available
        elif self.gemini_api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.provider = "gemini"
        elif self.together_api_key and REQUESTS_AVAILABLE:
            self.provider = "together"
        else:
            self.provider = "mock"
            print("[WARNING] No API keys found. Using mock data mode.")
            print("          Set OPENAI_API_KEY, GEMINI_API_KEY, or TOGETHER_API_KEY environment variable to use AI vision.")
    
    def encode_image_base64(self, image_path):
        """Encode image to base64 string"""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_system_prompt(self):
        """Generate the system prompt for receipt analysis"""
        prompt = """You are a Forensic Receipt Analyst AI for an Indian Health Insurance Company.

Your task is to analyze receipt/bill images and extract structured data while detecting fraud.

**VISUAL FRAUD DETECTION:**
Carefully examine the image for:
1. Date tampering - Look for pixel inconsistencies, font mismatches, or digital alterations in date fields
2. Amount manipulation - Check if amounts have been digitally modified or photoshopped
3. Duplicate receipts - Note if the image quality suggests it's a photo of a printout
4. Blurred or obscured sections - Flag if critical information is intentionally unclear
5. Font inconsistencies - Multiple font types suggest tampering
6. Missing mandatory fields - GST number, pharmacy/hospital registration, address

**DATA EXTRACTION:**
Extract the following information in JSON format:

{
  "fraud_detection": {
    "suspicious": boolean,
    "fraud_indicators": [list of detected issues],
    "confidence_score": float (0-1),
    "recommendation": "APPROVE" | "REJECT" | "MANUAL_REVIEW"
  },
  "claim_id": "Auto-generated based on date and merchant",
  "claim_type": "pharmacy_reimbursement" | "diagnostics_reimbursement" | "hospitalization_reimbursement",
  "merchant_name": "extracted name",
  "merchant_address": "extracted address",
  "gst_number": "extracted GST number if present",
  "date": "YYYY-MM-DD format",
  "patient_name": "extracted if present, else UNKNOWN",
  "line_items": [
    {
      "item_number": int,
      "name": "item name",
      "quantity": int,
      "unit_price": float,
      "total_price": float,
      "category": "Medicine" | "Supplement" | "Cosmetic" | "Diagnostic" | "Service" | "Other"
    }
  ],
  "subtotal": float,
  "gst_amount": float,
  "total_amount": float,
  "payment_method": "Cash" | "Card" | "UPI" | "Insurance",
  "notes": "Any additional observations"
}

**IMPORTANT RULES:**
1. Be thorough in fraud detection - flag any inconsistencies
2. Categorize items accurately (Medicine vs Supplement vs Cosmetic is critical)
3. All amounts must be in Indian Rupees (Rs.)
4. Date must be in YYYY-MM-DD format
5. Line items must have complete details
6. If GST number is missing, flag as suspicious
7. Output ONLY valid JSON, no additional text

**INDIAN CONTEXT:**
- Look for Indian pharmacy/hospital names
- GST numbers follow format: 22AAAAA0000A1Z5
- Common medicines: Paracetamol, Dolo-650, Crocin, Azithromycin, etc.
- Watch for excluded items: Protein powders, supplements, cosmetics

Analyze the receipt image thoroughly and provide the structured JSON response."""

        return prompt
    
    def analyze_with_openai(self, image_path):
        """Analyze receipt using OpenAI GPT-4 Vision API"""
        try:
            # Encode image to base64
            image_base64 = self.encode_image_base64(image_path)
            
            # Create the prompt
            prompt = self.get_system_prompt()
            prompt += "\n\nAnalyze this receipt image and provide the structured JSON response:"
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4-vision-preview" for more accuracy
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            # Extract JSON from response
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parse JSON
            result = json.loads(response_text)
            return result
            
        except Exception as e:
            print(f"[ERROR] Error with OpenAI API: {str(e)}")
            return None
    
    def analyze_with_gemini(self, image_path):
        """Analyze receipt using Google Gemini Vision API"""
        try:
            # Read the image
            from PIL import Image
            img = Image.open(image_path)
            
            # Create the prompt
            prompt = self.get_system_prompt()
            prompt += "\n\nAnalyze this receipt image and provide the structured JSON response:"
            
            # Generate content
            response = self.model.generate_content([prompt, img])
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parse JSON
            result = json.loads(response_text)
            return result
            
        except Exception as e:
            print(f"[ERROR] Error with Gemini API: {str(e)}")
            return None
    
    def analyze_with_together(self, image_path):
        """Analyze receipt using Together AI Vision API"""
        try:
            # Encode image to base64
            image_base64 = self.encode_image_base64(image_path)
            
            # Together AI API endpoint (using Llama Vision or similar)
            url = "https://api.together.xyz/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.together_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self.get_system_prompt()
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result_text = response.json()['choices'][0]['message']['content']
            
            # Extract JSON from response
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            elif "```" in result_text:
                json_start = result_text.find("```") + 3
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            print(f"[ERROR] Error with Together AI: {str(e)}")
            return None
    
    def load_mock_data(self):
        """Load mock data from claim_valid.json for testing"""
        mock_path = Path(__file__).parent.parent / "data" / "claim_valid.json"
        try:
            with open(mock_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add fraud detection info to mock data
            data['fraud_detection'] = {
                'suspicious': False,
                'fraud_indicators': [],
                'confidence_score': 1.0,
                'recommendation': 'APPROVE'
            }
            
            print("[INFO] Using mock data from claim_valid.json")
            return data
            
        except Exception as e:
            print(f"[ERROR] Error loading mock data: {str(e)}")
            return None
    
    def process_receipt(self, image_path):
        """
        Main function to process a receipt image
        
        Args:
            image_path: Path to the receipt image file
            
        Returns:
            dict: Structured claim data with fraud detection results
        """
        print(f"\n{'='*80}")
        print("CLAIMGUARD AI - VISION AGENT")
        print(f"{'='*80}")
        print(f"Processing: {image_path}")
        print(f"Provider: {self.provider.upper()}")
        print(f"{'='*80}\n")
        
        # Check if image exists
        if not Path(image_path).exists():
            print(f"[ERROR] Image file not found at {image_path}")
            return None
        
        # Process based on provider
        result = None
        
        if self.provider == "openai":
            print("[ANALYZING] Using OpenAI GPT-4 Vision API...")
            result = self.analyze_with_openai(image_path)
            
        elif self.provider == "gemini":
            print("[ANALYZING] Using Google Gemini Vision API...")
            result = self.analyze_with_gemini(image_path)
            
        elif self.provider == "together":
            print("[ANALYZING] Using Together AI Vision API...")
            result = self.analyze_with_together(image_path)
            
        else:  # mock mode
            print("[ANALYZING] Mock mode - returning sample data...")
            result = self.load_mock_data()
        
        if result:
            print("[OK] Receipt processed successfully!")
            print(f"\nFraud Detection: {result.get('fraud_detection', {}).get('recommendation', 'N/A')}")
            print(f"Merchant: {result.get('merchant_name', 'N/A')}")
            print(f"Total Amount: Rs.{result.get('total_amount', 0):,.2f}")
            print(f"Line Items: {len(result.get('line_items', []))}")
        else:
            print("[ERROR] Failed to process receipt")
        
        print(f"\n{'='*80}\n")
        return result
    
    def save_extracted_data(self, data, output_path):
        """Save extracted data to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[SAVED] Data written to: {output_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Error saving data: {str(e)}")
            return False


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python vision_agent.py <image_path> [output_json_path]")
        print("\nExample:")
        print("  python vision_agent.py receipt.jpg")
        print("  python vision_agent.py receipt.jpg extracted_claim.json")
        print("\nEnvironment Variables:")
        print("  OPENAI_API_KEY     - OpenAI API key (recommended)")
        print("  GEMINI_API_KEY     - Google Gemini API key")
        print("  TOGETHER_API_KEY   - Together AI API key")
        print("\nNote: If no API keys are set, mock data will be used for testing.")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Initialize agent
    agent = VisionAgent()
    
    # Process receipt
    result = agent.process_receipt(image_path)
    
    if result:
        # Print formatted result
        print("\nEXTRACTED DATA:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Save to file if output path provided
        if output_path:
            agent.save_extracted_data(result, output_path)
    else:
        print("[ERROR] Receipt processing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
