"""
ClaimGuard AI - Policy Engine Test Suite
Tests the Policy Adjudicator against sample claims
"""

import json
from policy_engine import PolicyAdjudicator
from pathlib import Path


def print_separator(title=""):
    """Print a visual separator"""
    if title:
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80)
    else:
        print("-"*80)


def print_line_item_details(line_items):
    """Print detailed line item decisions"""
    print_separator()
    print(f"{'Item Name':<40} {'Claimed':>12} {'Approved':>12} {'Status':<12}")
    print_separator()
    
    for item in line_items:
        print(f"{item['item_name'][:38]:<40} "
              f"Rs.{item['claimed_amount']:>10,.2f} "
              f"Rs.{item['approved_amount']:>10,.2f} "
              f"{item['status']:<12}")
        if item.get('reason'):
            print(f"  └─ {item['reason']}")
    print_separator()


def test_claim(adjudicator, claim_file, test_name):
    """Test a single claim file"""
    print_separator(f"TEST: {test_name}")
    print(f"File: {claim_file}\n")
    
    try:
        result = adjudicator.adjudicate_claim(claim_file)
        
        # Print summary
        print(f"Claim ID: {result['claim_id']}")
        print(f"Patient: {result['patient_name']}")
        print(f"Merchant: {result['merchant_name']}")
        print(f"Claim Type: {result['claim_type']}\n")
        
        # Print financial summary
        print("FINANCIAL SUMMARY:")
        print(f"  Total Claimed:    Rs.{result['total_claimed']:,.2f}")
        print(f"  Total Approved:   Rs.{result['total_approved']:,.2f}")
        print(f"  Total Deducted:   Rs.{result['total_deducted']:,.2f}")
        print(f"  Approval Rate:    {(result['total_approved']/result['total_claimed']*100):.2f}%\n")
        
        # Print status and flags
        print("ADJUDICATION STATUS:")
        print(f"  Final Status: {result['status']}")
        print(f"  Excluded Items: {result['excluded_items_count']}")
        print(f"  Room Rent Deduction: {result['room_rent_deduction_applied']}")
        if result['deduction_reason']:
            print(f"  Deduction Reason: {result['deduction_reason']}\n")
        
        # Print summary
        print("\nSUMMARY:")
        print(result['summary'])
        
        # Print detailed line items
        print("\nDETAILED LINE ITEM DECISIONS:")
        print_line_item_details(result['line_item_decisions'])
        
        return True
        
    except Exception as e:
        print(f"[ERROR] ERROR: {str(e)}")
        return False


def run_all_tests():
    """Run tests on all sample claim files"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "CLAIMGUARD AI - POLICY ENGINE TEST SUITE" + " "*18 + "║")
    print("╚" + "="*78 + "╝")
    
    # Initialize the adjudicator
    adjudicator = PolicyAdjudicator(policy_path="../data/policy_rules.json")
    
    # Define test cases
    test_cases = [
        {
            'name': 'Valid Claim - All Medicines (Should Approve)',
            'file': '../data/claim_valid.json',
            'expected': 'Should be fully approved with no deductions'
        },
        {
            'name': 'Exclusion Fraud - Whey Protein + Moisturizer (Should Reject Items)',
            'file': '../data/claim_fraud_exclusion.json',
            'expected': 'Should reject Whey Protein and Moisturizer, approve medicines only'
        },
        {
            'name': 'Room Rent Limit Exceeded (Should Apply Proportionate Deduction)',
            'file': '../data/claim_fraud_limit.json',
            'expected': 'Should apply 62.5% deduction due to room rent cap (5000/8000)'
        }
    ]
    
    results = []
    
    # Run each test
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'#'*80}")
        print(f"# TEST CASE {i} of {len(test_cases)}")
        print(f"{'#'*80}")
        print(f"Expected: {test_case['expected']}\n")
        
        success = test_claim(adjudicator, test_case['file'], test_case['name'])
        results.append({'name': test_case['name'], 'success': success})
    
    # Print final summary
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*28 + "TEST SUITE SUMMARY" + " "*32 + "║")
    print("╚" + "="*78 + "╝")
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    for i, result in enumerate(results, 1):
        status = "[OK] PASSED" if result['success'] else "[FAILED] FAILED"
        print(f"{i}. {status} - {result['name']}")
    
    print(f"\n{'='*80}")
    print(f"Results: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    print(f"{'='*80}\n")
    
    # Verification notes
    print("\n[NOTES] VERIFICATION NOTES:")
    print("="*80)
    print("✓ Check that claim_valid.json is fully approved with no deductions")
    print("✓ Check that Whey Protein (Rs.2,499) and Moisturizer (Rs.450) are rejected")
    print("✓ Check room rent math: (5000/8000) × 131,775 = Rs.82,359.38 approved")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()
