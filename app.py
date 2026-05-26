import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os
import base64

# Helper function to load local image as base64
def get_base64_image(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None


# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Thai Sin Anan Rubber Factory Sales Domestic Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling using HTML/CSS Injection
# Utilizing 'Prompt' Google Font for gorgeous Thai/English typography
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            font-family: 'Prompt', 'Inter', sans-serif;
        }
        .main-header {
            font-size: 32px;
            font-weight: 700;
            color: #4F46E5;
            background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 16px;
            color: #6B7280;
            margin-bottom: 25px;
        }
        .metric-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border-left: 5px solid #4F46E5;
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 160px;
        }
        .dark-theme .metric-card {
            background-color: #1F2937;
            border-left: 5px solid #6366F1;
        }
        .metric-title {
            font-size: 14px;
            color: #6B7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 26px;
            font-weight: 700;
            color: #111827;
            margin-top: 5px;
        }
        .dark-theme .metric-value {
            color: #F9FAFB;
        }
        .metric-delta {
            font-size: 13px;
            font-weight: 600;
            margin-top: 5px;
        }
        .delta-positive {
            color: #10B981;
        }
        .delta-negative {
            color: #EF4444;
        }
        .card-container {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid rgba(229, 231, 235, 0.5);
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            white-space: pre-wrap;
            background-color: #F3F4F6;
            border-radius: 8px;
            color: #4B5563;
            font-weight: 500;
            padding: 10px 20px;
            transition: all 0.3s;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4F46E5 !important;
            color: white !important;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# Helper function to load and process data
@st.cache_data
def load_data():
    csv_path = "all_sales_data.csv"
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    
    df = pd.read_csv(csv_path)
    
    # Parse Dates: dd/mm/yy (yy is BE e.g. 68 -> 2025, 69 -> 2026)
    def to_datetime(date_str):
        try:
            parts = date_str.split('/')
            day = int(parts[0])
            month = int(parts[1])
            year_be = int(parts[2])
            year_ce = 1957 + year_be
            return pd.Timestamp(year=year_ce, month=month, day=day)
        except Exception:
            return pd.NaT

    df['ParsedDate'] = df['Date'].apply(to_datetime)
    df['Year'] = df['ParsedDate'].dt.year
    df['MonthNum'] = df['ParsedDate'].dt.month
    
    # Month Name Mapping (Thai)
    month_names_th = {
        1: "มกราคม (Jan)", 2: "กุมภาพันธ์ (Feb)", 3: "มีนาคม (Mar)", 4: "เมษายน (Apr)",
        5: "พฤษภาคม (May)", 6: "มิถุนายน (Jun)", 7: "กรกฎาคม (Jul)", 8: "สิงหาคม (Aug)",
        9: "กันยายน (Sep)", 10: "ตุลาคม (Oct)", 11: "พฤศจิกายน (Nov)", 12: "ธันวาคม (Dec)"
    }
    df['MonthTH'] = df['MonthNum'].map(month_names_th)
    
    # Quarter
    df['Quarter'] = df['ParsedDate'].dt.quarter
    
    return df

# Load the parsed dataset
df = load_data()

if df.empty:
    st.error("ไม่พบข้อมูลยอดขายสุทธิ กรุณาตรวจสอบว่ามีไฟล์ 'all_sales_data.csv' หรือไม่")
else:
    # ------------------ SIDEBAR FILTER ------------------
    st.sidebar.markdown("### 🔍 ตัวกรองข้อมูล (Filters)")
    
    # Filter by Year
    years = sorted(df['Year'].dropna().unique())
    selected_years = st.sidebar.multiselect("เลือกปี (Year)", options=years, default=years)
    
    # Filter by Month
    months = sorted(df['MonthNum'].dropna().unique())
    month_names = {
        1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน", 5: "พฤษภาคม", 6: "มิถุนายน",
        7: "กรกฎาคม", 8: "สิงหาคม", 9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
    }
    selected_months = st.sidebar.multiselect(
        "เลือกเดือน (Month)", 
        options=months, 
        default=months,
        format_func=lambda x: month_names[x]
    )
    
    # Apply global sidebar filters
    filtered_df = df[
        (df['Year'].isin(selected_years)) & 
        (df['MonthNum'].isin(selected_months))
    ]
    
    # Helper to generate a readable string of the current filter status (Months and Years)
    def get_filter_status_str(selected_years, selected_months, all_years, all_months, month_names):
        if not selected_years and not selected_months:
            return "(ไม่ได้เลือกปีและเดือน)"
            
        # Years part
        if len(selected_years) == len(all_years):
            years_str = "ทุกปี"
        elif len(selected_years) == 0:
            years_str = "ไม่มีปี"
        elif len(selected_years) == 1:
            y = selected_years[0]
            years_str = f"ปี {y} ({y+543})"
        else:
            years_str = "ปี " + ", ".join([f"{y} ({y+543})" for y in sorted(selected_years)])
            
        # Months part
        if len(selected_months) == len(all_months):
            months_str = "ทุกเดือน"
        elif len(selected_months) == 0:
            months_str = "ไม่มีเดือน"
        elif len(selected_months) <= 3:
            months_str = ", ".join([month_names[m] for m in sorted(selected_months)])
        else:
            months_str = f"{len(selected_months)} เดือน"
            
        return f"({years_str} | {months_str})"
        
    filter_status_suffix = get_filter_status_str(selected_years, selected_months, years, months, month_names)
    
    # ------------------ MAIN HEADER ------------------
    # Load and encode Mitsuba logo to display beautifully alongside the header
    logo_base64 = get_base64_image("mitsuba_logo.jpg")
    
    if logo_base64:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 5px; flex-wrap: wrap;">
                <img src="data:image/jpeg;base64,{logo_base64}" style="height: 48px; border-radius: 4px; object-fit: contain;" />
                <div class="main-header" style="margin: 0; line-height: 1.2;">Thai Sin Anan Rubber Factory Sales Domestic Analytics Dashboard</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="main-header">📊 Thai Sin Anan Rubber Factory Sales Domestic Analytics Dashboard</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="subtitle">ระบบวิเคราะห์ข้อมูลยอดขายสุทธิของลูกค้า สินค้า ราคาต่อหน่วย และยอดเปรียบเทียบปี 2025 กับ 2026</div>', unsafe_allow_html=True)
    
    # Create main Tabs
    tab_overview, tab_customers, tab_products, tab_raw = st.tabs([
        "📈 ภาพรวมยอดขาย (Overview)", 
        "👥 เจาะลึกรายลูกค้า (Customer Deep Dive)", 
        "📦 ข้อมูลราคาสินค้า (Product & Prices)", 
        "🔍 ค้นหาข้อมูลดิบ (Search Raw Data)"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: OVERVIEW
    # -------------------------------------------------------------
    with tab_overview:
        # 1. Metric Calculations (Dynamic based on active sidebar month/year filters)
        # Determine the months that actually have data in both years to perform a fair comparison
        # 2026 has data for months 1, 2, 3. 2025 has data for months 1-12.
        # Therefore, for like-for-like comparison, we intersect selected_months with [1, 2, 3]
        common_months = [m for m in selected_months if m in [1, 2, 3]]
        if not common_months:
            common_months = [1, 2, 3] # default fallback
            
        # 2025 comparable period sales and quantity
        sales_2025_selected = df[(df['Year'] == 2025) & (df['MonthNum'].isin(common_months))]['NetSales'].sum()
        qty_2025_selected = df[(df['Year'] == 2025) & (df['MonthNum'].isin(common_months))]['Qty'].sum()
        
        # 2026 selected period sales and quantity (only has data for common_months anyway)
        sales_2026_selected = df[(df['Year'] == 2026) & (df['MonthNum'].isin(common_months))]['NetSales'].sum()
        qty_2026_selected = df[(df['Year'] == 2026) & (df['MonthNum'].isin(common_months))]['Qty'].sum()
        
        # Growth YoY for the selected period
        yoy_growth_selected = 0.0
        if sales_2025_selected > 0:
            yoy_growth_selected = ((sales_2026_selected - sales_2025_selected) / sales_2025_selected) * 100
            
        diff_selected = sales_2026_selected - sales_2025_selected
        growth_class = "delta-positive" if yoy_growth_selected >= 0 else "delta-negative"
        growth_prefix = "+" if yoy_growth_selected >= 0 else ""
        diff_prefix = "+" if diff_selected >= 0 else ""
        
        # Full year 2025 sales for run-rate calculation reference
        full_sales_2025 = df[df['Year'] == 2025]['NetSales'].sum()
        
        # Seasonality ratio of the selected months in 2025
        seasonality_ratio_selected = sales_2025_selected / full_sales_2025 if full_sales_2025 > 0 else (len(common_months) / 12.0)
        if seasonality_ratio_selected == 0:
            seasonality_ratio_selected = len(common_months) / 12.0
            
        projected_2026_selected = sales_2026_selected / seasonality_ratio_selected if seasonality_ratio_selected > 0 else sales_2026_selected
        projected_increase_selected = projected_2026_selected - full_sales_2025
        proj_prefix = "+" if projected_increase_selected >= 0 else ""
        proj_class = "delta-positive" if projected_increase_selected >= 0 else "delta-negative"

        # Display Metric Cards in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #6366F1;">
                    <div class="metric-title">ยอดขายปี 2025 (2568) (เทียบช่วงเดียวกัน)</div>
                    <div class="metric-value">฿{sales_2025_selected:,.2f}</div>
                    <div class="metric-delta delta-positive">ปริมาณรวม: {qty_2025_selected:,.0f} ชิ้น ({len(common_months)} เดือน)</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #10B981;">
                    <div class="metric-title">ยอดขายสะสมปี 2026 (2569) (ช่วงที่เลือก)</div>
                    <div class="metric-value">฿{sales_2026_selected:,.2f}</div>
                    <div class="metric-delta delta-positive">สะสมตามตัวกรองเดือนที่เลือก</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #8B5CF6;">
                    <div class="metric-title">อัตราเติบโตสะสม YoY (เทียบช่วงเดียวกัน)</div>
                    <div class="metric-value">{growth_prefix}{yoy_growth_selected:.2f}%</div>
                    <div class="metric-delta {growth_class}">
                        {diff_prefix}฿{diff_selected:,.2f} (เทียบกับปี 2568 ช่วงเดียวกัน)
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            
        with col4:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #F59E0B;">
                    <div class="metric-title">ประมาณการยอดขายปี 2026 (Run-Rate)</div>
                    <div class="metric-value">฿{projected_2026_selected:,.2f}</div>
                    <div class="metric-delta {proj_class}">
                        คาดการณ์: {proj_prefix}{projected_increase_selected/max(1, full_sales_2025)*100:.1f}% ({proj_prefix}฿{projected_increase_selected:,.2f})
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        # 2. Charts Section
        st.markdown("<br>", unsafe_allow_html=True)
        col_chart_left, col_chart_right = st.columns([3, 2])
        
        with col_chart_left:
            # Generate dynamic title for the monthly sales chart based on selected years and months
            if len(selected_years) == 1:
                y = selected_years[0]
                y_be = y + 543
                if len(selected_months) == 12:
                    months_desc = "ทุกเดือน"
                elif len(selected_months) <= 3:
                    months_desc = "เดือน " + ", ".join([month_names[m] for m in sorted(selected_months)])
                else:
                    months_desc = f"สะสม {len(selected_months)} เดือน"
                chart_title_text = f"📈 ยอดเปรียบเทียบยอดขายรายเดือน ปี {y} ({y_be}) ({months_desc})"
            elif len(selected_years) == 2 and sorted(selected_years) == [2025, 2026]:
                if len(selected_months) == 12:
                    months_desc = "ทุกเดือน"
                elif len(selected_months) <= 3:
                    months_desc = "เดือน " + ", ".join([month_names[m] for m in sorted(selected_months)])
                else:
                    months_desc = f"สะสม {len(selected_months)} เดือน"
                chart_title_text = f"📈 ยอดเปรียบเทียบยอดขายรายเดือน ปี 2025-2026 ({months_desc})"
            else:
                chart_title_text = f"📈 ยอดเปรียบเทียบยอดขายรายเดือน {filter_status_suffix}"
                
            st.markdown(f"### {chart_title_text}")
            
            # Aggregate monthly sales by year (dynamic based on selected months)
            monthly_sales = df[df['MonthNum'].isin(selected_months)].groupby(['Year', 'MonthNum', 'MonthTH'])['NetSales'].sum().reset_index()
            monthly_sales['YearStr'] = monthly_sales['Year'].astype(str)
            
            chart_yoy = alt.Chart(monthly_sales).mark_bar().encode(
                x=alt.X('MonthTH:N', title='เดือน', sort=alt.SortField('MonthNum'), axis=alt.Axis(labelAngle=0)),
                y=alt.Y('NetSales:Q', title='ยอดขายสุทธิ (บาท)'),
                color=alt.Color('YearStr:N', title='ปี ค.ศ.', scale=alt.Scale(domain=['2025', '2026'], range=['#3B82F6', '#10B981'])),
                xOffset='YearStr:N'
            ).properties(
                height=280
            ).configure_axis(
                labelFont='Prompt',
                titleFont='Prompt'
            ).configure_legend(
                labelFont='Prompt',
                titleFont='Prompt'
            )
            
            st.altair_chart(chart_yoy, use_container_width=True)
            
        with col_chart_right:
            st.markdown("### 🎯 เปรียบเทียบสัดส่วนยอดขายและปริมาณสินค้า")
            
            # Calculate values dynamically based on selected months that actually have data in both years for the summary table
            common_months = [m for m in selected_months if m in [1, 2, 3]]
            if not common_months:
                common_months = [1, 2, 3] # default fallback
                
            sel_2025_df = df[(df['Year'] == 2025) & (df['MonthNum'].isin(common_months))]
            sel_2025_sales = sel_2025_df['NetSales'].sum()
            sel_2025_qty = sel_2025_df['Qty'].sum()
            sel_2025_bills = sel_2025_df['DocNo'].nunique()
            
            sel_2026_df = df[(df['Year'] == 2026) & (df['MonthNum'].isin(common_months))]
            sel_2026_sales = sel_2026_df['NetSales'].sum()
            sel_2026_qty = sel_2026_df['Qty'].sum()
            sel_2026_bills = sel_2026_df['DocNo'].nunique()
            
            
            # Create a premium HTML table with larger font sizes for maximum readability
            html_table = f"""
            <style>
                .dynamic-summary-table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-family: 'Prompt', sans-serif;
                    margin-top: 10px;
                    background-color: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                }}
                .dynamic-summary-table th {{
                    background-color: #F8FAFC;
                    color: #475569;
                    font-size: 16px;
                    font-weight: 600;
                    padding: 14px 18px;
                    border-bottom: 2px solid #E2E8F0;
                    text-align: left;
                }}
                .dynamic-summary-table td {{
                    padding: 14px 18px;
                    border-bottom: 1px solid #F1F5F9;
                    color: #334155;
                    font-size: 16px;
                }}
                .dynamic-summary-table tr:last-child td {{
                    border-bottom: none;
                }}
                .dynamic-summary-table tr:hover {{
                    background-color: #F8FAFC;
                }}
                .val-highlight {{
                    font-weight: 600;
                    color: #0F172A;
                }}
            </style>
            <table class="dynamic-summary-table">
                <thead>
                    <tr>
                        <th>หัวข้อ</th>
                        <th>ปี 2025 (2568)</th>
                        <th>ปี 2026 (2569)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>ยอดขายรวม</b></td>
                        <td class="val-highlight">฿{sel_2025_sales:,.2f}</td>
                        <td class="val-highlight" style="color: #10B981;">฿{sel_2026_sales:,.2f}</td>
                    </tr>
                    <tr>
                        <td><b>จำนวนชิ้นที่ขาย</b></td>
                        <td>{sel_2025_qty:,.0f} ชิ้น</td>
                        <td style="color: #10B981; font-weight: 500;">{sel_2026_qty:,.0f} ชิ้น</td>
                    </tr>
                    <tr>
                        <td><b>จำนวนบิลที่เปิด</b></td>
                        <td>{sel_2025_bills:,.0f} บิล</td>
                        <td style="color: #10B981; font-weight: 500;">{sel_2026_bills:,.0f} บิล</td>
                    </tr>
                </tbody>
            </table>
            """
            st.markdown(html_table, unsafe_allow_html=True)
            
        # 3. Top 5 Customers & Products Section
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Aggregate top customers data first to handle selection robustly
        top_cust_df = filtered_df.groupby(['CustomerCode', 'CustomerName'])['NetSales'].sum().reset_index()
        top_cust_df = top_cust_df.sort_values(by='NetSales', ascending=False).head(5)
        
        # Retrieve selection from session state key "cust_table" robustly
        selected_customer_name = None
        if "cust_table" in st.session_state:
            sel_state = st.session_state["cust_table"]
            selected_rows = []
            if isinstance(sel_state, dict):
                selection = sel_state.get("selection", {})
                if isinstance(selection, dict):
                    selected_rows = selection.get("rows", [])
                elif hasattr(selection, "rows"):
                    selected_rows = selection.rows
            elif hasattr(sel_state, "selection"):
                selection = sel_state.selection
                if isinstance(selection, dict):
                    selected_rows = selection.get("rows", [])
                elif hasattr(selection, "rows"):
                    selected_rows = selection.rows
            
            if selected_rows and len(selected_rows) > 0:
                selected_row_idx = selected_rows[0]
                if selected_row_idx < len(top_cust_df):
                    selected_customer_name = top_cust_df.iloc[selected_row_idx]['CustomerName']
        
        # Symmetrical Layout separated into rows of columns to ensure perfect alignment
        # ROW 1: Titles
        col_title_left, col_title_right = st.columns(2)
        with col_title_left:
            st.markdown(f"### 👥 Top 5 ลูกค้าที่ทำยอดขายสูงสุด {filter_status_suffix}")
        with col_title_right:
            if selected_customer_name:
                st.markdown(f"### 📦 สินค้าขายดี 5 อันดับแรกของ '{selected_customer_name}'")
            else:
                st.markdown(f"### 📦 Top 5 สินค้าขายดีที่สุด {filter_status_suffix}")
                
        # ROW 2: Charts
        col_chart_left, col_chart_right = st.columns(2)
        with col_chart_left:
            chart_cust = alt.Chart(top_cust_df).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X('NetSales:Q', title='ยอดขายรวม (บาท)'),
                y=alt.Y('CustomerName:N', sort='-x', title='ชื่อลูกค้า'),
                color=alt.Color('NetSales:Q', scale=alt.Scale(scheme='blues'), legend=None)
            ).properties(height=280)
            
            st.altair_chart(chart_cust, use_container_width=True)
            
        with col_chart_right:
            if selected_customer_name:
                cust_filter_df = filtered_df[filtered_df['CustomerName'] == selected_customer_name]
                top_prod_df = cust_filter_df.groupby(['ProductCode', 'ProductName'])['NetSales'].sum().reset_index()
                top_prod_df = top_prod_df.sort_values(by='NetSales', ascending=False).head(5)
            else:
                top_prod_df = filtered_df.groupby(['ProductCode', 'ProductName'])['NetSales'].sum().reset_index()
                top_prod_df = top_prod_df.sort_values(by='NetSales', ascending=False).head(5)
            
            if not top_prod_df.empty:
                chart_prod = alt.Chart(top_prod_df).mark_bar(cornerRadiusEnd=4, color='#10B981').encode(
                    x=alt.X('NetSales:Q', title='ยอดขายรวม (บาท)'),
                    y=alt.Y('ProductName:N', sort='-x', title='ชื่อสินค้า'),
                    color=alt.Color('NetSales:Q', scale=alt.Scale(scheme='greens'), legend=None)
                ).properties(height=280)
                
                st.altair_chart(chart_prod, use_container_width=True)
            else:
                st.info("ไม่มีข้อมูลสินค้าขายดีสำหรับลูกค้ารายนี้ในตัวกรองปัจจุบัน")
                
        # ROW 3: Dataframes (Perfectly Symmetrical & Aligned!)
        col_table_left, col_table_right = st.columns(2)
        with col_table_left:
            display_cust_df = top_cust_df.copy()
            display_cust_df['ยอดขายรวมสุทธิ'] = display_cust_df['NetSales'].apply(lambda x: f"฿{x:,.2f}")
            display_cust_df = display_cust_df[['CustomerCode', 'CustomerName', 'ยอดขายรวมสุทธิ']].rename(
                columns={'CustomerCode': 'รหัสลูกค้า', 'CustomerName': 'ชื่อลูกค้า'}
            )
            
            st.dataframe(
                display_cust_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key="cust_table"
            )
            
        with col_table_right:
            if not top_prod_df.empty:
                display_prod_df = top_prod_df.copy()
                display_prod_df['ยอดขายรวมสุทธิ'] = display_prod_df['NetSales'].apply(lambda x: f"฿{x:,.2f}")
                display_prod_df = display_prod_df[['ProductCode', 'ProductName', 'ยอดขายรวมสุทธิ']].rename(
                    columns={'ProductCode': 'รหัสสินค้า', 'ProductName': 'ชื่อสินค้า'}
                )
                
                st.dataframe(display_prod_df, use_container_width=True, hide_index=True)
            else:
                st.info("ไม่มีข้อมูลสินค้าขายดีสำหรับลูกค้ารายนี้ในตัวกรองปัจจุบัน")

    # -------------------------------------------------------------
    # TAB 2: CUSTOMER DEEP DIVE
    # -------------------------------------------------------------
    with tab_customers:
        st.markdown("### 👥 วิเคราะห์และเจาะลึกพฤติกรรมการซื้อรายลูกค้า")
        
        # Customer Dropdown Selector
        all_customers = sorted(df['CustomerName'].dropna().unique())
        selected_cust = st.selectbox("เลือกรายชื่อลูกค้าที่คุณต้องการเจาะลึก:", options=all_customers)
        
        if selected_cust:
            cust_df = df[df['CustomerName'] == selected_cust]
            
            cust_code = cust_df['CustomerCode'].iloc[0] if not cust_df.empty else ""
            cust_sales_total = cust_df['NetSales'].sum()
            cust_qty_total = cust_df['Qty'].sum()
            cust_trx_count = cust_df['DocNo'].nunique()
            
            # Display selected customer summary metrics
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                st.metric("รหัสลูกค้า & ชื่อลูกค้า", f"{cust_code}", f"{selected_cust}")
            with cc2:
                st.metric("ยอดซื้อสะสมทั้งหมด", f"฿{cust_sales_total:,.2f}", f"จำนวนสินค้า: {cust_qty_total:,.0f} ชิ้น")
            with cc3:
                st.metric("จำนวนบิล/การสั่งซื้อทั้งหมด", f"{cust_trx_count} ครั้ง", f"เฉลี่ยต่อบิล: ฿{cust_sales_total/max(1, cust_trx_count):,.2f}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_cust_left, col_cust_right = st.columns([3, 2])
            
            with col_cust_left:
                st.markdown(f"#### 📦 Top 5 สินค้าที่ '{selected_cust}' ซื้อยอดสูงสุด")
                
                # Top 5 products bought by this customer
                cust_top_prod = cust_df.groupby(['ProductCode', 'ProductName'])['NetSales'].sum().reset_index()
                cust_top_prod = cust_top_prod.sort_values(by='NetSales', ascending=False).head(5)
                
                chart_cust_prod = alt.Chart(cust_top_prod).mark_bar(cornerRadiusEnd=4).encode(
                    x=alt.X('NetSales:Q', title='ยอดขายรวม (บาท)'),
                    y=alt.Y('ProductName:N', sort='-x', title='ชื่อสินค้า'),
                    color=alt.Color('NetSales:Q', scale=alt.Scale(scheme='purples'), legend=None)
                ).properties(height=280)
                
                st.altair_chart(chart_cust_prod, use_container_width=True)
                
            with col_cust_right:
                st.markdown("#### 💰 ประวัติราคาซื้อต่อหน่วยที่ได้รับ (Unit Price)")
                
                # Details table with unit prices
                # Show unique unit prices purchased per product
                cust_price_table = cust_df.groupby(['ProductCode', 'ProductName']).agg({
                    'UnitPrice': ['min', 'max', 'mean'],
                    'Qty': 'sum',
                    'NetSales': 'sum'
                }).reset_index()
                
                # Flatten multiindex columns and store raw numeric values
                cust_price_table.columns = ['รหัสสินค้า', 'ชื่อสินค้า', 'ราคาต่ำสุด_raw', 'ราคาสูงสุด_raw', 'ราคาเฉลี่ย_raw', 'จำนวนชิ้นรวม_raw', 'ยอดซื้อรวม_raw']
                cust_price_table = cust_price_table.sort_values(by='ยอดซื้อรวม_raw', ascending=False).head(10)
                
                # Format to strings in pandas to guarantee perfect Baht and comma display
                cust_price_table['ราคาต่ำสุด'] = cust_price_table['ราคาต่ำสุด_raw'].apply(lambda x: f"฿{x:,.2f}")
                cust_price_table['ราคาสูงสุด'] = cust_price_table['ราคาสูงสุด_raw'].apply(lambda x: f"฿{x:,.2f}")
                cust_price_table['ราคาเฉลี่ย'] = cust_price_table['ราคาเฉลี่ย_raw'].apply(lambda x: f"฿{x:,.2f}")
                cust_price_table['จำนวนชิ้นรวม'] = cust_price_table['จำนวนชิ้นรวม_raw'].apply(lambda x: f"{x:,.0f}")
                cust_price_table['ยอดซื้อรวม'] = cust_price_table['ยอดซื้อรวม_raw'].apply(lambda x: f"฿{x:,.2f}")
                
                display_cols = ['รหัสสินค้า', 'ชื่อสินค้า', 'ราคาต่ำสุด', 'ราคาสูงสุด', 'ราคาเฉลี่ย', 'จำนวนชิ้นรวม', 'ยอดซื้อรวม']
                st.write("ตารางแสดงรายการสินค้า 10 ลำดับแรกและระดับราคาต่อหน่วยที่ได้รับ:")
                st.dataframe(cust_price_table[display_cols], use_container_width=True, hide_index=True)
                
            # YoY Comparison for this customer
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f"#### 📅 ยอดซื้อเปรียบเทียบปี 2025 vs 2026 ของ '{selected_cust}'")
            
            cust_yoy = cust_df.groupby(['Year', 'MonthNum', 'MonthTH'])['NetSales'].sum().reset_index()
            cust_yoy['YearStr'] = cust_yoy['Year'].astype(str)
            
            chart_cust_yoy = alt.Chart(cust_yoy).mark_bar().encode(
                x=alt.X('MonthTH:N', title='เดือน', sort=alt.SortField('MonthNum')),
                y=alt.Y('NetSales:Q', title='ยอดซื้อ (บาท)'),
                color=alt.Color('YearStr:N', title='ปี ค.ศ.', scale=alt.Scale(domain=['2025', '2026'], range=['#8B5CF6', '#10B981'])),
                xOffset='YearStr:N'
            ).properties(height=300)
            
            st.altair_chart(chart_cust_yoy, use_container_width=True)

    # -------------------------------------------------------------
    # TAB 3: PRODUCT & PRICES
    # -------------------------------------------------------------
    with tab_products:
        st.markdown("### 📦 ค้นหาและวิเคราะห์ราคาสินค้าแยกรายลูกค้า (Dual-Search Pricing Lookup)")
        st.markdown("ระบบวิเคราะห์ราคาต่อหน่วยแยกตามรายลูกค้าและรายสินค้า เพื่อตรวจสอบระดับราคาซื้อขายจริง ประวัติการซื้อ และส่วนลดที่ลูกค้าได้รับ")
        
        # Dual-search layout: Column 1 for Customer, Column 2 for Product
        col_search_left, col_search_right = st.columns(2)
        
        with col_search_left:
            all_customers_pricing = sorted(df['CustomerName'].dropna().unique())
            selected_cust_pricing = st.selectbox(
                "👤 ส่วนที่ 1: ค้นหาด้วยชื่อลูกค้า (Customer Name)",
                options=["-- เลือกลูกค้าทั้งหมด --"] + all_customers_pricing,
                key="pricing_cust_select"
            )
            
        with col_search_right:
            # Filter product options dynamically based on the selected customer
            if selected_cust_pricing != "-- เลือกลูกค้าทั้งหมด --":
                cust_prods = sorted(df[df['CustomerName'] == selected_cust_pricing]['ProductName'].dropna().unique())
                show_all_checkbox = st.checkbox("แสดงสินค้าทั้งหมดของโรงงาน (แม้ลูกค้ายังไม่เคยซื้อ)", value=False)
                if show_all_checkbox:
                    prods_options = sorted(df['ProductName'].dropna().unique())
                else:
                    prods_options = cust_prods
            else:
                prods_options = sorted(df['ProductName'].dropna().unique())
                
            selected_prod_pricing = st.selectbox(
                "📦 ส่วนที่ 2: ค้นหาด้วยสินค้า (Product Name)",
                options=["-- เลือกสินค้า --"] + prods_options,
                key="pricing_prod_select"
            )
            
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Handle the four pricing lookup scenarios based on selection:
        if selected_cust_pricing != "-- เลือกลูกค้าทั้งหมด --" and selected_prod_pricing != "-- เลือกสินค้า --":
            # Case A: Specific Customer + Specific Product selected
            cust_prod_df = df[(df['CustomerName'] == selected_cust_pricing) & (df['ProductName'] == selected_prod_pricing)]
            
            # General factory-wide statistics for the same product to compare
            factory_prod_df = df[df['ProductName'] == selected_prod_pricing]
            factory_avg = factory_prod_df['UnitPrice'].mean() if not factory_prod_df.empty else 0.0
            
            if not cust_prod_df.empty:
                prod_code = cust_prod_df['ProductCode'].iloc[0]
                min_p = cust_prod_df['UnitPrice'].min()
                max_p = cust_prod_df['UnitPrice'].max()
                avg_p = cust_prod_df['UnitPrice'].mean()
                total_qty = cust_prod_df['Qty'].sum()
                total_sales = cust_prod_df['NetSales'].sum()
                
                # Display metrics
                st.markdown(f"#### 📊 ข้อมูลราคาซื้อขายจริงของ **{selected_cust_pricing}** กับสินค้า **{selected_prod_pricing}**")
                
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("ราคาเฉลี่ยที่ซื้อจริง", f"฿{avg_p:,.2f}", f"ต่ำสุด ฿{min_p:,.2f} - สูงสุด ฿{max_p:,.2f}")
                with m2:
                    st.metric("ราคาเฉลี่ยโรงงานทั้งหมด", f"฿{factory_avg:,.2f}", 
                              delta=f"ประหยัดกว่าเฉลี่ย ฿{factory_avg - avg_p:,.2f}" if factory_avg > avg_p else f"สูงกว่าเฉลี่ย ฿{avg_p - factory_avg:,.2f}",
                              delta_color="normal" if factory_avg != avg_p else "off")
                with m3:
                    st.metric("ปริมาณที่ซื้อสะสมรวม", f"{total_qty:,.0f} ชิ้น", f"รหัสสินค้า: {prod_code}")
                with m4:
                    st.metric("ยอดซื้อสุทธิสะสมรวม", f"฿{total_sales:,.2f}")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 📑 ประวัติการออกบิลและการซื้อขายรายรายการ (Transaction History)")
                
                # Detailed invoice table
                display_trx = cust_prod_df.copy().sort_values(by='ParsedDate', ascending=False)
                display_trx['วันที่'] = display_trx['Date']
                display_trx['เลขที่เอกสาร'] = display_trx['DocNo']
                display_trx['จำนวนชิ้น'] = display_trx['Qty'].apply(lambda x: f"{x:,.0f}")
                display_trx['ราคาต่อหน่วย'] = display_trx['UnitPrice'].apply(lambda x: f"฿{x:,.2f}")
                display_trx['ยอดซื้อสุทธิ'] = display_trx['NetSales'].apply(lambda x: f"฿{x:,.2f}")
                display_trx['เลขอ้างอิง'] = display_trx['Ref'].fillna("-")
                
                display_cols = ['วันที่', 'เลขที่เอกสาร', 'จำนวนชิ้น', 'ราคาต่อหน่วย', 'ยอดซื้อสุทธิ', 'เลขอ้างอิง']
                st.dataframe(display_trx[display_cols], use_container_width=True, hide_index=True)
            else:
                st.warning(f"⚠️ ลูกค้า **'{selected_cust_pricing}'** ยังไม่เคยซื้อสินค้า **'{selected_prod_pricing}'** ในฐานข้อมูล")
                st.info(f"💡 ราคาเฉลี่ยของสินค้าชิ้นนี้ในภาพรวมโรงงานคือ **฿{factory_avg:,.2f}** (จากลูกค้าท่านอื่นที่เคยซื้อ)")
                
        elif selected_cust_pricing != "-- เลือกลูกค้าทั้งหมด --" and selected_prod_pricing == "-- เลือกสินค้า --":
            # Case B: Specific Customer selected BUT No Product selected
            st.markdown(f"#### 📊 สรุปรายการสินค้าและระดับราคาที่ลูกค้า **{selected_cust_pricing}** เคยสั่งซื้อทั้งหมด")
            
            cust_all_df = df[df['CustomerName'] == selected_cust_pricing]
            
            if not cust_all_df.empty:
                cust_code = cust_all_df['CustomerCode'].iloc[0]
                total_cust_sales = cust_all_df['NetSales'].sum()
                total_cust_qty = cust_all_df['Qty'].sum()
                unique_prods_count = cust_all_df['ProductName'].nunique()
                
                # Metrics
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    st.metric("รหัสลูกค้า & ชื่อลูกค้า", f"{cust_code}", f"{selected_cust_pricing}")
                with mc2:
                    st.metric("ยอดซื้อสะสมทั้งหมด", f"฿{total_cust_sales:,.2f}", f"จำนวนสินค้า: {total_cust_qty:,.0f} ชิ้น")
                with mc3:
                    st.metric("จำนวนชนิดสินค้าที่ซื้อ", f"{unique_prods_count} ชนิดสินค้า")
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 📦 ตารางสรุปราคาสินค้าแต่ละชนิดที่เคยซื้อ")
                
                # Summarize products purchased by this customer
                prod_summary = cust_all_df.groupby(['ProductCode', 'ProductName']).agg({
                    'UnitPrice': ['min', 'max', 'mean'],
                    'Qty': 'sum',
                    'NetSales': 'sum'
                }).reset_index()
                
                # Flatten multiindex columns and store raw numeric values
                prod_summary.columns = ['ProductCode', 'ProductName', 'min_p', 'max_p', 'avg_p', 'total_qty', 'total_sales']
                prod_summary = prod_summary.sort_values(by='total_sales', ascending=False)
                
                # Format to strings in pandas
                prod_summary['ราคาต่ำสุด'] = prod_summary['min_p'].apply(lambda x: f"฿{x:,.2f}")
                prod_summary['ราคาสูงสุด'] = prod_summary['max_p'].apply(lambda x: f"฿{x:,.2f}")
                prod_summary['ราคาเฉลี่ย'] = prod_summary['avg_p'].apply(lambda x: f"฿{x:,.2f}")
                prod_summary['จำนวนชิ้นรวม'] = prod_summary['total_qty'].apply(lambda x: f"{x:,.0f}")
                prod_summary['ยอดซื้อสุทธิรวม'] = prod_summary['total_sales'].apply(lambda x: f"฿{x:,.2f}")
                
                display_cols = ['ProductCode', 'ProductName', 'ราคาต่ำสุด', 'ราคาสูงสุด', 'ราคาเฉลี่ย', 'จำนวนชิ้นรวม', 'ยอดซื้อสุทธิรวม']
                st.dataframe(
                    prod_summary[display_cols].rename(columns={
                        'ProductCode': 'รหัสสินค้า',
                        'ProductName': 'ชื่อสินค้า'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("ไม่มีข้อมูลการซื้อขายสำหรับลูกค้ารายนี้")
                
        elif selected_cust_pricing == "-- เลือกลูกค้าทั้งหมด --" and selected_prod_pricing != "-- เลือกสินค้า --":
            # Case C: All Customers selected BUT Specific Product selected
            st.markdown(f"#### 📊 สรุปประวัติการขายและระดับราคาตลาดรวมของสินค้า **{selected_prod_pricing}**")
            
            prod_df = df[df['ProductName'] == selected_prod_pricing]
            
            if not prod_df.empty:
                prod_code = prod_df['ProductCode'].iloc[0]
                prod_sales_total = prod_df['NetSales'].sum()
                prod_qty_total = prod_df['Qty'].sum()
                
                # Pricing info
                min_price = prod_df['UnitPrice'].min()
                max_price = prod_df['UnitPrice'].max()
                avg_price = prod_df['UnitPrice'].mean()
                unique_buyers = prod_df['CustomerName'].nunique()
                
                cp1, cp2, cp3, cp4 = st.columns(4)
                with cp1:
                    st.metric("รหัสสินค้า & ชื่อสินค้า", f"{prod_code}", f"{selected_prod_pricing}")
                with cp2:
                    st.metric("ราคาขายต่อหน่วยเฉลี่ยรวม", f"฿{avg_price:,.2f}", f"ราคาระหว่าง: ฿{min_price:,.2f} - ฿{max_price:,.2f}")
                with cp3:
                    st.metric("ปริมาณชิ้นที่ขายสะสมรวม", f"{prod_qty_total:,.0f} ชิ้น", f"จำนวนลูกค้าที่เคยซื้อ: {unique_buyers} ราย")
                with cp4:
                    st.metric("ยอดขายสุทธิรวมสะสม", f"฿{prod_sales_total:,.2f}")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 👥 รายชื่อลูกค้าและระดับราคาต่อหน่วยที่แต่ละรายเคยซื้อ")
                
                # Top buyers of this product
                prod_buyers = prod_df.groupby(['CustomerCode', 'CustomerName', 'UnitPrice']).agg({
                    'Qty': 'sum',
                    'NetSales': 'sum'
                }).reset_index().sort_values(by='NetSales', ascending=False)
                
                # Format
                display_buyers = prod_buyers.copy()
                display_buyers['ราคาขายต่อหน่วย'] = display_buyers['UnitPrice'].apply(lambda x: f"฿{x:,.2f}")
                display_buyers['จำนวนชิ้นที่ซื้อ'] = display_buyers['Qty'].apply(lambda x: f"{x:,.0f}")
                display_buyers['ยอดซื้อสุทธิรวม'] = display_buyers['NetSales'].apply(lambda x: f"฿{x:,.2f}")
                
                display_buyers = display_buyers[['CustomerCode', 'CustomerName', 'ราคาขายต่อหน่วย', 'จำนวนชิ้นที่ซื้อ', 'ยอดซื้อสุทธิรวม']].rename(
                    columns={'CustomerCode': 'รหัสลูกค้า', 'CustomerName': 'ชื่อลูกค้า'}
                )
                
                st.dataframe(display_buyers, use_container_width=True, hide_index=True)
            else:
                st.info("ไม่มีข้อมูลยอดขายสำหรับสินค้าชนิดนี้")
                
        else:
            # Case D: No selections made
            st.info("💡 กรุณาเลือกชื่อลูกค้าใน **ส่วนที่ 1** หรือเลือกชื่อสินค้าใน **ส่วนที่ 2** ด้านบนเพื่อเริ่มต้นสืบค้นประวัติราคาต่อหน่วย")
            
            # Renders a premium summary of all products sold
            st.markdown("#### 📈 ภาพรวมสินค้าที่มียอดขายสูงสุดของโรงงาน")
            top_all_prods = df.groupby(['ProductCode', 'ProductName']).agg({
                'UnitPrice': ['min', 'max', 'mean'],
                'Qty': 'sum',
                'NetSales': 'sum'
            }).reset_index()
            top_all_prods.columns = ['ProductCode', 'ProductName', 'min_p', 'max_p', 'avg_p', 'total_qty', 'total_sales']
            top_all_prods = top_all_prods.sort_values(by='total_sales', ascending=False).head(10)
            
            top_all_prods['ราคาต่ำสุด'] = top_all_prods['min_p'].apply(lambda x: f"฿{x:,.2f}")
            top_all_prods['ราคาสูงสุด'] = top_all_prods['max_p'].apply(lambda x: f"฿{x:,.2f}")
            top_all_prods['ราคาเฉลี่ย'] = top_all_prods['avg_p'].apply(lambda x: f"฿{x:,.2f}")
            top_all_prods['จำนวนชิ้นรวม'] = top_all_prods['total_qty'].apply(lambda x: f"{x:,.0f}")
            top_all_prods['ยอดรวมสุทธิ'] = top_all_prods['total_sales'].apply(lambda x: f"฿{x:,.2f}")
            
            display_cols = ['ProductCode', 'ProductName', 'ราคาต่ำสุด', 'ราคาสูงสุด', 'ราคาเฉลี่ย', 'จำนวนชิ้นรวม', 'ยอดรวมสุทธิ']
            st.dataframe(
                top_all_prods[display_cols].rename(columns={
                    'ProductCode': 'รหัสสินค้า',
                    'ProductName': 'ชื่อสินค้า'
                }),
                use_container_width=True,
                hide_index=True
            )

    # -------------------------------------------------------------
    # TAB 4: SEARCH RAW DATA
    # -------------------------------------------------------------
    with tab_raw:
        st.markdown("### 🔍 ค้นหาข้อมูลยอดขายดิบและดาวน์โหลด (Search and Export Raw Data)")
        st.write("คุณสามารถป้อนคำค้นหา (เช่น เลขที่เอกสาร, ชื่อลูกค้า, ชื่อสินค้า, รหัสสินค้า, หมายเลขอ้างอิง) เพื่อกรองข้อมูล และทำการดาวน์โหลดผลลัพธ์เป็นไฟล์ CSV ได้ทันที")
        
        # Text Search Box
        search_query = st.text_input("ป้อนคำค้นหา (Search):", placeholder="ตัวอย่าง: IV0027476, ทีวายเค, V-BELT, SD2501")
        
        # Apply Text Search Filter
        if search_query:
            search_df = df[
                df['DocNo'].astype(str).str.contains(search_query, case=False, na=False) |
                df['CustomerName'].astype(str).str.contains(search_query, case=False, na=False) |
                df['CustomerCode'].astype(str).str.contains(search_query, case=False, na=False) |
                df['ProductName'].astype(str).str.contains(search_query, case=False, na=False) |
                df['ProductCode'].astype(str).str.contains(search_query, case=False, na=False) |
                df['Ref'].astype(str).str.contains(search_query, case=False, na=False)
            ]
        else:
            search_df = filtered_df
            
        st.markdown(f"พบข้อมูลทั้งหมด **{len(search_df):,}** แถว")
        
        # Display the table
        display_cols = ['Date', 'DocNo', 'CustomerCode', 'CustomerName', 'ProductName', 'ProductCode', 'Qty', 'UnitPrice', 'NetSales', 'Ref']
        
        # Pre-format values in Pandas to bypass st.column_config bug with Thai headers
        display_search_df = search_df[display_cols].copy()
        display_search_df['Qty'] = display_search_df['Qty'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
        display_search_df['UnitPrice'] = display_search_df['UnitPrice'].apply(lambda x: f"฿{x:,.2f}" if pd.notnull(x) else "")
        display_search_df['NetSales'] = display_search_df['NetSales'].apply(lambda x: f"฿{x:,.2f}" if pd.notnull(x) else "")
        
        st.dataframe(
            display_search_df.rename(columns={
                'Date': 'วันที่',
                'DocNo': 'เลขที่เอกสาร',
                'CustomerCode': 'รหัสลูกค้า',
                'CustomerName': 'ชื่อลูกค้า',
                'ProductName': 'ชื่อสินค้า',
                'ProductCode': 'รหัสสินค้า',
                'Qty': 'จำนวนชิ้น',
                'UnitPrice': 'ราคาต่อหน่วย',
                'NetSales': 'ยอดขายสุทธิ',
                'Ref': 'เลขอ้างอิง'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Download Button
        csv_download = search_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูลนี้เป็นไฟล์ CSV",
            data=csv_download,
            file_name="filtered_sales_data.csv",
            mime="text/csv"
        )
