import streamlit as st
import hashlib
import json
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def check_login(username, password, users):
    return username in users and users[username] == hash_password(password)

def save_new_user(username, password):
    users = load_users()
    users[username] = hash_password(password)
    save_users(users)
    st.success("User registered successfully! Please log in.")

def main():
    st.title("Login Page")
    
    users = load_users()
    
    menu = ["Login", "Sign Up"]
    choice = st.selectbox("Select an option", menu)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if choice == "Login":
        if st.button("Login"):
            if check_login(username, password, users):
                st.success(f"Welcome {username}!")
            else:
                st.error("Invalid username or password.")
    
    elif choice == "Sign Up":
        if username in users:
            st.error("User already exists. Please log in.")
        elif st.button("Sign Up"):
            save_new_user(username, password)

if __name__ == "__main__":
    main()
