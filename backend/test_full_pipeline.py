"""
ClaimGuard AI - Full Pipeline Test
Tests the complete flow: Vision Agent -> Policy Engine
"""

import json
from vision_agent import VisionAgent
from policy_engine import PolicyAdjudicator
from pathlib import Path


def print_separator(title="", char="="):
    """Print a visual separator"""
    if title:
        print(f"\n{char*80}")
        print(f"  {title}")
        print(f"{char*80}")
    else:
        print(char*80)


def test_full_pipeline():
    """Test the complete claim processing pipeline"""
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "CLAIMGUARD AI - FULL PIPELINE TEST" + " "*29 + "║")
    print("╚" + "="*78 + "╝")
    print("\nThis test demonstrates the complete claim adjudication flow:")
    print("  1. Vision Agent: Extract data from receipt (mock mode)")
    print("  2. Policy Engine: Validate against policy rules")
    print("  3. Final Decision: Approve/Reject with detailed reasoning")
    
    # Initialize agents
    print_separator("INITIALIZING AGENTS")
    vision_agent = VisionAgent()
    policy_adjudicator = PolicyAdjudicator(policy_path="../data/policy_rules.json")
    print("[OK] Vision Agent initialized")
    print("[OK] Policy Adjudicator initialized")
    
    # Test with a dummy receipt image path (will use mock data)
    print_separator("STEP 1: VISION AGENT - RECEIPT SCANNING", "-")
    print("Note: Using mock mode since no API keys are configured")
    print("In production, this would analyze an actual receipt image\n")
    
    # In mock mode, the vision agent will return data from claim_valid.json
    # We just need to pass any path - it won't actually check for the file in mock mode
    dummy_receipt_path = "mock_receipt.jpg"
    
    # For mock mode, directly load the mock data
    if vision_agent.provider == "mock":
        extracted_data = vision_agent.load_mock_data()
    else:
        extracted_data = vision_agent.process_receipt(dummy_receipt_path)
    
    if not extracted_data:
        print("[ERROR] Vision Agent failed to process receipt")
        return False
    
    # Save extracted data temporarily
    temp_claim_file = "temp_extracted_claim.json"
    vision_agent.save_extracted_data(extracted_data, temp_claim_file)
    
    # Show what was extracted
    print("\n[DATA] EXTRACTED DATA SUMMARY:")
    print(f"  Claim ID: {extracted_data.get('claim_id', 'N/A')}")
    print(f"  Merchant: {extracted_data.get('merchant_name', 'N/A')}")
    print(f"  Date: {extracted_data.get('date', 'N/A')}")
    print(f"  Total Amount: Rs.{extracted_data.get('total_amount', 0):,.2f}")
    print(f"  Line Items: {len(extracted_data.get('line_items', []))}")
    
    fraud_detection = extracted_data.get('fraud_detection', {})
    print(f"\n[FRAUD] FRAUD DETECTION (Vision Agent):")
    print(f"  Suspicious: {fraud_detection.get('suspicious', 'N/A')}")
    print(f"  Confidence: {fraud_detection.get('confidence_score', 0)*100:.1f}%")
    print(f"  Recommendation: {fraud_detection.get('recommendation', 'N/A')}")
    
    # Step 2: Policy Adjudication
    print_separator("STEP 2: POLICY ENGINE - RULE VALIDATION", "-")
    print("Validating claim against Indian Health Insurance Policy rules...\n")
    
    result = policy_adjudicator.adjudicate_claim(temp_claim_file)
    
    # Show policy validation results
    print("[POLICY] POLICY VALIDATION RESULTS:")
    print(f"  Status: {result['status']}")
    print(f"  Total Claimed: Rs.{result['total_claimed']:,.2f}")
    print(f"  Total Approved: Rs.{result['total_approved']:,.2f}")
    print(f"  Total Deducted: Rs.{result['total_deducted']:,.2f}")
    print(f"  Excluded Items: {result['excluded_items_count']}")
    print(f"  Room Rent Deduction Applied: {result['room_rent_deduction_applied']}")
    
    print_separator("STEP 3: FINAL DECISION", "-")
    
    # Determine final decision
    vision_suspicious = fraud_detection.get('suspicious', False)
    vision_recommendation = fraud_detection.get('recommendation', 'APPROVE')
    policy_status = result['status']
    
    print("\n[DECISION] DECISION MATRIX:")
    print(f"  Vision Agent Fraud Check: {vision_recommendation}")
    print(f"  Policy Engine Status: {policy_status}")
    
    # Final decision logic
    if vision_recommendation == "REJECT" or vision_suspicious:
        final_decision = "REJECTED - Fraud detected by Vision Agent"
        final_color = "[REJECT]"
    elif policy_status == "REJECTED":
        final_decision = "REJECTED - Does not comply with policy"
        final_color = "[REJECT]"
    elif policy_status == "PARTIAL_APPROVAL":
        final_decision = f"PARTIALLY APPROVED - Rs.{result['total_approved']:,.2f} payable"
        final_color = "[PARTIAL]"
    else:
        final_decision = f"FULLY APPROVED - Rs.{result['total_approved']:,.2f} payable"
        final_color = "[APPROVE]"
    
    print(f"\n{final_color} FINAL DECISION: {final_decision}")
    
    # Show detailed summary
    print("\n" + result['summary'])
    
    # Show line items if there are exclusions or deductions
    if result['excluded_items_count'] > 0 or result['room_rent_deduction_applied']:
        print_separator("DETAILED LINE ITEM BREAKDOWN", "-")
        print(f"{'Item Name':<40} {'Claimed':>12} {'Approved':>12} {'Status':<12}")
        print("-"*80)
        for item in result['line_item_decisions'][:10]:  # Show first 10 items
            print(f"{item['item_name'][:38]:<40} "
                  f"Rs.{item['claimed_amount']:>10,.2f} "
                  f"Rs.{item['approved_amount']:>10,.2f} "
                  f"{item['status']:<12}")
    
    # Cleanup
    Path(temp_claim_file).unlink(missing_ok=True)
    
    print_separator("PIPELINE TEST COMPLETE")
    print("[OK] Full pipeline executed successfully!")
    print("\n[NEXT] NEXT STEPS:")
    print("  1. Add real receipt images to test with actual Vision AI")
    print("  2. Set OPENAI_API_KEY environment variable")
    print("  3. Create Kestra workflows to orchestrate this pipeline")
    print("  4. Build React frontend for user uploads")
    print_separator()
    
    return True


def test_three_scenarios():
    """Test all three claim scenarios through the pipeline"""
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*12 + "TESTING ALL THREE CLAIM SCENARIOS" + " "*31 + "║")
    print("╚" + "="*78 + "╝")
    
    policy_adjudicator = PolicyAdjudicator(policy_path="../data/policy_rules.json")
    
    scenarios = [
        ("Valid Claim", "../data/claim_valid.json"),
        ("Exclusion Fraud", "../data/claim_fraud_exclusion.json"),
        ("Room Rent Limit", "../data/claim_fraud_limit.json")
    ]
    
    for i, (name, claim_file) in enumerate(scenarios, 1):
        print(f"\n{'#'*80}")
        print(f"# SCENARIO {i}: {name}")
        print(f"{'#'*80}\n")
        
        result = policy_adjudicator.adjudicate_claim(claim_file)
        
        print(f"Status: {result['status']}")
        print(f"Claimed: Rs.{result['total_claimed']:,.2f}")
        print(f"Approved: Rs.{result['total_approved']:,.2f}")
        print(f"Deducted: Rs.{result['total_deducted']:,.2f}")
        print(f"\nSummary:\n{result['summary']}")
    
    print(f"\n{'='*80}")
    print("[OK] All scenarios tested successfully!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Test full pipeline with mock vision agent
    test_full_pipeline()
    
    # Test all three scenarios
    print("\n\n")
    test_three_scenarios()
