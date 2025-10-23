import pandas as pd

# Read the dataset
df = pd.read_csv('/Users/saaralvarunie/Downloads/dwdm/ecommerce_dataset_preprocessed.csv')
df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'], format='%d-%m-%Y')

# Get transactions per user
transactions_per_user = df.groupby('User_ID').size()

print("\nTransactions per user:")
print("Mean:", transactions_per_user.mean())
print("Min:", transactions_per_user.min())
print("Max:", transactions_per_user.max())

# Check for users with multiple purchases on same day
df['date_only'] = df['Purchase_Date'].dt.date
multi_purchases = df.groupby(['User_ID', 'date_only']).size()
print("\nUsers with multiple purchases on same day:", (multi_purchases > 1).sum())

# Print sample of users with most transactions
print("\nTop 5 users by number of transactions:")
print(transactions_per_user.sort_values(ascending=False).head())