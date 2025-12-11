"""
ClaimGuard AI - Medical Necessity Judge
Evaluates clinical necessity of claimed items based on diagnosis.
"""

import os
import json
import sys

# Try importing OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class MedicalJudge:
    """Evaluates medical necessity of claims using clinical logic"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        
        if self.openai_api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.openai_api_key)
            self.mode = "active"
        else:
            self.mode = "mock"
            print("[WARN] Medical Judge running in MOCK mode (No OpenAI Key)")

    def evaluate_necessity(self, diagnosis, line_items):
        """
        Check if line items are medically logical for the diagnosis.
        
        Args:
            diagnosis (str): Extracted diagnosis (e.g., "Viral Fever")
            line_items (list): List of item dictionaries
            
        Returns:
            dict: Mapping of item_name -> {status: PASS/FLAG, reason: str}
        """
        if self.mode == "mock" or diagnosis == "Unknown":
            return self._mock_evaluation(line_items)

        try:
            # Prepare item list for LLM (names only to save tokens)
            item_list = [item.get('name', 'Unknown Item') for item in line_items]
            
            system_prompt = f"""You are a Medical Claim Adjudicator.
Diagnosis: {diagnosis}
Items: {json.dumps(item_list)}

Task: Return a JSON object mapping each item name to a status object.
Structure:
{{
  "item_name": {{
    "status": "PASS" or "FLAG",
    "reason": "Short explanation"
  }}
}}

Rules:
1. Flag items clearly unrelated to diagnosis (e.g. 'MRI' for 'Fever', 'Dentist' for 'Fracture').
2. Flag 'Cosmetics' or 'Non-medical' items as FLAG.
3. Be lenient if diagnosis is vague.
4. Return ONLY valid JSON."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"[ERROR] Medical Judge failed: {e}")
            return self._mock_evaluation(line_items)

    def _mock_evaluation(self, line_items):
        """Fallback for mock mode or errors - Passes everything"""
        return {
            item.get('name', 'Unknown'): {"status": "PASS", "reason": "Mock Approval"}
            for item in line_items
        }
