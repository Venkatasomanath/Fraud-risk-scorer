# Fraud-Risk-Scorer
A powerful fraud detection system that analyzes transaction data and assigns risk scores based on 6 different fraud detection flags.

## Features
- Automated Column Mapping: Automatically detects and maps common column names
- 6 Fraud Detection Flags: Comprehensive fraud indicators
- Interactive Visualization: Beautiful risk breakdown charts
- Risk Level Classification: No Risk, Low, Medium, or High Risk
- CSV Export: Save analyzed data with risk scores
## Data Format
Your CSV should contain:
•	Amount (required): Transaction amounts
•	Date (optional): Transaction dates
•	User (optional): Customer identifiers
•	Description (optional): Transaction details
## Fraud Detection Flags
6 Fraud Indicators Checked:
1. Round Number Amounts
Detects: Amounts that are multiples of 100 or 1000
Why Suspicious: Fraudsters often use round numbers
Examples: $100, $500, $1000
Flag: round_num
2. Weekend Transactions
Detects: Transactions on Saturdays or Sundays
Why Suspicious: Reduced monitoring on weekends
Flag: weekend
3. Large Amount Transactions
Detects: Top 5% of transaction amounts (95th percentile)
Why Suspicious: Unusually large amounts vs normal activity
Flag: large
4. Suspicious Keywords
	Detects: Suspicious terms in descriptions
Keywords: cash, void, reverse, adjust, write-off, refund, urgent, gift
Why Suspicious: Associated with fraudulent activities
Flag: sus_keyword
5. High-Volume Users
Detects: Users with >30% of total transaction volume
Why Suspicious: Concentrated activity may indicate fraud
Flag: high_user
6. Backdated Transactions
Detects: Transactions dated in the past
Why Suspicious: Timing manipulation attempts
Flag: backdated
## Risk Scoring
•	Score Formula: (Number of Flags Triggered ÷ 6) × 100
•	Risk Levels:
o	No Risk: 0% (0 flags)
o	Low Risk: 0.1-33.33% (1-2 flags)
o	Medium Risk: 33.34-66.66% (3-4 flags)
o	High Risk: 66.67-100% (5-6 flags)
## Output
•	Overall risk assessment
•	Risk breakdown by category
•	Top 10 riskiest transactions
•	Export to fraud_risk_data.csv
Example output:
Overall Fraud Risk: 18.5%
## Risk Breakdown:
 • No Risk: 85 (56.7%)
 • Low Risk: 45 (30.0%) 
 • Medium Risk: 15 (10.0%)
 • High Risk: 5 (3.3%)

## Key Improvements:
1. Clear Fraud Flag Documentation
Explicitly states "6 fraud detection flags" throughout

Each flag has a detailed explanation above

Code includes self.fraud_flags_count = 6 for clarity

2. Enhanced User Interface
Better visual formatting with emojis and sections

Progress indicators and clear steps

Professional output formatting

3. Improved Code Structure
Better comments and documentation

Separate methods for each functionality

Error handling and user feedback

4. Comprehensive Sample Data
Includes examples that trigger different fraud flags

Realistic transaction scenarios

5. Professional Output
Clear risk breakdowns

Visual charts with better styling

Actionable results
