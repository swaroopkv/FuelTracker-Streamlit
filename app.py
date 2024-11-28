import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
import os

# Set page configuration
st.set_page_config(page_title="Fuel Tracker", layout="wide")

# Initialize data file
DATA_FILE = "data/fuel_data.csv"

# Create the data file if it doesn’t exist
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Vehicle", "Date", "Odometer", "Fuel_Quantity", "Fuel_Cost", "Mileage"])
    df.to_csv(DATA_FILE, index=False)

# Load data
def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(data):
    data.to_csv(DATA_FILE, index=False)

# Title and Description
st.title("🚗 Fuel & Mileage Tracker")
st.sidebar.header("Menu")
menu = st.sidebar.radio("", ["Dashboard", "Add Fuel Log", "Manage Vehicles"])

# Load existing data
df = load_data()

if menu == "Dashboard":
    st.subheader("Dashboard: Fuel and Mileage Analysis")

    if df.empty:
        st.info("No data available. Add some fuel logs!")
    else:
        # Show Data Summary
        st.write("### Fuel Logs Data")
        st.dataframe(df)

        # Group data by Month and Vehicle for analysis
        df["Date"] = pd.to_datetime(df["Date"])  # Ensure Date is in datetime format
        monthly_expense = df.groupby([df["Date"].dt.to_period("M"), "Vehicle"]).agg(
            Monthly_Cost=("Fuel_Cost", "sum")
        ).reset_index()
        monthly_expense["Date"] = monthly_expense["Date"].dt.to_timestamp()

        # Monthly Expense Bar Chart
        st.write("### Monthly Expense by Vehicle")
        fig_monthly, ax_monthly = plt.subplots(figsize=(10, 5))
        sns.barplot(
            data=monthly_expense,
            x="Date",
            y="Monthly_Cost",
            hue="Vehicle",
            ax=ax_monthly,
        )
        ax_monthly.set_title("Monthly Fuel Expense")
        ax_monthly.set_ylabel("Expense (Rs)")
        ax_monthly.set_xlabel("Month")
        plt.xticks(rotation=45)
        st.pyplot(fig_monthly)

        # Summary Metrics
        st.write("### Summary Metrics")
        total_cost = df["Fuel_Cost"].sum()
        total_fuel = df["Fuel_Quantity"].sum()
        avg_mileage = df["Mileage"].mean()
        st.metric("Total Fuel Cost", f"Rs{total_cost:.2f}")
        st.metric("Total Fuel Used", f"{total_fuel:.2f} liters")
        st.metric("Average Mileage", f"{avg_mileage:.2f} km/l")



        


elif menu == "Add Fuel Log":
    st.subheader("Add Fuel Log")

    # Extract list of unique vehicles
    vehicles = df["Vehicle"].unique().tolist()
    vehicles = sorted(vehicles)  # Sort the list for easy selection

    # Form for input
    with st.form("fuel_log_form"):
        # Dropdown to select vehicle or add a new one
        vehicle_option = st.radio("Choose an option:", ["Select an existing vehicle", "Add a new vehicle"])
        
        if vehicle_option == "Select an existing vehicle":
            if vehicles:
                vehicle = st.selectbox("Select Vehicle", vehicles)
            else:
                st.info("No vehicles available. Add a new vehicle below.")
                vehicle = st.text_input("New Vehicle Name")
        else:
            vehicle = st.text_input("New Vehicle Name")
        
        # Other inputs
        date_logged = st.date_input("Date", date.today())
        odometer = st.number_input("Odometer Reading (km)", min_value=0.0)
        fuel_quantity = st.number_input("Fuel Quantity (liters)", min_value=0.0)
        fuel_cost = st.number_input("Fuel Cost (Re.)", min_value=0.0)
        
        submit = st.form_submit_button("Add Log")

        if submit:
            if not vehicle.strip():
                st.error("Vehicle name cannot be empty!")
            else:
                # Retrieve previous odometer reading for the selected vehicle
                if vehicle in df["Vehicle"].values:
                    vehicle_logs = df[df["Vehicle"] == vehicle]
                    previous_odometer = vehicle_logs["Odometer"].max()
                else:
                    # If this is the first log for the vehicle
                    previous_odometer = None

                # Calculate mileage
                if previous_odometer is None:
                    # First log: no mileage calculation
                    mileage = None
                    st.warning("Mileage cannot be calculated for the first log. Please ensure consistent logging.")
                else:
                    # Calculate mileage based on the difference in odometer readings
                    mileage = (odometer - previous_odometer) / fuel_quantity if fuel_quantity > 0 else 0

                # Add new log entry
                new_entry = pd.DataFrame([{
                    "Vehicle": vehicle,
                    "Date": date_logged,
                    "Odometer": odometer,
                    "Fuel_Quantity": fuel_quantity,
                    "Fuel_Cost": fuel_cost,
                    "Mileage": mileage
                }])

                # Append the new log to the DataFrame
                df = pd.concat([df, new_entry], ignore_index=True)
                save_data(df)
                st.success(f"Fuel log added successfully for {vehicle}!")




elif menu == "Manage Vehicles":
    st.subheader("Manage Vehicles")

    # Extract list of unique vehicles
    vehicles = df["Vehicle"].unique().tolist()
    vehicles = sorted(vehicles)

    if not vehicles:
        st.info("No vehicles available to manage. Add fuel logs to create vehicles.")
    else:
        # Dropdown to select a vehicle to delete
        vehicle_to_delete = st.selectbox("Select Vehicle to Delete", vehicles)
        if st.button("Delete Vehicle"):
            # Filter out all rows with the selected vehicle
            df = df[df["Vehicle"] != vehicle_to_delete]
            save_data(df)
            st.success(f"Vehicle '{vehicle_to_delete}' and all its logs have been deleted!")
            # Refresh the page after deletion
            st.rerun()

    # Display all vehicles with stats
    st.write("### Current Vehicles")
    if not df.empty:
        vehicles_summary = df.groupby("Vehicle").agg(
            Total_Cost=("Fuel_Cost", "sum"),
            Total_Fuel=("Fuel_Quantity", "sum"),
            Avg_Mileage=("Mileage", "mean")
        ).reset_index()
        st.dataframe(vehicles_summary,hide_index=True,)


