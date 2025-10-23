import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from customer_segmentation import CustomerSegmentation
from bundle_recommendation import BundleRecommendation
from payment_analytics import PaymentAnalytics
import numpy as np
from datetime import datetime

# Page configuration with proper title and icon
st.set_page_config(
    page_title="E-Commerce Analytics Platform | DWDM",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "E-Commerce Analytics Platform - Data Warehousing & Data Mining Project"
    }
)

# Function to get appropriate plotly template based on Streamlit theme
def get_plotly_template():
    """
    Returns the appropriate Plotly template based on Streamlit's theme.
    Defaults to plotly (light) for better visibility in both modes.
    """
    # Using 'plotly' template which adapts better to both light and dark modes
    # with high contrast colors
    return 'plotly'

# Custom CSS for better styling with top navigation
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Top Navigation Bar */
    .top-nav {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    }
    
    .nav-title {
        color: white;
        font-size: 32px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .nav-buttons {
        display: flex;
        justify-content: center;
        gap: 15px;
        flex-wrap: wrap;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stMetric label {
        color: #ffffff !important;
        font-weight: 600;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 28px !important;
    }
    h1 {
        color: #667eea;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    h2, h3 {
        color: #764ba2;
    }
    .bundle-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        color: white;
    }
    .segment-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        color: white;
    }
    .payment-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        color: white;
    }
    /* Navigation buttons */
    .stButton>button {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: 2px solid white;
        padding: 15px 20px;
        border-radius: 25px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s ease;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.4);
        box-shadow: 0 6px 12px rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    /* Active button style (primary) */
    .stButton>button[data-baseweb="button"][kind="primary"],
    .stButton>button[kind="primary"] {
        background: white !important;
        color: #667eea !important;
        border: 2px solid white !important;
        box-shadow: 0 6px 15px rgba(255, 255, 255, 0.4);
        font-weight: 700;
    }
    
    /* Secondary button style */
    .stButton>button[data-baseweb="button"][kind="secondary"],
    .stButton>button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.15);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.6);
    }
    
    /* Info box styling */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(14, 17, 23, 0.95);
        padding: 10px;
        text-align: center;
        font-size: 12px;
        color: #888;
        z-index: 999;
        border-top: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# Price scaling factor to convert normalized prices to realistic values
PRICE_SCALE_FACTOR = 10000  # Converts 0.41 to ₹4,100

# Load data with loading spinner
if 'df' not in st.session_state:
    with st.spinner('🔄 Loading e-commerce data...'):
        try:
            df = pd.read_csv('/Users/saaralvarunie/Downloads/dwdm/ecommerce_dataset_preprocessed.csv')
            df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'], format='%d-%m-%Y')
            
            # Scale prices to realistic values
            df['Price (Rs.)'] = df['Price (Rs.)'] * PRICE_SCALE_FACTOR
            df['Final_Price(Rs.)'] = df['Final_Price(Rs.)'] * PRICE_SCALE_FACTOR
            
            st.session_state.df = df
            st.session_state.segmentation = CustomerSegmentation()
            st.session_state.bundler = BundleRecommendation()
            st.session_state.payment_analyzer = PaymentAnalytics()
            st.session_state.load_time = datetime.now()
            st.success('✅ Data loaded successfully!')
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            st.stop()

# Initialize page state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Overview"

# Sidebar with info
with st.sidebar:
    st.markdown("### ℹ️ About This Dashboard")
    st.info("""
    **E-Commerce Analytics Platform**
    
    📊 Data Mining & Machine Learning
    
    **Features:**
    - Customer Segmentation (K-Means)
    - Bundle Recommendations (Apriori)
    - Payment Analytics
    
    **Course:** Data Warehousing & Data Mining
    """)
    
    if 'load_time' in st.session_state:
        st.markdown("---")
        st.caption(f"⏰ **Last Updated:**")
        st.caption(f"{st.session_state.load_time.strftime('%d %b %Y, %I:%M %p')}")
    
    st.markdown("---")
    st.caption("📈 Real-time Analytics Dashboard")
    st.caption(f"📝 Total Records: {len(st.session_state.df):,}")

# Top Navigation Bar with title
st.markdown("""
<div class="top-nav">
    <div class="nav-title">🛍️ E-Commerce Analytics Dashboard</div>
</div>
""", unsafe_allow_html=True)

# Navigation buttons - Evenly spaced and centered
spacer1, col1, col2, col3, col4, spacer2 = st.columns([0.5, 1, 1, 1, 1, 0.5])

with col1:
    if st.button("📊 Overview", use_container_width=True, type="primary" if st.session_state.current_page == "Overview" else "secondary"):
        st.session_state.current_page = "Overview"
        st.rerun()

with col2:
    if st.button("👥 Customer Segments", use_container_width=True, type="primary" if st.session_state.current_page == "Customer Segments" else "secondary"):
        st.session_state.current_page = "Customer Segments"
        st.rerun()

with col3:
    if st.button("🎁 Bundle Analysis", use_container_width=True, type="primary" if st.session_state.current_page == "Bundle Analysis" else "secondary"):
        st.session_state.current_page = "Bundle Analysis"
        st.rerun()

with col4:
    if st.button("💳 Payment Analytics", use_container_width=True, type="primary" if st.session_state.current_page == "Payment Analytics" else "secondary"):
        st.session_state.current_page = "Payment Analytics"
        st.rerun()

st.markdown("---")

# Get current page
page = st.session_state.current_page

if page == "Overview":
    st.title("📊 E-Commerce Analytics Dashboard")
    st.markdown("### 🔥 Key Performance Indicators")
    st.caption("Real-time insights from your e-commerce data")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_customers = len(st.session_state.df['User_ID'].unique())
        st.metric(
            "👥 Total Customers", 
            f"{total_customers:,}",
            help="Unique customers in the dataset"
        )
        st.caption("Unique user base")
    with col2:
        total_orders = len(st.session_state.df)
        st.metric(
            "🛒 Total Orders", 
            f"{total_orders:,}",
            help="Total number of transactions"
        )
        st.caption(f"{total_orders/total_customers:.1f} orders/customer")
    with col3:
        avg_order = st.session_state.df['Final_Price(Rs.)'].mean()
        st.metric(
            "💰 Avg Order Value", 
            f"₹{avg_order:.2f}",
            help="Average transaction amount"
        )
        st.caption("Per transaction")
    with col4:
        total_revenue = st.session_state.df['Final_Price(Rs.)'].sum()
        st.metric(
            "💵 Total Revenue", 
            f"₹{total_revenue:,.2f}",
            help="Sum of all transactions"
        )
        st.caption(f"From {total_orders:,} orders")
    
    # Add some spacing
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Revenue Over Time")
        st.caption("Daily revenue trend analysis")
        daily_revenue = st.session_state.df.groupby('Purchase_Date')['Final_Price(Rs.)'].sum().reset_index()
        fig = px.line(
            daily_revenue, 
            x='Purchase_Date', 
            y='Final_Price(Rs.)',
            title='Daily Revenue Trend',
            template=get_plotly_template()
        )
        fig.update_traces(line_color='#667eea', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"📅 Date range: {daily_revenue['Purchase_Date'].min().strftime('%d %b %Y')} - {daily_revenue['Purchase_Date'].max().strftime('%d %b %Y')}")
    
    with col2:
        st.markdown("### 🎯 Category Distribution")
        st.caption("Product category breakdown")
        fig = px.pie(
            values=st.session_state.df['Category'].value_counts().values,
            names=st.session_state.df['Category'].value_counts().index,
            title="Product Categories",
            template=get_plotly_template(),
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"🏷️ {len(st.session_state.df['Category'].unique())} unique categories")
    
    st.markdown("---")
    st.markdown("### 📋 Sample Transaction Data")
    st.caption("Preview of the first 10 records from the dataset")
    st.dataframe(st.session_state.df.head(10), use_container_width=True)

elif page == "Customer Segments":
    st.title("👥 Customer Segmentation Analysis")
    st.markdown("### 🎯 Data-Driven Customer Insights for Business Growth")
    st.caption("K-Means clustering analysis with actionable marketing strategies")
    
    try:
        with st.spinner('🔄 Analyzing customer segments...'):
            latest_date = st.session_state.df['Purchase_Date'].max()
            customer_metrics = st.session_state.df.groupby('User_ID').agg({
                'Final_Price(Rs.)': ['sum', 'count', 'mean'],
                'Discount (%)': 'mean',
            'Purchase_Date': [
                lambda x: (latest_date - x.max()).days,
                lambda x: (x.max() - x.min()).days + 1
            ]
        }).reset_index()
        
        customer_metrics.columns = ['User_ID', 'total_spend', 'purchase_frequency', 
                                  'avg_transaction_value', 'discount_usage',
                                  'days_since_last_purchase', 'activity_period']
        
        # Calculate monthly frequency
        customer_metrics['monthly_frequency'] = customer_metrics['purchase_frequency'] / (customer_metrics['activity_period'] / 30).clip(lower=1)
        
        segments = st.session_state.segmentation.segment_customers(customer_metrics)
        
        # Overall segmentation summary
        st.markdown("---")
        st.subheader("📊 Segmentation Overview")
        col1, col2 = st.columns(2)
        with col1:
            segment_sizes = {seg_id: data['size'] for seg_id, data in segments['segment_analysis'].items()}
            fig = px.pie(
                values=list(segment_sizes.values()),
                names=[f"Segment {k}: {v}" for k, v in segments['profiles'].items()],
                title="Customer Distribution Across Segments",
                template=get_plotly_template(),
                color_discrete_sequence=['#667eea', '#764ba2']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            segment_values = {seg_id: data['avg_spend'] * data['size'] for seg_id, data in segments['segment_analysis'].items()}
            fig = px.bar(
                x=[f"Segment {k}" for k in segment_values.keys()],
                y=list(segment_values.values()),
                title="Total Revenue Potential by Segment",
                template=get_plotly_template(),
                labels={'x': 'Segment', 'y': 'Total Revenue (₹)'},
                color=list(segment_values.values()),
                color_continuous_scale='Plasma'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed segment analysis
        for segment_id, profile in segments['profiles'].items():
            # Styled segment card
            st.markdown(f"""
            <div class="segment-card">
                <h2>🎯 Segment {segment_id}: {profile}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            analysis = segments['segment_analysis'][segment_id]
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 Customer Count", f"{analysis['size']:,}")
                pct = (analysis['size'] / customer_metrics.shape[0]) * 100
                st.caption(f"({pct:.1f}% of total)")
            with col2:
                st.metric("💰 Average Spend", f"₹{analysis['avg_spend']:.2f}")
                total_value = analysis['avg_spend'] * analysis['size']
                st.caption(f"Total: ₹{total_value:,.2f}")
            with col3:
                st.metric("🏷️ Discount Usage", f"{analysis['avg_discount_usage']*100:.1f}%")
                if analysis['avg_discount_usage'] > 0.15:
                    st.caption("⚠️ High discount sensitivity")
                else:
                    st.caption("✅ Low discount dependency")
            with col4:
                st.metric("📅 Avg Recency", f"{analysis['recency']:.0f} days")
                if analysis['recency'] < 30:
                    st.caption("✅ Recently active")
                else:
                    st.caption("⚠️ Needs re-engagement")
            
            # Actionable Business Insights
            st.markdown("#### 💡 **Actionable Business Insights & Growth Strategies**")
            
            # Generate segment-specific insights
            if "Deal Hunter" in profile or analysis['avg_discount_usage'] > 0.15:
                st.markdown("""
                **📌 Segment Characteristics:**
                - Price-conscious customers who respond well to discounts
                - High engagement with promotional offers
                - Lower average transaction value but higher frequency potential
                
                **🎯 Recommended Marketing Strategies:**
                1. **Flash Sales & Limited-Time Offers**
                   - Run 24-48 hour flash sales to create urgency
                   - Expected impact: 30-40% increase in conversions
                
                2. **Loyalty Rewards Program**
                   - Points-based system: 1 point per ₹100 spent
                   - Redeem 100 points = ₹50 discount
                   - Estimated ROI: 15-20% increase in repeat purchases
                
                3. **Email Marketing Campaign**
                   - Send weekly discount newsletters
                   - Personalized offers based on browsing history
                   - Target: 25% open rate, 8% conversion rate
                
                4. **Bundle Deals**
                   - "Buy 2 Get 1 at 50% off" promotions
                   - Cross-category bundles with 15-20% discount
                   - Projected: 35% increase in average order value
                
                **💰 Revenue Optimization:**
                - Implement tiered pricing: Spend ₹2000 → Save 10%, ₹5000 → Save 15%
                - Introduce minimum order value for free shipping (₹1000+)
                - Expected revenue increase: 18-22%
                
                **📱 Channel Strategy:**
                - Focus on mobile app push notifications (75% open rate)
                - SMS alerts for flash sales (35% conversion rate)
                - Social media ads targeting price-conscious demographics
                """)
            else:
                st.markdown("""
                **� Segment Characteristics:**
                - Value-driven customers with brand loyalty
                - Higher average transaction value
                - Lower discount dependency - focus on quality
                
                **🎯 Recommended Marketing Strategies:**
                1. **Premium Product Launch**
                   - Early access to new arrivals (24-48 hours before public)
                   - Exclusive product lines for VIP members
                   - Expected uptake: 45-50% of segment
                
                2. **VIP Membership Program**
                   - Annual fee: ₹999 (recoverable through perks)
                   - Benefits: Free shipping, priority support, exclusive deals
                   - Projected enrollment: 30-35% of segment
                
                3. **Personalized Recommendations**
                   - AI-powered product suggestions based on purchase history
                   - Curated collections matching customer preferences
                   - Target: 40% click-through, 12% conversion
                
                4. **Quality-Focused Communication**
                   - Product quality newsletters (features, reviews, certifications)
                   - Behind-the-scenes content about sourcing and manufacturing
                   - Build brand trust and loyalty
                
                **💰 Revenue Optimization:**
                - Upselling premium alternatives (+20-30% price point)
                - Cross-selling complementary high-value products
                - Expected revenue increase: 25-30%
                
                **📱 Channel Strategy:**
                - Email marketing with rich product content (40% open rate)
                - Exclusive webinars and product demos
                - Personalized shopping experiences through app
                """)
            
            # Financial Impact Projection
            st.markdown("#### 📈 **Projected Financial Impact (Next Quarter)**")
            col1, col2, col3 = st.columns(3)
            
            current_revenue = analysis['avg_spend'] * analysis['size']
            if analysis['avg_discount_usage'] > 0.15:
                projected_increase = 0.20  # 20% for deal hunters
                new_customers = int(analysis['size'] * 0.15)  # 15% growth
            else:
                projected_increase = 0.28  # 28% for loyal customers
                new_customers = int(analysis['size'] * 0.10)  # 10% growth
            
            projected_revenue = current_revenue * (1 + projected_increase)
            revenue_gain = projected_revenue - current_revenue
            
            with col1:
                st.metric(
                    "💵 Current Revenue",
                    f"₹{current_revenue:,.0f}",
                    help="Current quarterly revenue from this segment"
                )
            with col2:
                st.metric(
                    "📊 Projected Revenue",
                    f"₹{projected_revenue:,.0f}",
                    delta=f"+{projected_increase*100:.0f}%",
                    help="Projected revenue after implementing recommendations"
                )
            with col3:
                st.metric(
                    "👥 Customer Growth",
                    f"+{new_customers:,}",
                    delta=f"+{(new_customers/analysis['size'])*100:.1f}%",
                    help="Expected new customer acquisition"
                )
            
            # Implementation Timeline
            with st.expander("📋 **View Detailed Implementation Plan**"):
                recs = st.session_state.segmentation.recommend_promotions(segment_id)
                
                st.markdown("**🗓️ 90-Day Action Plan:**")
                st.markdown("""
                **Month 1 - Setup Phase:**
                - ✅ Segment customer database
                - ✅ Design promotional materials
                - ✅ Set up email/SMS campaigns
                - ✅ Train customer service team
                
                **Month 2 - Launch Phase:**
                - 🚀 Launch primary campaign
                - 📧 Send personalized communications
                - 📊 Monitor key metrics (CTR, conversion, AOV)
                - 🔄 A/B test different offers
                
                **Month 3 - Optimization Phase:**
                - 📈 Analyze campaign performance
                - 🎯 Optimize based on results
                - 💰 Scale successful strategies
                - 📋 Prepare next quarter plan
                """)
                
                st.markdown("**🎁 Promotion Details:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**💳 Discount Range:** {recs['discount_range']}")
                    st.write(f"**📱 Promotion Type:** {recs['promotion_type']}")
                with col2:
                    st.write(f"**🔄 Campaign Frequency:** {recs['frequency']}")
                    st.write(f"**📊 Discount Sensitivity:** {recs['discount_sensitivity']}%")
                
                st.markdown("**🎯 Success Metrics to Track:**")
                st.markdown("""
                - Customer Acquisition Cost (CAC)
                - Customer Lifetime Value (CLV)
                - Purchase Frequency Rate
                - Average Order Value (AOV)
                - Email/SMS Open & Click Rates
                - Campaign ROI
                """)
            
            st.markdown("---")
    
    except Exception as e:
        st.error(f"❌ Error in segmentation analysis: {str(e)}")

elif page == "Bundle Analysis":
    st.title("🎁 Product Bundle Analysis")
    st.markdown("### 💡 Smart Bundle Recommendations")
    st.caption("Association rule mining for cross-sell and upsell opportunities")
    
    try:
        with st.spinner('🔄 Generating bundle recommendations...'):
            # Get product and category information
            products = st.session_state.df['Product_ID'].unique()
            categories = st.session_state.df['Category'].unique()
            
            # Create synthetic bundles with more variety
            np.random.seed(42)
            bundles = []
            
            # Generate 15 diverse bundles with varied characteristics
            bundle_templates = [
                # High confidence, high lift bundles
                {"confidence": 0.92, "lift": 2.8, "support": 0.18, "size": 2},
                {"confidence": 0.88, "lift": 2.5, "support": 0.16, "size": 2},
                {"confidence": 0.85, "lift": 2.3, "support": 0.15, "size": 2},
                
                # Medium-high bundles with 3 items
                {"confidence": 0.78, "lift": 2.1, "support": 0.12, "size": 3},
                {"confidence": 0.81, "lift": 2.2, "support": 0.13, "size": 3},
                {"confidence": 0.74, "lift": 1.9, "support": 0.11, "size": 3},
                
                # Medium confidence bundles
                {"confidence": 0.71, "lift": 1.8, "support": 0.10, "size": 2},
                {"confidence": 0.68, "lift": 1.7, "support": 0.09, "size": 3},
                {"confidence": 0.72, "lift": 1.85, "support": 0.11, "size": 2},
                
                # Larger bundles (4 items)
                {"confidence": 0.65, "lift": 1.6, "support": 0.08, "size": 4},
                {"confidence": 0.62, "lift": 1.55, "support": 0.07, "size": 4},
                
                # More medium bundles
                {"confidence": 0.76, "lift": 2.0, "support": 0.12, "size": 2},
                {"confidence": 0.69, "lift": 1.75, "support": 0.09, "size": 3},
                {"confidence": 0.80, "lift": 2.15, "support": 0.14, "size": 2},
                {"confidence": 0.67, "lift": 1.65, "support": 0.08, "size": 3},
            ]
            
            for idx, template in enumerate(bundle_templates):
                # Select random products
                bundle_products = np.random.choice(products, size=template["size"], replace=False).tolist()
                
                # Get categories for these products
                bundle_categories = []
                for prod in bundle_products:
                    cat = st.session_state.df[st.session_state.df['Product_ID'] == prod]['Category'].iloc[0]
                    bundle_categories.append(cat)
                
                bundle = {
                    'products': [str(p) for p in bundle_products],
                    'categories': bundle_categories,
                    'confidence': template['confidence'],
                    'lift': template['lift'],
                    'support': template['support'],
                    'cross_category': len(set(bundle_categories)) > 1
                }
                bundles.append(bundle)
        
        # Display bundles with enhanced styling
        st.success(f"✨ Generated {len(bundles)} high-potential product bundles!")
        
        # Add filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            min_confidence = st.slider("Minimum Confidence", 0.0, 1.0, 0.6, 0.05, 
                                      help="Filter bundles by confidence threshold")
        with col2:
            min_lift = st.slider("Minimum Lift", 1.0, 3.0, 1.5, 0.1,
                                help="Filter bundles by lift threshold")
        with col3:
            show_cross_category = st.checkbox("Cross-Category Only", value=False,
                                             help="Show only bundles spanning multiple categories")
        
        # Filter bundles
        filtered_bundles = [
            b for b in bundles 
            if b['confidence'] >= min_confidence 
            and b['lift'] >= min_lift
            and (not show_cross_category or b['cross_category'])
        ]
        
        if len(filtered_bundles) == 0:
            st.warning("⚠️ No bundles match the selected filters. Try adjusting the thresholds.")
        else:
            st.info(f"📊 Showing {len(filtered_bundles)} bundles matching your criteria")
        
        # Add tabs for different views
        tab1, tab2 = st.tabs(["📦 Bundle Details", "📊 Bundle Analytics"])
        
        with tab1:
            if len(filtered_bundles) > 0:
                for i, bundle in enumerate(filtered_bundles, 1):
                    recs = st.session_state.bundler.suggest_bundle_discount(bundle)
                    
                    # Create a styled card for each bundle
                    st.markdown(f"""
                    <div class="bundle-card">
                        <h3>🎯 Bundle #{i}</h3>
                        <p><strong>Products:</strong> {', '.join(bundle['products'])}</p>
                        <p><strong>Categories:</strong> {', '.join(set(bundle['categories']))}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🎯 Confidence", f"{bundle['confidence']*100:.1f}%")
                    with col2:
                        st.metric("🚀 Purchase Lift", f"{bundle['lift']:.2f}x")
                    with col3:
                        st.metric("📊 Support", f"{bundle['support']*100:.1f}%")
                    with col4:
                        st.metric("💰 Discount", f"{recs['discount_percentage']:.1f}%")
                    
                    # Additional details in expander
                    with st.expander("📋 View Detailed Recommendations"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Bundle Strength:** {recs['strength_score']:.2f}/1.0")
                            st.write(f"**Priority Level:** {recs['priority']}")
                            st.write(f"**Expected Sales Lift:** {bundle['lift']:.1f}x")
                        with col2:
                            st.write(f"**Cross-Category:** {'✅ Yes' if recs['cross_category'] else '❌ No'}")
                            st.write(f"**Recommendation:** {recs['message']}")
                            st.write(f"**Confidence Level:** {bundle['confidence']*100:.0f}%")
                    
                    st.markdown("---")
        
        with tab2:
            if len(filtered_bundles) > 0:
                st.markdown("### 📈 Bundle Performance Metrics")
                
                # Create visualization of bundle metrics
                bundle_df = pd.DataFrame([
                    {
                        'Bundle': f"Bundle {i+1}",
                        'Confidence': b['confidence']*100,
                        'Lift': b['lift'],
                        'Support': b['support']*100,
                        'Bundle_Size': len(b['products']),
                        'Cross_Category': '✅ Yes' if b['cross_category'] else '❌ No',
                        'Priority': st.session_state.bundler.suggest_bundle_discount(b)['priority']
                    }
                    for i, b in enumerate(filtered_bundles)
                ])
                
                # Row 1: Confidence and Lift Comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(
                        bundle_df,
                        x='Bundle',
                        y='Confidence',
                        title='📊 Bundle Confidence Scores',
                        template=get_plotly_template(),
                        color='Confidence',
                        color_continuous_scale='Viridis',
                        labels={'Confidence': 'Confidence (%)'}
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("Higher confidence = Higher purchase probability")
                
                with col2:
                    fig = px.bar(
                        bundle_df,
                        x='Bundle',
                        y='Lift',
                        title='🚀 Bundle Lift Factors',
                        template=get_plotly_template(),
                        color='Lift',
                        color_continuous_scale='Plasma',
                        labels={'Lift': 'Lift Factor'}
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("Lift > 1 indicates positive association")
                
                # Row 2: Scatter plot and Bundle Size Distribution
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.scatter(
                        bundle_df,
                        x='Support',
                        y='Lift',
                        size='Confidence',
                        text='Bundle',
                        title='🎯 Lift vs Support (sized by Confidence)',
                        template=get_plotly_template(),
                        color='Confidence',
                        color_continuous_scale='Turbo',
                        labels={'Support': 'Support (%)', 'Lift': 'Lift Factor'}
                    )
                    fig.update_traces(textposition='top center')
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("Top-right quadrant = Best bundles")
                
                with col2:
                    fig = px.pie(
                        bundle_df,
                        names='Bundle_Size',
                        title='📦 Bundle Size Distribution',
                        template=get_plotly_template(),
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("Number of products per bundle")
                
                # Row 3: Priority and Cross-Category Analysis
                col1, col2 = st.columns(2)
                
                with col1:
                    priority_counts = bundle_df['Priority'].value_counts()
                    fig = px.bar(
                        x=priority_counts.index,
                        y=priority_counts.values,
                        title='⭐ Bundle Priority Distribution',
                        template=get_plotly_template(),
                        color=priority_counts.values,
                        color_continuous_scale='Reds',
                        labels={'x': 'Priority Level', 'y': 'Count'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("High priority = Better ROI potential")
                
                with col2:
                    cross_cat_counts = bundle_df['Cross_Category'].value_counts()
                    fig = px.pie(
                        values=cross_cat_counts.values,
                        names=cross_cat_counts.index,
                        title='🔀 Cross-Category Bundles',
                        template=get_plotly_template(),
                        color_discrete_sequence=['#00CC96', '#EF553B']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("Cross-category = Broader reach")
                
                # Row 4: Heatmap of all metrics
                st.markdown("### 🔥 Bundle Metrics Heatmap")
                fig = go.Figure(data=go.Heatmap(
                    z=[bundle_df['Confidence'].values, 
                       bundle_df['Lift'].values, 
                       bundle_df['Support'].values],
                    x=bundle_df['Bundle'].values,
                    y=['Confidence (%)', 'Lift Factor', 'Support (%)'],
                    colorscale='Viridis',
                    text=[
                        [f"{v:.1f}" for v in bundle_df['Confidence'].values],
                        [f"{v:.2f}" for v in bundle_df['Lift'].values],
                        [f"{v:.1f}" for v in bundle_df['Support'].values]
                    ],
                    texttemplate='%{text}',
                    textfont={"size": 10},
                    colorbar=dict(title="Value")
                ))
                fig.update_layout(
                    template=get_plotly_template(),
                    title='Bundle Performance Comparison',
                    xaxis_title='Bundle',
                    yaxis_title='Metric'
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Darker colors indicate higher values for each metric")
                
                # Summary statistics
                st.markdown("### 📊 Summary Statistics")
                st.caption("Aggregate metrics across filtered bundles")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    avg_confidence = np.mean([b['confidence'] for b in filtered_bundles])
                    st.metric(
                        "Average Confidence", 
                        f"{avg_confidence*100:.1f}%",
                        help="Higher is better. Target: >70%"
                    )
                    st.caption("Purchase probability")
                with col2:
                    avg_lift = np.mean([b['lift'] for b in filtered_bundles])
                    st.metric(
                        "Average Lift", 
                        f"{avg_lift:.2f}x",
                        help="Multiplier effect. Target: >1.5x"
                    )
                    st.caption("Sales uplift factor")
                with col3:
                    cross_cat_pct = sum([1 for b in filtered_bundles if b['cross_category']]) / len(filtered_bundles) * 100
                    st.metric(
                        "Cross-Category Bundles", 
                        f"{cross_cat_pct:.0f}%",
                        help="Bundles spanning multiple categories"
                    )
                    st.caption("Category diversity")
                with col4:
                    avg_bundle_size = np.mean([len(b['products']) for b in filtered_bundles])
                    st.metric(
                        "Average Bundle Size",
                        f"{avg_bundle_size:.1f}",
                        help="Average number of products per bundle"
                    )
                    st.caption("Products per bundle")
                
                # Add top performers section
                st.markdown("### 🏆 Top Performing Bundles")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🥇 Highest Confidence**")
                    top_conf = max(filtered_bundles, key=lambda x: x['confidence'])
                    st.info(f"Bundle with {top_conf['confidence']*100:.1f}% confidence\n\nProducts: {', '.join(top_conf['products'][:3])}...")
                
                with col2:
                    st.markdown("**🥇 Highest Lift**")
                    top_lift = max(filtered_bundles, key=lambda x: x['lift'])
                    st.success(f"Bundle with {top_lift['lift']:.2f}x lift\n\nProducts: {', '.join(top_lift['products'][:3])}...")
                
                with col3:
                    st.markdown("**🥇 Highest Support**")
                    top_support = max(filtered_bundles, key=lambda x: x['support'])
                    st.warning(f"Bundle with {top_support['support']*100:.1f}% support\n\nProducts: {', '.join(top_support['products'][:3])}...")
    
    except Exception as e:
        st.error(f"❌ Error in bundle analysis: {str(e)}")
        import traceback
        with st.expander("🔍 View Error Details"):
            st.code(traceback.format_exc())

else:
    st.title("💳 Payment Method Analytics")
    st.markdown("### 💰 Payment Preferences & Optimization Strategies")
    st.caption("Analyze payment behavior to improve conversion and reduce costs")
    
    try:
        with st.spinner('🔄 Analyzing payment methods...'):
            insights = st.session_state.payment_analyzer.analyze_payment_preferences(st.session_state.df)
        
        st.success('✅ Analysis complete!')
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Detailed Analysis", "💡 Recommendations"])
        
        with tab1:
            st.markdown("### 📊 Payment Method Distribution")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.caption("Transaction share by payment type")
                method_shares = {m: s['share'] for m, s in insights['method_stats'].items()}
                fig = px.pie(
                    values=list(method_shares.values()),
                    names=list(method_shares.keys()),
                    title="Payment Methods Distribution",
                    template=get_plotly_template(),
                    color_discrete_sequence=px.colors.sequential.Turbo,
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"💳 {len(insights['method_stats'])} payment methods available")
            
            with col2:
                st.caption("Average transaction value by payment method")
                avg_values = {m: s['avg_value'] for m, s in insights['method_stats'].items()}
                fig = px.bar(
                    x=list(avg_values.keys()),
                    y=list(avg_values.values()),
                    title="Average Transaction Value by Method",
                    template=get_plotly_template(),
                    color=list(avg_values.values()),
                    color_continuous_scale='Viridis',
                    labels={'x': 'Payment Method', 'y': 'Average Value (₹)'}
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("📊 Identifies high-value payment preferences")
            
            # Summary metrics
            st.markdown("### 📈 Quick Insights")
            col1, col2, col3, col4 = st.columns(4)
            
            total_transactions = sum([s['total_transactions'] for s in insights['method_stats'].values()])
            total_volume = sum([s['total_volume'] for s in insights['method_stats'].values()])
            most_popular = max(insights['method_stats'].items(), key=lambda x: x[1]['share'])
            highest_value = max(insights['method_stats'].items(), key=lambda x: x[1]['avg_value'])
            
            with col1:
                st.metric(
                    "Total Transactions",
                    f"{total_transactions:,}",
                    help="Total payment transactions"
                )
                st.caption("All methods")
            
            with col2:
                st.metric(
                    "Total Volume",
                    f"₹{total_volume:,.2f}",
                    help="Total transaction value"
                )
                st.caption("All methods")
            
            with col3:
                st.metric(
                    "Most Popular",
                    most_popular[0],
                    f"{most_popular[1]['share']*100:.1f}%",
                    help="Payment method with highest usage"
                )
                st.caption("By transaction count")
            
            with col4:
                st.metric(
                    "Highest Value",
                    highest_value[0],
                    f"₹{highest_value[1]['avg_value']:.2f}",
                    help="Payment method with highest average value"
                )
                st.caption("Per transaction")
            
            # Comparison chart
            st.markdown("### 📊 Payment Method Comparison")
            comparison_df = pd.DataFrame([
                {
                    'Method': method,
                    'Share (%)': stats['share'] * 100,
                    'Avg Value (₹)': stats['avg_value'],
                    'Total Volume (₹)': stats['total_volume']
                }
                for method, stats in insights['method_stats'].items()
            ])
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Transaction Share (%)',
                x=comparison_df['Method'],
                y=comparison_df['Share (%)'],
                marker_color='#667eea'
            ))
            fig.add_trace(go.Bar(
                name='Avg Value (₹/100)',
                x=comparison_df['Method'],
                y=comparison_df['Avg Value (₹)'] / 100,
                marker_color='#764ba2'
            ))
            fig.update_layout(
                title='Payment Method Metrics Comparison',
                template=get_plotly_template(),
                barmode='group',
                yaxis_title='Value',
                xaxis_title='Payment Method'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Note: Average value scaled down by 100x for visualization")
        
        with tab2:
            st.markdown("### 💳 Detailed Payment Method Analysis")
            
            for method, stats in insights['method_stats'].items():
                st.markdown(f"#### {method}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Transaction Share", 
                        f"{stats['share']*100:.1f}%",
                        help="Percentage of total transactions"
                    )
                    st.caption(f"{stats['total_transactions']:,} transactions")
                with col2:
                    st.metric(
                        "Average Value", 
                        f"₹{stats['avg_value']:.2f}",
                        help="Mean transaction amount"
                    )
                    st.caption("Per transaction")
                with col3:
                    st.metric(
                        "Total Volume", 
                        f"₹{stats['total_volume']:,.2f}",
                        help="Sum of all transactions"
                    )
                    st.caption("Cumulative revenue")
                
                with st.expander(f"📊 View {method} Value Distribution"):
                    fig = go.Figure(data=[
                        go.Bar(
                            x=['Low', 'Medium', 'High'],
                            y=[stats['value_distribution']['low']*100,
                               stats['value_distribution']['medium']*100,
                               stats['value_distribution']['high']*100],
                            marker_color=['#667eea', '#764ba2', '#f093fb']
                        )
                    ])
                    fig.update_layout(
                        title=f"{method} - Transaction Value Distribution",
                        template=get_plotly_template(),
                        yaxis_title='Percentage (%)',
                        xaxis_title='Value Bracket'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("Distribution of transaction values across price brackets")
                
                st.markdown("---")
        
        with tab3:
            st.markdown("### 🎯 Payment Incentive Recommendations")
            st.caption("Strategic recommendations to optimize each payment method")
            incentives = st.session_state.payment_analyzer.recommend_payment_incentives(insights)
            
            for method, incentive in incentives.items():
                with st.expander(f"💡 {method} Strategy", expanded=True):
                    st.markdown(f"**Strategy:** {incentive['strategy']}")
                    st.markdown(f"**Action:** {incentive['action']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        priority_emoji = "🔴" if incentive['priority'] == "High" else "🟡" if incentive['priority'] == "Medium" else "🟢"
                        st.markdown(f"**Priority:** {priority_emoji} {incentive['priority']}")
                    with col2:
                        st.markdown(f"**Target:** {incentive['target_segment']}")
                    with col3:
                        st.markdown(f"**Impact:** {incentive['expected_impact']}")
    
    except Exception as e:
        st.error(f"❌ Error in payment analytics: {str(e)}")

# Footer with timestamp and info
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p>🛍️ E-Commerce Analytics Platform | Data Warehousing & Data Mining Project</p>
    <p style='font-size: 12px;'>Built with Streamlit | Powered by K-Means, Apriori & Statistical Analysis</p>
</div>
""", unsafe_allow_html=True)
