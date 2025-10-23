import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from customer_segmentation import CustomerSegmentation
from bundle_recommendation import BundleRecommendation
from payment_analytics import PaymentAnalytics

# Set page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# Custom CSS for neon theme
st.markdown("""
<style>
    /* Dark theme with neon accents */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Neon headers */
    h1, h2, h3 {
        color: #00FF88;
        text-shadow: 0 0 10px rgba(0,255,136,0.5);
    }
    
    /* Neon metric cards */
    div[data-testid="stMetricValue"] {
        color: #00FFFF;
        text-shadow: 0 0 10px rgba(0,255,255,0.5);
    }
    
    /* Button styling */
    .stButton button {
        background-color: #1E1E1E;
        color: #00FF88;
        border: 2px solid #00FF88;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,255,136,0.3);
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #00FF88;
        color: #1E1E1E;
        box-shadow: 0 0 20px rgba(0,255,136,0.6);
    }
    
    /* Menu styling */
    .stSelectbox {
        background-color: #1E1E1E;
        color: #00FFFF;
    }
    
    /* Plot background */
    .js-plotly-plot {
        background-color: #1E1E1E;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('/Users/saaralvarunie/Downloads/dwdm/ecommerce_dataset_preprocessed.csv')
    df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'], format='%d-%m-%Y')
    return df

# Initialize analytics classes
@st.cache_resource
def init_analytics():
    return {
        'segmentation': CustomerSegmentation(),
        'bundle': BundleRecommendation(),
        'payment': PaymentAnalytics()
    }

# Load data and initialize analytics
df = load_data()
analytics = init_analytics()

# Navigation
selected = option_menu(
    menu_title=None,
    options=["Overview", "Customer Segments", "Bundle Analysis", "Payment Analytics"],
    icons=["house", "people-fill", "box-seam", "credit-card"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#1E1E1E"},
        "icon": {"color": "#00FF88", "font-size": "25px"}, 
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin":"0px",
            "--hover-color": "#2D3250",
        },
        "nav-link-selected": {"background-color": "#2D3250"},
    }
)

if selected == "Overview":
    st.title("E-commerce Analytics Dashboard")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", len(df['User_ID'].unique()))
    with col2:
        st.metric("Total Transactions", len(df))
    with col3:
        st.metric("Total Products", len(df['Product_ID'].unique()))
    with col4:
        st.metric("Avg. Transaction Value", f"₹{df['Final_Price(Rs.)'].mean():.2f}")
    
    # Data Preview
    st.subheader("Recent Transactions")
    st.dataframe(df.head(10), use_container_width=True)
    
    # Category Distribution
    st.subheader("Product Category Distribution")
    fig = px.pie(df['Category'].value_counts().reset_index(), 
                 values='count', names='Category',
                 template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    # Transaction Trends
    st.subheader("Daily Transaction Trends")
    daily_trends = df.groupby('Purchase_Date')['Final_Price(Rs.)'].agg(['count', 'sum']).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_trends['Purchase_Date'], 
                            y=daily_trends['count'],
                            name='Number of Transactions'))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Customer Segments":
    st.title("Customer Segmentation Analysis")
    
    # Process data for segmentation
    with st.spinner("Analyzing customer segments..."):
        customer_metrics = df.groupby('User_ID').agg({
            'Final_Price(Rs.)': ['sum', 'count', 'mean'],
            'Discount (%)': 'mean'
        }).reset_index()
        customer_metrics.columns = ['User_ID', 'total_spend', 'purchase_frequency', 
                                  'avg_transaction_value', 'discount_usage']
        
        segment_results = analytics['segmentation'].segment_customers(customer_metrics)
    
    # Display segments
    for segment_id, profile in segment_results['profiles'].items():
        st.subheader(f"Segment {segment_id}: {profile}")
        col1, col2, col3 = st.columns(3)
        
        analysis = segment_results['segment_analysis'][segment_id]
        with col1:
            st.metric("Size", f"{analysis['size']} customers")
        with col2:
            st.metric("Average Spend", f"₹{analysis['avg_spend']:.2f}")
        with col3:
            st.metric("Discount Usage", f"{analysis['avg_discount_usage']*100:.1f}%")
        
        # Promotion recommendations
        st.markdown("### Recommended Promotions")
        recommendations = analytics['segmentation'].recommend_promotions(segment_id)
        st.info(f"""
        - Discount Range: {recommendations['discount_range']}
        - Type: {recommendations['promotion_type']}
        - Frequency: {recommendations['frequency']}
        - Sensitivity: {recommendations['discount_sensitivity']}%
        """)

elif selected == "Bundle Analysis":
    st.title("Product Bundle Analysis")
    
    # Process data for bundle analysis
    with st.spinner("Analyzing product bundles..."):
        processed_df = analytics['bundle'].prepare_transaction_data(df)
        bundles = analytics['bundle'].generate_bundle_recommendations(processed_df)
    
    if bundles:
        # Display top bundles
        for i, bundle in enumerate(bundles[:5], 1):
            st.subheader(f"Bundle {i}")
            recommendations = analytics['bundle'].suggest_bundle_discount(bundle)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Confidence", f"{bundle['confidence']*100:.1f}%")
            with col2:
                st.metric("Purchase Lift", f"{bundle['lift']:.2f}x")
            with col3:
                st.metric("Recommended Discount", f"{recommendations['discount_percentage']:.1f}%")
            
            st.markdown(f"""
            - **Categories**: {', '.join(set(bundle['categories']))}
            - **Bundle Strength**: {recommendations['strength_score']:.2f}
            - **Priority**: {recommendations['priority']}
            """)
            
            if recommendations['cross_category']:
                st.success("✓ Cross-category bundle")
    else:
        st.warning("No significant bundle patterns found in the data.")

elif selected == "Payment Analytics":
    st.title("Payment Method Analytics")
    
    # Process payment data
    with st.spinner("Analyzing payment patterns..."):
        payment_insights = analytics['payment'].analyze_payment_preferences(df)
        incentives = analytics['payment'].recommend_payment_incentives(payment_insights)
    
    # Payment method distribution
    st.subheader("Payment Method Distribution")
    method_stats = payment_insights['method_stats']
    
    # Create distribution chart
    shares = {method: stats['share'] for method, stats in method_stats.items()}
    fig = px.pie(values=shares.values(), names=shares.keys(),
                 title="Transaction Share by Payment Method",
                 template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed metrics for each payment method
    st.subheader("Payment Method Performance")
    for method, stats in method_stats.items():
        with st.expander(f"{method} Analytics"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Transaction Share", f"{stats['share']*100:.1f}%")
            with col2:
                st.metric("Average Value", f"₹{stats['avg_value']:.2f}")
            with col3:
                st.metric("Total Volume", f"₹{stats['total_volume']:.2f}")
            
            # Value distribution chart
            value_dist = stats['value_distribution']
            fig = px.bar(
                x=['Low', 'Medium', 'High'],
                y=[value_dist['low']*100, value_dist['medium']*100, value_dist['high']*100],
                title=f"Transaction Value Distribution for {method}",
                labels={'x': 'Value Range', 'y': 'Percentage'},
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Payment incentive recommendations
    st.subheader("Recommended Payment Incentives")
    for method, incentive in incentives.items():
        with st.expander(f"{method} Recommendations"):
            st.markdown(f"""
            - **Strategy**: {incentive['strategy']}
            - **Action**: {incentive['action']}
            - **Priority**: {incentive['priority']}
            - **Target Segment**: {incentive['target_segment']}
            - **Expected Impact**: {incentive['expected_impact']}
            """)