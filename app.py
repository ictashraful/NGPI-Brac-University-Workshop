import streamlit as st
from supabase import create_client, Client
import pandas as pd
from io import BytesIO

# -------------------------
# SET PAGE CONFIG (সবার আগে থাকতে হবে)
# -------------------------
st.set_page_config(page_title="Student Registration", layout="centered")

# -------------------------
# SUPABASE & SECRETS
# -------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# SETTINGS
# -------------------------
LIMITS = {
    "CT": 30,
    "CST": 20,
    "FT": 20,
    "ET": 20,
    "RAC": 10
}

MAX_STUDENTS = 100

# -------------------------
# LOAD DATA FUNCTION
# -------------------------
def load_data():
    return supabase.table("students").select("*").execute().data

# এখন ডাটা লোড করা নিরাপদ
data = load_data()

# -------------------------
# COUNT FUNCTIONS
# -------------------------
def dept_count(data):
    counts = {k: 0 for k in LIMITS}
    for d in data:
        if d["department"] in counts:
            counts[d["department"]] += 1
    return counts

counts = dept_count(data)
total = len(data)

# -------------------------
# UI HEADER
# -------------------------
st.title("🎓 7th Semester Registration Portal")
st.caption("Only eligible students can apply")

# -------------------------
# FULL CHECK
# -------------------------
if total >= MAX_STUDENTS:
    st.error("❌ Registration Closed (100 Students Reached)")
    st.stop()

# -------------------------
# AVAILABLE DEPARTMENTS
# -------------------------
available_dept = [d for d, l in LIMITS.items() if counts[d] < l]

# -------------------------
# STUDENT FORM
# -------------------------
with st.form("form"):

    st.subheader("Student Information")

    name = st.text_input("Full Name")
    roll = st.text_input("Roll Number")
    reg = st.text_input("Registration Number")

    department = st.selectbox("Department", available_dept)

    shift = st.selectbox("Shift", ["1st Shift", "2nd Shift"])

    session = st.text_input("Session (e.g. 2020-21)")

    mobile = st.text_input("Mobile Number")
    email = st.text_input("Email Address")

    confirm = st.checkbox("I confirm I am a 7th Semester student")

    submit = st.form_submit_button("Submit")

    if submit:

        if not confirm:
            st.error("Eligibility confirmation required")
            st.stop()

        if not all([name, roll, reg, department, shift, session, mobile, email]):
            st.error("All fields are required")
            st.stop()

        # VALIDATION HELPERS
        if not mobile.startswith("01") or len(mobile) != 11:
            st.error("Invalid Bangladeshi mobile number")
            st.stop()

        # DUPLICATE CHECK (efficient)
        roll_check = supabase.table("students").select("*").eq("roll", roll).execute().data
        reg_check = supabase.table("students").select("*").eq("registration", reg).execute().data

        if roll_check:
            st.error("Roll already exists")
            st.stop()

        if reg_check:
            st.error("Registration already exists")
            st.stop()

        # INSERT DATA
        student = {
            "name": name,
            "roll": roll,
            "registration": reg,
            "department": department,
            "shift": shift,
            "semester": "7th",
            "session": session,
            "mobile": mobile,
            "email": email
        }

        supabase.table("students").insert(student).execute()

        st.success("🎉 Registration Successful!")

        st.info(f"""
        Name: {name}
        Roll: {roll}
        Department: {department}
        """)

        st.rerun()

# -------------------------
# ADMIN PANEL
# -------------------------
st.divider()
st.subheader("🔐 Admin Dashboard")

if "admin" not in st.session_state:
    st.session_state.admin = False

if not st.session_state.admin:
    pwd = st.text_input("Admin Password", type="password")

    if pwd == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.admin = True
        st.rerun()

else:
    st.success("Admin Logged In")

    data = load_data()
    counts = dept_count(data)

    st.write("## 📊 Overview")

    col1, col2 = st.columns(2)
    col1.metric("Total Students", len(data))
    col2.metric("Remaining Slots", MAX_STUDENTS - len(data))

    st.write("## Department Status")

    for d in LIMITS:
        st.progress(counts[d] / LIMITS[d])
        st.write(f"{d}: {counts[d]} / {LIMITS[d]}")

    st.write("## Search Student")

    search = st.text_input("Search by Roll or Registration")

    if search:
        result = [x for x in data if x["roll"] == search or x["registration"] == search]
        st.write(result)

    st.write("## All Students")

    df = pd.DataFrame(data)
    st.dataframe(df)

    # -------------------------
    # EXCEL DOWNLOAD
    # -------------------------
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')

    st.download_button(
        "⬇ Download Excel",
        data=output.getvalue(),
        file_name="students.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🔄 Refresh Data"):
        st.rerun()
