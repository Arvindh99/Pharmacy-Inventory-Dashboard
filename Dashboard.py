import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
import numpy as np

# Streamlit App Configuration
st.set_page_config(page_title="Advanced Pharma Dashboard", layout="wide")

st.title("PHARMACY INVENTORY DASHBOARD")
st.divider()
# Load Data
@st.cache_data
def load_data():
    file_path = 'enhanced_medicine_inventory_dataset.csv'
    data = pd.read_csv(file_path,encoding='cp1252')
    data['Expiry Date'] = pd.to_datetime(data['Expiry Date'])
    data['Manufacture Date'] = pd.to_datetime(data['Manufacture Date'])
    data['Total Cost'] = data['Cost Price ($)'] * data['Units Sold']
    data['Total Revenue'] = data['Selling Price ($)'] * data['Units Sold']
    data['Profit'] = data['Total Revenue'] - data['Total Cost']
    data['Total Profit Margin (%)'] = (data['Profit'] / data['Total Revenue']) * 100
    data['Cost Efficiency (%)'] = (data['Total Cost'] / data['Total Revenue']) * 100
    data['Stock Gap'] = data['Reorder Level'] - data['Count']

    return data

data = load_data()

if "selected_section" not in st.session_state:
    st.session_state.selected_section = "📊 Overview"

# Section selection buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Overview"):
        st.session_state.selected_section = "📊 Overview"
with col2:
    if st.button("💰 Financial Metrics"):
        st.session_state.selected_section = "💰 Financial Metrics"
with col3:
    if st.button("📈 Performance Metrics"):
        st.session_state.selected_section = "📈 Performance Metrics"
with col4:
    if st.button("⚙️ Operational Metrics"):
        st.session_state.selected_section = "⚙️ Operational Metrics"
st.divider()

# Layout for Each Section
if st.session_state.selected_section == "📊 Overview":
    st.markdown("📊 Overview", unsafe_allow_html=True)
    
    unique_Category = data['Category'].unique()
    unique_DosageForm = data['Dosage Form'].unique()
    unique_warehouse = data['Warehouse Location'].unique()
    unique_ailment = data['Target Ailment'].unique()
    unique_supplier = data['Supplier Name'].unique()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        catg = st.multiselect("Category: ",unique_Category, key="key1")
    with col2:
        dose = st.multiselect("Dosage Form: ",unique_DosageForm, key="key2")
    with col3:  
        ware = st.multiselect("Warehouse: ",unique_warehouse, key="key3")
    with col4:
        target = st.multiselect("Target Ailment: ",unique_ailment, key="key4")
    with col5:
        supplier = st.multiselect("Supplier Name: ",unique_supplier, key="key5")

    filter_condition = pd.Series(True, index=data.index)

    ## """Making the filter conditions work inside the Dashboard"""

    if catg:
        filter_condition &= data['Category'].isin(catg)
    if dose:
        filter_condition &= data['Dosage Form'].isin(dose)
    if ware:
        filter_condition &= data['Warehouse Location'].isin(ware)
    if target:
        filter_condition &= data['Target Ailment'].isin(target)
    if supplier:
        filter_condition &= data['Supplier Name'].isin(supplier)

    filtered_data = data[filter_condition]
    st.divider()
    
    if not filtered_data.empty:
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Unique Medicines", filtered_data['Medicine Name'].nunique(), border=True)
        col2.metric("Avg Units in Stock", round(filtered_data['Count'].mean(), 0), border=True)
        col3.metric("No.of Tablets Expiring Soon", filtered_data[filtered_data['Days to Expiry'] <= 30]['Count'].sum(), border=True)
        col4.metric("Total Batches", filtered_data['Batch Number'].nunique(), border=True)
        st.divider()
    
        # Charts
        #st.markdown("### Key Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            top_medicines = (filtered_data.groupby('Medicine Name', as_index=False)['Total Revenue'].sum().sort_values(by='Total Revenue', ascending=False).head(10))
            st.markdown("Top 10 Medicines by Revenue")
            st.dataframe(top_medicines,hide_index=True,use_container_width=True)
    
    
        with col2:
            expiring_soon = filtered_data[filtered_data['Days to Expiry'] <= 30][['Medicine Name', 'Days to Expiry', 'Category']].sort_values(by='Days to Expiry')
            st.markdown("Medicines Expiring Soon (Within 30 Days)")
            st.dataframe(expiring_soon,hide_index=True,use_container_width=True)
    
        st.divider()
        col3, col4, col5 = st.columns(3)
        
        with col3:
            fig1 = px.box(filtered_data,x='Category', y='Selling Price ($)', title="Distribution of Selling Price by Category",color='Category',
            color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col4:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=filtered_data['Medicine Name'],y=filtered_data['Count'],name="Count",marker_color="green",
                text=filtered_data['Count'],textposition="outside"))
            fig.add_trace(go.Bar(x=filtered_data['Medicine Name'],y=filtered_data['Reorder Level'],name="Reorder Level",marker_color="red",
             	opacity=0.6,text=filtered_data['Reorder Level'],textposition="outside"))
            fig.update_layout(title="Thermometer Chart: Count vs Reorder Level",xaxis_title="Medicine Name",
                yaxis_title="Count",barmode="overlay", template="plotly_white",legend=dict(title="Metrics"))
            st.plotly_chart(fig, use_container_width=True)
    
        with col5:
            fig3 = px.box(filtered_data, y='Profit Margin (%)', title="Profit Margin Distribution")
            st.plotly_chart(fig3, use_container_width=True)
        
    else:
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Unique Medicines", data['Medicine Name'].nunique(), border=True)
        col2.metric("Avg Units in Stock", round(data['Count'].mean(), 0), border=True)
        col3.metric("No.of Tablets Expiring Soon", data[data['Days to Expiry'] <= 30]['Count'].sum(), border=True)
        col4.metric("Total Batches", data['Batch Number'].nunique(), border=True)
        st.divider()
    
        # Charts
        #st.markdown("### Key Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            top_medicines = (filtered_data.groupby('Medicine Name', as_index=False)['Total Revenue'].sum().sort_values(by='Total Revenue', ascending=False).head(10))
            st.markdown("Top 10 Medicines by Revenue")
            st.dataframe(top_medicines,hide_index=True,use_container_width=True)
    
    
        with col2:
            expiring_soon = data[data['Days to Expiry'] <= 30][['Medicine Name', 'Days to Expiry', 'Category']].sort_values(by='Days to Expiry')
            st.markdown("Medicines Expiring Soon (Within 30 Days)")
            st.dataframe(expiring_soon,hide_index=True,use_container_width=True)
    
        st.divider()
        col3, col4, col5 = st.columns(3)
        
        with col3:
            fig1 = px.box(data,x='Category', y='Selling Price ($)', title="Distribution of Selling Price by Category",color='Category',
            color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col4:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=data['Medicine Name'],y=data['Count'],name="Count",marker_color="green",
                text=data['Count'],textposition="outside"))
            fig.add_trace(go.Bar(x=data['Medicine Name'],y=data['Reorder Level'],name="Reorder Level",marker_color="red",
             	opacity=0.6,text=data['Reorder Level'],textposition="outside"))
            fig.update_layout(title="Thermometer Chart: Count vs Reorder Level",xaxis_title="Medicine Name",
                yaxis_title="Count",barmode="overlay", template="plotly_white",legend=dict(title="Metrics"))
            st.plotly_chart(fig, use_container_width=True)
    
        with col5:
            fig3 = px.box(data, y='Profit Margin (%)', title="Profit Margin Distribution")
            st.plotly_chart(fig3, use_container_width=True)
        st.divider()

elif st.session_state.selected_section == "💰 Financial Metrics":
    st.markdown("💰 Financial Metrics", unsafe_allow_html=True)
    
    unique_Category = data['Category'].unique()
    unique_DosageForm = data['Dosage Form'].unique()
    unique_warehouse = data['Warehouse Location'].unique()
    unique_ailment = data['Target Ailment'].unique()
    unique_supplier = data['Supplier Name'].unique()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        catg = st.multiselect("Category: ",unique_Category, key="key6")
    with col2:
        dose = st.multiselect("Dosage Form: ",unique_DosageForm, key="key7")
    with col3:  
        ware = st.multiselect("Warehouse: ",unique_warehouse, key="key8")
    with col4:
        target = st.multiselect("Target Ailment: ",unique_ailment, key="key9")
    with col5:
        supplier = st.multiselect("Supplier Name: ",unique_supplier, key="key10")

    filter_condition = pd.Series(True, index=data.index)

    ## """Making the filter conditions work inside the Dashboard"""

    if catg:
        filter_condition &= data['Category'].isin(catg)
    if dose:
        filter_condition &= data['Dosage Form'].isin(dose)
    if ware:
        filter_condition &= data['Warehouse Location'].isin(ware)
    if target:
        filter_condition &= data['Target Ailment'].isin(target)
    if supplier:
        filter_condition &= data['Supplier Name'].isin(supplier)

    filtered_data = data[filter_condition]
    st.divider()
    
    if not filtered_data.empty:
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Avg Cost Price", round(filtered_data['Cost Price ($)'].mean(), 2), border=True)
        col2.metric("Avg Selling Price", round(filtered_data['Selling Price ($)'].mean(), 2), border=True)
        col3.metric("Total Discounts in %", round(filtered_data['Discount (%)'].mean(), 2), border=True)
        col4.metric("Profit Margin", round(filtered_data['Profit Margin (%)'].mean(), 2), border=True)
        st.divider()
    
        # Charts
        #st.markdown("### Financial Trends")
        col1, col2 = st.columns(2)
    
        fig1 = px.sunburst(filtered_data,path=['Category'],values='Total Revenue',color='Profit',color_continuous_scale='RdBu',
                           title="Financial Breakdown by Category")
        col1.plotly_chart(fig1, use_container_width=True)
    
    
        fig2 = px.bar(filtered_data, x='Category', y='Selling Price ($)', title="Avg Selling Price by Category", color='Category')
        col2.plotly_chart(fig2, use_container_width=True)
        st.divider()
    
        col3, col4 = st.columns(2)
    
        fig4 = px.scatter(filtered_data,x='Total Revenue',y='Profit',size='Units Sold',color='Category',
        title="Revenue vs Profit",hover_data=['Category', 'Total Revenue', 'Profit'])
        col3.plotly_chart(fig4, use_container_width=True)
    
        fig5 = px.treemap(filtered_data, path=['Category', 'Medicine Name'], values='Profit Margin (%)', title="Profit Margin by Category")
        col4.plotly_chart(fig5, use_container_width=True)
        st.divider()
        
    else:
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Avg Cost Price", round(data['Cost Price ($)'].mean(), 2), "$", border=True)
        col2.metric("Avg Selling Price", round(data['Selling Price ($)'].mean(), 2), "$", border=True)
        col3.metric("Total Discounts in %", round(data['Discount (%)'].mean(), 2), "%", border=True)
        col4.metric("Profit Margin", round(data['Profit Margin (%)'].mean(), 2), "%", border=True)
    
        # Charts
        #st.markdown("### Financial Trends")
        col1, col2 = st.columns(2)
    
        fig1 = px.sunburst(data,path=['Category'],values='Total Revenue',color='Profit',color_continuous_scale='RdBu',
                           title="Financial Breakdown by Category")
        col1.plotly_chart(fig1, use_container_width=True)
    
    
        fig2 = px.bar(data, x='Category', y='Selling Price ($)', title="Avg Selling Price by Category", color='Category')
        col2.plotly_chart(fig2, use_container_width=True)
        st.divider()
    
        col3, col4 = st.columns(2)
    
        fig4 = px.scatter(data,x='Total Revenue',y='Profit',size='Units Sold',color='Category',
        title="Revenue vs Profit",hover_data=['Category', 'Total Revenue', 'Profit'])
        col3.plotly_chart(fig4, use_container_width=True)
    
        fig5 = px.treemap(data, path=['Category', 'Medicine Name'], values='Profit Margin (%)', title="Profit Margin by Category")
        col4.plotly_chart(fig5, use_container_width=True)
        st.divider()

elif st.session_state.selected_section == "📈 Performance Metrics":
    st.markdown("📈 Performance Metrics", unsafe_allow_html=True)
    
    unique_Category = data['Category'].unique()
    unique_supplier = data['Supplier Name'].unique()
    unique_warehouse = data['Warehouse Location'].unique()
    unique_ailment = data['Target Ailment'].unique()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        catg = st.multiselect("Category: ",unique_Category, key="key11")
    with col2:
        supplier = st.multiselect("Supplier Name: ",unique_supplier, key="key12")
    with col3:  
        ware = st.multiselect("Warehouse: ",unique_warehouse, key="key13")
    with col4:
        target = st.multiselect("Target Ailment: ",unique_ailment, key="key14")

    filter_condition = pd.Series(True, index=data.index)

    ## """Making the filter conditions work inside the Dashboard"""

    if catg:
        filter_condition &= data['Category'].isin(catg)
    if supplier:
        filter_condition &= data['Supplier Name'].isin(supplier)
    if ware:
        filter_condition &= data['Warehouse Location'].isin(ware)
    if target:
        filter_condition &= data['Target Ailment'].isin(target)

    filtered_data = data[filter_condition]
    st.divider()
    
    if not filtered_data.empty:
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Units Sold", filtered_data['Units Sold'].sum(), border=True)
        high_demand_medicines = (filtered_data.groupby('Medicine Name', as_index=False)['Units Sold'].sum().query("`Units Sold` > 800").nunique())
        col2.metric("High Demand Medicines", high_demand_medicines['Medicine Name'], border=True)
        col3.metric("Avg Units Sold", round(filtered_data['Units Sold'].mean(), 0), border=True)
        col4.metric("Top Seller", filtered_data.loc[filtered_data['Units Sold'].idxmax(), 'Medicine Name'], border=True)
        st.divider()
    
        # Charts
        #st.markdown("### Performance Insights")
        col1, col2 = st.columns(2)
    
        fig1 = px.bar(filtered_data.nlargest(10, 'Units Sold'), x='Medicine Name', y='Units Sold', title="Top 10 Medicines by Sales")
        col1.plotly_chart(fig1, use_container_width=True)
    
        fig2 = px.pie(filtered_data, names='Dosage Form', title="Sales Distribution by Dosage Form", hole=0.4)
        col2.plotly_chart(fig2, use_container_width=True)
        st.divider()
    
        col3, col4, col5 = st.columns(3)
        # Speedometer (Gauge) Chart for Average Profit Margin
        avg_profit_margin = filtered_data['Profit Margin (%)'].mean()
        
        fig3 = go.Figure(go.Indicator(mode="gauge+number",value=avg_profit_margin,title={'text': "Average Profit Margin (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#4CAF50"},
                'steps': [
                    {'range': [0, 50], 'color': '#FFCDD2'},
                    {'range': [50, 75], 'color': '#FFF9C4'},
                    {'range': [75, 100], 'color': '#C8E6C9'}
                ],
            }
        ))
        col3.plotly_chart(fig3, use_container_width=True)
    
    
        revenue_by_category = filtered_data.groupby('Category')['Total Revenue'].sum().reset_index()
    
        fig4 = px.pie(
            revenue_by_category,
            values='Total Revenue',
            names='Category',
            title="Revenue Distribution by Category",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        col4.plotly_chart(fig4, use_container_width=True)
    
        # Bullet Chart for Revenue Target
        revenue_target = 5000000  # Example revenue target
        total_revenue = filtered_data['Total Revenue'].sum()
        fig5 = go.Figure(go.Indicator(
            mode="number+gauge+delta",
            value=total_revenue,
            delta={'reference': revenue_target, 'relative': True},
            gauge={
                'shape': "bullet",
                'axis': {'range': [0, revenue_target]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, revenue_target * 0.5], 'color': "#FFCDD2"},
                    {'range': [revenue_target * 0.5, revenue_target * 0.8], 'color': "#FFF9C4"},
                    {'range': [revenue_target * 0.8, revenue_target], 'color': "#C8E6C9"}
                ]
            },
            title={'text': "Revenue Target Achievement"}
        ))
        col5.plotly_chart(fig5, use_container_width=True)
        st.divider()
        
    else:

        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Units Sold", data['Units Sold'].sum(), border=True)
        high_demand_medicines = (data.groupby('Medicine Name', as_index=False)['Units Sold'].sum().query("`Units Sold` > 800").nunique())
        col2.metric("High Demand Medicines", high_demand_medicines['Medicine Name'], border=True)
        col3.metric("Avg Units Sold", round(data['Units Sold'].mean(), 0), border=True)
        col4.metric("Top Seller", data.loc[data['Units Sold'].idxmax(), 'Medicine Name'], border=True)
        st.divider()
    
        # Charts
        #st.markdown("### Performance Insights")
        col1, col2 = st.columns(2)
    
        fig1 = px.bar(data.nlargest(10, 'Units Sold'), x='Medicine Name', y='Units Sold', title="Top 10 Medicines by Sales")
        col1.plotly_chart(fig1, use_container_width=True)
    
        fig2 = px.pie(data, names='Dosage Form', title="Sales Distribution by Dosage Form", hole=0.4)
        col2.plotly_chart(fig2, use_container_width=True)
        st.divider()
    
        col3, col4, col5 = st.columns(3)
        # Speedometer (Gauge) Chart for Average Profit Margin
        avg_profit_margin = data['Profit Margin (%)'].mean()
        
        fig3 = go.Figure(go.Indicator(mode="gauge+number",value=avg_profit_margin,title={'text': "Average Profit Margin (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#4CAF50"},
                'steps': [
                    {'range': [0, 50], 'color': '#FFCDD2'},
                    {'range': [50, 75], 'color': '#FFF9C4'},
                    {'range': [75, 100], 'color': '#C8E6C9'}
                ],
            }
        ))
        col3.plotly_chart(fig3, use_container_width=True)
    
    
        revenue_by_category = data.groupby('Category')['Total Revenue'].sum().reset_index()
    
        fig4 = px.pie(
            revenue_by_category,
            values='Total Revenue',
            names='Category',
            title="Revenue Distribution by Category",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        col4.plotly_chart(fig4, use_container_width=True)
    
        # Bullet Chart for Revenue Target
        revenue_target = 5000000  # Example revenue target
        total_revenue = data['Total Revenue'].sum()
        fig5 = go.Figure(go.Indicator(
            mode="number+gauge+delta",
            value=total_revenue,
            delta={'reference': revenue_target, 'relative': True},
            gauge={
                'shape': "bullet",
                'axis': {'range': [0, revenue_target]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, revenue_target * 0.5], 'color': "#FFCDD2"},
                    {'range': [revenue_target * 0.5, revenue_target * 0.8], 'color': "#FFF9C4"},
                    {'range': [revenue_target * 0.8, revenue_target], 'color': "#C8E6C9"}
                ]
            },
            title={'text': "Revenue Target Achievement"}
        ))
        col5.plotly_chart(fig5, use_container_width=True)
        st.divider()


elif st.session_state.selected_section == "⚙️ Operational Metrics":
    st.markdown("⚙️ Operational Metrics", unsafe_allow_html=True)
    
    unique_Category = data['Category'].unique()
    unique_DosageForm = data['Dosage Form'].unique()
    unique_warehouse = data['Warehouse Location'].unique()
    unique_ailment = data['Target Ailment'].unique()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        catg = st.multiselect("Category: ",unique_Category, key="key15")
    with col2:
        dose = st.multiselect("Dosage Form: ",unique_DosageForm, key="key16")
    with col3:  
        ware = st.multiselect("Warehouse: ",unique_warehouse, key="key17")
    with col4:
        target = st.multiselect("Target Ailment: ",unique_ailment, key="key18")

    filter_condition = pd.Series(True, index=data.index)

    ## """Making the filter conditions work inside the Dashboard"""

    if catg:
        filter_condition &= data['Category'].isin(catg)
    if dose:
        filter_condition &= data['Dosage Form'].isin(dose)
    if ware:
        filter_condition &= data['Warehouse Location'].isin(ware)
    if target:
        filter_condition &= data['Target Ailment'].isin(target)

    filtered_data = data[filter_condition]
    st.divider()
    
    if not filtered_data.empty:
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Avg Days to Expiry", round(filtered_data['Days to Expiry'].mean(), 0), border=True)
        col2.metric("Stock in Warehouses", filtered_data['Count'].sum(), border=True)
        col3.metric("Prescription Medicines", filtered_data[filtered_data['Prescription Required']].shape[0],border=True)
        col4.metric("Avg Stock per Category", round(filtered_data.groupby('Category')['Count'].mean().mean(), 0), border=True)
        st.divider()

        # Charts
        col1, col2 = st.columns(2)

        # Chart 1: Bar chart with custom colors
        fig1 = px.bar(filtered_data.groupby('Medicine Name')['Count'].sum().reset_index(), x='Medicine Name', y='Count', 
            title="Stock by Medicine",color_discrete_sequence=px.colors.qualitative.Vivid)
        col1.plotly_chart(fig1, use_container_width=True)
        
        # Chart 2: Line chart with a gradient color scale
        fig2 = px.line(filtered_data.groupby('Expiry Date')['Count'].sum().reset_index(), x="Expiry Date", y="Count", 
            title="Days to Expiry by Count",line_shape='spline',color_discrete_sequence=px.colors.qualitative.Bold)
        col2.plotly_chart(fig2, use_container_width=True)
        st.divider()
        
        col3, col4 = st.columns(2)
        
        # Chart 3: Box plot with vibrant colors
        fig3 = px.box(filtered_data, x='Warehouse Location', y='Days to Expiry', title="Days to Expiry by Warehouse",
            color='Warehouse Location', color_discrete_sequence=px.colors.qualitative.Pastel)
        col3.plotly_chart(fig3, use_container_width=True)
        
        # Chart 4: Normal distribution line chart with colors
        expiry_days = filtered_data['Days to Expiry'].dropna()
        density = gaussian_kde(expiry_days)
        x_vals = np.linspace(expiry_days.min(), expiry_days.max(), 1000)  # Generate x-axis values
        y_vals = density(x_vals)  # Compute the density for each x value
        
        fig4 = px.line(x=x_vals, y=y_vals, title="Days to Expiry Distribution (Normal Distribution)")
        fig4.update_layout(xaxis_title="Days to Expiry",yaxis_title="Density",template="plotly_white")
        col4.plotly_chart(fig4, use_container_width=True)
        st.divider()
    
    else:
    
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Avg Days to Expiry", round(data['Days to Expiry'].mean(), 0), border=True)
        col2.metric("Stock in Warehouses", data['Count'].sum(), border=True)
        col3.metric("Prescription Medicines", data[data['Prescription Required']].shape[0],border=True)
        col4.metric("Avg Stock per Category", round(data.groupby('Category')['Count'].mean().mean(), 0), border=True)
        st.divider()
    
        # Charts
        col1, col2 = st.columns(2)

        # Chart 1: Bar chart with custom colors
        fig1 = px.bar(data.groupby('Medicine Name')['Count'].sum().reset_index(), x='Medicine Name', y='Count', 
            title="Stock by Medicine",color_discrete_sequence=px.colors.qualitative.Vivid)
        col1.plotly_chart(fig1, use_container_width=True)
        
        # Chart 2: Line chart with a gradient color scale
        fig2 = px.line(data.groupby('Expiry Date')['Count'].sum().reset_index(), x="Expiry Date", y="Count", 
            title="Days to Expiry by Count",line_shape='spline',color_discrete_sequence=px.colors.qualitative.Bold)
        col2.plotly_chart(fig2, use_container_width=True)
        st.divider()
        
        col3, col4 = st.columns(2)
        
        # Chart 3: Box plot with vibrant colors
        fig3 = px.box(data, x='Warehouse Location', y='Days to Expiry', title="Days to Expiry by Warehouse",
            color='Warehouse Location', color_discrete_sequence=px.colors.qualitative.Pastel)
        col3.plotly_chart(fig3, use_container_width=True)
        
        # Chart 4: Normal distribution line chart with colors
        expiry_days = data['Days to Expiry'].dropna()
        density = gaussian_kde(expiry_days)
        x_vals = np.linspace(expiry_days.min(), expiry_days.max(), 1000)  # Generate x-axis values
        y_vals = density(x_vals)  # Compute the density for each x value
        
        fig4 = px.line(x=x_vals, y=y_vals, title="Days to Expiry Distribution (Normal Distribution)")
        fig4.update_layout(xaxis_title="Days to Expiry",yaxis_title="Density",template="plotly_white")
        col4.plotly_chart(fig4, use_container_width=True)
        st.divider()
        
