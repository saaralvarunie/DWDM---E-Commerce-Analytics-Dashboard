import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
from typing import Dict, List, Tuple

class BundleRecommendation:
    def __init__(self):
        self.min_support = 0.00001    # Ultra-low support for initial pattern discovery
        self.min_confidence = 0.001   # Ultra-low confidence for initial pattern discovery
        self.product_categories = {}   # Will be populated from data
        self.max_basket_size = 5      # Maximum number of items to consider in a basket
        
    def prepare_transaction_data(self, transactions: pd.DataFrame) -> pd.DataFrame:
        """
        Convert transaction data into one-hot encoded format and store category information
        """
        # Store category information
        self.product_categories = transactions.groupby('Product_ID')['Category'].first().to_dict()

        # Group transactions and limit basket size
        grouped_transactions = []
        for _, group in transactions.groupby('basket_id'):  # Changed from transaction_id to basket_id
            if len(group) > 1 and len(group) <= self.max_basket_size:
                grouped_transactions.append(group)
        
        if not grouped_transactions:
            print("\nWarning: No multi-product baskets found. Bundle analysis may be limited.")
            return pd.DataFrame()
            
        processed_transactions = pd.concat(grouped_transactions)
        
        # Create transaction matrix
        unique_transactions = (processed_transactions.groupby(['basket_id', 'Product_ID'])  # Changed from transaction_id to basket_id
                            .size()
                            .reset_index())

        # Create a pivot table for product occurrences
        transaction_matrix = pd.pivot_table(
            unique_transactions,
            index='basket_id',  # Changed from transaction_id to basket_id
            columns='Product_ID',
            aggfunc='size',
            fill_value=0
        )

        # Filter out very infrequent products (appear in less than 0.1% of transactions)
        min_occurrences = 1  # At least appear once since we have synthetic baskets
        frequent_products = transaction_matrix.sum() >= min_occurrences
        transaction_matrix = transaction_matrix.loc[:, frequent_products]

        # Convert to boolean (purchased or not)
        return transaction_matrix.astype(bool)
    
    def find_frequent_itemsets(self, transaction_matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Discover frequently co-purchased products using Apriori algorithm
        """
        # Ensure we have some transactions
        if transaction_matrix.empty:
            return pd.DataFrame()
            
        # Adjust min_support based on data sparsity
        n_transactions = len(transaction_matrix)
        adaptive_min_support = max(2 / n_transactions, self.min_support)
        
        # Find frequent itemsets
        try:
            frequent_itemsets = apriori(
                transaction_matrix, 
                min_support=adaptive_min_support,
                use_colnames=True,
                max_len=3  # Limit to bundles of 3 items or less
            )
            
            # If no itemsets found, try with lower support
            if len(frequent_itemsets) == 0:
                adaptive_min_support = adaptive_min_support / 2
                frequent_itemsets = apriori(
                    transaction_matrix, 
                    min_support=adaptive_min_support,
                    use_colnames=True,
                    max_len=2  # Reduce to pairs only with lower support
                )
            
            return frequent_itemsets
            
        except Exception as e:
            print(f"Warning: Error in finding frequent itemsets: {str(e)}")
            return pd.DataFrame()
    
    def get_product_category(self, product_id: int) -> str:
        """
        Get the category of a product based on its ID
        """
        return self.product_categories.get(product_id, "Other")

    def generate_bundle_recommendations(self, transaction_matrix: pd.DataFrame) -> List[Dict]:
        """
        Generate product bundle recommendations based on association rules
        """
        frequent_itemsets = self.find_frequent_itemsets(transaction_matrix)
        
        # Check if we have any frequent itemsets
        if frequent_itemsets.empty or len(frequent_itemsets) < 2:
            print("Warning: Not enough frequent itemsets found to generate bundles.")
            return []
        
        try:
            rules = association_rules(frequent_itemsets, 
                                    metric="confidence",
                                    min_threshold=self.min_confidence)
            
            # Check if any rules were generated
            if rules.empty:
                print("Warning: No association rules generated from itemsets.")
                return []
            
            # Sort rules by lift ratio
            rules = rules.sort_values(['lift', 'confidence'], ascending=[False, False])
            
            bundles = []
            for _, rule in rules.iterrows():
                products = list(rule['antecedents']) + list(rule['consequents'])
                categories = [self.get_product_category(p) for p in products]
                
                bundle = {
                    'products': products,
                    'categories': categories,
                    'confidence': rule['confidence'],
                    'lift': rule['lift'],
                    'support': rule['support'],
                    'cross_category': len(set(categories)) > 1
                }
                bundles.append(bundle)
            
            return bundles
        except Exception as e:
            print(f"Warning: Error generating bundle recommendations: {str(e)}")
            return []
    
    def suggest_bundle_discount(self, bundle: Dict) -> Dict:
        """
        Calculate suggested discount and provide detailed recommendations for a bundle
        """
        base_discount = 0.05  # 5% base discount
        
        # Calculate bundle strength score
        strength_score = (bundle['lift'] * 0.4 + bundle['confidence'] * 0.4 + bundle['support'] * 0.2)
        cross_category_bonus = 0.02 if bundle['cross_category'] else 0
        
        # Adjust discount based on metrics
        if strength_score > 0.8:
            discount = 0.15 + cross_category_bonus  # Up to 17% for strong cross-category bundles
            message = "Premium bundle with very high purchase likelihood"
            priority = "High"
        elif strength_score > 0.6:
            discount = 0.10 + cross_category_bonus  # Up to 12% for moderate cross-category bundles
            message = "Popular complementary products"
            priority = "Medium"
        else:
            discount = base_discount + cross_category_bonus  # Up to 7% for basic cross-category bundles
            message = "Basic bundle offer"
            priority = "Low"
        
        return {
            'discount_percentage': discount * 100,
            'message': message,
            'priority': priority,
            'strength_score': strength_score,
            'cross_category': bundle['cross_category'],
            'categories': bundle['categories'],
            'estimated_lift': bundle['lift']
        }