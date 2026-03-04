import streamlit as st
try:
    print("Testing st.Page...")
    home_page = st.Page("views/home.py", title="Home", icon="🏠", default=True, url_path="")
    print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
