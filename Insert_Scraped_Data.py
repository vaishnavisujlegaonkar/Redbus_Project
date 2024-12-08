import sqlite3
import pandas as pd
import re
import os

# List of all state CSV files
csv_files = [
    "Assam_scraped_data.csv",
    "Bihar_scraped_data.csv",
	"Telangana_scraped_data.csv",
    "Himachal_scraped_data.csv",
	"Kerala_scraped_data.csv",
    "Punjab_scraped_data.csv",
    "Rajasthan_scraped_data.csv",
	"JammuKashmir_scraped_data.csv",
	"AndhraPradesh_scraped_data.csv",
	"Chandigrah_scraped_data.csv"
    # Add paths for all 10 CSV files here
]

# function to clean the price
def clean_price(price):
    # Remove "INR" and any non-numeric characters
    match = re.search(r'\d+', str(price))
    return int(match.group()) if match else 0

# function to clean seats available
def clean_seats(seats):
    # Extract numeric part of the string
    match = re.search(r'\d+', str(seats))
    return int(match.group()) if match else 0

# Connect to the SQLite database
connection = sqlite3.connect("redbus_data.db", timeout=10)  # Sets a 10-second timeout
cursor = connection.cursor()

# Insert the data into the database
insert_query = """
INSERT INTO bus_routes (
    route_name, route_link, busname, bustype, departing_time, 
    duration, reaching_time, star_rating, price, seats_available
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

# Process each CSV file
for csv_file in csv_files:
    if not os.path.exists(csv_file):
        print(f"File {csv_file} does not exist. Skipping.")
        continue

    # Read the CSV file into a DataFrame
    try:
        df = pd.read_csv(csv_file)
        print(f"Data successfully read from {csv_file}")
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        continue

    # cleaning functions
    df["Price"] = df["Price"].apply(clean_price)
    df["Seat_availability"] = df["Seat_availability"].apply(clean_seats)

    # Insert data into the database
    for _, row in df.iterrows():
        try:
            cursor.execute(insert_query, (
                row["Bus_Routes_Name"], row["Bus_Routes_links"], row["Bus_name"], row["Bus_type"],
                row["Departing_time"], row["Duration"], row["Reaching_time"],
                None if row["Star_rating"] == "N/A" else float(row["Star_rating"]),
                row["Price"], row["Seat_availability"]
            ))
        except Exception as e:
            print(f"Error inserting row from {csv_file}: {e}")

# Commit changes and close the connection
connection.commit()
print("Data successfully inserted into the database.")
connection.close()
