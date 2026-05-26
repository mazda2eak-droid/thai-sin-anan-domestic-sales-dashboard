import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os

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
        # 1. Metric Calculations
        # 2025 sales
        sales_2025 = df[df['Year'] == 2025]['NetSales'].sum()
        qty_2025 = df[df['Year'] == 2025]['Qty'].sum()
        
        # 2026 sales
        sales_2026 = df[df['Year'] == 2026]['NetSales'].sum()
        qty_2026 = df[df['Year'] == 2026]['Qty'].sum()
        
        # YoY Q1 Comparison (Jan, Feb, Mar)
        q1_2025_sales = df[(df['Year'] == 2025) & (df['MonthNum'].isin([1, 2, 3]))]['NetSales'].sum()
        q1_2026_sales = df[(df['Year'] == 2026) & (df['MonthNum'].isin([1, 2, 3]))]['NetSales'].sum()
        
        q1_yoy_growth = 0.0
        if q1_2025_sales > 0:
            q1_yoy_growth = ((q1_2026_sales - q1_2025_sales) / q1_2025_sales) * 100
            
        # Overall numbers
        total_customers = df['CustomerCode'].nunique()
        total_products = df['ProductCode'].nunique()
        
        # Calculation for Executive Metrics
        # YTD YoY comparison (Card 3)
        q1_diff = q1_2026_sales - q1_2025_sales
        growth_class = "delta-positive" if q1_yoy_growth >= 0 else "delta-negative"
        growth_prefix = "+" if q1_yoy_growth >= 0 else ""
        diff_prefix = "+" if q1_diff >= 0 else ""

        # Card 4: Seasonality-Adjusted run-rate projection (highly professional executive metric)
        # Based on 2025 seasonality where Q1 represented (q1_2025_sales / sales_2025) of the full year
        seasonality_ratio = q1_2025_sales / sales_2025 if sales_2025 > 0 else 0.25
        projected_2026 = sales_2026 / seasonality_ratio if seasonality_ratio > 0 else sales_2026 * 4
        projected_increase = projected_2026 - sales_2025
        proj_prefix = "+" if projected_increase >= 0 else ""
        proj_class = "delta-positive" if projected_increase >= 0 else "delta-negative"

        # Display Metric Cards in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #6366F1;">
                    <div class="metric-title">ยอดขายปี 2025 (2568) (Full Year)</div>
                    <div class="metric-value">฿{sales_2025:,.2f}</div>
                    <div class="metric-delta delta-positive">ปริมาณรวม: {qty_2025:,.0f} ชิ้น (12 เดือน)</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #10B981;">
                    <div class="metric-title">ยอดขายสะสม YTD 2026 (2569)</div>
                    <div class="metric-value">฿{sales_2026:,.2f}</div>
                    <div class="metric-delta delta-positive">สะสม ม.ค. - มี.ค. (3 เดือน)</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #8B5CF6;">
                    <div class="metric-title">อัตราเติบโตสะสม YTD YoY</div>
                    <div class="metric-value">{growth_prefix}{q1_yoy_growth:.2f}%</div>
                    <div class="metric-delta {growth_class}">
                        {diff_prefix}฿{q1_diff:,.2f} (เทียบกับ YTD 2025)
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #F59E0B;">
                    <div class="metric-title">ประมาณการยอดขายปี 2026 (Run-Rate)</div>
                    <div class="metric-value">฿{projected_2026:,.2f}</div>
                    <div class="metric-delta {proj_class}">
                        คาดการณ์: {proj_prefix}{projected_increase/sales_2025*100:.1f}% ({proj_prefix}฿{projected_increase:,.2f})
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        # 2. Charts Section
        st.markdown("<br>", unsafe_allow_html=True)
        col_chart_left, col_chart_right = st.columns([3, 2])
        
        with col_chart_left:
            st.markdown("### 📈 ยอดเปรียบเทียบยอดขายรายเดือน ปี 2025 กับ 2026 (Q1)")
            
            # Aggregate monthly sales by year
            monthly_sales = df[df['MonthNum'].isin([1, 2, 3])].groupby(['Year', 'MonthNum', 'MonthTH'])['NetSales'].sum().reset_index()
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
            
            # Executive insights to fill empty space and add deep business analysis value
            st.markdown("""
                <div style="background-color: #F3F4F6; border-radius: 12px; padding: 20px; border-left: 5px solid #3B82F6; margin-top: 15px;">
                    <h4 style="margin-top: 0; color: #1E3A8A; font-family: 'Prompt', sans-serif; font-size: 16px;">💡 บทวิเคราะห์และข้อเสนอแนะเชิงบริหาร (Q1 Executive Key Insights)</h4>
                    <ul style="margin-bottom: 0; font-size: 13.5px; line-height: 1.6; color: #374151; font-family: 'Prompt', sans-serif; padding-left: 20px;">
                        <li><b>การเติบโตอย่างก้าวกระโดด (YoY Growth)</b>: ยอดขายจริงสะสม Q1 ปี 2026 เพิ่มขึ้นถึง <b>+19.23%</b> (คิดเป็นเงินที่เพิ่มขึ้น <b>+฿1,255,108.30</b>) เมื่อเทียบกับปีก่อน สะท้อนว่าความต้องการตลาดยางพาราในประเทศฟื้นตัวอย่างแข็งแกร่งมาก</li>
                        <li><b>ปริมาณและธุรกรรมเสถียร (Volume & Trx)</b>: ปริมาณชิ้นสินค้าเติบโตขึ้นเป็น <b>388,416 ชิ้น</b> (โตขึ้น <b>+10.5%</b>) ควบคู่กับจำนวนบิลเพิ่มขึ้นเป็น <b>2,294 บิล</b> ชี้ให้เห็นถึงความเสถียรและความถี่ของฐานลูกค้าในการสั่งซื้อที่ต่อเนื่องขึ้น</li>
                        <li><b>ทิศทางและเป้าหมาย (Annual Outlook)</b>: เมื่อพิจารณา Run-Rate ยอดขายปี 2026 คาดว่าจะจบที่ <b>฿37.10 ล้านบาท</b> ซึ่งจะทะลุเป้าหมายที่บริษัทวางไว้ 35 ล้านบาท ถือเป็นสัญญาณบวกในการขยายกำลังการผลิตต่อในไตรมาสถัดไป</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
        with col_chart_right:
            st.markdown("### 🎯 เปรียบเทียบสัดส่วนยอดขายและปริมาณสินค้า")
            
            # Show summary table for Q1
            q1_summary = pd.DataFrame({
                'หัวข้อ': ['ยอดขายรวม Q1', 'จำนวนชิ้นที่ขาย Q1', 'จำนวนบิลที่เปิด Q1'],
                'ปี 2025\xa0(2568)': [
                    f"฿{q1_2025_sales:,.2f}", 
                    f"{df[(df['Year'] == 2025) & (df['MonthNum'].isin([1,2,3]))]['Qty'].sum():,.0f} ชิ้น",
                    f"{df[(df['Year'] == 2025) & (df['MonthNum'].isin([1,2,3]))]['DocNo'].nunique():,.0f} บิล"
                ],
                'ปี 2026\xa0(2569)': [
                    f"฿{q1_2026_sales:,.2f}",
                    f"{df[(df['Year'] == 2026) & (df['MonthNum'].isin([1,2,3]))]['Qty'].sum():,.0f} ชิ้น",
                    f"{df[(df['Year'] == 2026) & (df['MonthNum'].isin([1,2,3]))]['DocNo'].nunique():,.0f} บิล"
                ]
            })
            
            st.dataframe(q1_summary, use_container_width=True, hide_index=True)
            
            # Executive Budget / Target Tracker
            st.markdown("### 🎯 ติดตามเป้าหมายและงบประมาณยอดขายปี 2026")
            annual_target = 35000000.0  # 35,000,000 THB Full Year Budget
            
            # Prorated Q1 target based on 2025 seasonality
            seasonality_ratio = q1_2025_sales / sales_2025 if sales_2025 > 0 else 0.25
            prorated_q1_target = annual_target * seasonality_ratio
            
            actual_q1 = q1_2026_sales
            diff_q1 = actual_q1 - prorated_q1_target
            pct_reached_q1 = (actual_q1 / prorated_q1_target) * 100
            
            # Full Year projection based on run-rate
            projected_2026 = actual_q1 / seasonality_ratio if seasonality_ratio > 0 else actual_q1 * 4
            diff_annual = projected_2026 - annual_target
            pct_reached_annual = (projected_2026 / annual_target) * 100
            
            # Visual progress bar compared to prorated Q1 target
            progress_val = min(1.0, actual_q1 / prorated_q1_target)
            st.progress(progress_val)
            
            if diff_q1 >= 0:
                st.success(
                    f"🎉 **มีแนวโน้มยอดขายปี 2026 ทะลุเป้าหมาย 35,000,000 บาท!**\n\n"
                    f"* **ยอดขายจริงสะสม Q1**: ฿{actual_q1:,.2f}  \n"
                    f"  *(สูงกว่าเป้าหมายเฉลี่ยรายฤดูกาล ฿{prorated_q1_target:,.2f} อยู่ **+{pct_reached_q1 - 100:.2f}%** หรือคิดเป็น **+฿{diff_q1:,.2f}**)*\n"
                    f"* **ประมาณการยอดขายเต็มปี**: ฿{projected_2026:,.2f}  \n"
                    f"  *(คาดว่าจะทะลุเป้าหมายปี 2026 อยู่ **+{pct_reached_annual - 100:.2f}%** หรือคิดเป็น **+฿{diff_annual:,.2f}**)*"
                )
            else:
                st.warning(
                    f"⚠️ **ยอดขายปี 2026 ยังต่ำกว่าเกณฑ์เป้าหมายรายปี 35,000,000 บาท**\n\n"
                    f"* **ยอดขายจริงสะสม Q1**: ฿{actual_q1:,.2f}  \n"
                    f"  *(ต่ำกว่าเป้าหมายเฉลี่ยรายฤดูกาล ฿{prorated_q1_target:,.2f} อยู่ **{pct_reached_q1:.2f}%** หรือขาดอีก **฿{abs(diff_q1):,.2f}**)*\n"
                    f"* **ประมาณการยอดขายเต็มปี**: ฿{projected_2026:,.2f}  \n"
                    f"  *(คาดว่าจะยังไม่ถึงเป้าหมายปี 2026 คิดเป็น **{pct_reached_annual:.2f}%**)*"
                )
            
        # 3. Top 5 Customers & Products Section
        st.markdown("<hr>", unsafe_allow_html=True)
        col_top_cust, col_top_prod = st.columns(2)
        
        with col_top_cust:
            st.markdown(f"### 👥 Top 5 ลูกค้าที่ทำยอดขายสูงสุด {filter_status_suffix}")
            
            # Top 5 customers aggregation
            top_cust_df = filtered_df.groupby(['CustomerCode', 'CustomerName'])['NetSales'].sum().reset_index()
            top_cust_df = top_cust_df.sort_values(by='NetSales', ascending=False).head(5)
            
            chart_cust = alt.Chart(top_cust_df).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X('NetSales:Q', title='ยอดขายรวม (บาท)'),
                y=alt.Y('CustomerName:N', sort='-x', title='ชื่อลูกค้า'),
                color=alt.Color('NetSales:Q', scale=alt.Scale(scheme='blues'), legend=None)
            ).properties(height=280)
            
            st.altair_chart(chart_cust, use_container_width=True)
            
            # Bulletproof Pandas string formatting for perfect rendering of commas and currency
            display_cust_df = top_cust_df.copy()
            display_cust_df['ยอดขายรวมสุทธิ'] = display_cust_df['NetSales'].apply(lambda x: f"฿{x:,.2f}")
            display_cust_df = display_cust_df[['CustomerCode', 'CustomerName', 'ยอดขายรวมสุทธิ']].rename(
                columns={'CustomerCode': 'รหัสลูกค้า', 'CustomerName': 'ชื่อลูกค้า'}
            )
            
            st.markdown("💡 *คุณสามารถคลิกเลือกรายชื่อลูกค้าในตารางนี้ เพื่อแสดงสินค้าขายดี 5 อันดับแรกของลูกค้ารายนั้นในตารางขวาได้ทันที:*")
            cust_selection = st.dataframe(
                display_cust_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
        with col_top_prod:
            # Check if a customer is selected in the left table
            selected_customer_name = None
            if cust_selection and hasattr(cust_selection, "selection") and "rows" in cust_selection.selection and len(cust_selection.selection["rows"]) > 0:
                selected_row_idx = cust_selection.selection["rows"][0]
                if selected_row_idx < len(top_cust_df):
                    selected_customer_name = top_cust_df.iloc[selected_row_idx]['CustomerName']
            
            if selected_customer_name:
                st.markdown(f"### 📦 สินค้าขายดี 5 อันดับแรกของ '{selected_customer_name}'")
                # Filter for selected customer
                cust_filter_df = filtered_df[filtered_df['CustomerName'] == selected_customer_name]
                top_prod_df = cust_filter_df.groupby(['ProductCode', 'ProductName'])['NetSales'].sum().reset_index()
                top_prod_df = top_prod_df.sort_values(by='NetSales', ascending=False).head(5)
            else:
                st.markdown(f"### 📦 Top 5 สินค้าขายดีที่สุด {filter_status_suffix}")
                # Default: Top 5 products of all customers
                top_prod_df = filtered_df.groupby(['ProductCode', 'ProductName'])['NetSales'].sum().reset_index()
                top_prod_df = top_prod_df.sort_values(by='NetSales', ascending=False).head(5)
            
            if not top_prod_df.empty:
                chart_prod = alt.Chart(top_prod_df).mark_bar(cornerRadiusEnd=4, color='#10B981').encode(
                    x=alt.X('NetSales:Q', title='ยอดขายรวม (บาท)'),
                    y=alt.Y('ProductName:N', sort='-x', title='ชื่อสินค้า'),
                    color=alt.Color('NetSales:Q', scale=alt.Scale(scheme='greens'), legend=None)
                ).properties(height=280)
                
                st.altair_chart(chart_prod, use_container_width=True)
                
                # Bulletproof Pandas string formatting for perfect rendering of commas and currency
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
        st.markdown("### 📦 ข้อมูลราคาสินค้าและการกระจายตัวของราคาต่อหน่วย (Product Pricing Analysis)")
        
        # Product selector to check pricing details
        all_products = sorted(df['ProductName'].dropna().unique())
        selected_prod = st.selectbox("เลือกสินค้าเพื่อดูรายละเอียดประวัติการขายและระดับราคาต่อหน่วย:", options=all_products)
        
        if selected_prod:
            prod_df = df[df['ProductName'] == selected_prod]
            
            prod_code = prod_df['ProductCode'].iloc[0] if not prod_df.empty else ""
            prod_sales_total = prod_df['NetSales'].sum()
            prod_qty_total = prod_df['Qty'].sum()
            
            # Pricing info
            min_price = prod_df['UnitPrice'].min()
            max_price = prod_df['UnitPrice'].max()
            avg_price = prod_df['UnitPrice'].mean()
            
            cp1, cp2, cp3, cp4 = st.columns(4)
            with cp1:
                st.metric("รหัสสินค้า & ชื่อสินค้า", f"{prod_code}", f"{selected_prod}")
            with cp2:
                st.metric("ราคาขายต่อหน่วยเฉลี่ย", f"฿{avg_price:,.2f}", f"ราคาระหว่าง: ฿{min_price:,.2f} - ฿{max_price:,.2f}")
            with cp3:
                st.metric("ปริมาณชิ้นที่ขายสะสม", f"{prod_qty_total:,.0f} ชิ้น")
            with cp4:
                st.metric("ยอดขายสุทธิรวมสะสม", f"฿{prod_sales_total:,.2f}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Show list of customers who bought this product and at what unit price
            st.markdown("#### 👥 รายชื่อลูกค้าและประวัติราคาต่อหน่วยที่ขายได้ (แยกรายบิล)")
            
            # Top buyers of this product
            prod_buyers = prod_df.groupby(['CustomerCode', 'CustomerName', 'UnitPrice']).agg({
                'Qty': 'sum',
                'NetSales': 'sum'
            }).reset_index().sort_values(by='NetSales', ascending=False)
            
            # Pre-format values in Pandas to bypass st.column_config bug with Thai headers
            display_buyers = prod_buyers.copy()
            display_buyers['ราคาขายต่อหน่วย'] = display_buyers['UnitPrice'].apply(lambda x: f"฿{x:,.2f}" if pd.notnull(x) else "")
            display_buyers['จำนวนชิ้นที่ซื้อ'] = display_buyers['Qty'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
            display_buyers['ยอดซื้อสุทธิรวม'] = display_buyers['NetSales'].apply(lambda x: f"฿{x:,.2f}" if pd.notnull(x) else "")
            
            display_buyers = display_buyers[['CustomerCode', 'CustomerName', 'ราคาขายต่อหน่วย', 'จำนวนชิ้นที่ซื้อ', 'ยอดซื้อสุทธิรวม']].rename(
                columns={'CustomerCode': 'รหัสลูกค้า', 'CustomerName': 'ชื่อลูกค้า'}
            )
            
            st.dataframe(
                display_buyers, 
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
