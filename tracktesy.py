import streamlit as st
import pandas as pd
from datetime import datetime
import re
from pymongo import MongoClient

# MongoDB Atlas connection string
client = MongoClient("mongodb+srv://test:test@cluster0.qdyup.mongodb.net/")
db = client['item_changes']  # 'item_changes' is the database name
changes_collection = db.changes  # 'changes' is the collection name

def log_changes_to_db(item_numbers, changes, name, change_options, notes):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in item_numbers:
        document = {
            "item_number": item,
            "date": date,
            "entered_by": name,
            "price_change": 'Yes' if "Price Change" in changes else 'No',
            "description_update": 'Yes' if "Description Update" in changes else 'No',
            "discontinued": 'Yes' if "Discontinued" in changes else 'No',
            "quantity_adjustment": 'Yes' if "Quantity Adjustment" in changes else 'No',
            "category_change": 'Yes' if "Category Change" in changes else 'No',
            "notes": notes
        }
        changes_collection.insert_one(document)

def fetch_changes():
    return pd.DataFrame(list(changes_collection.find({}, {'_id': 0})))  # Excludes the MongoDB '_id' from the DataFrame

# Streamlit app layout
st.title("Item Change Tracker")
cols1 = st.columns((1,1))
item_numbers_input = cols1[0].text_area("Enter Item Numbers (space, comma, or newline separated)", height=300)
names = ["John Doe", "Jane Smith", "Mark Johnson", "Emily Davis"]
name = cols1[1].selectbox("Select Your Name", names)

cols2 = st.columns((1,1))
change_options = ["Price Change", "Description Update", "Discontinued", "Quantity Adjustment", "Category Change"]
changes = cols2[0].multiselect("Select Changes", change_options)
notes = cols2[1].text_area("Enter Additional Notes", height=300)

if st.button("Log Changes"):
    if item_numbers_input and changes and name:
        item_numbers = re.split(r'[,\s\n]+', item_numbers_input.strip())
        item_numbers = [i for i in item_numbers if i]
        if not item_numbers:
            st.error("No valid item numbers provided.")
        else:
            try:
                log_changes_to_db(item_numbers, changes, name, change_options, notes)
                st.success("Changes have been logged successfully.")
                df = fetch_changes()
                st.subheader("Updated Change Log")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.error("Please enter item numbers, select changes, and select your name.")
