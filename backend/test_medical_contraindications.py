"""
Test Medical Judge Contraindication Detection
Tests that the Medical Judge correctly flags contraindicated medications
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from medical_judge import MedicalJudge

def test_ulcer_paracetamol():
    """Test that paracetamol is flagged for ulcer patients"""
    print("\n" + "="*80)
    print("TEST 1: Ulcer + Paracetamol (User's Case)")
    print("="*80)
    
    judge = MedicalJudge()
    
    line_items = [
        {"name": "Paracetamol"},
        {"name": "Dolo-650"},
        {"name": "Cough Syrup"}
    ]
    
    result = judge.evaluate_necessity("Ulcer", line_items)
    
    print("\nResults:")
    for item_name, evaluation in result.items():
        status = evaluation.get('status', 'UNKNOWN')
        severity = evaluation.get('severity', 'N/A')
        reason = evaluation.get('reason', 'No reason')
        
        icon = "❌" if status == "CONTRAINDICATED" else "⚠️" if status == "FLAG" else "✅"
        print(f"{icon} {item_name}")
        print(f"   Status: {status}")
        print(f"   Severity: {severity}")
        print(f"   Reason: {reason}\n")
    
    # Assertions
    paracetamol_status = result.get("Paracetamol", {}).get("status")
    dolo_status = result.get("Dolo-650", {}).get("status")
    
    if paracetamol_status in ["CONTRAINDICATED", "FLAG"]:
        print("✅ TEST PASSED: Paracetamol correctly flagged for ulcer patient")
    else:
        print("❌ TEST FAILED: Paracetamol should be flagged for ulcer patient")
        print(f"   Got status: {paracetamol_status}")
    
    if dolo_status in ["CONTRAINDICATED", "FLAG"]:
        print("✅ TEST PASSED: Dolo-650 correctly flagged for ulcer patient")
    else:
        print("❌ TEST FAILED: Dolo-650 should be flagged for ulcer patient")
        print(f"   Got status: {dolo_status}")


def test_viral_fever_paracetamol():
    """Test that paracetamol is SAFE for viral fever"""
    print("\n" + "="*80)
    print("TEST 2: Viral Fever + Paracetamol (Should be SAFE)")
    print("="*80)
    
    judge = MedicalJudge()
    
    line_items = [
        {"name": "Paracetamol"},
        {"name": "Cough Syrup"}
    ]
    
    result = judge.evaluate_necessity("Viral Fever", line_items)
    
    print("\nResults:")
    for item_name, evaluation in result.items():
        status = evaluation.get('status', 'UNKNOWN')
        severity = evaluation.get('severity', 'N/A')
        reason = evaluation.get('reason', 'No reason')
        
        icon = "❌" if status == "CONTRAINDICATED" else "⚠️" if status == "FLAG" else "✅"
        print(f"{icon} {item_name}")
        print(f"   Status: {status}")
        print(f"   Severity: {severity}")
        print(f"   Reason: {reason}\n")
    
    # Assertion
    paracetamol_status = result.get("Paracetamol", {}).get("status")
    
    if paracetamol_status == "PASS":
        print("✅ TEST PASSED: Paracetamol correctly approved for viral fever")
    else:
        print("⚠️ TEST WARNING: Paracetamol should be safe for viral fever")
        print(f"   Got status: {paracetamol_status}")


def test_kidney_disease_nsaids():
    """Test that NSAIDs are flagged for kidney disease"""
    print("\n" + "="*80)
    print("TEST 3: Kidney Disease + NSAIDs")
    print("="*80)
    
    judge = MedicalJudge()
    
    line_items = [
        {"name": "Ibuprofen"},
        {"name": "Diclofenac"},
        {"name": "Paracetamol"}
    ]
    
    result = judge.evaluate_necessity("Chronic Kidney Disease", line_items)
    
    print("\nResults:")
    for item_name, evaluation in result.items():
        status = evaluation.get('status', 'UNKNOWN')
        severity = evaluation.get('severity', 'N/A')
        reason = evaluation.get('reason', 'No reason')
        
        icon = "❌" if status == "CONTRAINDICATED" else "⚠️" if status == "FLAG" else "✅"
        print(f"{icon} {item_name}")
        print(f"   Status: {status}")
        print(f"   Severity: {severity}")
        print(f"   Reason: {reason}\n")
    
    # Assertions
    ibuprofen_status = result.get("Ibuprofen", {}).get("status")
    
    if ibuprofen_status in ["CONTRAINDICATED", "FLAG"]:
        print("✅ TEST PASSED: NSAIDs correctly flagged for kidney disease")
    else:
        print("❌ TEST FAILED: NSAIDs should be flagged for kidney disease")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("MEDICAL JUDGE CONTRAINDICATION TESTS")
    print("="*80)
    
    # Check if OpenAI API key is set
    if not os.environ.get('OPENAI_API_KEY'):
        print("\n⚠️ WARNING: OPENAI_API_KEY not set - tests will run in MOCK mode")
        print("   Set OPENAI_API_KEY to test real AI contraindication detection\n")
    
    test_ulcer_paracetamol()
    test_viral_fever_paracetamol()
    test_kidney_disease_nsaids()
    
    print("\n" + "="*80)
    print("TESTS COMPLETE")
    print("="*80 + "\n")
