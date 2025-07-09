import streamlit as st
import pandas as pd
import os
from datetime import date
from io import BytesIO

# Constants
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

ITEMS = [
    "TUSKER", "PILISNER", "TUSKER MALT", "TUSKER LITE", "GUINESS KUBWA",
    "GUINESS SMALL", "BALOZICAN", "WHITE CAP", "BALOZI", "SMIRNOFF ICE",
    "SAVANNAH", "SNAPP", "TUSKER CIDER", "KINGFISHER", "ALLSOPPS",
    "G.K CAN", "T.LITE CAN", "GUARANA", "REDBULL", "RICHOT ½",
    "RICHOT ¼", "VICEROY ½", "VICEROY ¼", "VODKA½", "VODKA¼",
    "KENYACANE ¾", "KENYACANE ½", "KENYACANE ¼", "GILBEYS ½", "GILBEYS ¼",
    "V&A 750ml", "CHROME", "TRIPLE ACE", "BLACK AND WHITE", "KIBAO½",
    "KIBAO¼", "HUNTERS ½", "HUNTERS ¼", "CAPTAIN MORGAN", "KONYAGI",
    "V&A", "COUNTY", "BEST 750ml", "WATER 1L", "WATER½",
    "LEMONADE", "CAPRICE", "FAXE", "C.MORGAN", "VAT 69",
    "SODA300ML", "SODA500ML", "BLACK AND WHITE", "BEST", "CHROME 750ml",
    "MANGO", "TRUST", "PUNCH", "VODKA 750ml", "KONYAGI 500ml",
    "GILBEYS 750ml"
]

# Helper Functions
def get_filepath(date_str, section):
    return os.path.join(DATA_DIR, f"{section}_{date_str}.csv")

def load_section_df(date_str, section, default_df):
    path = get_filepath(date_str, section)
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except pd.errors.EmptyDataError:
            return default_df
    else:
        return default_df

def save_section_df(date_str, section, df):
    path = get_filepath(date_str, section)
    df.to_csv(path, index=False)

def load_money_val(date_str, key):
    path = os.path.join(DATA_DIR, f"{key}_{date_str}.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return float(f.read())
            except ValueError:
                return 0.0
    return 0.0

def save_money_val(date_str, key, val):
    path = os.path.join(DATA_DIR, f"{key}_{date_str}.txt")
    with open(path, "w") as f:
        f.write(str(val))

def to_excel(df_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    processed_data = output.getvalue()
    return processed_data

# Streamlit App
st.set_page_config(page_title="Pillars Bar Management App", layout="wide")
st.title("Pillars Bar & Accommodation Management")

# Sidebar for Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose the app mode", ["Data Entry", "View Past Reports"])

if app_mode == "Data Entry":
    # --- Date Selection ---
    record_date = st.date_input("Select Date", value=date.today())
    date_str = record_date.strftime("%Y-%m-%d")

    # --- Stock Management ---
    st.header("Stock Management")
    default_stock_df = pd.DataFrame({
        "Item": ITEMS,
        "Opening Stock": [0] * len(ITEMS),
        "Purchases": [0] * len(ITEMS),
        "Closing Stock": [0] * len(ITEMS),
        "Selling Price": [0.0] * len(ITEMS)
    })
    stock_df = load_section_df(date_str, "stock", default_stock_df)

    edited_stock_df = st.data_editor(
        stock_df,
        num_rows="dynamic",
        use_container_width=True,
        key="stock_editor"
    )

    edited_stock_df["Sales"] = (
        edited_stock_df["Opening Stock"] + edited_stock_df["Purchases"] - edited_stock_df["Closing Stock"]
    )
    edited_stock_df["Amount"] = (
        edited_stock_df["Sales"] * edited_stock_df["Selling Price"]
    )

    st.dataframe(edited_stock_df)

    if st.button("Save Stock Data"):
        save_section_df(date_str, "stock", edited_stock_df.drop(columns=["Sales", "Amount"]))
        st.success("Stock data saved!")

    # --- Accommodation Data ---
    st.header("Accommodation Data")
    default_accom_df = pd.DataFrame({
        "Room Number": ["" for _ in range(10)],
        "1st Floor Rooms": ["" for _ in range(10)],
        "Ground Floor Rooms": ["" for _ in range(10)],
        "Money Lendered": [0.0 for _ in range(10)],
        "Payment Method": ["" for _ in range(10)],
    })
    accom_df = load_section_df(date_str, "accommodation", default_accom_df)

    edited_accom_df = st.data_editor(accom_df, num_rows="dynamic", use_container_width=True)

    total_first_floor = edited_accom_df["1st Floor Rooms"].apply(lambda x: 1 if str(x).strip() else 0).sum()
    total_ground_floor = edited_accom_df["Ground Floor Rooms"].apply(lambda x: 1 if str(x).strip() else 0).sum()
    total_lendered = edited_accom_df["Money Lendered"].sum()

    st.markdown(f"Total 1st Floor Rooms Used: {total_first_floor}")
    st.markdown(f"Total Ground Floor Rooms Used: {total_ground_floor}")
    st.markdown(f"Total Money Lendered: KES {total_lendered:,.2f}")

    if st.button("Save Accommodation Data"):
        save_section_df(date_str, "accommodation", edited_accom_df)
        st.success("Accommodation data saved!")

    # --- Expenses ---
    st.header("Expenses")
    default_expenses_df = pd.DataFrame({
        "Description": ["" for _ in range(10)],
        "Amount": [0.0 for _ in range(10)],
    })
    expenses_df = load_section_df(date_str, "expenses", default_expenses_df)

    edited_expenses_df = st.data_editor(expenses_df, num_rows="dynamic", use_container_width=True)
    total_expenses = edited_expenses_df["Amount"].sum()
    st.markdown(f"Total Expenses: KES {total_expenses:,.2f}")

    if st.button("Save Expenses"):
        save_section_df(date_str, "expenses", edited_expenses_df)
        st.success("Expenses saved!")

    # --- Money Transactions ---
    st.header("Money Transactions")

    money_paid = load_money_val(date_str, "money_paid")
    money_invested = load_money_val(date_str, "money_invested")

    money_paid_input = st.number_input("Money Paid to Boss", min_value=0.0, value=money_paid, step=1.0)
    money_invested_input = st.number_input("Money Invested (e.g., from Chama)", min_value=0.0, value=money_invested, step=1.0)

    if st.button("Save Money Transactions"):
        save_money_val(date_str, "money_paid", money_paid_input)
        save_money_val(date_str, "money_invested", money_invested_input)
        st.success("Money transactions saved!")

    # --- Summary ---
    st.header("Summary")
    total_sales_amount = edited_stock_df["Amount"].sum()
    profit = total_sales_amount - total_expenses - money_paid_input

    st.markdown(f"Total Sales Amount: KES {total_sales_amount:,.2f}")
    st.markdown(f"Total Expenses: KES {total_expenses:,.2f}")
    st.markdown(f"Money Paid to Boss: KES {money_paid_input:,.2f}")
    st.markdown(f"Money Invested: KES {money_invested_input:,.2f}")
    st.markdown(f"Profit: KES {profit:,.2f}")

elif app_mode == "View Past Reports":
    st.header("📁 View Past Reports")

    saved_dates = sorted([
        f.split("_")[1].replace(".csv", "").replace(".txt", "")
        for f in os.listdir(DATA_DIR)
        if f.endswith(".csv") or f.endswith(".txt")
    ], reverse=True)
    # Remove duplicates and keep only unique dates
    saved_dates = list(dict.fromkeys(saved_dates))


    if saved_dates:
        selected = st.selectbox("Select Date", saved_dates)
        st.markdown(f"### Report for: {selected}")

        stock = load_section_df(selected, "stock", pd.DataFrame())
        accom = load_section_df(selected, "accommodation", pd.DataFrame())
        expenses = load_section_df(selected, "expenses", pd.DataFrame())

        try:
            money_paid = load_money_val(selected, "money_paid")
            money_invested = load_money_val(selected, "money_invested")
        except:
            money_paid = 0.0
            money_invested = 0.0


        st.subheader("Stock Sheet")
        if not stock.empty:
            st.dataframe(stock)
        else:
            st.info("No stock data available for this date.")


        st.subheader("Accommodation Data")
        if not accom.empty:
            st.dataframe(accom)
        else:
            st.info("No accommodation data available for this date.")


        st.subheader("Expenses")
        if not expenses.empty:
            st.dataframe(expenses)
        else:
            st.info("No expenses data available for this date.")

        st.subheader("Money Transactions")
        st.markdown(f"Money Paid to Boss: KES {money_paid:,.2f}")
        st.markdown(f"Money Invested: KES {money_invested:,.2f}")

    else:
        st.warning("No saved reports found.")
