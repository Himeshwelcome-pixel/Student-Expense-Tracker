
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Student Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

FILE_NAME = "expenses.csv"

COLUMNS = ["Date", "Amount", "Category", "Description"]

CATEGORIES = [
    "Food", "Travel", "Books", "Shopping",
    "College", "Entertainment", "Other"
]

# ==================================================
# 2. PROFESSIONAL DESIGN
# ==================================================

st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .hero {
        padding: 25px;
        border-radius: 15px;
        background: linear-gradient(120deg, #172554, #2563eb);
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: white;
        margin-bottom: 5px;
    }

    .hero p {
        color: #dbeafe;
        font-size: 16px;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# 3. CSV FILE MANAGEMENT
# ==================================================

def load_expenses():

    if not os.path.exists(FILE_NAME):
        pd.DataFrame(columns=COLUMNS).to_csv(
            FILE_NAME, index=False
        )

    try:
        df = pd.read_csv(FILE_NAME)

    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        df = pd.DataFrame(columns=COLUMNS)

    if df.empty:
        return pd.DataFrame(columns=COLUMNS)

    for column in COLUMNS:
        if column not in df.columns:
            df[column] = ""

    df = df[COLUMNS]

    df["Date"] = pd.to_datetime(
        df["Date"], errors="coerce"
    )

    df["Amount"] = pd.to_numeric(
        df["Amount"], errors="coerce"
    )

    df = df.dropna(subset=["Date", "Amount"])

    df = df[df["Amount"] > 0]

    return df.reset_index(drop=True)


def save_expenses(df):
    df[COLUMNS].to_csv(FILE_NAME, index=False)


# ==================================================
# 4. LOAD LATEST DATA
# ==================================================

# The CSV is read again whenever Streamlit reruns.
# This ensures the dashboard shows the latest saved data.

df = load_expenses()


# ==================================================
# 5. HEADER
# ==================================================

st.markdown("""
<div class="hero">
    <h1>💰 Student Expense Tracker</h1>
    <p>Take control of your money. Track expenses.
    Manage your monthly budget. Make smarter decisions.</p>
</div>
""", unsafe_allow_html=True)


# ==================================================
# 6. SIDEBAR SETTINGS
# ==================================================

st.sidebar.title("⚙️ Settings")

monthly_budget = st.sidebar.number_input(
    "Monthly Budget (₹)",
    min_value=1.0,
    value=5000.0,
    step=500.0
)

st.sidebar.divider()

st.sidebar.markdown("### Quick Navigation")
st.sidebar.markdown("""
- Dashboard
- Add Expense
- Expense History
- Edit Expense
- Delete Expense
- Download Report
""")

st.sidebar.divider()

st.sidebar.caption(
    "Student Expense Tracker | Version 2.0"
)


# ==================================================
# 7. ADD NEW EXPENSE
# ==================================================

st.markdown(
    '<p class="section-title">➕ Add New Expense</p>',
    unsafe_allow_html=True
)

with st.form("add_expense_form", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        expense_date = st.date_input(
            "Expense Date",
            value=date.today(),
            max_value=date.today()
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=10.0
        )

    with col2:
        category = st.selectbox(
            "Category",
            CATEGORIES
        )

        description = st.text_input(
            "Description",
            placeholder="Example: Lunch, bus fare, textbooks"
        )

    submitted = st.form_submit_button(
        "💾 Save Expense",
        use_container_width=True
    )

    if submitted:

        if amount <= 0:
            st.error("Please enter an amount greater than zero.")

        elif not description.strip():
            st.error("Please enter a description.")

        else:

            new_expense = pd.DataFrame([{
                "Date": pd.Timestamp(expense_date),
                "Amount": amount,
                "Category": category,
                "Description": description.strip()
            }])

            df = pd.concat(
                [df, new_expense],
                ignore_index=True
            )

            save_expenses(df)

            st.success("Expense saved successfully!")

            # Refresh the complete application
            st.rerun()


st.divider()


# ==================================================
# 8. DASHBOARD FILTERS
# ==================================================

st.markdown(
    '<p class="section-title">📊 Expense Dashboard</p>',
    unsafe_allow_html=True
)

if not df.empty:

    df["Month"] = df["Date"].dt.strftime("%Y-%m")

    available_months = sorted(
        df["Month"].unique(),
        reverse=True
    )

    col1, col2 = st.columns(2)

    with col1:
        selected_month = st.selectbox(
            "Select Month",
            available_months
        )

    monthly_df = df[
        df["Month"] == selected_month
    ].copy()

    with col2:
        selected_category = st.selectbox(
            "Filter by Category",
            ["All Categories"] + CATEGORIES
        )

    filtered_df = monthly_df.copy()

    if selected_category != "All Categories":
        filtered_df = filtered_df[
            filtered_df["Category"] == selected_category
        ]

else:
    selected_month = date.today().strftime("%Y-%m")
    monthly_df = df.copy()
    filtered_df = df.copy()


# ==================================================
# 9. SUMMARY CARDS
# ==================================================

st.markdown("### 📌 Financial Overview")

monthly_total = monthly_df["Amount"].sum()
all_time_total = df["Amount"].sum()
remaining_budget = monthly_budget - monthly_total

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Monthly Spending",
    f"₹{monthly_total:,.2f}"
)

col2.metric(
    "All-Time Spending",
    f"₹{all_time_total:,.2f}"
)

col3.metric(
    "Remaining Budget",
    f"₹{remaining_budget:,.2f}"
)

col4.metric(
    "Transactions",
    len(monthly_df)
)


# ==================================================
# 10. BUDGET TRACKER
# ==================================================

st.markdown("### 🎯 Monthly Budget Tracker")

budget_percentage = monthly_total / monthly_budget

st.progress(
    min(budget_percentage, 1.0)
)

st.caption(
    f"Budget used: {budget_percentage * 100:.1f}%"
)

if monthly_total > monthly_budget:

    st.error(
        f"⚠️ Budget exceeded by "
        f"₹{monthly_total - monthly_budget:,.2f}"
    )

elif budget_percentage >= 0.8:

    st.warning(
        "You have used 80% or more of your monthly budget."
    )

else:

    st.success(
        "You are within your monthly budget. Keep it up!"
    )


st.divider()


# ==================================================
# 11. SPENDING CHARTS
# ==================================================

st.markdown("### 📈 Spending Analytics")

if not monthly_df.empty:

    col1, col2 = st.columns(2)

    # Category pie chart
    category_totals = (
        monthly_df.groupby("Category", as_index=False)
        ["Amount"].sum()
    )

    with col1:

        st.markdown("**Category-wise Spending**")

        pie_chart = px.pie(
            category_totals,
            names="Category",
            values="Amount",
            hole=0.45,
            title="Where Does Your Money Go?"
        )

        st.plotly_chart(
            pie_chart,
            use_container_width=True
        )

    # Daily bar chart
    daily_totals = (
        monthly_df.groupby(
            monthly_df["Date"].dt.date
        )["Amount"].sum().reset_index()
    )

    daily_totals.columns = ["Date", "Amount"]

    with col2:

        st.markdown("**Daily Spending**")

        bar_chart = px.bar(
            daily_totals,
            x="Date",
            y="Amount",
            title="Daily Expense Pattern",
            labels={"Amount": "Amount (₹)"},
            text_auto=".2f"
        )

        st.plotly_chart(
            bar_chart,
            use_container_width=True
        )

else:

    st.info("Add expenses to see your spending analytics.")


st.divider()


# ==================================================
# 12. EXPENSE HISTORY
# ==================================================

st.markdown("### 📋 Expense History")

if not filtered_df.empty:

    display_df = filtered_df[COLUMNS].copy()

    display_df["Date"] = display_df["Date"].dt.strftime(
        "%d-%m-%Y"
    )

    display_df = display_df.sort_values(
        "Date",
        ascending=False
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No expenses found for the selected filters.")


st.divider()


# ==================================================
# 13. EDIT EXPENSE
# ==================================================

st.markdown("### ✏️ Edit Expense")

if not df.empty:

    edit_options = df.index.tolist()

    selected_edit = st.selectbox(
        "Select an expense to edit",
        edit_options,
        format_func=lambda i: (
            f"{df.loc[i, 'Date'].strftime('%d-%m-%Y')} | "
            f"{df.loc[i, 'Category']} | "
            f"₹{df.loc[i, 'Amount']:.2f}"
        ),
        key="edit_selection"
    )

    selected_expense = df.loc[selected_edit]

    with st.form("edit_form"):

        edit_date = st.date_input(
            "New Date",
            value=selected_expense["Date"].date(),
            max_value=date.today()
        )

        edit_amount = st.number_input(
            "New Amount (₹)",
            min_value=0.01,
            value=float(selected_expense["Amount"])
        )

        edit_category = st.selectbox(
            "New Category",
            CATEGORIES,
            index=(
                CATEGORIES.index(selected_expense["Category"])
                if selected_expense["Category"] in CATEGORIES
                else 0
            )
        )

        edit_description = st.text_input(
            "New Description",
            value=str(selected_expense["Description"])
        )

        update_button = st.form_submit_button(
            "Update Expense",
            use_container_width=True
        )

        if update_button:

            if not edit_description.strip():

                st.error("Description cannot be empty.")

            else:

                df.loc[
                    selected_edit,
                    ["Date", "Amount", "Category", "Description"]
                ] = [
                    pd.Timestamp(edit_date),
                    edit_amount,
                    edit_category,
                    edit_description.strip()
                ]

                save_expenses(df)

                st.success("Expense updated successfully!")

                st.rerun()

else:

    st.info("No expenses available to edit.")


st.divider()


# ==================================================
# 14. DELETE EXPENSE
# ==================================================

st.markdown("### 🗑️ Delete Expense")

if not df.empty:

    delete_options = df.index.tolist()

    selected_delete = st.selectbox(
        "Select an expense to delete",
        delete_options,
        format_func=lambda i: (
            f"{df.loc[i, 'Date'].strftime('%d-%m-%Y')} | "
            f"{df.loc[i, 'Category']} | "
            f"₹{df.loc[i, 'Amount']:.2f}"
        ),
        key="delete_selection"
    )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this expense."
    )

    if st.button(
        "Delete Selected Expense",
        use_container_width=True
    ):

        if confirm_delete:

            df = df.drop(index=selected_delete).reset_index(drop=True)

            save_expenses(df)

            st.success("Expense deleted successfully!")

            st.rerun()

        else:

            st.warning("Please confirm before deleting.")

else:

    st.info("No expenses available to delete.")


st.divider()


# ==================================================
# 15. DOWNLOAD REPORT
# ==================================================

st.markdown("### 📥 Download Expense Report")

if not filtered_df.empty:

    report = filtered_df[COLUMNS].copy()

    csv_data = report.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Monthly Expense Report",
        data=csv_data,
        file_name=f"expense_report_{selected_month}.csv",
        mime="text/csv",
        use_container_width=True
    )

else:

    st.info("No records available to download.")


# ==================================================
# 16. FOOTER
# ==================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:gray;">
        <p>Student Expense Tracker | Version 2.0</p>
        <p>Built using Python • Streamlit • Pandas • Plotly</p>
    </div>
    """,
    unsafe_allow_html=True
)