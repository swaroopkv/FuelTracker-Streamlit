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
st.sidebar.header("Navigation")
menu = st.sidebar.radio("Menu", ["Dashboard", "Add Fuel Log", "Manage Vehicles"])

# Load existing data
df = load_data()

if menu == "Dashboard":
    st.subheader("Dashboard: Fuel and Mileage Analysis")

    if df.empty:
        st.info("No data available. Add some fuel logs!")
    else:
        st.dataframe(df)

        # Summary Metrics
        total_cost = df["Fuel_Cost"].sum()
        total_fuel = df["Fuel_Quantity"].sum()
        avg_mileage = df["Mileage"].mean()
        st.metric("Total Fuel Cost", f"${total_cost:.2f}")
        st.metric("Total Fuel Used", f"{total_fuel:.2f} liters")
        st.metric("Average Mileage", f"{avg_mileage:.2f} km/l")

        # Visualization
        st.subheader("Mileage Over Time")
        fig, ax = plt.subplots()
        sns.lineplot(data=df, x="Date", y="Mileage", hue="Vehicle", marker="o", ax=ax)
        ax.set_title("Mileage Trends")
        st.pyplot(fig)

elif menu == "Add Fuel Log":
    st.subheader("Add Fuel Log")

    # Form for input
    with st.form("fuel_log_form"):
        vehicle = st.text_input("Vehicle Name")
        date_logged = st.date_input("Date", date.today())
        odometer = st.number_input("Odometer Reading (km)", min_value=0.0)
        fuel_quantity = st.number_input("Fuel Quantity (liters)", min_value=0.0)
        fuel_cost = st.number_input("Fuel Cost (Rs.)", min_value=0.0)
        submit = st.form_submit_button("Add Log")

        if submit:
            mileage = odometer / fuel_quantity if fuel_quantity > 0 else 0
            new_entry = pd.DataFrame([{
            "Vehicle": vehicle,
            "Date": date_logged,
            "Odometer": odometer,
            "Fuel_Quantity": fuel_quantity,
            "Fuel_Cost": fuel_cost,
            "Mileage": mileage
            }])
    
            # Concatenate the new entry with the existing data
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)
            st.success("Fuel log added successfully!")


elif menu == "Manage Vehicles":
    st.subheader("Manage Vehicles")
    st.write("Feature coming soon!")

