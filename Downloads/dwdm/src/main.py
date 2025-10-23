import pandas as pd
import numpy as np
from customer_segmentation import CustomerSegmentation
from bundle_recommendation import BundleRecommendation
from payment_analytics import PaymentAnalytics

def preprocess_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess transaction data to create meaningful baskets based on product relationships
    """
    # Create price ranges
    df['price_range'] = pd.qcut(df['Final_Price(Rs.)'], q=5, labels=['very_low', 'low', 'medium', 'high', 'very_high'])
    
    # Create product groups based on category and price range
    df['product_group'] = df['Category'] + '_' + df['price_range'].astype(str)
    
    # Calculate category affinities based on price range overlap
    category_affinity = {}
    for cat1 in df['Category'].unique():
        cat1_prices = df[df['Category'] == cat1]['Final_Price(Rs.)']
        for cat2 in df['Category'].unique():
            if cat1 >= cat2:  # Only process each pair once
                continue
            cat2_prices = df[df['Category'] == cat2]['Final_Price(Rs.)']
            
            # Calculate price range overlap
            min_price = max(cat1_prices.min(), cat2_prices.min())
            max_price = min(cat1_prices.max(), cat2_prices.max())
            overlap = max(0, max_price - min_price)
            total_range = max(cat1_prices.max(), cat2_prices.max()) - min(cat1_prices.min(), cat2_prices.min())
            
            if total_range > 0:
                affinity = overlap / total_range
                category_affinity[(cat1, cat2)] = affinity
                category_affinity[(cat2, cat1)] = affinity
    
    # Create baskets based on category affinity and price similarity
    baskets = []
    basket_id = 0
    products = df.to_dict('records')
    
    # Create sorted product pairs by price similarity within affine categories
    for i, product1 in enumerate(products):
        category1 = product1['Category']
        price1 = product1['Final_Price(Rs.)']
        price_range1 = product1['price_range']
        
        # Find complementary products
        candidates = []
        for product2 in products[i+1:]:
            category2 = product2['Category']
            if category2 == category1:
                continue
                
            # Get category affinity
            affinity = category_affinity.get((category1, category2), 0)
            if affinity < 0.2:  # Minimum affinity threshold
                continue
            
            # Calculate price similarity
            price2 = product2['Final_Price(Rs.)']
            price_diff = abs(price1 - price2) / max(price1, 1)
            price_score = 1 - min(price_diff, 1)
            
            # Combined score (weighted average)
            score = (affinity * 0.6) + (price_score * 0.4)
            candidates.append((score, product2))
        
        # Create baskets from top candidates
        if candidates:
            # Sort candidates by score
            candidates.sort(reverse=True, key=lambda x: x[0])
            basket_items = [product1]
            current_categories = {category1}
            
            # Add up to 2 more products with highest scores
            for score, product2 in candidates[:2]:
                if product2['Category'] not in current_categories and score >= 0.5:  # Minimum combined score threshold
                    basket_items.append(product2)
                    current_categories.add(product2['Category'])
            
            # Create basket if we have complementary products
            if len(basket_items) > 1:
                for item in basket_items:
                    baskets.append({
                        'basket_id': f'basket_{basket_id}',
                        'Product_ID': item['Product_ID'],
                        'Category': item['Category'],
                        'Final_Price(Rs.)': item['Final_Price(Rs.)'],
                        'product_group': item['product_group'],
                        'Purchase_Date': item['Purchase_Date']
                    })
                basket_id += 1
    
    if baskets:
        df_baskets = pd.DataFrame(baskets)
        return df_baskets
    else:
        print("\nWarning: Could not create meaningful product relationships")
        return df
    
    if baskets:
        df_baskets = pd.DataFrame(baskets)
        return df_baskets
    else:
        print("\nWarning: Could not create meaningful product relationships")
        return df_sorted

def load_real_data():
    """
    Load and prepare real e-commerce data for analysis
    """
    # Read the dataset
    df = pd.read_csv('/Users/saaralvarunie/Downloads/dwdm/ecommerce_dataset_preprocessed.csv')
    
    # Convert Purchase_Date to datetime
    df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'], format='%d-%m-%Y')
    
    # Preprocess transactions to create baskets
    processed_df = preprocess_transactions(df)
    
    # Calculate customer metrics
    latest_date = df['Purchase_Date'].max()
    customer_metrics = df.groupby('User_ID').agg({
        'Final_Price(Rs.)': ['sum', 'count', 'mean'],
        'Discount (%)': 'mean',
        'Purchase_Date': [
            lambda x: (latest_date - x.max()).days,  # Days since last purchase
            lambda x: (x.max() - x.min()).days + 1   # Activity period in days
        ]
    }).reset_index()
    
    # Flatten column names
    customer_metrics.columns = ['User_ID', 'total_spend', 'purchase_frequency', 'avg_transaction_value',
                              'discount_usage', 'days_since_last_purchase', 'activity_period']
    
    # Normalize frequency to monthly and handle edge cases
    customer_metrics['monthly_frequency'] = customer_metrics['purchase_frequency'].copy()
    mask = customer_metrics['activity_period'] > 0
    customer_metrics.loc[mask, 'monthly_frequency'] = (
        customer_metrics.loc[mask, 'purchase_frequency'] / 
        customer_metrics.loc[mask, 'activity_period'] * 30
    )
    
    # Replace infinite values with NaN and fill with median
    customer_metrics = customer_metrics.replace([np.inf, -np.inf], np.nan)
    numeric_columns = customer_metrics.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        customer_metrics[col] = customer_metrics[col].fillna(customer_metrics[col].median())
    
    return customer_metrics, processed_df

def main():
    # Load real e-commerce data
    customer_metrics, transaction_data = load_real_data()
    
    # Print data summary
    print("\nData Summary:")
    print(f"Total Customers: {len(customer_metrics)}")
    print(f"Total Transactions: {len(transaction_data)}")
    print(f"Unique Products: {transaction_data['Product_ID'].nunique()}")
    print(f"Date Range: {transaction_data['Purchase_Date'].min().strftime('%Y-%m-%d')} to {transaction_data['Purchase_Date'].max().strftime('%Y-%m-%d')}")

    # 1. Customer Segmentation
    segmentation = CustomerSegmentation()
    segment_results = segmentation.segment_customers(customer_metrics)

    print("\nCustomer Segment Analysis:")
    for segment_id, profile in segment_results['profiles'].items():
        print(f"\nSegment {segment_id}: {profile}")  # profile is already the name string
        analysis = segment_results['segment_analysis'][segment_id]
        print(f"Size: {analysis['size']} customers")
        print(f"Average Spend: ₹{analysis['avg_spend']:.2f}")
        print(f"Purchase Frequency: {analysis['avg_frequency']:.1f} times")
        print(f"Average Basket Size: ₹{analysis['avg_basket']:.2f}")
        print(f"Discount Usage: {analysis['avg_discount_usage']*100:.1f}%")

        # Get promotion recommendations
        recommendations = segmentation.recommend_promotions(segment_id)
        print("\nRecommended Promotions:")
        print(f"Discount Range: {recommendations['discount_range']}")
        print(f"Type: {recommendations['promotion_type']}")
        print(f"Frequency: {recommendations['frequency']}")
        print(f"Discount Sensitivity: {recommendations['discount_sensitivity']}%")  # Already formatted in CustomerSegmentation class
    
    # 2. Bundle Recommendations
    # Print product distribution
    print(f"\nProduct Category Distribution:")
    category_counts = transaction_data['Category'].value_counts()
    for category, count in category_counts.items():
        print(f"{category}: {count} products ({count/len(transaction_data)*100:.1f}%)")
    
    # Print price range distribution
    if 'price_range' in transaction_data.columns:
        print(f"\nPrice Range Distribution:")
        price_counts = transaction_data['price_range'].value_counts()
        for price_range, count in price_counts.items():
            print(f"{price_range}: {count} products ({count/len(transaction_data)*100:.1f}%)")
    
    # Prepare basket data for bundle analysis
    if 'basket_id' in transaction_data.columns:
        basket_data = transaction_data[['basket_id', 'Product_ID', 'Category', 'product_group']].copy()
        
        # Count baskets and average size
        unique_baskets = basket_data['basket_id'].nunique()
        avg_basket_size = basket_data.groupby('basket_id').size().mean()
        print(f"\nBasket Analysis:")
        print(f"Total Baskets: {unique_baskets}")
        print(f"Average Basket Size: {avg_basket_size:.2f} items")
        
        bundler = BundleRecommendation()
        transaction_matrix = bundler.prepare_transaction_data(basket_data)
        bundles = bundler.generate_bundle_recommendations(transaction_matrix)
        
        print("\nTop Product Bundle Recommendations:")
        print("==================================")

        if not bundles:
            print("No frequent product bundles found. Try adjusting basket creation parameters.")
        else:
            for i, bundle in enumerate(bundles[:5], 1):
                recommendations = bundler.suggest_bundle_discount(bundle)
                print(f"\nBundle {i}:")
                print(f"Products: {bundle['products']}")
                print(f"Categories: {', '.join(set(bundle['categories']))}")
                print(f"Confidence: {bundle['confidence']*100:.1f}%")
                print(f"Purchase Lift: {bundle['lift']:.2f}x")
                print(f"Support: {bundle['support']*100:.1f}% of transactions")
                print(f"Recommended Discount: {recommendations['discount_percentage']:.1f}%")
                print(f"Bundle Strength: {recommendations['strength_score']:.2f}")
                print(f"Priority: {recommendations['priority']}")
                if recommendations['cross_category']:
                    print("✓ Cross-category bundle")
    else:
        print("\nNo basket data available for bundle analysis")
    
    # 3. Payment Analytics
    original_df = pd.read_csv('/Users/saaralvarunie/Downloads/dwdm/ecommerce_dataset_preprocessed.csv')
    payment_analyzer = PaymentAnalytics()
    payment_insights = payment_analyzer.analyze_payment_preferences(original_df)
    incentives = payment_analyzer.recommend_payment_incentives(payment_insights)
    
    print("\nPayment Method Analysis:")
    print("========================")
    
    # Distribution of payment methods
    print("\nPayment Method Distribution:")
    for method, stats in payment_insights['method_stats'].items():
        print(f"\n{method}:")
        print(f"Transaction Share: {stats['share']*100:.1f}%")
        print(f"Average Transaction Value: ₹{stats['avg_value']:.2f}")
        print(f"Total Volume: ₹{stats['total_volume']:,.2f}")
        
        if 'success_rate' in stats:
            print(f"Success Rate: {stats['success_rate']*100:.1f}%")
        
        print("\nValue Distribution:")
        print(f"Low (<₹0.3): {stats['value_distribution']['low']*100:.1f}%")
        print(f"Medium (₹0.3-₹0.6): {stats['value_distribution']['medium']*100:.1f}%")
        print(f"High (>₹0.6): {stats['value_distribution']['high']*100:.1f}%")
    
    print("\nRecommended Payment Incentives:")
    print("===============================")
    for method, incentive in incentives.items():
        print(f"\n{method}:")
        print(f"Strategy: {incentive['strategy']}")
        print(f"Action: {incentive['action']}")
        print(f"Priority: {incentive['priority']}")
        if 'target_segment' in incentive:
            print(f"Target Segment: {incentive['target_segment']}")
        if 'expected_impact' in incentive:
            print(f"Expected Impact: {incentive['expected_impact']}")

if __name__ == "__main__":
    main()