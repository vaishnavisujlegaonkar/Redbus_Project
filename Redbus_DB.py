import sqlite3

# Create or connect to the SQLite database
connection = sqlite3.connect("redbus_data.db")  # This file will be created in your project directory

# Create a cursor to execute SQL queries
cursor = connection.cursor()

# Create the buses table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS bus_routes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_name TEXT NOT NULL,
        route_link TEXT NOT NULL,
        busname TEXT,
        bustype TEXT,
        departing_time TIME,
        duration TEXT,
        reaching_time TIME,
        star_rating FLOAT,
        price DECIMAL,
        seats_available INT
);
"""
cursor.execute(create_table_query)

# Commit changes and close the connection
connection.commit()
print("Database and table created successfully...")
connection.close()

