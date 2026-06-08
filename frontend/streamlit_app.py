import streamlit as st
import requests
import pandas as pd
from datetime import date
import json

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI CRM Automation Suite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


def api_call(endpoint, method="GET", json_data=None):
    """Make API call"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=json_data)
        elif method == "POST":
            response = requests.post(url, json=json_data)
        elif method == "PUT":
            response = requests.put(url, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


with st.sidebar:
    st.title("🤖 AI CRM Suite")
    st.markdown("---")
    
    module = st.radio(
        "Select Module",
        ["📊 Dashboard", "🎯 Lead Qualification", "💬 CRM Copilot", "📧 Follow-Up Automation"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("**Tech Stack**:")
    st.markdown("• FastAPI | PostgreSQL")
    st.markdown("• OpenAI | Streamlit")
    st.markdown("• APScheduler | SQLAlchemy")


if module == "📊 Dashboard":
    st.markdown('<p class="main-header">📊 CRM Dashboard</p>', unsafe_allow_html=True)
    
    stats = api_call("/leads/stats/summary")
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Leads", stats["total_leads"], delta_color="normal")
        
        with col2:
            st.metric("🔥 Hot Leads", stats["hot_leads"], 
                     delta=f"{stats['hot_percentage']}%",
                     delta_color="normal")
        
        with col3:
            st.metric("🟡 Warm Leads", stats["warm_leads"])
        
        with col4:
            st.metric("🟢 Cold Leads", stats["cold_leads"])
        
        st.markdown("---")
        st.subheader("📅 Today's Tasks")
        daily_tasks = api_call("/tasks/dashboard/daily")
        
        if daily_tasks:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Pending Tasks", daily_tasks["total_pending"])
            
            with col2:
                st.metric("⚠️ Overdue", daily_tasks["overdue"], delta_color="inverse")
            
            if daily_tasks["tasks"]:
                tasks_df = pd.DataFrame([{
                    "Task ID": t["task_id"],
                    "Lead": t["lead_id"],
                    "Type": t["task_type"],
                    "Due": t["due_date"],
                    "Status": t["status"]
                } for t in daily_tasks["tasks"]])
                
                st.dataframe(tasks_df, use_container_width=True)


elif module == "🎯 Lead Qualification":
    st.markdown('<p class="main-header">🎯 AI Lead Qualification & Scoring</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 Add New Lead", "📄 Upload CSV"])
    
    with tab1:
        with st.form("lead_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name")
                company = st.text_input("Company")
                email = st.text_input("Email")
                industry = st.selectbox("Industry", 
                    ["SaaS", "Technology", "Finance", "Healthcare", "Retail", "Other"])
            
            with col2:
                employees = st.number_input("Employees", min_value=1, value=50)
                revenue = st.number_input("Revenue ($)", min_value=0, value=0)
                phone = st.text_input("Phone")
            
            message = st.text_area("Lead Message/Interest")
            
            submitted = st.form_submit_button("🤖 Score & Add Lead", type="primary")
            
            if submitted:
                if not all([name, company, email]):
                    st.error("Name, Company, and Email are required")
                else:
                    result = api_call("/leads/", method="POST", json_data={
                        "name": name,
                        "company": company,
                        "email": email,
                        "phone": phone,
                        "industry": industry,
                        "employees": employees,
                        "revenue": revenue,
                        "message": message
                    })
                    
                    if result:
                        st.success("Lead added successfully!")
                        
                        st.markdown("### 🤖 AI Analysis")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Lead Score", f"{result['score']}/100")
                        
                        with col2:
                            st.metric("Category", result["category"])
                        
                        with col3:
                            st.info(result["reason"])


    with tab2:
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        
        if uploaded_file:
            if st.button("📤 Upload Leads"):
                result = api_call("/leads/upload-csv", method="POST")
                if result:
                    st.success(result["message"])


elif module == "💬 CRM Copilot":
    st.markdown('<p class="main-header">💬 CRM Copilot</p>', unsafe_allow_html=True)
    
    st.info("🔍 Ask questions about your CRM data in natural language")
    
    st.subheader("⚡ Quick Queries")
    quick_queries = [
        "Show hot leads",
        "Leads not contacted in 7 days",
        "Summarize customer interactions",
        "Show all leads in SaaS industry"
    ]
    
    selected_query = st.selectbox("Choose a query", quick_queries)
    custom_query = st.text_input("Or enter custom query")
    
    query = custom_query if custom_query else selected_query
    
    if st.button("🚀 Run Query", type="primary"):
        with st.spinner("AI is generating SQL and executing..."):
            result = api_call("/copilot/query", method="POST", json_data={"user_query": query})
            
            if result:
                st.markdown("### 📊 Results")
                
                with st.expander("🔧 Generated SQL"):
                    st.code(result["sql_query"], language="sql")
                    st.info(result["explanation"])
                
                if result["results"]:
                    df = pd.DataFrame(result["results"])
                    st.dataframe(df, use_container_width=True)
                
                st.markdown("### 📝 AI Summary")
                st.info(result["summary"])


    st.markdown("---")
    st.subheader("📧 AI Email Generator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_company = st.text_input("Company Name")
        email_type = st.selectbox("Email Type", ["follow_up", "demo", "proposal"])
    
    with col2:
        lead_context = st.text_area("Lead Context (optional)")
    
    if st.button("✉️ Generate Email"):
        if email_company:
            result = api_call("/copilot/email/generate", method="POST", json_data={
                "company": email_company,
                "lead_context": lead_context,
                "email_type": email_type
            })
            
            if result:
                st.markdown("### 📧 Generated Email")
                st.text_area("Email Draft", result["email_draft"], height=300)


elif module == "📧 Follow-Up Automation":
    st.markdown('<p class="main-header">📧 Follow-Up Automation Engine</p>', unsafe_allow_html=True)
    
    st.subheader("🎯 AI Task Recommendations")
    recommendations = api_call("/copilot/recommendations")
    
    if recommendations and recommendations["recommendations"]:
        for rec in recommendations["recommendations"]:
            with st.expander(f"🔥 {rec['company']} - {rec['priority']} Priority"):
                st.write(f"**Action:** {rec['action']}")
                st.write(f"**Reason:** {rec['reason']}")
                
                if st.button(f"Create Task for {rec['company']}"):
                    result = api_call("/tasks/", method="POST", json_data={
                        "lead_id": rec["lead_id"],
                        "task_type": "follow_up",
                        "description": f"Follow up with {rec['company']}"
                    })
                    
                    if result:
                        st.success("Task created!")
                        st.code(result.get("email_draft", ""), language="text")
    
    st.markdown("---")
    st.subheader("📋 All Tasks")
    tasks = api_call("/tasks/")
    
    if tasks and tasks["tasks"]:
        tasks_df = pd.DataFrame([{
            "Task ID": t["task_id"],
            "Lead ID": t["lead_id"],
            "Type": t["task_type"],
            "Due Date": t["due_date"],
            "Status": t["status"]
        } for t in tasks["tasks"]])
        
        st.dataframe(tasks_df, use_container_width=True)


st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 AI CRM Automation Suite | Built with FastAPI, PostgreSQL, OpenAI & Streamlit</p>
</div>
""", unsafe_allow_html=True)