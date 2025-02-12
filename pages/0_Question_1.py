import streamlit as st
import sqlite3
import pandas as pd

import requests

st.set_page_config(page_title="Intern/FTE Recruitment Simulation")
st.title("Question 1")

PANTRY_ID = "8732fb03-8ddd-4949-a7e3-9f9f6528170e"
PANTRY_URL = f"https://getpantry.cloud/apiv1/pantry/{PANTRY_ID}/basket/scores"

submit_btn = False

st.sidebar.subheader("Candidate Details")
roll_number = st.sidebar.text_input("Enter your Roll Number")
if roll_number:
    submit_btn = st.sidebar.button("Submit")

if submit_btn:
    st.write("Works")

conn = sqlite3.connect('intern.db')
cur = conn.cursor()

# Create Tables
cur.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        salary INTEGER,
        department INTEGER
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

employees = [
    (1, 'Joe', 85000, 1),
    (2, 'Henry', 80000, 2),
    (3, 'Sam', 60000, 2),
    (4, 'Max', 90000, 1),
    (5, 'Janet', 69000, 1),
    (6, 'Randy', 85000, 1),
    (7, 'Will', 70000, 1)
]
cur.executemany("INSERT OR IGNORE INTO employees VALUES (?, ?, ?, ?)", employees)

departments = [
    (1, 'IT'),
    (2, 'Sales')
]
cur.executemany("INSERT OR IGNORE INTO departments VALUES (?, ?)", departments)

conn.commit()

# Load data into Pandas DataFrames
employees_df = pd.read_sql_query("SELECT * FROM employees", conn)
departments_df = pd.read_sql_query("SELECT * FROM departments", conn)

# Merge both DataFrames to get department names
merged_df = employees_df.merge(departments_df, left_on="department", right_on="id")

# Select only relevant columns and rename
sorted_df = merged_df[["name_y", "name_x", "salary"]]
sorted_df.columns = ["Department", "Employee", "Salary"]

# Sort by Department (IT first, Sales second) and then by Salary (descending)
sorted_df = sorted_df.sort_values(by=["Department", "Salary"], ascending=[True, False]).reset_index(drop=True)

col1,col2=st.columns(2)

with col1:
    st.subheader("Employees Table, named 'employees'")
    st.write(employees_df)

with col2:
    st.subheader("Departments Table, named 'departments'")
    st.write(departments_df)

st.markdown("""
# Employee and Department Salary Listing

## Problem Statement

You are given two database tables:

### 1. Employees Table (`employees`)
Contains information about employees, including:
- `id`: Employee ID
- `name`: Employee Name
- `salary`: Employee Salary
- `department`: Department ID (Foreign Key)

### 2. Departments Table (`departments`)
Contains department details, including:
- `id`: Department ID (Primary Key)
- `name`: Department Name

### Task
Write an SQL query to generate a report displaying:
- The department name (`Department`)
- The employee's name (`Employee`)
- The employee's salary (`Salary`)

### Sorting Requirements
- First, sort by **department name in ascending order**.
- Then, within each department, sort employees by **salary in descending order**.

### Expected Output
A table where employees are grouped by their respective departments, with salaries listed in descending order.

""")

st.subheader("Expected Table:")
st.write(sorted_df)

# SQL Query input
code = st.text_area("Write SQL query here")

if st.button("Run SQL"):
    try:
        user_df = pd.read_sql_query(code, conn)
        
        if user_df.equals(sorted_df):
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
            existing_data[roll_number]["question1"] = 20  # Change "question1" accordingly based on the page

            # Send the updated data back to PantryDB
            response = requests.put(PANTRY_URL, json=existing_data)

            if response.status_code == 200:
                st.success("✅ Score updated in PantryDB!")
            else:
                st.error("❌ Failed to update score. Please try again.")

        else:
            st.warning("⚠ SOLUTION FAILED! Try Again.")
            st.write("Expected Output:")
            st.dataframe(sorted_df)
            st.write("Your Output:")
            st.dataframe(user_df)
    except Exception as e:
        st.error(f"❌ SYNTAX ERROR: {e}")

conn.close()
