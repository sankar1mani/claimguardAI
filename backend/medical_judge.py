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
            
            system_prompt = f"""You are a Medical Claims Reviewer evaluating post-hospitalization pharmacy reimbursement claims.

**CONTEXT**: 
- Patient Diagnosis: {diagnosis}
- Claimed Medications: {json.dumps(item_list)}

**YOUR TASK**: 
For EACH medication, evaluate if it is clinically appropriate for this specific diagnosis. Consider:
1. Is this medication commonly prescribed for {diagnosis}?
2. Are there any contraindications (medical reasons this medication could harm a patient with {diagnosis})?
3. Is this medication medically necessary or is it unrelated to the diagnosis?

**CRITICAL INSTRUCTIONS**:
- **DEFAULT TO SAFE**: If a medication is commonly used and safe for the diagnosis, mark it as PASS
- **BE DIAGNOSIS-SPECIFIC**: Only flag contraindications that apply to THIS diagnosis
- **PRIORITIZE PATIENT SAFETY**: If a medication could cause serious harm for this diagnosis, mark it CRITICAL

**OUTPUT FORMAT** (JSON only, no other text):
{{
  "medication_name": {{
    "status": "PASS" | "FLAG" | "CONTRAINDICATED",
    "severity": "INFO" | "WARNING" | "CRITICAL",
    "reason": "Brief clinical explanation"
  }}
}}

**STATUS DEFINITIONS**:
- **PASS**: Medication is safe and appropriate for {diagnosis}
- **FLAG**: Medication may be unnecessary or questionable for {diagnosis} (but not harmful)
- **CONTRAINDICATED**: Medication is medically contraindicated and could harm patient with {diagnosis}

**SEVERITY DEFINITIONS**:
- **INFO**: Safe and appropriate medication
- **WARNING**: Questionable necessity but not harmful
- **CRITICAL**: Contraindicated - could cause serious harm to patient

**EXAMPLES** (for reference only):

Example 1 - Viral Fever:
- Paracetamol → PASS (INFO) - "Commonly used antipyretic for fever management"
- Antibiotics → FLAG (WARNING) - "Not indicated for viral infections"
- NSAIDs → PASS (INFO) - "Appropriate for fever and pain relief"

Example 2 - Gastric Ulcer:
- Paracetamol → CONTRAINDICATED (CRITICAL) - "Can worsen gastric ulcers, risk of bleeding"
- Antacids → PASS (INFO) - "Appropriate for ulcer management"
- NSAIDs → CONTRAINDICATED (CRITICAL) - "Contraindicated in peptic ulcer disease"

Example 3 - Diabetes:
- Insulin → PASS (INFO) - "Essential for diabetes management"
- Steroids → CONTRAINDICATED (CRITICAL) - "Can cause hyperglycemia in diabetic patients"
- Paracetamol → PASS (INFO) - "Safe for diabetic patients"

**NOW EVALUATE**: For diagnosis "{diagnosis}", evaluate each medication in {json.dumps(item_list)}

Return ONLY valid JSON with no additional text."""

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
            item.get('name', 'Unknown'): {
                "status": "PASS", 
                "severity": "INFO",
                "reason": "Mock Approval"
            }
            for item in line_items
        }
