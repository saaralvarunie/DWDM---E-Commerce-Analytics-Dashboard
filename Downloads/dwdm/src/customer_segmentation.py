import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import Dict, List

class CustomerSegmentation:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.features = [
            'total_spend',
            'monthly_frequency',
            'avg_transaction_value',
            'discount_usage',
            'days_since_last_purchase'
        ]
        self.segment_profiles = {
            0: "Deal Hunters",      # High discount usage, price sensitive
            1: "Loyal Customers"    # High frequency, value relationship
        }
        
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess customer data for segmentation
        """
        return self.scaler.fit_transform(data[self.features])
    
    def segment_customers(self, data: pd.DataFrame, n_segments: int = 2) -> Dict:
        """
        Segment customers based on their shopping behavior
        """
        X = self.preprocess_data(data)
        self.model = KMeans(n_clusters=n_segments, random_state=42)
        segments = self.model.fit_predict(X)
        
        # Store raw data for analysis
        self.data = data.copy()
        self.data['segment'] = segments
        
        return {
            'segments': segments,
            'profiles': self.segment_profiles,
            'centroids': self.model.cluster_centers_,
            'segment_analysis': self.analyze_segments()
        }
    
    def analyze_segments(self) -> Dict:
        """
        Analyze characteristics of each segment
        """
        segment_analysis = {}
        
        for segment_id in range(len(self.segment_profiles)):
            segment_data = self.data[self.data['segment'] == segment_id]
            
            analysis = {
                'size': len(segment_data),
                'avg_spend': segment_data['total_spend'].mean(),
                'avg_frequency': segment_data['monthly_frequency'].mean(),
                'avg_basket': segment_data['avg_transaction_value'].mean(),
                'avg_discount_usage': segment_data['discount_usage'].mean(),
                'recency': segment_data['days_since_last_purchase'].mean(),
                'total_revenue': segment_data['total_spend'].sum(),
                'discount_sensitivity': self._calculate_discount_sensitivity(segment_data)
            }
            
            segment_analysis[segment_id] = analysis
            
        return segment_analysis
    
    def _calculate_discount_sensitivity(self, segment_data: pd.DataFrame) -> float:
        """
        Calculate how sensitive a segment is to discounts
        Returns a score between 0 and 1
        """
        correlation = segment_data['total_spend'].corr(segment_data['discount_usage'])
        return (correlation + 1) / 2  # Normalize to 0-1 scale
    
    def recommend_promotions(self, customer_segment: int) -> Dict:
        """
        Generate detailed promotion recommendations based on customer segment
        """
        segment_data = self.data[self.data['segment'] == customer_segment]
        discount_sensitivity = self._calculate_discount_sensitivity(segment_data)
        
        base_recommendations = {
            0: {  # Deal Hunters
                "discount_range": "20-35%",
                "promotion_type": "Flash sales and time-limited discounts",
                "frequency": "Weekly",
                "channels": ["Email", "Mobile App Notifications", "SMS"],
                "conditions": "Limited time windows, minimum purchase requirements",
                "targeted_offers": [
                    "Weekend flash sales",
                    "Buy-one-get-one deals",
                    "Clearance event access",
                    "Price-drop alerts"
                ]
            },
            1: {  # Loyal Customers
                "discount_range": "10-25%",
                "promotion_type": "Loyalty rewards and personalized offers",
                "frequency": "Monthly",
                "channels": ["Email", "Loyalty Program Portal", "Personal SMS"],
                "conditions": "Points-based rewards, cumulative purchase discounts",
                "targeted_offers": [
                    "Birthday month specials",
                    "Loyalty points multipliers",
                    "Early access to sales",
                    "Member-exclusive bundles"
                ]
            }
        }
        
        recommendations = base_recommendations.get(customer_segment, {})
        recommendations.update({
            "segment_name": self.segment_profiles[customer_segment],
            "discount_sensitivity": f"{discount_sensitivity:.2f}",
            "segment_size": len(segment_data),
            "avg_transaction": segment_data['total_spend'].mean()
        })
        
        return recommendations