import streamlit as st
import pandas as pd
import os
from datetime import date
from io import BytesIO
from fpdf import FPDF

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def save_section_df(date_str, key, df):
    path = os.path.join(DATA_DIR, f"{key}_{date_str}.csv")
    df.to_csv(path, index=False)

def load_section_df(date_str, key, default_df):
    path = os.path.join(DATA_DIR, f"{key}_{date_str}.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return default_df

def save_money_val(date_str, key, val):
    path = os.path.join(DATA_DIR, f"{key}_{date_str}.txt")
    with open(path, "w") as f:
        f.write(str(val))

def load_money_val(date_str, key):
    path = os.path.join(DATA_DIR, f"{key}_{date_str}.txt")
    if os.path.exists(path):
        with open(path) as f:
            return float(f.read())
    return 0.0

def to_excel(df_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    processed_data = output.getvalue()
    return processed_data

def generate_pdf_report(stock_df, accom_df, expenses_df, money_paid, money_invested, profit, date_str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Pillars Bar & Restaurant Report - {date_str}", ln=True, align="C")

    # Stock Section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Stock Sheet", ln=True)
    pdf.set_font("Arial", size=10)
    cols = list(stock_df.columns)
    col_width = pdf.w / (len(cols) + 1)
    for col in cols:
        pdf.cell(col_width, 8, str(col), border=1)
    pdf.ln()
    for _, row in stock_df.iterrows():
        for col in cols:
            pdf.cell(col_width, 8, str(row[col]), border=1)
        pdf.ln()

    pdf.ln(10)

    # Accommodation Section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Accommodation Data", ln=True)
    pdf.set_font("Arial", size=10)
    cols = list(accom_df.columns)
    col_width = pdf.w / (len(cols) + 1)
    for col in cols:
        pdf.cell(col_width, 8, str(col), border=1)
    pdf.ln()
    for _, row in accom_df.iterrows():
        for col in cols:
            pdf.cell(col_width, 8, str(row[col]), border=1)
        pdf.ln()

    pdf.ln(10)

    # Expenses Section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Expenses", ln=True)
    pdf.set_font("Arial", size=10)
    cols = list(expenses_df.columns)
    col_width = pdf.w / (len(cols) + 1)
    for col in cols:
        pdf.cell(col_width, 8, str(col), border=1)
    pdf.ln()
    for _, row in expenses_df.iterrows():
        for col in cols:
            pdf.cell(col_width, 8, str(row[col]), border=1)
        pdf.ln()

    pdf.ln(10)

    # Money Transactions & Summary
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Money Transactions & Summary", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Money Paid to Boss: KES {money_paid:,.2f}", ln=True)
    pdf.cell(0, 10, f"Money Invested: KES {money_invested:,.2f}", ln=True)
    pdf.cell(0, 10, f"Profit: KES {profit:,.2f}", ln=True)

    return pdf.output(dest='S').encode('latin1')

#Streamlit UI
st.set_page_config(page_title="Pillars Bar Management App", layout="wide")
st.title("Pillars Bar & Accommodation Management")

st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose the app mode", ["Data Entry", "View Past Reports"])

if app_mode == "Data Entry":
    record_date = st.date_input("Select Date", value=date.today())
    date_str = record_date.strftime("%Y-%m-%d")

    st.header("Stock Sheet Data")
    stock = st.text_area("Paste stock CSV data here", height=150)
    stock_df = pd.DataFrame()
    if stock:
        try:
            stock_df = pd.read_csv(BytesIO(stock.encode()))
            st.write(stock_df)
        except Exception as e:
            st.error("Error loading stock data")

    st.header("Accommodation Data")
    accom = st.text_area("Paste accommodation CSV data here", height=150)
    accom_df = pd.DataFrame()
    if accom:
        try:
            accom_df = pd.read_csv(BytesIO(accom.encode()))
            st.write(accom_df)
        except Exception as e:
            st.error("Error loading accommodation data")

    st.header("Expenses")
    expenses = st.text_area("Paste expenses CSV data here", height=150)
    expenses_df = pd.DataFrame()
    if expenses:
        try:
            expenses_df = pd.read_csv(BytesIO(expenses.encode()))
            st.write(expenses_df)
        except Exception as e:
            st.error("Error loading expenses data")

    money_paid = st.number_input("Money Paid to Boss (KES)", min_value=0.0, format="%f")
    money_invested = st.number_input("Money Invested (KES)", min_value=0.0, format="%f")

    profit = money_paid - money_invested

    if st.button("Save Data"):
        if not stock_df.empty:
            save_section_df(date_str, "stock", stock_df)
        if not accom_df.empty:
            save_section_df(date_str, "accommodation", accom_df)
        if not expenses_df.empty:
            save_section_df(date_str, "expenses", expenses_df)
        save_money_val(date_str, "money_paid", money_paid)
        save_money_val(date_str, "money_invested", money_invested)
        st.success(f"Data saved for {date_str}")

    if st.button("Generate Excel Report"):
        dfs = {
            "Stock": stock_df,
            "Accommodation": accom_df,
            "Expenses": expenses_df
        }
        excel_bytes = to_excel(dfs)
        st.download_button(
            label="Download Excel Report",
            data=excel_bytes,
            file_name=f"Pillars_Report_{date_str}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if st.button("Generate PDF Report"):
        pdf_bytes = generate_pdf_report(stock_df, accom_df, expenses_df, money_paid, money_invested, profit, date_str)
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=f"Pillars_Report_{date_str}.pdf",
            mime="application/pdf"
        )

elif app_mode == "View Past Reports":
    st.header("📁 View Past Reports")

    saved_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv") or f.endswith(".txt")]
    saved_dates = sorted(list({f.split("_")[1].replace(".csv", "").replace(".txt", "") for f in saved_files}), reverse=True)

    if saved_dates:
        selected = st.selectbox("Select Date", saved_dates)
        st.markdown(f"### Report for: {selected}")

        stock_df = load_section_df(selected, "stock", pd.DataFrame())
        accom_df = load_section_df(selected, "accommodation", pd.DataFrame())
        expenses_df = load_section_df(selected, "expenses", pd.DataFrame())
        money_paid = load_money_val(selected, "money_paid")
        money_invested = load_money_val(selected, "money_invested")
        profit = money_paid - money_invested

        st.subheader("Stock Sheet")
        if not stock_df.empty:
            st.dataframe(stock_df)
        else:
            st.info("No stock data available for this date.")

        st.subheader("Accommodation Data")
        if not accom_df.empty:
            st.dataframe(accom_df)
        else:
            st.info("No accommodation data available for this date.")

        st.subheader("Expenses")
        if not expenses_df.empty:
            st.dataframe(expenses_df)
        else:
            st.info("No expenses data available for this date.")

        st.subheader("Money Transactions")
        st.markdown(f"Money Paid to Boss: KES {money_paid:,.2f}")
        st.markdown(f"Money Invested: KES {money_invested:,.2f}")
        st.markdown(f"Profit: KES {profit:,.2f}")

    else:
        st.warning("No saved reports found.")
