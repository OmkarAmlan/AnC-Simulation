import streamlit as st
import requests
 
st.set_page_config(page_title="About Intern Recruitment Simulation")
st.title("About This Application")

PANTRY_ID = "8732fb03-8ddd-4949-a7e3-9f9f6528170e"
PANTRY_URL = f"https://getpantry.cloud/apiv1/pantry/{PANTRY_ID}/basket/scores"

st.markdown(
    """
    ## About This Application
    
    Welcome to the **Intern/FTE Recruitment Simulation**! This app is designed to evaluate candidates' SQL skills in a structured, interactive environment.
    
    Follow all instructions else your solutions wont be marked.
    STEPS:
    
    1. Fill your roll number in this Home Page and click Submit.
    2. Navigate to questions via the left side of the screen.
    3. On each question, fill your roll number, click submit and then write your sql query.
    4. Wait for confirmation about your score updation.
    
    ### Contact
    If you have any feedback or queries, feel free to reach out to us.
    
    Happy coding! 🚀
    """
)

st.sidebar.subheader("Candidate Details")
roll_number = st.sidebar.text_input("Enter your Roll Number")
submit_btn = st.sidebar.button("Submit")

if submit_btn and roll_number:
    # Fetch existing data from PantryDB
    response = requests.get(PANTRY_URL)
    if response.status_code == 200:
        existing_data = response.json()
    else:
        existing_data = {}
    
    # Update or initialize the roll number entry
    if roll_number not in existing_data:
        existing_data[roll_number] = {"question1": 0, "question2": 0}
    
    # Send updated data back to PantryDB
    response = requests.put(PANTRY_URL, json=existing_data)
    
    if response.status_code == 200:
        st.success("✅ Successfully logged roll number in PantryDB!")
    else:
        st.error("❌ Failed to log roll number. Please try again.")
