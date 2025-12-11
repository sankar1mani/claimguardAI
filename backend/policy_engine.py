"""
ClaimGuard AI - Policy Adjudicator Agent
Enforces Indian Health Insurance Policy Rules for Claims Processing
"""

import json
import sys
from pathlib import Path


class PolicyAdjudicator:
    def __init__(self, policy_path="data/policy_rules.json"):
        """Initialize the Policy Adjudicator with policy rules"""
        self.policy_path = Path(policy_path)
        self.policy_rules = self.load_policy_rules()
        
    def load_policy_rules(self):
        """Load policy rules from JSON file"""
        try:
            with open(self.policy_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Policy rules file not found at {self.policy_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in policy rules file")
            sys.exit(1)
    
    def load_claim(self, claim_path):
        """Load claim data from JSON file"""
        try:
            with open(claim_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Claim file not found at {claim_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in claim file")
            sys.exit(1)
    
    def is_excluded_item(self, item_name):
        """Check if an item matches any excluded category"""
        item_name_lower = item_name.lower()
        excluded_categories = self.policy_rules.get('excluded_items', {}).get('categories', [])
        
        # Check exact matches in excluded items list
        for category in excluded_categories:
            for excluded_item in category.get('items', []):
                if excluded_item.lower() in item_name_lower or item_name_lower in excluded_item.lower():
                    return True, category['category'], category['reason']
        
        # Check partial keyword matches
        partial_keywords = self.policy_rules.get('excluded_items', {}).get('partial_match_keywords', [])
        for keyword in partial_keywords:
            if keyword.lower() in item_name_lower:
                return True, "Partial Match", f"Contains excluded keyword: {keyword}"
        
        return False, None, None
    
    def calculate_proportionate_deduction(self, claim_data):
        """Calculate proportionate deduction if room rent exceeds limit"""
        room_rent_rules = self.policy_rules.get('room_rent_rules', {})
        allowed_percentage = room_rent_rules.get('allowed_percentage', 1) / 100
        
        # Get sum insured from claim
        sum_insured = claim_data.get('sum_insured', 500000)  # Default to 5 lakhs
        allowed_room_rent = sum_insured * allowed_percentage
        
        # Find room rent item in line items
        room_rent_item = None
        actual_room_rent_per_day = 0
        
        for item in claim_data.get('line_items', []):
            item_name_lower = item.get('name', '').lower()
            if 'room rent' in item_name_lower or 'room charge' in item_name_lower:
                room_rent_item = item
                actual_room_rent_per_day = item.get('unit_price', 0)
                break
        
        # Calculate proportionate ratio if room rent exceeds limit
        proportionate_ratio = 1.0
        deduction_applied = False
        deduction_reason = None
        
        if room_rent_item and actual_room_rent_per_day > allowed_room_rent:
            proportionate_ratio = allowed_room_rent / actual_room_rent_per_day
            deduction_applied = True
            deduction_reason = (
                f"Room rent of Rs.{actual_room_rent_per_day:,.2f}/day exceeds allowed limit of "
                f"Rs.{allowed_room_rent:,.2f}/day (1% of Rs.{sum_insured:,.2f} sum insured). "
                f"Proportionate deduction ratio: {proportionate_ratio:.4f}"
            )
        
        return {
            'proportionate_ratio': proportionate_ratio,
            'deduction_applied': deduction_applied,
            'deduction_reason': deduction_reason,
            'allowed_room_rent': allowed_room_rent,
            'actual_room_rent': actual_room_rent_per_day
        }
    
    def adjudicate_claim(self, claim_path):
        """Main function to adjudicate a claim"""
        claim_data = self.load_claim(claim_path)
        
        # Initialize tracking variables
        total_claimed = claim_data.get('total_amount', 0)
        total_approved = 0
        line_item_decisions = []
        excluded_items_count = 0
        
        # Calculate proportionate deduction for room rent
        deduction_info = self.calculate_proportionate_deduction(claim_data)
        proportionate_ratio = deduction_info['proportionate_ratio']
        
        # Process each line item
        for item in claim_data.get('line_items', []):
            item_name = item.get('name', '')
            item_price = item.get('total_price', 0)
            
            # Check if item is excluded
            is_excluded, exclusion_category, exclusion_reason = self.is_excluded_item(item_name)
            
            decision = {
                'item_name': item_name,
                'claimed_amount': item_price,
                'approved_amount': 0,
                'status': '',
                'reason': ''
            }
            
            if is_excluded:
                # Item is excluded - reject it
                decision['status'] = 'REJECTED'
                decision['reason'] = f"Excluded: {exclusion_category} - {exclusion_reason}"
                decision['approved_amount'] = 0
                excluded_items_count += 1
            else:
                # Item is approved - apply proportionate deduction if applicable
                approved_amount = item_price * proportionate_ratio
                decision['approved_amount'] = round(approved_amount, 2)
                decision['status'] = 'APPROVED'
                
                if deduction_info['deduction_applied'] and 'room rent' not in item_name.lower():
                    decision['reason'] = f"Approved with proportionate deduction ({proportionate_ratio:.2%})"
                elif 'room rent' in item_name.lower() and deduction_info['deduction_applied']:
                    decision['reason'] = f"Room rent capped at policy limit (Rs.{deduction_info['allowed_room_rent']:,.2f}/day)"
                else:
                    decision['reason'] = "Approved - complies with policy"
                
                total_approved += decision['approved_amount']
            
            line_item_decisions.append(decision)
        
        # Determine overall status
        if total_approved == 0:
            status = "REJECTED"
        elif total_approved < total_claimed:
            status = "PARTIAL_APPROVAL"
        else:
            status = "APPROVED"
        
        # Build result
        result = {
            'claim_id': claim_data.get('claim_id', 'UNKNOWN'),
            'claim_type': claim_data.get('claim_type', 'UNKNOWN'),
            'merchant_name': claim_data.get('merchant_name', 'UNKNOWN'),
            'patient_name': claim_data.get('patient_name', 'UNKNOWN'),
            'total_claimed': round(total_claimed, 2),
            'total_approved': round(total_approved, 2),
            'total_deducted': round(total_claimed - total_approved, 2),
            'status': status,
            'excluded_items_count': excluded_items_count,
            'room_rent_deduction_applied': deduction_info['deduction_applied'],
            'deduction_reason': deduction_info['deduction_reason'],
            'line_item_decisions': line_item_decisions,
            'summary': self.generate_summary(status, total_claimed, total_approved, excluded_items_count, deduction_info)
        }
        
        return result
    
    def generate_summary(self, status, total_claimed, total_approved, excluded_count, deduction_info):
        """Generate a human-readable summary of the adjudication"""
        summary_lines = []
        
        if status == "APPROVED":
            summary_lines.append("[OK] Claim FULLY APPROVED - All items comply with policy rules")
        elif status == "PARTIAL_APPROVAL":
            summary_lines.append("[WARNING] Claim PARTIALLY APPROVED - Some deductions applied")
            if excluded_count > 0:
                summary_lines.append(f"   • {excluded_count} excluded item(s) found and rejected")
            if deduction_info['deduction_applied']:
                summary_lines.append(f"   • Room rent exceeded policy limit - proportionate deduction applied")
        else:
            summary_lines.append("[REJECT] Claim REJECTED - Does not comply with policy")
        
        summary_lines.append(f"   • Claimed: Rs.{total_claimed:,.2f}")
        summary_lines.append(f"   • Approved: Rs.{total_approved:,.2f}")
        summary_lines.append(f"   • Deducted: Rs.{total_claimed - total_approved:,.2f}")
        
        return "\n".join(summary_lines)


def main():
    """Main entry point for CLI usage"""
    if len(sys.argv) < 2:
        print("Usage: python policy_engine.py <claim_file_path>")
        print("Example: python policy_engine.py ../data/claim_valid.json")
        sys.exit(1)
    
    claim_file_path = sys.argv[1]
    
    # Initialize adjudicator
    adjudicator = PolicyAdjudicator()
    
    # Adjudicate the claim
    result = adjudicator.adjudicate_claim(claim_file_path)
    
    # Print result as formatted JSON
    print("\n" + "="*80)
    print("CLAIMGUARD AI - POLICY ADJUDICATION RESULT")
    print("="*80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("="*80)


if __name__ == "__main__":
    main()
