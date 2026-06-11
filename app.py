import streamlit as st
from supabase import create_client, Client
import pandas as pd
from io import BytesIO

# -----------------------------------------------------------------------------
# STEP 1: SET PAGE CONFIG (সবার আগে থাকা বাধ্যতামূলক)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NGPI Student Registration", 
    page_icon="🎓",
    layout="centered"
)

# -----------------------------------------------------------------------------
# STEP 2: SUPABASE & SECRETS
# -----------------------------------------------------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------------------------------------------------------
# STEP 3: INSTITUTION CONFIGURATIONS (NGPI Seats)
# -----------------------------------------------------------------------------
LIMITS = {
    "CT": 30,    # Computer Technology
    "CST": 20,   # Computer Science & Technology
    "FT": 20,    # Food Technology
    "ET": 20,    # Electrical Technology
    "RAC": 10    # Refrigeration and Air Conditioning
}

MAX_STUDENTS = 100

# -----------------------------------------------------------------------------
# STEP 4: DATA FUNCTIONS
# -----------------------------------------------------------------------------
def load_data():
    try:
        res = supabase.table("students").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []

data = load_data()

def dept_count(data_list):
    counts = {k: 0 for k in LIMITS}
    for d in data_list:
        if d.get("department") in counts:
            counts[d["department"]] += 1
    return counts

counts = dept_count(data)
total = len(data)

# -----------------------------------------------------------------------------
# STEP 5: PREMIUM CENTERED WHITE-TEXT HEADER
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 25px 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    ">
        <h2 style="
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
            margin: 0 0 8px 0;
            white-space: nowrap;
            letter-spacing: 0.5px;
        ">
            Narsingdi Government Polytechnic Institute
        </h2>
        <p style="
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 14px;
            color: #f1f5f9;
            margin: 0 0 4px 0;
            font-weight: 500;
        ">
            🎓 Online Information Collection Portal — 7th Semester
        </p>
        <p style="
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 12px;
            color: #cbd5e1;
            margin: 0;
            font-style: italic;
        ">
            Please fill out the form carefully with accurate institutional information.
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)
st.write("")

# -----------------------------------------------------------------------------
# STEP 6: REGISTRATION CAPACITY CHECK
# -----------------------------------------------------------------------------
if total >= MAX_STUDENTS:
    st.error("⚠️ Registration Closed (Maximum capacity of 100 students has been reached).")
    st.stop()

available_dept = [d for d, l in LIMITS.items() if counts[d] < l]

if not available_dept:
    st.warning("⚠️ All departments are currently full. Registration is paused.")
    st.stop()

# -----------------------------------------------------------------------------
# STEP 7: MODERN BALANCED STUDENT FORM
# -----------------------------------------------------------------------------
with st.form("student_registration_form", clear_on_submit=False):
    
    st.write("### 📝 Student Profile Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name (Capital Letters)", placeholder="e.g. RAHAT KHAN")
        roll = st.text_input("Roll Number (6 Digits)", placeholder="e.g. 153245")
        department = st.selectbox("Department / Technology", available_dept)
        
    with col2:
        reg = st.text_input("Registration Number (10 Digits)", placeholder="e.g. 1502145326")
        semester = st.selectbox("Semester", ["7th"])
        shift = st.selectbox("Shift", ["1st Shift", "2nd Shift"])
        
    col3, col4 = st.columns(2)
    with col3:
        session = st.text_input("Academic Session", placeholder="e.g. 2021-22")
    with col4:
        mobile = st.text_input("Mobile Number", placeholder="01XXXXXXXXX")
        
    email = st.text_input("Email Address", placeholder="name@example.com")

    st.write("")
    confirm = st.checkbox("I hereby declare that all the information provided above is correct and I am a regular student of 7th Semester.")
    
    submit = st.form_submit_button("Submit Application", use_container_width=True)

    if submit:
        if not confirm:
            st.error("🔒 Please check the declaration checkbox to proceed.")
            st.stop()

        if not all([name, roll, reg, department, shift, semester, session, mobile, email]):
            st.error("❌ All fields are mandatory. Please fill out the missing information.")
            st.stop()

        if not mobile.startswith("01") or len(mobile) != 11:
            st.error("📱 Invalid Bangladeshi mobile number. It must be 11 digits and start with '01'.")
            st.stop()

        roll_check = supabase.table("students").select("*").eq("roll", roll.strip()).execute().data
        reg_check = supabase.table("students").select("*").eq("registration", reg.strip()).execute().data

        if roll_check:
            st.error(f"🚫 Roll Number '{roll}' is already registered in the system.")
            st.stop()

        if reg_check:
            st.error(f"🚫 Registration Number '{reg}' is already registered in the system.")
            st.stop()

        student_data = {
            "name": name.strip().upper(),
            "roll": roll.strip(),
            "registration": reg.strip(),
            "department": department,
            "shift": shift,
            "semester": semester,
            "session": session.strip(),
            "mobile": mobile.strip(),
            "email": email.strip()
        }

        supabase.table("students").insert(student_data).execute()
        
        st.success("🎉 Registration Successful! Your data has been securely saved.")
        st.balloons()
        st.rerun()

# -----------------------------------------------------------------------------
# STEP 8: PREMIUM ADMIN PANEL (ডিলিট লজিক ফিক্সড করা হয়েছে)
# -----------------------------------------------------------------------------
st.write("")
st.write("")
st.divider()

st.write("### 🔐 Management & Administration Panel")

if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    admin_password = st.text_input("Enter secure access code", type="password", placeholder="Admin Password")
    if admin_password == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.admin_auth = True
        st.rerun()
else:
    st.success("🔓 Administrative Access Granted")
    
    admin_data = load_data()
    admin_counts = dept_count(admin_data)
    
    st.write("#### 📊 Dashboard Overview")
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Total Enrolled", len(admin_data))
    m_col2.metric("Remaining Slots", MAX_STUDENTS - len(admin_data))
    m_col3.metric("Institute Code", 10022) 
    
    st.write("#### 📂 Technology-wise Enrollment Status")
    for d, limit in LIMITS.items():
        current = admin_counts[d]
        percentage = min(current / limit, 1.0)
        st.write(f"**{d} Technology** ({current} / {limit})")
        st.progress(percentage)

    st.write("#### 🔍 Student Search Engine")
    search_query = st.text_input("Search student by Roll or Registration number", placeholder="Type roll/reg here...")
    
    if search_query:
        search_results = [s for s in admin_data if search_query in str(s.get("roll")) or search_query in str(s.get("registration"))]
        if search_results:
            st.write(search_results)
        else:
            st.caption("No matching student records found.")

    st.write("#### 📋 Master Database Records")
    if admin_data:
        df = pd.DataFrame(admin_data)
        
        if not df.empty:
            cols_order = ["name", "roll", "registration", "department", "semester", "shift", "session", "mobile", "email", "created_at"]
            df = df.reindex(columns=cols_order)
            st.dataframe(df, use_container_width=True)

            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='NGPI_7th_Sem')
            
            st.download_button(
                label="⬇️ Export Full Database to Excel",
                data=excel_buffer.getvalue(),
                file_name="NGPI_Student_Database.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            # --- 🛠️ শতভাগ ফিক্সড ডিলিট সেকশন ---
            st.write("")
            st.markdown("---")
            st.write("#### 🗑️ Delete Student Record")
            
            delete_roll = st.text_input("Enter Roll Number to delete", placeholder="e.g. 123456")
            
            if delete_roll:
                # String এবং Integer দুটোর সাথেই যেন ম্যাচ করতে পারে সেই সেফটি লজিক
                cleaned_roll = delete_roll.strip()
                match = [s for s in admin_data if str(s.get("roll")).strip() == cleaned_roll]
                
                if match:
                    target_student = match[0]
                    st.warning(f"⚠️ Are you sure you want to delete **{target_student['name']}** (Roll: {target_student['roll']}, Dept: {target_student['department']})?")
                    
                    confirm_delete = st.button("Confirm Permanent Delete", type="primary", use_container_width=True)
                    
                    if confirm_delete:
                        try:
                            # ফিক্সড কোয়েরি: ডাটাবেজে ডাটা টাইপ ইন্টিজার বা স্ট্রিং যা-ই থাকুক, দুটোই ট্রাই করবে
                            # ১. প্রথমে ইন্টিজার ট্রাই করবে যদি রোলটি শুধু সংখ্যা হয়
                            if cleaned_roll.isdigit():
                                supabase.table("students").delete().eq("roll", int(cleaned_roll)).execute()
                            
                            # ২. সেফটি হিসেবে স্ট্রিং ফরম্যাটেও ডিলিট কোয়েরি ফায়ার করবে
                            supabase.table("students").delete().eq("roll", cleaned_roll).execute()
                            
                            st.success(f"🗑️ Record for Roll {cleaned_roll} has been successfully deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting record: {e}")
                else:
                    st.error("❌ No student record found with this Roll Number.")
    else:
        st.info("The student table is currently empty.")

    if st.button("🔄 Force Refresh Database"):
        st.rerun()
