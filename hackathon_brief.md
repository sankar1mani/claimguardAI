# Project: ClaimGuard AI (Assemble Hack 2025)

## 🎯 Goal
Build an automated "Forensic Adjudication Engine" for Indian Health Insurance Reimbursement Claims.
Target Audience: Post-hospitalization claims (Pharmacy, Diagnostics) which have high volume and high fraud.

## 🏗 Tech Stack (The "Infinity Stones")
1. **Orchestrator:** Kestra (Manages the flow: Upload -> Vision Check -> Policy Check -> Payout)
2. **Frontend:** Vercel (React + Tailwind for users to upload bills)
3. **AI Logic:** Python Scripts (using OpenAI)
4. **Developer:** Cline (You are building this!)

## 🧠 The Business Logic (Crucial)
We are solving "Soft Fraud" and "Complex Rules" that humans miss:
1. **Visual Fraud:** Detect if a receipt date has been photoshopped or if the receipt is a duplicate.
2. **Room Rent Capping:** If the user's room rent > 1% of Sum Insured, deduct the claim proportionately.
   - *Formula:* (Allowed Limit / Actual Rent) * Claim Amount = Payable Amount.
3. **Exclusions:** Scan line items. If "Protein Powder" or "Cosmetics" are found -> Auto-Reject that specific line.

## 📂 Architecture Plan
- /frontend: React app (Vite)/ Vercel
- /backend: Python scripts for the Agents (Vision Agent, Policy Agent)
- /kestra: YAML flows for orchestration
- /data: Sample receipts (Valid, Edited, Fraudulent) and Policy text.