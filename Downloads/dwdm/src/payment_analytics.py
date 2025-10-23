import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime

class PaymentAnalytics:
    def analyze_payment_preferences(self, df):
        """
        Analyze payment method preferences and patterns
        """
        # Distribution of payment methods and key metrics
        method_stats = {}
        
        for method in df['Payment_Method'].unique():
            method_data = df[df['Payment_Method'] == method]
            total_transactions = len(method_data)
            
            # Calculate metrics
            stats = {
                'share': total_transactions / len(df),
                'avg_value': method_data['Final_Price(Rs.)'].mean(),
                'total_volume': method_data['Final_Price(Rs.)'].sum(),
                'total_transactions': total_transactions
            }
            
            # Transaction value distribution
            values = method_data['Final_Price(Rs.)']
            value_dist = {
                'low': len(values[values < 0.3]) / len(values),
                'medium': len(values[(values >= 0.3) & (values <= 0.6)]) / len(values),
                'high': len(values[values > 0.6]) / len(values)
            }
            stats['value_distribution'] = value_dist
            
            # Time-based patterns
            stats['time_patterns'] = self._analyze_time_patterns(method_data)
            
            method_stats[method] = stats
        
        return {'method_stats': method_stats}
    
    def _analyze_time_patterns(self, transactions: pd.DataFrame) -> Dict:
        """
        Analyze payment method usage patterns over time
        """
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(transactions['Purchase_Date']):
            transactions = transactions.copy()
            transactions['Purchase_Date'] = pd.to_datetime(transactions['Purchase_Date'], format='%d-%m-%Y')
        else:
            transactions = transactions.copy()
        
        # Extract time components
        transactions['hour'] = transactions['Purchase_Date'].dt.hour
        transactions['day_of_week'] = transactions['Purchase_Date'].dt.day_name()
        transactions['month'] = transactions['Purchase_Date'].dt.month
        
        # Analyze patterns
        patterns = {
            'hourly': transactions.groupby('hour')['Final_Price(Rs.)'].agg(['count', 'mean']).to_dict(),
            'daily': transactions.groupby('day_of_week')['Final_Price(Rs.)'].agg(['count', 'mean']).to_dict(),
            'monthly': transactions.groupby('month')['Final_Price(Rs.)'].agg(['count', 'mean']).to_dict()
        }
        
        return patterns
    
    def recommend_payment_incentives(self, payment_insights):
        """
        Generate payment method incentive recommendations
        """
        incentives = {}
        method_stats = payment_insights['method_stats']
        
        for method, stats in method_stats.items():
            incentive = {
                'strategy': 'Maintain current performance',
                'action': 'Continue monitoring',
                'priority': 'Low'
            }
            
            # High-value method (high average transaction value)
            if stats['avg_value'] > 0.5:
                if stats['share'] < 0.3:  # Good performance but low adoption
                    incentive.update({
                        'strategy': 'Increase adoption of high-value method',
                        'action': f'Offer 2% cashback on {method} transactions above ₹0.6',
                        'priority': 'High',
                        'target_segment': 'High-value customers',
                        'expected_impact': '15-20% increase in high-value transactions'
                    })
                else:  # Good performance and good adoption
                    incentive.update({
                        'strategy': 'Maintain premium position',
                        'action': f'Exclusive {method} benefits for premium customers',
                        'priority': 'Medium',
                        'target_segment': 'Loyal Customers',
                        'expected_impact': 'Strengthen customer loyalty'
                    })
            
            # Popular method (high share)
            elif stats['share'] > 0.3:
                incentive.update({
                    'strategy': 'Optimize popular method',
                    'action': f'Streamline {method} processing and reduce fees',
                    'priority': 'Medium',
                    'target_segment': 'All customers',
                    'expected_impact': 'Reduced transaction costs'
                })
            
            # Low-value, low-share method
            else:
                incentive.update({
                    'strategy': 'Evaluate method viability',
                    'action': f'Analyze {method} usage patterns and customer feedback',
                    'priority': 'Low',
                    'target_segment': 'New customers',
                    'expected_impact': 'Data for strategic decision-making'
                })
            
            incentives[method] = incentive
        
        return incentives