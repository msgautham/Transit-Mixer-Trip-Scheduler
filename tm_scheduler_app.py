import streamlit as st
import pandas as pd
import io

def calculate_trip_times(start_time, batch_qty, pour_time, travel_time, pump_interval, buffer_time, qty_per_trip, num_vehicles):
    trips = []
    cumulative_qty = 0
    next_available_time = [start_time] * num_vehicles  # Track availability of each vehicle

    for i in range(batch_qty // qty_per_trip):
        trip_no = i + 1
        vehicle_no = (i % num_vehicles) + 1

        if vehicle_no == 1:
            work_start_time = next_available_time[vehicle_no - 1]
        else:
            previous_trip = trips[-1]
            work_start_time = max(next_available_time[vehicle_no - 1], previous_trip['Plant Reach Time'])

        plant_start_time = work_start_time + pour_time
        site_reach_time = plant_start_time + travel_time
        pump_start_time = site_reach_time + buffer_time
        site_left_time = pump_start_time + pump_interval
        plant_reach_time = site_left_time + travel_time

        next_available_time[vehicle_no - 1] = plant_reach_time

        cumulative_qty += qty_per_trip

        trip = {
            'Trip No.': trip_no,
            'Vehicle No.': vehicle_no,
            'Work Start Time': work_start_time,
            'Plant Start Time': plant_start_time,
            'Site Reach Time': site_reach_time,
            'Pump Start Time': pump_start_time,
            'Site Left Time After Pumping': site_left_time,
            'Buffer Time': buffer_time,
            'Plant Reach Time': plant_reach_time,
            'Round Trip Time': plant_reach_time - work_start_time,
            'Batch Qty per Trip': qty_per_trip,
            'Cumulative Qty': cumulative_qty
        }

        trips.append(trip)

    return trips

def format_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

st.title("Transit Mixer Trip Scheduler")

# Input fields
start_time = st.number_input("Start Time (in minutes, e.g., 300 for 5:00 AM):", min_value=0, step=1)
batch_qty = st.number_input("Total Required Batch Quantity:", min_value=0, step=1)
pour_time = st.number_input("Pour Time (minutes):", min_value=0, step=1)
travel_time = st.number_input("Travel Time (minutes):", min_value=0, step=1)
pump_interval = st.number_input("Pumping Interval (minutes):", min_value=0, step=1)
buffer_time = st.number_input("Buffer Time (minutes):", min_value=0, step=1)
qty_per_trip = st.number_input("Batch Quantity per Trip:", min_value=1, step=1)
num_vehicles = st.number_input("Number of Vehicles (TM's):", min_value=1, step=1)

# Calculate button
if st.button("Generate Schedule"):
    if batch_qty > 0 and qty_per_trip > 0:
        trips = calculate_trip_times(start_time, batch_qty, pour_time, travel_time, pump_interval, buffer_time, qty_per_trip, num_vehicles)

        # Format and display data
        for trip in trips:
            trip['Work Start Time'] = format_time(trip['Work Start Time'])
            trip['Plant Start Time'] = format_time(trip['Plant Start Time'])
            trip['Site Reach Time'] = format_time(trip['Site Reach Time'])
            trip['Pump Start Time'] = format_time(trip['Pump Start Time'])
            trip['Site Left Time After Pumping'] = format_time(trip['Site Left Time After Pumping'])
            trip['Plant Reach Time'] = format_time(trip['Plant Reach Time'])

        df = pd.DataFrame(trips)
        st.write("### Trip Schedule")
        st.dataframe(df)

        # Export to Excel
        excel_file = io.BytesIO()  # Use in-memory buffer
        df.to_excel(excel_file, index=False, engine='openpyxl')
        excel_file.seek(0)  # Reset the buffer pointer
        st.success("Trip schedule exported successfully!")
        st.download_button("Download Excel File", data=excel_file, file_name="transit_mixer_trip_schedule.xlsx", mime="application/vnd.ms-excel")

    else:
        st.error("Please ensure all inputs are valid!")