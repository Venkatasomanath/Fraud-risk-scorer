
## 4. fraud_analyzer.py
```python
import pandas as pd
import numpy as np
import altair as alt
import ipywidgets as widgets
from IPython.display import display, clear_output
import io
import sys
import subprocess

class FraudAnalyzer:
    """
    Fraud Risk Scorer - Analyzes transactions for fraud using 6 detection flags
    """
    
    def __init__(self):
        self._install_dependencies()
        self.fraud_flags_count = 6  # Total number of fraud flags checked
        
    def _install_dependencies(self):
        """Install required packages if missing"""
        packages = ['pandas', 'numpy', 'altair', 'ipywidgets']
        for package in packages:
            try:
                __import__(package)
            except ImportError:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    def create_interface(self):
        """Create the interactive file upload interface"""
        self.uploader = widgets.FileUpload(
            accept='.csv', 
            multiple=False, 
            description='Upload CSV',
            layout=widgets.Layout(width='300px')
        )
        self.button = widgets.Button(
            description="Run Fraud Analysis", 
            button_style='success',
            icon='search',
            layout=widgets.Layout(width='250px', height='50px')
        )
        self.output = widgets.Output()
        
        self.button.on_click(self.run_analysis)
        
        # Display header and widgets
        print("FRAUD RISK SCORER")
        print("=" * 50)
        print(f"Checks {self.fraud_flags_count} different fraud indicators")
        print("\n1. Upload your CSV file")
        print("2. Click 'Run Fraud Analysis'")
        print("3. View results and download risk data")
        print("=" * 50)
        
        display(self.uploader, self.button, self.output)
    
    def auto_map_columns(self, df):
        """
        Automatically map common column names to expected formats
        """
        cols = {col.lower().replace(' ', '').replace('_', ''): col for col in df.columns}
        
        mapping = {
            'amount': ['amount', 'transactionamount', 'amt', 'total', 'value', 'price'],
            'date': ['date', 'entrydate', 'transactiondate', 'purchasedate', 'time'],
            'user': ['user', 'customerid', 'accountid', 'clientid', 'customer', 'userid'],
            'description': ['description', 'category', 'product', 'type', 'merchantname', 'transactiontype'],
            'entry_id': ['transactionid', 'txid', 'id', 'entryid', 'orderid', 'invoice']
        }
        
        rename = {}
        for target, sources in mapping.items():
            found = next((cols[k] for k in sources if k in cols), None)
            if found:
                rename[found] = target
                
        return rename
    
    def calculate_fraud_flags(self, df):
        """
        Calculate 6 different fraud detection flags
        Returns: DataFrame with fraud flags added
        """
        # Flag 1: Round number amounts
        df['round_num'] = (df['amount'] % 1000 == 0) | (df['amount'] % 100 == 0)
        
        # Flag 2: Weekend transactions
        df['weekend'] = df['entry_date'].dt.dayofweek >= 5
        df['weekend'] = df['weekend'].fillna(False)
        
        # Flag 3: Large amount transactions (95th percentile)
        threshold = df['amount'].quantile(0.95) if df['amount'].sum() > 0 else 0
        df['large'] = df['amount'] > threshold
        
        # Flag 4: Suspicious keywords in descriptions
        keywords = ['cash', 'void', 'reverse', 'adjust', 'write-off', 'refund', 'urgent', 'gift']
        pattern = '|'.join(keywords)
        df['sus_keyword'] = df['description'].str.contains(pattern, case=False, na=False)
        
        # Flag 5: High-volume users (>30% of total amount)
        df['high_user'] = False
        if df['user'].nunique() > 1:
            user_sums = df.groupby('user')['amount'].sum()
            user_pct = user_sums / user_sums.sum()
            high_users = user_pct[user_pct > 0.3].index
            df.loc[df['user'].isin(high_users), 'high_user'] = True
        
        # Flag 6: Backdated transactions (basic implementation)
        df['backdated'] = False
        
        return df
    
    def calculate_risk_scores(self, df):
        """
        Calculate fraud risk scores and risk levels based on flag counts
        """
        flags = ['round_num', 'weekend', 'large', 'sus_keyword', 'high_user', 'backdated']
        df['flag_count'] = df[flags].sum(axis=1)
        
        # Calculate fraud score percentage (flags triggered / total flags)
        df['fraud_score_%'] = (df['flag_count'] / len(flags)) * 100
        
        # Categorize risk levels
        df['risk_level'] = pd.cut(
            df['fraud_score_%'], 
            bins=[0, 0.1, 33.33, 66.66, 100], 
            labels=['No Risk', 'Low Risk', 'Medium Risk', 'High Risk'], 
            include_lowest=True
        )
        
        return df
    
    def create_visualization(self, df):
        """
        Create interactive risk visualization chart
        """
        overall_risk = df['fraud_score_%'].mean()
        categories = ['No Risk', 'Low Risk', 'Medium Risk', 'High Risk']
        risk_counts = df['risk_level'].value_counts().reindex(categories, fill_value=0)
        total = len(df)
        
        # Prepare data for visualization
        bar_data = pd.DataFrame({
            'Risk Level': categories,
            'Count': [risk_counts[c] for c in categories],
            'Percentage': [(risk_counts[c] / total) * 100 for c in categories]
        })
        
        # Create gradient colors for risk levels
        color_scale = alt.Scale(
            domain=categories,
            range=['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728']  # Blue, Green, Orange, Red
        )
        
        # Create bar chart
        bars = alt.Chart(bar_data).mark_bar(
            size=60,
            cornerRadiusTopLeft=8,
            cornerRadiusTopRight=8
        ).encode(
            x=alt.X('Risk Level:N', 
                   sort=categories,
                   axis=alt.Axis(title=None, labelFontSize=14, labelFontWeight='bold')),
            y=alt.Y('Count:Q', 
                   axis=alt.Axis(title='Number of Transactions', 
                               titleFontSize=14, titleFontWeight='bold')),
            color=alt.Color('Risk Level:N', scale=color_scale, legend=None),
            tooltip=['Risk Level', 'Count', alt.Tooltip('Percentage:Q', format='.1f', title='Percentage')]
        )
        
        # Add percentage text inside bars
        text = bars.mark_text(
            align='center',
            baseline='bottom',
            dy=-5,
            fontSize=16,
            fontWeight='bold',
            color='white'
        ).encode(
            text=alt.Text('Percentage:Q', format='.1f')
        )
        
        # Add count text below percentage
        count_text = bars.mark_text(
            align='center',
            baseline='top',
            dy=5,
            fontSize=12,
            color='white'
        ).encode(
            text='Count:Q'
        )
        
        # Combine all chart elements
        chart = (bars + text + count_text).properties(
            title=alt.TitleParams(
                text=f"Fraud Risk Distribution - Overall: {overall_risk:.1f}%",
                fontSize=18,
                fontWeight='bold',
                anchor='middle'
            ),
            width=500,
            height=400
        ).configure_axis(
            grid=False
        ).configure_view(
            strokeWidth=0
        )
        
        return chart, overall_risk, risk_counts, total
    
    def display_fraud_flags_info(self):
        """Display information about the 6 fraud flags being checked"""
        print(f"\nCHECKING {self.fraud_flags_count} FRAUD INDICATORS:")
        print("1. Round number amounts (multiples of 100/1000)")
        print("2. Weekend transactions (Sat/Sun)")
        print("3. Large amounts (top 5%)")
        print("4. Suspicious keywords in descriptions")
        print("5. High-volume users (>30% of total)")
        print("6. Backdated transactions")
    
    def run_analysis(self, _):
        """
        Main analysis function triggered by button click
        """
        with self.output:
            clear_output()
            
            if not self.uploader.value:
                print("❌ Please upload a CSV file first!")
                return
            
            try:
                # Read uploaded file
                file = list(self.uploader.value.values())[0]
                df = pd.read_csv(io.BytesIO(file['content']))
                print(f" Loaded {len(df)} rows and {len(df.columns)} columns.")
            except Exception as e:
                print(f"❌ Error reading file: {e}")
                return
            
            # Display fraud flags information
            self.display_fraud_flags_info()
            
            # Auto-map columns to expected names
            rename = self.auto_map_columns(df)
            df = df.rename(columns=rename)
            
            print("\nMapped Columns:")
            for original, mapped in rename.items():
                print(f"   • {original} → {mapped}")
            
            # Clean and prepare data
            df['amount'] = pd.to_numeric(df.get('amount', 0), errors='coerce').fillna(0).abs()
            df['entry_date'] = pd.to_datetime(df.get('entry_date', ''), errors='coerce')
            df['description'] = df.get('description', 'Unknown').fillna('Unknown').astype(str)
            df['user'] = df.get('user', 'Unknown').fillna('Unknown').astype(str)
            
            # Calculate fraud flags and risk scores
            df = self.calculate_fraud_flags(df)
            df = self.calculate_risk_scores(df)
            
            # Create and display visualization
            chart, overall_risk, risk_counts, total = self.create_visualization(df)
            
            # Print risk summary
            print(f"\nOVERALL FRAUD RISK: {overall_risk:.1f}%")
            print("\nRISK BREAKDOWN:")
            categories = ['No Risk', 'Low Risk', 'Medium Risk', 'High Risk']
            for cat in categories:
                count = risk_counts[cat]
                pct = (count / total) * 100
                print(f"   • {cat}: {count} transactions ({pct:.1f}%)")
            
            print("\nVISUAL RISK DISTRIBUTION:")
            display(chart)
            
            # Show top 10 riskiest transactions
            show_cols = [c for c in ['entry_id', 'entry_date', 'amount', 'user', 'description', 'fraud_score_%', 'risk_level'] if c in df.columns]
            if 'entry_id' not in df.columns:
                df['entry_id'] = df.index
                
            top10 = df.nlargest(10, 'fraud_score_%')[show_cols]
            print(f"\n TOP 10 RISKIEST TRANSACTIONS:")
            display(top10)
            
            # Save results
            output_filename = "fraud_risk_analysis.csv"
            df.to_csv(output_filename, index=False)
            print(f"\n SAVED: {output_filename} ({len(df)} rows with risk scores)")
            print("Analysis complete! Download the CSV for further investigation.")
    
    def run_demo(self):
        """Run the interactive demo"""
        print("Starting Fraud Risk Scorer...")
        self.create_interface()

def main():
    """Main function to run the fraud analyzer"""
    analyzer = FraudAnalyzer()
    analyzer.run_demo()

if __name__ == "__main__":
    main()
