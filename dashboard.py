import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Travel Spend Intelligence", layout="wide")

# --- SIMPLE SECURITY ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "admin123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password incorrect", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('travel_data.xlsx')
    except FileNotFoundError:
        # Fallback dummy data
        data = {
            'Organisation Name': ['Alpha Corp', 'Beta Ltd', 'Gamma Inc', 'Delta Sol'],
            'Month': ['June', 'June', 'July', 'July'],
            'Spend': [150000, 45000, 160000, 50000],
            'Status': ['Onboarded', 'Unmanaged', 'Onboarded', 'Unmanaged'],
            'Org Type': ['Enterprise', 'SME', 'Enterprise', 'SME']
        }
        df = pd.DataFrame(data)
    return df

df = load_data()

# --- DASHBOARD LAYOUT ---
st.title("✈️ Travel Spend & Onboarding Intelligence")

# Filters
st.sidebar.header("Filter Views")
status = st.sidebar.multiselect("Status", df["Status"].unique(), default=df["Status"].unique())
org_type = st.sidebar.multiselect("Org Type", df["Org Type"].unique(), default=df["Org Type"].unique())
df_selection = df.query("Status == @status & `Org Type` == @org_type")

# KPIs
total_spend = df_selection["Spend"].sum()
col1, col2 = st.columns(2)
col1.metric("Total Spend", f"₹ {total_spend:,.0f}")
col2.metric("Active Orgs", df_selection["Organisation Name"].nunique())

st.markdown("---")

# Charts
c1, c2 = st.columns(2)
with c1:
    st.subheader("Spend by Status")
    pie_data = df_selection.groupby('Status')['Spend'].sum().reset_index()
    fig = px.pie(pie_data, values='Spend', names='Status', color='Status', 
                 color_discrete_map={'Onboarded':'#00CC96', 'Unmanaged':'#EF553B'})
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Top Unmanaged Spend")
    unmanaged = df_selection[df_selection["Status"] == "Unmanaged"]
    if not unmanaged.empty:
        top_orgs = unmanaged.groupby("Organisation Name")["Spend"].sum().nlargest(5).reset_index()
        fig = px.bar(top_orgs, x="Spend", y="Organisation Name", orientation='h', color_discrete_sequence=["#EF553B"])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No unmanaged data.")

# Data Table
st.dataframe(df_selection)
