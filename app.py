# Import important libraries
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import numpy as np
import base64
import time


from database import get_connection, create_tables
create_tables()   # Tables ensure ho jaye
conn = get_connection()
c = conn.cursor()



from auth import is_strong_password, hash_password, generate_otp, is_valid_email
from email_service import send_otp_email
from pdf_service import generate_pdf

# ------------------------------------------------------ App Configuration -------------------------------------------------------------------
st.set_page_config(page_title="Spendora", page_icon="SpendoraLOGO.png",layout="wide")

def get_base64_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

if "show_splash" not in st.session_state:
    st.session_state.show_splash = True


if st.session_state.show_splash:

    logo_base64 = get_base64_image("appLOGO-removebg-preview.png")

    st.markdown(f"""
    <style>
    .logo-container {{
        display:flex;
        justify-content:center;
        align-items:center;
        height:90vh;
        flex-direction:column;
    }}

    .blink {{
        animation: blink 1s infinite;
    }}

    @keyframes blink {{
        0% {{opacity:1;}}
        50% {{opacity:0.2;}}
        100% {{opacity:1;}}
    }}
    </style>

    <div class="logo-container">
        <img src="data:image/png;base64,{logo_base64}" width="200" class="blink">
        <h1 style="color:white;">Spendora</h1>
        <p style="color:gray;">Expense Risk Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)

    time.sleep(2)

    st.session_state.show_splash = False
    st.rerun()

# ----------------------------------------------------------- For Email Verification ---------------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if "current_user" not in st.session_state:
    st.session_state.current_user=None

if "reset_mode" not in st.session_state:
    st.session_state.reset_mode = False


# --------------------------------------------------- To improve the UI of the App, adding CSS -------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0B1220;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #0F172A;
    border-right: 1px solid #1F2937;
}

hr {
    border: 1px solid #1F2937;
}

div[data-testid="metric-container"] {
    background-color: #111827;
    border: 1px solid #1F2937;
    padding: 18px;
    border-radius: 14px;
}

.stButton>button {
    background-color: #3B82F6;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: #2563EB;
}

</style>
""", unsafe_allow_html=True)


# Hero Section Add
# Header
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center;">
    <h2 style="margin:0;">Spendora</h2>
    <span style="color:#9CA3AF;">Financial Risk Dashboard</span>
</div>
<hr>
""", unsafe_allow_html=True)


# Setup for Spendora
if st.session_state.logged_in:
    c.execute("SELECT name FROM users WHERE email=?",
          (st.session_state.current_user,))
    result = c.fetchone()

    if result:
        user_name = result[0]
    else:
        user_name = "User"

    st.markdown(f"""
        <div style="font-size:44px; font-weight:700; color:white;">
            Welcome, {user_name}!
        </div>
        <div style="color:#9CA3AF; font-size:22px;">
            Control Your Expenses. Reduce Financial Risk. 
        </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
<h1 style="color:white;">Navigation</h1>
""", unsafe_allow_html=True)


#--------------------------------------------------- Ask user to enter Salary and other details---------------------------------------------------

st.sidebar.header("Enter Financial Details")

from datetime import datetime

current_year = datetime.now().year

months = [
            f"January {current_year}",
            f"February {current_year}",
            f"March {current_year}",
            f"April {current_year}",
            f"May {current_year}",
            f"June {current_year}",
            f"July {current_year}",
            f"August {current_year}",
            f"September {current_year}",
            f"October {current_year}",
            f"November {current_year}",
            f"December {current_year}",
        ]

selected_month = st.sidebar.selectbox("Select Month", months) 

salary = st.sidebar.number_input("Monthly Salary", min_value=0)
rent = st.sidebar.number_input("Rent", key="rent")
emi = st.sidebar.number_input("EMI", key="emi")
bills = st.sidebar.number_input("Bills", key="bills")
food = st.sidebar.number_input("Food", key="food")
travel = st.sidebar.number_input("Travel", key="travel")
entertainment = st.sidebar.number_input("Entertainment", key="entertainment")
shopping = st.sidebar.number_input("Shopping", key="shopping")
other = st.sidebar.number_input("Other", key="other")
data = {
        "Category": ["Rent","EMI","Bills","Food","Travel","Entertainment","Shopping","Other"],
        "Amount": [rent,emi,bills,food,travel,entertainment,shopping,other]
    }



# --------------------------------------------------------- Sign-Up/LogIn LOGIC ------------------------------------------------------------------
if not st.session_state.logged_in:

    st.title("✍️ Create Account")

    menu = st.sidebar.radio("Account", ["Sign Up", "Login"])

# ---------------- SIGN UP ----------------
    if menu == "Sign Up":

        

        name = st.text_input("Your Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Send OTP"):

            if not name:
                st.error("Please enter your name")

            elif not is_valid_email(email):
                st.error("Invalid email address")

            elif not is_strong_password(password):
                st.error("""
        Password must contain:
        • At least 8 characters  
        • One uppercase letter  
        • One lowercase letter  
        • One number  
        • One special character
                """)

            else:
                otp = generate_otp()
                st.session_state.generated_otp = otp
                st.session_state.temp_user = {
                    "name": name,
                    "email": email,
                    "password": hash_password(password)
                }

                send_otp_email(email, otp, name)
                st.success("OTP sent to your email.")

        entered_otp = st.text_input("Enter OTP")

        if st.button("Verify OTP"):

            if entered_otp == st.session_state.get("generated_otp"):

                user = st.session_state.temp_user

                c.execute("SELECT * FROM users WHERE email=?",
                      (user["email"],))
                existing_user = c.fetchone()

                if existing_user:
                    st.error("User already registered. Please login.")
                else:
                    c.execute("INSERT INTO users VALUES (?, ?, ?)",
                          (user["email"], user["name"], user["password"]))
                    conn.commit()

                    st.session_state.logged_in = True
                    st.session_state.current_user = user["email"]

                    st.success("Account verified successfully!")
                    st.rerun()
            else:
                st.error("Invalid OTP")

            

# ---------------- LOGIN ----------------

    elif menu == "Login" and not st.session_state.reset_mode:


        

        st.title("Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        # --------------------------------------------- IF USER FORGET HIS PASSWORD -------------------------------------------------

        if st.button("👤 Login"):

            hashed_password = hash_password(password)

            c.execute("SELECT * FROM users WHERE email=? AND password=?",
                  (email, hashed_password))
            user = c.fetchone()

            if user:
                st.session_state.logged_in = True
                st.session_state.current_user = email
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid email or password")

# -----------------------------------------------------Add the Dashboard+Analytics code here for a flow ------------------------------------------- 

if st.session_state.logged_in:
    # Logout Button
    if st.button("👋 Logout"):
    
        # Clear financial data
        keys_to_clear = [
            "salary", "rent", "emi", "bills", "food",
            "travel", "entertainment", "shopping", "other"
        ]

        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        # Reset login state
        st.session_state.logged_in = False
        st.session_state.current_user = None

        st.rerun()

    # ----------------------------------------------------- SideBar ---------------------------------------------------------------------
    page = st.sidebar.radio("Go to", ["Dashboard", "Analytics"])

    selected_month = st.sidebar.selectbox("Selected Month",months)

    # ---------------------------------------------------- PAGE (Dashboard) -------------------------------------------------------------
    if page=="Dashboard":

    # If user enter 0 or <0 value in salary bar
        if salary <=0:
            print("Salary is Invalid")
        # After enter all entries, thay need to click on button "Analyze"
        if st.button("Analyze"):
            total_expense = rent+emi+bills+food+travel+entertainment+shopping+other
            savings = salary - total_expense

            from datetime import datetime

            month = selected_month

            saving_percentage = (savings / salary) * 100 if salary > 0 else 0

            c.execute("""
            INSERT OR REPLACE INTO financial_data
            (email, month, salary, rent, emi, bills, food, travel,
            entertainment, shopping, other, total_expense, savings, saving_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                st.session_state.current_user,
                month,
                salary,
                rent,
                emi,
                bills,
                food,
                travel,
                entertainment,
                shopping,
                other,
                total_expense,
                savings,
                saving_percentage
            ))

            conn.commit()

        # Condition, if salary more than 0 
            if salary > 0:
                saving_percentage = (savings/salary)*100
            else:
                saving_percentage = 0

            # 2️⃣ Simulate previous month
                variation = np.random.uniform(0.9, 1.1)

                prev_total_expense = total_expense * variation
                prev_savings = salary - prev_total_expense

                # 3️⃣ Create comparison df
                comparison_df = pd.DataFrame({
                    "Month": ["Previous Month", "Current Month"],
                    "Total Expense": [prev_total_expense, total_expense],
                    "Savings": [prev_savings, savings]
                })

            #----------------------------------------- Saving Percentange Analysis --------------------------------------------------
            # KPI 
            if saving_percentage >= 35:
                risk_score = 20
                status = "💎 Excellent! Your savings rate is strong and your financial health looks stable."
    
            elif saving_percentage >= 15:
                risk_score = 50
                status = "📊 Moderate Savings. Try to increase your savings to improve financial security."

            else:
                risk_score = 80
                status = "⚠️ High Financial Risk! Your savings are very low. Consider reducing expenses and saving more."

            st.markdown(
        "<hr style='border:1px solid #1F2937;'>",
        unsafe_allow_html=True
    )

            with st.container():
                st.markdown("## 📊 Financial Overview")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                    label="💸 Total Expense",
                    value=f"₹ {total_expense:,.0f}"
                )

                with col2:
                    st.metric(
                        label="💰 Savings",
                        value=f"₹ {savings:,.0f}"
                    )

                with col3:
                    st.metric(
                        label="📈 Savings %",
                        value=f"{saving_percentage:.1f}%"
                    )

            st.subheader(status)

# ---------------------------------------------------------- ANALYTICS CODE ------------------------------------------------------------------

    elif page == "Analytics":

        

        analysis_text = f"""
        Total Revenue: ₹2,50,000
        Total Expenses: ₹1,40,000
        Net Profit: ₹1,10,000
        Growth Rate: 12%
        """

        st.title("📊 Expense Analytics")

        # Category wise expense
        df = pd.DataFrame(data)

        # Category wise expense
        category_data = df.groupby("Category")["Amount"].sum().reset_index()

        fig = px.pie(
        df,
        names="Category",
        values="Amount",
        hole=0.5
    )

        fig.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="white"),
            legend=dict(font=dict(color="white"))
        )

        st.plotly_chart(fig, use_container_width=True)

        # ------------------------------- This bar will show where your money is going!!!--------------------------------------------------

        st.markdown("### 📊 Expense Ranking")
        df = pd.DataFrame(data)

        df_sorted = df.sort_values(by="Amount", ascending=False)

        st.table(df_sorted)

        total_expense = rent+emi+bills+food+travel+entertainment+shopping+other
        savings = salary - total_expense

        variation = np.random.uniform(0.9, 1.1)
        prev_total_expense = total_expense * variation
        prev_savings = salary - prev_total_expense

        comparison_df = pd.DataFrame({
                    "Month": ["Previous Month", "Current Month"],
                    "Total Expense": [prev_total_expense, total_expense],
                    "Savings": [prev_savings, savings]
                })
        st.markdown("### 📈 Monthly Comparison")
        fig_trend = px.bar(
            comparison_df,
            x="Month",
            y=["Total Expense", "Savings"],
            barmode="group",
        )

        fig_trend.update_layout(
            paper_bgcolor="#0B1220",
            plot_bgcolor="#0B1220",
            font=dict(color="white"),
        )

        st.plotly_chart(fig_trend, use_container_width=True)


        # ----------------------------------------------------- Monthly Trend Simulation ----------------------------------------------------------

        # Monthly Trend Simulation
        if salary > 0:

            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

            base_expense = rent + emi + bills + food + travel + entertainment + shopping + other

            expense_trend = []
            savings_trend = []
            saving_percent_trend = []

            for i in range(6):
                variation = np.random.uniform(0.9, 1.1)

                monthly_expense = base_expense * variation
                monthly_savings = salary - monthly_expense
                saving_percent = (monthly_savings / salary) * 100

                expense_trend.append(monthly_expense)
                savings_trend.append(monthly_savings)
                saving_percent_trend.append(saving_percent)

            trend_df = pd.DataFrame({
                "Month": months,
                "Expense": expense_trend,
                "Savings": savings_trend,
                "Savings %": saving_percent_trend
            })

            st.markdown("## 📈 Financial Trend Analysis")

            fig = px.line(
                trend_df,
                x="Month",
                y=["Expense", "Savings"],
                markers=True
            )

            fig.update_layout(
                paper_bgcolor="#0B1220",
                plot_bgcolor="#0B1220",
                font=dict(color="white")
            )

            st.plotly_chart(fig, use_container_width=True)

            # ---------------------------------------- Savings % Chart (INSIDE SAME BLOCK) ------------------------------------------------------
            st.markdown("### 📊 Savings Percentage Movement")

            fig_percent = px.line(
                trend_df,
                x="Month",
                y="Savings %",
                markers=True
            )

            fig_percent.update_layout(
                paper_bgcolor="#0B1220",
                plot_bgcolor="#0B1220",
                font=dict(color="white")
            )

            st.plotly_chart(fig_percent, use_container_width=True)

        else:
            st.warning("Please enter salary and expenses to view analytics.")


        st.markdown("## 📜 Previous Statements")

        c.execute("""
        SELECT *
        FROM financial_data
        WHERE email=? AND month=?
        ORDER BY rowid DESC
        """, (st.session_state.current_user, selected_month))

        rows = c.fetchall()   # ✅ THIS LINE MUST BE HERE

        if rows:


            history_df = pd.DataFrame(rows, columns=[
                "Email","Month","Salary","Rent","EMI","Bills","Food",
                "Travel","Entertainment","Shopping","Other",
                "Total Expense","Savings","Saving %"
            ])

            history_df = history_df.drop(columns=["Email"])

            st.dataframe(history_df)

            if st.button("📥 Download Detailed Financial Report"):

                user_name = st.session_state.current_user

                pdf_file = generate_pdf(user_name, selected_month, history_df)

                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="Click Here to Download",
                        data=f,
                        file_name="Spendora_Detailed_Report.pdf",
                        mime="application/pdf"
                    )

        else:
            st.warning("No data found for selected month.")

            empty_data = {
                "Salary": [0],
                "Rent": [0],
                "EMI": [0],
                "Bills": [0],
                "Food": [0],
                "Travel": [0],
                "Entertainment": [0],
                "Shopping": [0],
                "Other": [0],
                "Total Expense": [0],
                "Savings": [0],
                "Saving %": [0],
            }

            empty_df = pd.DataFrame(empty_data)

            st.dataframe(empty_df)


    else:
        st.info("No previous data found.")