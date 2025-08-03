import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os
import base64
from io import BytesIO
import json
import calendar
import requests

# Page configuration
st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    
    .status-pending { background-color: #ffd700; color: #000; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; }
    .status-interviewing { background-color: #ff6b6b; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; }
    .status-offered { background-color: #51cf66; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; }
    .status-rejected { background-color: #868e96; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; }
    .status-applied { background-color: #339af0; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    .upload-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .dataframe {
        font-size: 0.9rem;
    }
    
    .dataframe th {
        background-color: #f0f2f6;
        font-weight: bold;
        text-align: center;
    }
    
    .dataframe td {
        text-align: center;
        padding: 0.5rem;
    }
    
    .alert-box {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #c44569;
    }
    
    .success-box {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #2f9e44;
    }
    
    .info-box {
        background: linear-gradient(135deg, #339af0 0%, #228be6 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1971c2;
    }
</style>
""", unsafe_allow_html=True)

# Data file path
DATA_FILE = "job_applications.csv"
BACKUP_FILE = "job_applications_backup.json"

def load_data():
    """Load job applications data from local file"""
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            # Convert date columns back to datetime
            if 'date_applied' in df.columns:
                df['date_applied'] = pd.to_datetime(df['date_applied']).dt.date
            if 'follow_up_date' in df.columns:
                df['follow_up_date'] = pd.to_datetime(df['follow_up_date']).dt.date
            if 'deadline' in df.columns:
                df['deadline'] = pd.to_datetime(df['deadline']).dt.date
            if 'interview_date' in df.columns:
                df['interview_date'] = pd.to_datetime(df['interview_date']).dt.date
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def save_data(df):
    """Save job applications data to local file with backup"""
    try:
        # Save to CSV file
        df.to_csv(DATA_FILE, index=False)
        
        # Create JSON backup
        backup_data = df.to_dict('records')
        with open(BACKUP_FILE, 'w') as f:
            json.dump(backup_data, f, default=str)
        
        st.success("✅ Data saved successfully!")
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def create_sample_data():
    """Create sample data if no data exists"""
    sample_data = {
        'job_title': ['Software Engineer', 'Data Analyst', 'Product Manager', 'Strategy Consulting Intern'],
        'company': ['Tech Corp', 'Data Inc', 'Product Co', 'JLL'],
        'status': ['Applied', 'Interviewing', 'Pending', 'Pending'],
        'priority': ['High', 'Medium', 'Low', 'High'],
        'channel': ['LinkedIn', 'Company Website', 'Referral', 'LinkedIn'],
        'salary_range': ['$80k-$100k', '$60k-$80k', '$100k-$120k', '4,000'],
        'location': ['Remote', 'New York', 'San Francisco', 'Dubai'],
        'date_applied': [date.today() - timedelta(days=5), date.today() - timedelta(days=3), date.today() - timedelta(days=1), date.today()],
        'follow_up_date': [date.today() + timedelta(days=7), None, None, None],
        'deadline': [date.today() + timedelta(days=14), None, None, None],
        'interview_date': [None, date.today() + timedelta(days=2), None, None],
        'notes': ['Great opportunity', 'Good company culture', 'Interesting role', 'Strategy consulting role'],
        'referral': ['No', 'Yes', 'No', 'No'],
        'application_id': ['APP001', 'APP002', 'APP003', 'APP004'],
        'contact_person': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Sarah Wilson'],
        'contact_email': ['john@techcorp.com', 'jane@datainc.com', 'bob@productco.com', 'sarah@jll.com']
    }
    return pd.DataFrame(sample_data)

def add_job_application():
    """Add new job application form"""
    st.markdown("### 📝 Add New Job Application")
    
    with st.form("job_application_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title *", placeholder="e.g., Senior Software Engineer")
            company = st.text_input("Company *", placeholder="e.g., Google")
            location = st.text_input("Location", placeholder="e.g., Remote, New York")
            salary_range = st.text_input("Salary Range", placeholder="e.g., $80k-$100k")
            application_id = st.text_input("Application ID", placeholder="e.g., APP001")
            deadline = st.date_input("Application Deadline", value=None)
        
        with col2:
            status = st.selectbox("Status *", 
                                ["Applied", "Interviewing", "Pending", "Offered", "Rejected", "Withdrawn"])
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            channel = st.selectbox("Application Channel", 
                                 ["LinkedIn", "Company Website", "Referral", "Indeed", "Glassdoor", "Other"])
            referral = st.selectbox("Referral", ["No", "Yes"])
            date_applied = st.date_input("Date Applied *", value=date.today())
            interview_date = st.date_input("Interview Date", value=None)
        
        # Contact information
        col3, col4 = st.columns(2)
        with col3:
            contact_person = st.text_input("Contact Person", placeholder="e.g., John Doe")
            contact_email = st.text_input("Contact Email", placeholder="e.g., john@company.com")
        
        with col4:
            follow_up_date = st.date_input("Follow-up Date", value=None)
            notes = st.text_area("Notes", placeholder="Add any notes about this application...")
        
        submitted = st.form_submit_button("💼 Add Application", use_container_width=True)
        
        if submitted:
            if job_title and company and date_applied:
                return {
                    'job_title': job_title,
                    'company': company,
                    'status': status,
                    'priority': priority,
                    'channel': channel,
                    'salary_range': salary_range,
                    'location': location,
                    'date_applied': date_applied,
                    'follow_up_date': follow_up_date,
                    'deadline': deadline,
                    'interview_date': interview_date,
                    'notes': notes,
                    'referral': referral,
                    'application_id': application_id,
                    'contact_person': contact_person,
                    'contact_email': contact_email
                }
            else:
                st.error("Please fill in all required fields (marked with *)")
                return None
    return None

def display_dashboard(df):
    """Display dashboard with quick actions and alerts"""
    st.markdown("### 🎯 Quick Dashboard")
    
    if df.empty:
        st.info("No applications yet. Add your first application to see the dashboard!")
        return
    
    # Alerts and notifications
    today = pd.Timestamp.now().date()
    
    # Upcoming deadlines
    if 'deadline' in df.columns:
        try:
            # Convert deadline to datetime for comparison
            df_deadline = df.copy()
            df_deadline['deadline'] = pd.to_datetime(df_deadline['deadline'])
            
            # Convert today to datetime for comparison
            today_dt = pd.Timestamp(today)
            
            upcoming_deadlines = df_deadline[
                (df_deadline['deadline'] >= today_dt) & 
                (df_deadline['deadline'] <= today_dt + pd.Timedelta(days=7)) &
                (df_deadline['deadline'].notna())
            ]
            
            if not upcoming_deadlines.empty:
                st.markdown('<div class="alert-box">', unsafe_allow_html=True)
                st.markdown("⚠️ **Upcoming Deadlines**")
                for _, row in upcoming_deadlines.iterrows():
                    days_left = (row['deadline'].date() - today).days
                    st.markdown(f"• **{row['company']}** - {row['job_title']} (Deadline: {row['deadline'].date()}, {days_left} days left)")
                st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Could not process deadlines: {e}")
    
    # Follow-up reminders
    if 'follow_up_date' in df.columns:
        try:
            # Convert follow_up_date to datetime for comparison
            df_followup = df.copy()
            df_followup['follow_up_date'] = pd.to_datetime(df_followup['follow_up_date'])
            
            # Convert today to datetime for comparison
            today_dt = pd.Timestamp(today)
            
            follow_ups = df_followup[
                (df_followup['follow_up_date'] >= today_dt) & 
                (df_followup['follow_up_date'] <= today_dt + pd.Timedelta(days=3)) &
                (df_followup['follow_up_date'].notna())
            ]
            
            if not follow_ups.empty:
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.markdown("📞 **Follow-up Reminders**")
                for _, row in follow_ups.iterrows():
                    days_left = (row['follow_up_date'].date() - today).days
                    st.markdown(f"• **{row['company']}** - {row['job_title']} (Follow-up: {row['follow_up_date'].date()}, {days_left} days left)")
                st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Could not process follow-ups: {e}")
    
    # Interview reminders
    if 'interview_date' in df.columns:
        try:
            # Convert interview_date to datetime for comparison
            df_interview = df.copy()
            df_interview['interview_date'] = pd.to_datetime(df_interview['interview_date'])
            
            # Convert today to datetime for comparison
            today_dt = pd.Timestamp(today)
            
            upcoming_interviews = df_interview[
                (df_interview['interview_date'] >= today_dt) & 
                (df_interview['interview_date'] <= today_dt + pd.Timedelta(days=2)) &
                (df_interview['interview_date'].notna())
            ]
            
            if not upcoming_interviews.empty:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown("🎯 **Upcoming Interviews**")
                for _, row in upcoming_interviews.iterrows():
                    days_left = (row['interview_date'].date() - today).days
                    st.markdown(f"• **{row['company']}** - {row['job_title']} (Interview: {row['interview_date'].date()}, {days_left} days left)")
                st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Could not process interviews: {e}")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_apps = len(df[df['status'].isin(['Applied', 'Interviewing', 'Pending'])])
        st.metric("Active Applications", active_apps)
    
    with col2:
        try:
            if 'interview_date' in df.columns:
                df_interview_stats = df.copy()
                df_interview_stats['interview_date'] = pd.to_datetime(df_interview_stats['interview_date'])
                today_dt = pd.Timestamp(today)
                interviews_this_week = len(df_interview_stats[
                    (df_interview_stats['interview_date'] >= today_dt) & 
                    (df_interview_stats['interview_date'] <= today_dt + pd.Timedelta(days=7)) &
                    (df_interview_stats['interview_date'].notna())
                ])
            else:
                interviews_this_week = 0
        except:
            interviews_this_week = 0
        st.metric("Interviews This Week", interviews_this_week)
    
    with col3:
        try:
            if 'follow_up_date' in df.columns:
                df_followup_stats = df.copy()
                df_followup_stats['follow_up_date'] = pd.to_datetime(df_followup_stats['follow_up_date'])
                today_dt = pd.Timestamp(today)
                follow_ups_this_week = len(df_followup_stats[
                    (df_followup_stats['follow_up_date'] >= today_dt) & 
                    (df_followup_stats['follow_up_date'] <= today_dt + pd.Timedelta(days=7)) &
                    (df_followup_stats['follow_up_date'].notna())
                ])
            else:
                follow_ups_this_week = 0
        except:
            follow_ups_this_week = 0
        st.metric("Follow-ups This Week", follow_ups_this_week)
    
    with col4:
        offers = len(df[df['status'] == 'Offered'])
        st.metric("Total Offers", offers)

def display_tracker(df):
    """Display job applications in an interactive table with edit functionality"""
    st.markdown("### 📊 Job Applications Tracker")
    
    if df.empty:
        st.info("No job applications found. Add your first application in the 'Add Application' tab!")
        return
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect("Filter by Status", df['status'].unique(), default=df['status'].unique())
    
    with col2:
        priority_filter = st.multiselect("Filter by Priority", df['priority'].unique(), default=df['priority'].unique())
    
    with col3:
        channel_filter = st.multiselect("Filter by Channel", df['channel'].unique(), default=df['channel'].unique())
    
    with col4:
        search_term = st.text_input("Search", placeholder="Search by company or job title...")
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    if priority_filter:
        filtered_df = filtered_df[filtered_df['priority'].isin(priority_filter)]
    if channel_filter:
        filtered_df = filtered_df[filtered_df['channel'].isin(channel_filter)]
    if search_term:
        filtered_df = filtered_df[
            filtered_df['company'].str.contains(search_term, case=False, na=False) |
            filtered_df['job_title'].str.contains(search_term, case=False, na=False)
        ]
    
    # Display filtered data
    if not filtered_df.empty:
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        # Edit functionality
        st.markdown("### ✏️ Edit Application")
        
        # Select application to edit
        if not filtered_df.empty:
            # Create a list of applications for selection
            application_options = []
            for idx, row in filtered_df.iterrows():
                option_text = f"{row['company']} - {row['job_title']} ({row['status']})"
                application_options.append((idx, option_text))
            
            # Dropdown to select application
            selected_option = st.selectbox(
                "Select application to edit:",
                options=[opt[1] for opt in application_options],
                index=0
            )
            
            # Find the selected application
            selected_idx = None
            for idx, opt in application_options:
                if opt == selected_option:
                    selected_idx = idx
                    break
            
            if selected_idx is not None:
                selected_app = filtered_df.iloc[selected_idx]
                
                # Edit form
                with st.expander(f"Edit: {selected_app['company']} - {selected_app['job_title']}", expanded=True):
                    with st.form(f"edit_form_{selected_idx}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            job_title = st.text_input("Job Title *", value=selected_app['job_title'], key=f"title_{selected_idx}")
                            company = st.text_input("Company *", value=selected_app['company'], key=f"company_{selected_idx}")
                            location = st.text_input("Location", value=selected_app.get('location', ''), key=f"location_{selected_idx}")
                            salary_range = st.text_input("Salary Range", value=selected_app.get('salary_range', ''), key=f"salary_{selected_idx}")
                            application_id = st.text_input("Application ID", value=selected_app.get('application_id', ''), key=f"id_{selected_idx}")
                            # Handle None/NaT values for deadline
                            deadline_value = selected_app.get('deadline')
                            if deadline_value is None or pd.isna(deadline_value):
                                deadline_value = None
                            deadline = st.date_input("Application Deadline", value=deadline_value, key=f"deadline_{selected_idx}")
                        
                        with col2:
                            status = st.selectbox("Status *", 
                                                ["Applied", "Interviewing", "Pending", "Offered", "Rejected", "Withdrawn"],
                                                index=["Applied", "Interviewing", "Pending", "Offered", "Rejected", "Withdrawn"].index(selected_app['status']),
                                                key=f"status_{selected_idx}")
                            priority = st.selectbox("Priority", ["High", "Medium", "Low"],
                                                  index=["High", "Medium", "Low"].index(selected_app['priority']),
                                                  key=f"priority_{selected_idx}")
                            channel = st.selectbox("Application Channel", 
                                                 ["LinkedIn", "Company Website", "Referral", "Indeed", "Glassdoor", "Other"],
                                                 index=["LinkedIn", "Company Website", "Referral", "Indeed", "Glassdoor", "Other"].index(selected_app['channel']),
                                                 key=f"channel_{selected_idx}")
                            referral = st.selectbox("Referral", ["No", "Yes"],
                                                  index=["No", "Yes"].index(selected_app['referral']),
                                                  key=f"referral_{selected_idx}")
                            date_applied = st.date_input("Date Applied *", value=selected_app['date_applied'], key=f"date_{selected_idx}")
                            # Handle None/NaT values for interview_date
                            interview_value = selected_app.get('interview_date')
                            if interview_value is None or pd.isna(interview_value):
                                interview_value = None
                            interview_date = st.date_input("Interview Date", value=interview_value, key=f"interview_{selected_idx}")
                        
                        # Contact information
                        col3, col4 = st.columns(2)
                        with col3:
                            contact_person = st.text_input("Contact Person", value=selected_app.get('contact_person', ''), key=f"contact_{selected_idx}")
                            contact_email = st.text_input("Contact Email", value=selected_app.get('contact_email', ''), key=f"email_{selected_idx}")
                        
                        with col4:
                            # Handle None/NaT values for follow_up_date
                            followup_value = selected_app.get('follow_up_date')
                            if followup_value is None or pd.isna(followup_value):
                                followup_value = None
                            follow_up_date = st.date_input("Follow-up Date", value=followup_value, key=f"followup_{selected_idx}")
                            notes = st.text_area("Notes", value=selected_app.get('notes', ''), key=f"notes_{selected_idx}")
                        
                        # Action buttons
                        col5, col6, col7 = st.columns(3)
                        
                        with col5:
                            update_submitted = st.form_submit_button("💾 Update Application", use_container_width=True)
                        
                        with col6:
                            delete_submitted = st.form_submit_button("🗑️ Delete Application", use_container_width=True)
                        
                        with col7:
                            duplicate_submitted = st.form_submit_button("📋 Duplicate Application", use_container_width=True)
                        
                        if update_submitted:
                            if job_title and company and date_applied:
                                # Update the application
                                updated_app = {
                                    'job_title': job_title,
                                    'company': company,
                                    'status': status,
                                    'priority': priority,
                                    'channel': channel,
                                    'salary_range': salary_range,
                                    'location': location,
                                    'date_applied': date_applied,
                                    'follow_up_date': follow_up_date,
                                    'deadline': deadline,
                                    'interview_date': interview_date,
                                    'notes': notes,
                                    'referral': referral,
                                    'application_id': application_id,
                                    'contact_person': contact_person,
                                    'contact_email': contact_email
                                }
                                
                                # Find the original index in the main dataframe
                                original_idx = df[df['company'] == selected_app['company']].index[0]
                                for key, value in updated_app.items():
                                    df.at[original_idx, key] = value
                                
                                if save_data(df):
                                    st.success("✅ Application updated successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to update application.")
                            else:
                                st.error("Please fill in all required fields (marked with *)")
                        
                        if delete_submitted:
                            # Find the original index in the main dataframe
                            original_idx = df[df['company'] == selected_app['company']].index[0]
                            df = df.drop(original_idx).reset_index(drop=True)
                            
                            if save_data(df):
                                st.success("✅ Application deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete application.")
                        
                        if duplicate_submitted:
                            # Create a duplicate with "Copy" added to company name
                            duplicated_app = {
                                'job_title': job_title,
                                'company': f"{company} (Copy)",
                                'status': 'Applied',  # Reset status for new application
                                'priority': priority,
                                'channel': channel,
                                'salary_range': salary_range,
                                'location': location,
                                'date_applied': date.today(),  # Reset to today
                                'follow_up_date': None,
                                'deadline': deadline,
                                'interview_date': None,
                                'notes': f"Duplicated from {company} - {notes}",
                                'referral': referral,
                                'application_id': f"{application_id}_COPY" if application_id else "COPY",
                                'contact_person': contact_person,
                                'contact_email': contact_email
                            }
                            
                            # Add to dataframe
                            new_df = pd.DataFrame([duplicated_app])
                            df = pd.concat([df, new_df], ignore_index=True)
                            
                            if save_data(df):
                                st.success("✅ Application duplicated successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to duplicate application.")
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"job_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No applications match your current filters.")

def display_insights(df):
    """Display analytics and insights"""
    st.markdown("### 📈 Analytics & Insights")
    
    if df.empty:
        st.info("No data available for analytics. Add some job applications first!")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Applications", len(df))
    
    with col2:
        offers = len(df[df['status'] == 'Offered'])
        st.metric("Offers Received", offers)
    
    with col3:
        interviews = len(df[df['status'] == 'Interviewing'])
        st.metric("In Interview Process", interviews)
    
    with col4:
        rejection_rate = len(df[df['status'] == 'Rejected']) / len(df) * 100
        st.metric("Rejection Rate", f"{rejection_rate:.1f}%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_counts = df['status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Application Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_status.update_layout(height=400)
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Channel effectiveness
        channel_counts = df['channel'].value_counts()
        fig_channel = px.bar(
            x=channel_counts.index,
            y=channel_counts.values,
            title="Applications by Channel",
            color=channel_counts.values,
            color_continuous_scale="viridis"
        )
        fig_channel.update_layout(height=400, xaxis_title="Channel", yaxis_title="Count")
        st.plotly_chart(fig_channel, use_container_width=True)
    
    # Timeline chart
    st.markdown("### 📅 Application Timeline")
    df_timeline = df.copy()
    df_timeline['date_applied'] = pd.to_datetime(df_timeline['date_applied'])
    df_timeline = df_timeline.sort_values('date_applied')
    
    # Convert priority to numeric for size mapping
    priority_mapping = {'High': 3, 'Medium': 2, 'Low': 1}
    df_timeline['priority_size'] = df_timeline['priority'].map(priority_mapping)
    
    fig_timeline = px.scatter(
        df_timeline,
        x='date_applied',
        y='company',
        color='status',
        size='priority_size',
        title="Application Timeline",
        hover_data=['job_title', 'location', 'salary_range', 'priority']
    )
    fig_timeline.update_layout(height=500)
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Priority vs Status heatmap
    st.markdown("### 🔥 Priority vs Status Analysis")
    pivot_table = pd.crosstab(df['priority'], df['status'])
    fig_heatmap = px.imshow(
        pivot_table,
        title="Priority vs Status Heatmap",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Salary analysis (if salary data exists)
    if 'salary_range' in df.columns and not df['salary_range'].isna().all():
        st.markdown("### 💰 Salary Analysis")
        # Extract numeric values from salary ranges for analysis
        salary_data = df[df['salary_range'].notna()].copy()
        if not salary_data.empty:
            # Simple salary analysis - you can enhance this
            st.write(f"Applications with salary info: {len(salary_data)}")
            st.write("Salary ranges in your applications:")
            for salary in salary_data['salary_range'].unique():
                count = len(salary_data[salary_data['salary_range'] == salary])
                st.write(f"• {salary}: {count} applications")

def display_calendar(df):
    """Display calendar view of applications and events"""
    st.markdown("### 📅 Calendar View")
    
    if df.empty:
        st.info("No applications to display in calendar view.")
        return
    
    # Create calendar data
    calendar_data = []
    
    # Add application dates
    for _, row in df.iterrows():
        calendar_data.append({
            'date': row['date_applied'],
            'event': f"Applied: {row['company']} - {row['job_title']}",
            'type': 'application'
        })
    
    # Add follow-up dates
    if 'follow_up_date' in df.columns:
        for _, row in df[df['follow_up_date'].notna()].iterrows():
            calendar_data.append({
                'date': row['follow_up_date'],
                'event': f"Follow-up: {row['company']}",
                'type': 'follow_up'
            })
    
    # Add interview dates
    if 'interview_date' in df.columns:
        for _, row in df[df['interview_date'].notna()].iterrows():
            calendar_data.append({
                'date': row['interview_date'],
                'event': f"Interview: {row['company']} - {row['job_title']}",
                'type': 'interview'
            })
    
    # Add deadlines
    if 'deadline' in df.columns:
        for _, row in df[df['deadline'].notna()].iterrows():
            calendar_data.append({
                'date': row['deadline'],
                'event': f"Deadline: {row['company']} - {row['job_title']}",
                'type': 'deadline'
            })
    
    if calendar_data:
        # Create calendar dataframe
        calendar_df = pd.DataFrame(calendar_data)
        calendar_df['date'] = pd.to_datetime(calendar_df['date'])
        calendar_df = calendar_df.sort_values('date')
        
        # Display upcoming events
        today = pd.Timestamp.now().date()
        upcoming_events = calendar_df[calendar_df['date'].dt.date >= today].head(10)
        
        if not upcoming_events.empty:
            st.markdown("#### 🗓️ Upcoming Events")
            for _, event in upcoming_events.iterrows():
                days_until = (event['date'].date() - today).days
                if days_until == 0:
                    time_text = "**TODAY**"
                elif days_until == 1:
                    time_text = "**TOMORROW**"
                else:
                    time_text = f"in {days_until} days"
                
                st.write(f"📅 **{event['date'].strftime('%B %d, %Y')}** ({time_text})")
                st.write(f"   {event['event']}")
                st.write("---")
        else:
            st.info("No upcoming events in the next 30 days.")
    else:
        st.info("No events to display in calendar view.")

def main():
    """Main application function"""
    # Header
    st.markdown('<h1 class="main-header">💼 Job Application Tracker</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Create sample data if no data exists
    if df.empty:
        if st.button("🚀 Create Sample Data"):
            df = create_sample_data()
            save_data(df)
            st.success("Sample data created! You can now explore the app.")
            st.rerun()
    
    # Sidebar
    st.sidebar.markdown("## 🎯 Quick Stats")
    if not df.empty:
        st.sidebar.metric("Total Applications", len(df))
        st.sidebar.metric("Active Applications", len(df[df['status'].isin(['Applied', 'Interviewing', 'Pending'])]))
        st.sidebar.metric("Success Rate", f"{len(df[df['status'] == 'Offered']) / len(df) * 100:.1f}%")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Navigation")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dashboard", "➕ Add Application", "📊 Tracker", "📈 Insights", "📅 Calendar"])
    
    with tab1:
        display_dashboard(df)
    
    with tab2:
        new_job = add_job_application()
        if new_job:
            # Add to dataframe
            new_df = pd.DataFrame([new_job])
            if df.empty:
                df = new_df
            else:
                df = pd.concat([df, new_df], ignore_index=True)
            
            # Save data
            if save_data(df):
                st.success("✅ Job application added successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed to save application. Please try again.")
    
    with tab3:
        display_tracker(df)
    
    with tab4:
        display_insights(df)
    
    with tab5:
        display_calendar(df)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>💡 <strong>Tip:</strong> Your data is automatically saved locally and backed up to prevent data loss.</p>
            <p>🔄 The app will remember your applications even if it goes offline!</p>
            <p>📧 Add contact information to keep track of who to follow up with.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 