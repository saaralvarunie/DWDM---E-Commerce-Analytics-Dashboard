# Data Warehouse Analytics for Customer Segmentation

This project implements a data warehouse analytics system for analyzing customer shopping behavior, focusing on three main components:

1. Customer Segmentation
2. Product Bundle Recommendations
3. Payment Method Analytics

## Features

### Customer Segmentation
- Classifies customers into distinct segments based on shopping behavior
- Uses KMeans clustering algorithm
- Segments: Deal Hunters, Loyal Customers, Occasional Buyers, Premium Buyers
- Provides targeted promotion recommendations for each segment

### Bundle Recommendations
- Discovers frequently co-purchased products using Apriori algorithm
- Generates product bundle recommendations with confidence scores
- Suggests optimal discounts based on association strength
- Helps create targeted bundle offers

### Payment Analytics
- Analyzes payment method preferences and patterns
- Tracks conversion rates and transaction values
- Provides time-based usage analysis
- Recommends payment incentives based on performance metrics

## Requirements

```bash
pip install pandas numpy scikit-learn mlxtend
```

## Project Structure

```
dwdm/
├── src/
│   ├── customer_segmentation.py
│   ├── bundle_recommendation.py
│   ├── payment_analytics.py
│   └── main.py
└── data/
```

## Usage

1. Ensure all dependencies are installed
2. Run the main analysis:

```bash
python src/main.py
```

## Data Requirements

The system expects transaction data with the following fields:
- customer_id
- total_spend
- purchase_frequency
- avg_basket_size
- discount_usage
- days_since_last_purchase
- payment_method
- status

For production use, replace the sample data in `main.py` with actual data warehouse connection.