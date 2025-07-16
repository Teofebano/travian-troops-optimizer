import streamlit as st
import json

def auth(username, password, user_file="users.json"):
    try:
        with open(user_file, "r") as f:
            users = json.load(f)
        return users.get(username) == password
    except FileNotFoundError:
        st.error("User database not found.")
        return False

def login():
    st.title("Travian Optimizer Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if auth(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Welcome, {username}!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

def login_required():
    if not st.session_state.get("logged_in"):
        login()
        st.stop()
