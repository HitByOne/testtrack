import streamlit as st
import pandas as pd
from datetime import datetime
import re
from pymongo import MongoClient
import os

# Securely fetch the connection string
mongo_conn_str = os.getenv("MONGO_CONN_STR")
client = MongoClient(mongo_conn_str)
db = client['item_changes']
changes_collection = db.changes

def log_changes_to_db(item_numbers, changes, name, notes):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entries = []
    for item in item_numbers:
        document = {
            "item_number": item,
            "date": date,
            "entered_by": name,
            **{change: 'Yes' for change in changes},
            "notes": notes
        }
        entries.append(document)
    changes_collection.insert_many(entries)

def fetch_changes(limit=100):
    # Fetch the latest 100 changes by default
    return pd.DataFrame(list(changes_collection.find({}, {'_id': 0}).sort("date", -1).limit(limit)))

st.title("Item Change Tracker")
item_numbers_input = st.text_area("Enter Item Numbers (space, comma, or newline separated)", height=150)
names = ["John Doe", "Jane Smith", "Mark Johnson", "Emily Davis"]
name = st.selectbox("Select Your Name", names)
change_options = ["Price Change", "Description Update", "Discontinued", "Quantity Adjustment", "Category Change"]
changes = st.multiselect("Select Changes", change_options)
notes = st.text_area("Enter Additional Notes", height=150)

if st.button("Log Changes"):
    item_numbers = re.split(r'[,\s\n]+', item_numbers_input.strip())
    item_numbers = [i for i in item_numbers if i]
    if item_numbers and changes:
        try:
            log_changes_to_db(item_numbers, changes, name, notes)
            st.success("Changes have been logged successfully.")
            df = fetch_changes()
            st.subheader("Recent Change Log")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error logging changes: {e}")
    else:
        st.error("Please check your input. Ensure item numbers and changes are correctly specified.")
