"""
Universal Expiry Date Monitoring System - Web Platform
Streamlit Web Application

Author: Sara Abdullah
Version: 1.0.0
Date: January 30, 2025
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io
import base64
from pathlib import Path
import json

# Page configuration
st.set_page_config(
    page_title="Expiry Monitoring Platform",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful design
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #0891B2 0%, #06B6D4 100%);
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(8, 145, 178, 0.4);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #0891B2;
    }
    .alert-critical {
        background: #fee;
        border-left: 4px solid #c00;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .alert-urgent {
        background: #ffe;
        border-left: 4px solid #c60;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .alert-warning {
        background: #ffc;
        border-left: 4px solid #960;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .header-banner {
        background: linear-gradient(135deg, #0891B2 0%, #06B6D4 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


class ExpiryCheckerApp:
    """Main application class for the Streamlit web platform."""
    
    def __init__(self):
        self.expiring_items = []
        self.stats = {
            'total_rows': 0,
            'sheets_processed': 0,
            'items_found': 0
        }
    
    def detect_date_columns(self, df):
        """Detect columns containing expiry dates."""
        date_keywords = [
            'expiry', 'expiration', 'expire', 'expires', 'expiring',
            'valid', 'validity', 'valid until', 'valid till',
            'use by', 'best before', 'shelf life', 'due date', 'end date', 'date'
        ]
        
        date_columns = []
        
        # Method 1: Keyword matching
        for col in df.columns:
            col_str = str(col).lower()
            for keyword in date_keywords:
                if keyword in col_str:
                    date_columns.append(col)
                    break
        
        # Method 2: Data type analysis if no keywords found
        if not date_columns:
            for col in df.columns:
                try:
                    temp_series = pd.to_datetime(df[col], errors='coerce')
                    valid_dates = temp_series.notna().sum()
                    total_values = len(temp_series)
                    
                    if total_values > 0 and (valid_dates / total_values) > 0.5:
                        future_dates = (temp_series > pd.Timestamp.now()).sum()
                        if future_dates > 0:
                            date_columns.append(col)
                except Exception:
                    continue
        
        return date_columns
    
    def detect_item_column(self, df, date_col):
        """Detect column containing item names."""
        item_keywords = ['name', 'item', 'product', 'reagent', 'chemical', 'material', 'description']
        
        # Method 1: Keyword matching
        for col in df.columns:
            if col == date_col:
                continue
            col_str = str(col).lower()
            for keyword in item_keywords:
                if keyword in col_str:
                    return col
        
        # Method 2: First text column to left of date
        try:
            date_col_idx = df.columns.get_loc(date_col)
            for i in range(date_col_idx - 1, -1, -1):
                col = df.columns[i]
                if df[col].dtype == 'object':
                    return col
        except Exception:
            pass
        
        # Method 3: First text column overall
        for col in df.columns:
            if col != date_col and df[col].dtype == 'object':
                return col
        
        return None
    
    def extract_additional_info(self, row, all_columns, item_col, date_col):
        """Extract additional information from row."""
        info = {}
        
        additional_keywords = {
            'lot': ['lot', 'batch', 'lot number', 'batch number'],
            'catalog': ['catalog', 'cat#', 'cat no', 'catalogue'],
            'quantity': ['quantity', 'qty', 'amount', 'volume', 'vol'],
            'location': ['location', 'storage', 'position', 'shelf', 'cabinet'],
            'supplier': ['supplier', 'vendor', 'manufacturer', 'company']
        }
        
        for col in all_columns:
            if col == date_col or col == item_col:
                continue
            
            col_str = str(col).lower()
            value = row[col]
            
            if pd.notna(value):
                for info_type, keywords in additional_keywords.items():
                    for keyword in keywords:
                        if keyword in col_str:
                            info[info_type] = str(value)
                            break
        
        return info
    
    def calculate_urgency(self, days_left, warning_days):
        """Calculate urgency level."""
        if days_left < 0:
            return 'expired'
        elif days_left <= 30:
            return 'critical'
        elif days_left <= 60:
            return 'urgent'
        elif days_left <= warning_days:
            return 'warning'
        else:
            return 'info'
    
    def process_excel_file(self, uploaded_file, warning_days, exclude_sheets):
        """Process uploaded Excel file."""
        self.expiring_items = []
        self.stats = {'total_rows': 0, 'sheets_processed': 0, 'items_found': 0}
        
        try:
            excel_data = pd.ExcelFile(uploaded_file)
            sheet_names = excel_data.sheet_names
            
            today = datetime.now()
            warning_date = today + timedelta(days=warning_days)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, sheet_name in enumerate(sheet_names):
                # Update progress
                progress = (idx + 1) / len(sheet_names)
                progress_bar.progress(progress)
                status_text.text(f"Processing sheet: {sheet_name}")
                
                # Skip excluded sheets
                if sheet_name in exclude_sheets:
                    continue
                
                try:
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                    
                    if df.empty:
                        continue
                    
                    self.stats['sheets_processed'] += 1
                    
                    # Detect date columns
                    date_columns = self.detect_date_columns(df)
                    
                    if not date_columns:
                        continue
                    
                    # Process each date column
                    for date_col in date_columns:
                        item_col = self.detect_item_column(df, date_col)
                        
                        # Convert to datetime
                        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                        
                        # Check each row
                        for idx, row in df.iterrows():
                            expiry_date = row[date_col]
                            
                            if pd.isna(expiry_date):
                                continue
                            
                            self.stats['total_rows'] += 1
                            
                            days_until_expiry = (expiry_date - today).days
                            
                            # Check if within warning period
                            if 0 <= days_until_expiry <= warning_days:
                                # Get item name
                                item_name = "Unknown Item"
                                if item_col and item_col in row.index and pd.notna(row[item_col]):
                                    item_name = str(row[item_col])
                                else:
                                    # Use first non-empty text value
                                    for col in df.columns:
                                        if col != date_col and pd.notna(row[col]):
                                            item_name = str(row[col])
                                            break
                                
                                # Extract additional info
                                additional_info = self.extract_additional_info(
                                    row, df.columns, item_col, date_col
                                )
                                
                                item_data = {
                                    'sheet': sheet_name,
                                    'item': item_name,
                                    'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                                    'days_left': days_until_expiry,
                                    'urgency': self.calculate_urgency(days_until_expiry, warning_days),
                                    'additional_info': additional_info
                                }
                                
                                self.expiring_items.append(item_data)
                                self.stats['items_found'] += 1
                
                except Exception as e:
                    st.warning(f"Error processing sheet '{sheet_name}': {e}")
                    continue
            
            progress_bar.empty()
            status_text.empty()
            
            # Sort by urgency and days
            urgency_order = {'expired': 0, 'critical': 1, 'urgent': 2, 'warning': 3, 'info': 4}
            self.expiring_items.sort(key=lambda x: (urgency_order.get(x['urgency'], 999), x['days_left']))
            
            return True
            
        except Exception as e:
            st.error(f"Error processing Excel file: {e}")
            return False
    
    def generate_email_html(self, warning_days):
        """Generate HTML email content."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #0891B2 0%, #06B6D4 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .summary {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-left: 4px solid #0891B2; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #0891B2; color: white; padding: 15px; text-align: left; }}
        td {{ padding: 12px 15px; border-bottom: 1px solid #e9ecef; }}
        .critical {{ background-color: #ffebee; }}
        .urgent {{ background-color: #fff3e0; }}
        .warning {{ background-color: #fffde7; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
        .badge-critical {{ background: #fee; color: #c00; }}
        .badge-urgent {{ background: #ffe; color: #c60; }}
        .badge-warning {{ background: #ffc; color: #960; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚠️ Expiry Date Monitoring Alert</h1>
        <p>Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    <div class="summary">
        <h2>📊 Summary</h2>
        <p><strong>Warning Period:</strong> {warning_days} days</p>
        <p><strong>Total Rows Scanned:</strong> {self.stats['total_rows']}</p>
        <p><strong>Sheets Processed:</strong> {self.stats['sheets_processed']}</p>
        <p><strong>Items Expiring Soon:</strong> {len(self.expiring_items)}</p>
    </div>
    <table>
        <tr>
            <th>Status</th>
            <th>Source</th>
            <th>Item</th>
            <th>Expiry Date</th>
            <th>Days Left</th>
        </tr>
"""
        
        for item in self.expiring_items:
            urgency = item['urgency']
            row_class = f"{urgency}"
            
            badge_text = {
                'critical': '🔴 CRITICAL',
                'urgent': '🟠 URGENT',
                'warning': '🟡 WARNING'
            }
            
            additional_html = ""
            if item['additional_info']:
                info_parts = [f"{k.title()}: {v}" for k, v in item['additional_info'].items()]
                if info_parts:
                    additional_html = f"<br><small>{' • '.join(info_parts)}</small>"
            
            html += f"""
        <tr class="{row_class}">
            <td><span class="badge badge-{urgency}">{badge_text.get(urgency, urgency.upper())}</span></td>
            <td><strong>{item['sheet']}</strong></td>
            <td>{item['item']}{additional_html}</td>
            <td>{item['expiry_date']}</td>
            <td><strong>{item['days_left']} days</strong></td>
        </tr>
"""
        
        html += """
    </table>
    <p><em>Please take necessary action to order replacements.</em></p>
    <p><small>Generated by Universal Expiry Monitoring Platform</small></p>
</body>
</html>
"""
        return html
    
    def send_email(self, smtp_server, smtp_port, sender_email, sender_password, 
                   recipient_email, warning_days):
        """Send email alert."""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"⚠️ Expiry Alert - {len(self.expiring_items)} Item(s) Require Attention"
            
            html_body = self.generate_email_html(warning_days)
            msg.attach(MIMEText(html_body, 'html'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            return True, "Email sent successfully!"
            
        except Exception as e:
            return False, f"Error sending email: {str(e)}"


def main():
    """Main application function."""
    
    # Header
    st.markdown("""
    <div class="header-banner">
        <h1>🧪 Universal Expiry Date Monitoring Platform</h1>
        <p>Intelligent monitoring system that works with ANY Excel structure</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize app
    if 'app' not in st.session_state:
        st.session_state.app = ExpiryCheckerApp()
    
    app = st.session_state.app
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # File upload
        uploaded_file = st.file_uploader(
            "📁 Upload Excel File",
            type=['xlsx', 'xls', 'csv'],
            help="Upload your Excel file with expiry dates"
        )
        
        st.markdown("---")
        
        # Settings
        warning_days = st.slider(
            "⏰ Warning Period (days)",
            min_value=30,
            max_value=180,
            value=90,
            step=10,
            help="Alert for items expiring within this many days"
        )
        
        exclude_sheets = st.text_input(
            "🚫 Exclude Sheets (comma-separated)",
            placeholder="Archive, Template, Old Data",
            help="Sheets to skip (optional)"
        )
        exclude_list = [s.strip() for s in exclude_sheets.split(',') if s.strip()]
        
        st.markdown("---")
        
        # Email settings
        with st.expander("📧 Email Settings", expanded=False):
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=587, step=1)
            sender_email = st.text_input("Sender Email", placeholder="your@gmail.com")
            sender_password = st.text_input("App Password", type="password", 
                                           help="Gmail App Password (not regular password)")
            recipient_email = st.text_input("Recipient Email", placeholder="recipient@gmail.com")
        
        st.markdown("---")
        
        # Info
        st.info("""
        **How it works:**
        1. Upload your Excel file
        2. System finds expiry dates automatically
        3. View results instantly
        4. Send email alerts or download reports
        """)
    
    # Main content area
    if uploaded_file is None:
        # Welcome screen
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>🎯 Universal</h3>
                <p>Works with ANY Excel structure. No modifications needed!</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>🤖 Intelligent</h3>
                <p>Automatically detects dates and item names</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>📧 Automated</h3>
                <p>Professional email alerts with all details</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        ### 🚀 Getting Started
        
        1. **Upload your Excel file** using the sidebar
        2. **Configure settings** (warning period, email)
        3. **Click "Check Expiry Dates"** to analyze
        4. **View results** and send alerts
        
        ### ✨ Features
        
        - ✅ Supports multiple sheets with different structures
        - ✅ Detects all date formats automatically
        - ✅ Identifies item names intelligently
        - ✅ Extracts additional info (lot#, location, etc.)
        - ✅ Color-coded urgency levels
        - ✅ Professional HTML email alerts
        - ✅ Downloadable Excel/CSV reports
        
        ### 📊 Supported Excel Structures
        
        The system works with **any** Excel layout:
        - Simple tables with just Item + Date
        - Complex spreadsheets with many columns
        - Multiple sheets with different formats
        - Merged cells, headers, formatted tables
        
        **No need to modify your existing files!**
        """)
    
    else:
        # File uploaded - show processing options
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🔍 Check Expiry Dates", type="primary"):
                with st.spinner("Analyzing Excel file..."):
                    success = app.process_excel_file(uploaded_file, warning_days, exclude_list)
                
                if success:
                    st.session_state.processed = True
                    st.rerun()
        
        with col2:
            st.metric("Warning Period", f"{warning_days} days")
        
        # Show results if processed
        if st.session_state.get('processed', False):
            st.markdown("---")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📄 Rows Scanned", app.stats['total_rows'])
            with col2:
                st.metric("📊 Sheets Processed", app.stats['sheets_processed'])
            with col3:
                st.metric("⚠️ Items Expiring", app.stats['items_found'])
            with col4:
                urgency_counts = {}
                for item in app.expiring_items:
                    urgency_counts[item['urgency']] = urgency_counts.get(item['urgency'], 0) + 1
                critical_count = urgency_counts.get('critical', 0)
                st.metric("🔴 Critical", critical_count)
            
            st.markdown("---")
            
            # Display results
            if app.expiring_items:
                st.subheader("📋 Expiring Items")
                
                # Filter by urgency
                urgency_filter = st.multiselect(
                    "Filter by urgency:",
                    ['critical', 'urgent', 'warning'],
                    default=['critical', 'urgent', 'warning']
                )
                
                filtered_items = [item for item in app.expiring_items if item['urgency'] in urgency_filter]
                
                # Display items
                for item in filtered_items:
                    urgency = item['urgency']
                    
                    if urgency == 'critical':
                        alert_class = "alert-critical"
                        icon = "🔴"
                        urgency_text = "CRITICAL"
                    elif urgency == 'urgent':
                        alert_class = "alert-urgent"
                        icon = "🟠"
                        urgency_text = "URGENT"
                    else:
                        alert_class = "alert-warning"
                        icon = "🟡"
                        urgency_text = "WARNING"
                    
                    additional_info = ""
                    if item['additional_info']:
                        info_parts = [f"{k.title()}: {v}" for k, v in item['additional_info'].items()]
                        additional_info = " • " + " • ".join(info_parts)
                    
                    st.markdown(f"""
                    <div class="{alert_class}">
                        <strong>{icon} {urgency_text}</strong> - <strong>{item['item']}</strong> ({item['sheet']})<br>
                        Expires: {item['expiry_date']} ({item['days_left']} days remaining){additional_info}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Send email
                    if st.button("📧 Send Email Alert", type="primary"):
                        if not sender_email or not sender_password or not recipient_email:
                            st.error("Please configure email settings in the sidebar first!")
                        else:
                            with st.spinner("Sending email..."):
                                success, message = app.send_email(
                                    smtp_server, smtp_port, sender_email,
                                    sender_password, recipient_email, warning_days
                                )
                            
                            if success:
                                st.success(f"✅ {message}")
                            else:
                                st.error(f"❌ {message}")
                
                with col2:
                    # Download Excel report
                    df_report = pd.DataFrame(app.expiring_items)
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_report.to_excel(writer, index=False, sheet_name='Expiring Items')
                    
                    excel_data = output.getvalue()
                    
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=excel_data,
                        file_name=f"expiry_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                with col3:
                    # Download CSV report
                    csv_data = df_report.to_csv(index=False)
                    
                    st.download_button(
                        label="📄 Download CSV Report",
                        data=csv_data,
                        file_name=f"expiry_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            else:
                st.success("✅ Good news! No items are expiring within the warning period.")
                st.balloons()


if __name__ == "__main__":
    main()
