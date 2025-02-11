import streamlit as st
import sqlite3
import pandas as pd
import requests

st.set_page_config(page_title="Intern/FTE Recruitment Simulation")
st.title("Question 2")

PANTRY_ID = "8732fb03-8ddd-4949-a7e3-9f9f6528170e"
PANTRY_URL = f"https://getpantry.cloud/apiv1/pantry/{PANTRY_ID}/basket/scores"

submit_btn = False

st.sidebar.subheader("Candidate Details")
roll_number = st.sidebar.text_input("Enter your Roll Number")
if roll_number:
    submit_btn = st.sidebar.button("Submit")

conn = sqlite3.connect('intern.db')
cur = conn.cursor()

# Create Tables
def create_tables():
    cur.execute('''
        CREATE TABLE IF NOT EXISTS customer_contracts (
            customer_id INTEGER,
            product_id INTEGER,
            amount INTEGER
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER,
            product_category TEXT,
            product_name TEXT
        )
    ''')
    
    customer_data = [
        (1, 1, 1000),
        (1, 3, 2000),
        (1, 5, 1500),
        (2, 2, 3000),
        (2, 6, 2000)
    ]
    cur.executemany("INSERT OR IGNORE INTO customer_contracts VALUES (?, ?, ?)", customer_data)

    product_data = [
        (1, 'Analytics', 'Azure Databricks'),
        (2, 'Analytics', 'Azure Stream Analytics'),
        (3, 'Containers', 'Azure Kubernetes Service'),
        (4, 'Containers', 'Azure Service Fabric'),
        (5, 'Compute', 'Virtual Machines'),
        (6, 'Compute', 'Azure Functions')
    ]
    cur.executemany("INSERT OR IGNORE INTO products VALUES (?, ?, ?)", product_data)
    conn.commit()

create_tables()

# Load data into Pandas DataFrames
customer_df = pd.read_sql_query("SELECT * FROM customer_contracts", conn)
product_df = pd.read_sql_query("SELECT * FROM products", conn)

# Expected SQL Query
expected_query = '''
    SELECT customer_id
    FROM customer_contracts cc
    JOIN products p ON cc.product_id = p.product_id
    GROUP BY customer_id
    HAVING COUNT(DISTINCT p.product_category) = (SELECT COUNT(DISTINCT product_category) FROM products)
'''
expected_df = pd.read_sql_query(expected_query, conn)
st.subheader("Customer Contracts Table, named 'customer_contracts'")
st.write(customer_df)

st.subheader("Products Table, named 'products'")
st.write(product_df)

st.subheader("Expected Output Table")
st.write(expected_df)

# SQL Query input
code = st.text_area("Write SQL query here")

if st.button("Run SQL"):
    try:
        user_df = pd.read_sql_query(code, conn)
        if user_df.equals(expected_df):
            st.success("✅ SOLUTION ACCEPTED! 🎉")

            # Fetch existing data from PantryDB
            response = requests.get(PANTRY_URL)
            if response.status_code == 200:
                existing_data = response.json()
            else:
                existing_data = {}

            # Ensure the roll number exists in the database
            if roll_number not in existing_data:
                existing_data[roll_number] = {"question1": 0, "question2": 0}

            # Update the score for the respective question
            existing_data[roll_number]["question2"] = 20  # Change "question1" accordingly based on the page

            # Send the updated data back to PantryDB
            response = requests.put(PANTRY_URL, json=existing_data)

            if response.status_code == 200:
                st.success("✅ Score updated in PantryDB!")
            else:
                st.error("❌ Failed to update score. Please try again.")
        else:
            st.warning("⚠ SOLUTION FAILED! Try Again.")
            st.write("Expected Output:")
            st.dataframe(expected_df)
            st.write("Your Output:")
            st.dataframe(user_df)
    except Exception as e:
        st.error(f"❌ SYNTAX ERROR: {e}")

conn.close()
