import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu



# Function to fetch data from the database
def fetch_data(query):
    conn = sqlite3.connect("redbus_data.db")
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data

# Fetch distinct route and bustype values
routes_df = fetch_data("SELECT DISTINCT route_name FROM bus_routes")
bustype_df = fetch_data("SELECT DISTINCT bustype FROM bus_routes")

# Handle missing values in `bustype` column
bustype_df['bustype'] = bustype_df['bustype'].fillna("Unknown")

# Extract Seat types from the `bustype` column
bustype_df['seat_type'] = bustype_df['bustype'].apply(
    lambda x: 'Sleeper' if 'Sleeper' in x else ('Seater / Sleeper' if 'Seater / Sleeper' in x else 'Seater')
)

# Streamlit Sidebar
with st.sidebar:
    # Add a colored top margin with the "RedBus" title
    st.markdown(
        """
        <style>
            .top-margin {
                background-color: #FF4B4B; /* Red color for the margin */
                padding: 3px; /* Add padding for some spacing */
                text-align: center; /* Center-align the title */
                color: white; /* White text for contrast */
                font-size: 30px; /* Font size for the title */
                font-weight: bold; /* Bold text */
                margin-bottom: 10px; /* Add spacing below the margin */
            }
        </style>
        <div class="top-margin">
            RedBus
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sidebar Navigation using option_menu
    menu = option_menu(
        "Main Menu",
        ["Home", "Select the Bus"],
        icons=['house', 'map'],
        menu_icon="cast",
        default_index=0,
        styles={
            "icon": {"font-size": "18px"},
            "nav-link-selected": {"background-color": "#FF4B4B", "font-size": "15px"}
        }
    )

# Update session state based on selected menu
if "page" not in st.session_state:
    st.session_state.page = "home"  # Default page

if menu == "Home":
    st.session_state.page = "home"
elif menu == "Select the Bus":
    st.session_state.page = "select_bus"

# Main Section based on selected page
if st.session_state.page == "home":
    st.title("Welcome to RedBus!")
    st.write("This is the home page. Please select an option from the sidebar.")

elif st.session_state.page == "select_bus":
    # Layout for dropdowns and filters
    with st.container():
        # First row: Two dropdowns (Route and Seat Type)
        col1, col2 = st.columns(2)
        with col1:
            route_options = ["Select"] + routes_df['route_name'].tolist()
            route = st.selectbox("Select the Route", route_options)
        with col2:
            seat_type_options = ["Select"] + sorted(bustype_df['seat_type'].unique())
            seat_type = st.selectbox("Select Seat Type", seat_type_options)

    with st.container():
        # Second row: Three dropdowns (Star Rating, Start Time, Fare Range)
        col1, col2, col3 = st.columns(3)
        with col1:
            star_rating_options = [
                "Any",
                "1 to 2",
                "2 to 3",
                "3 to 4",
                "4 to 5"
            ]
            star_rating_range = st.selectbox("Select Ratings", star_rating_options)
        with col2:
            time_intervals = [f"{hour:02d}:00-{hour + 1:02d}:00" for hour in range(24)]
            time_intervals = ["Select"] + time_intervals
            time_range = st.selectbox("Starting Time", time_intervals)
        with col3:
            fare_ranges = ["Select", "100-500", "500-1000", "1000-2000", "2000+"]
            fare_range = st.selectbox("Bus Fare Range", fare_ranges)

    with st.container():
        # Third row: Search button
        if st.button("Search Buses"):
            # Validate selections
            if (
                    route == "Select" or
                    seat_type == "Select" or
                    star_rating_range == "Select" or
                    time_range == "Select" or
                    fare_range == "Select"
            ):
                st.warning("Please select a route, seat type, star rating range, time range, and fare range.")
            else:
                # Parse the selected star rating range
                if star_rating_range != "Any":
                    min_rating, max_rating = map(int, star_rating_range.split(" to "))
                else:
                    min_rating, max_rating = None, None  # No filtering for "Any"

                # Parse the selected time range
                start_time, end_time = time_range.split("-")
                start_time = datetime.strptime(start_time, "%H:%M").time()
                end_time = datetime.strptime(end_time, "%H:%M").time()

                # Parse the selected fare range
                if fare_range == "2000+":
                    min_fare, max_fare = 2000, float('inf')  # No upper limit
                else:
                    min_fare, max_fare = map(int, fare_range.split("-"))

                # Fetch bus data based on selected route
                filtered_data = fetch_data(f"SELECT * FROM bus_routes WHERE route_name = '{route}'")

                # Further filter by seat_type
                filtered_data = filtered_data[filtered_data['bustype'].str.contains(seat_type, case=False)]

                # Further filter by star rating range (including N/A ratings)
                if min_rating is not None and max_rating is not None:
                    filtered_data = filtered_data[
                        (filtered_data['star_rating'].fillna(0) >= min_rating) &  # Treat N/A as 0
                        (filtered_data['star_rating'].fillna(0) <= max_rating)
                    ]

                # Further filter by start time range
                filtered_data = filtered_data[
                    (filtered_data['departing_time'] >= start_time.strftime("%H:%M")) &
                    (filtered_data['departing_time'] <= end_time.strftime("%H:%M"))
                ]

                # Further filter by fare range
                filtered_data = filtered_data[
                    (filtered_data['price'] >= min_fare) & (filtered_data['price'] <= max_fare)
                ]

                # Display results
                if not filtered_data.empty:
                    # Add a serial number column to the filtered data
                    filtered_data.reset_index(drop=True, inplace=True)
                    filtered_data.insert(0, 'Serial No', filtered_data.index + 1)

                    st.subheader(f"Available Buses for Route: {route}")
                    st.dataframe(filtered_data[['route_name', 'route_link', 'bustype', 'departing_time',
                                                'duration', 'reaching_time', 'star_rating', 'price',
                                                'seats_available']])
                else:
                    st.warning(f"No buses found matching the selected criteria for Route: {route}.")
