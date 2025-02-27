import streamlit as st
import hashlib
import toml

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username, password, secrets):
    if username in secrets and secrets[username] == hash_password(password):
        return True
    return False

def save_new_user(username, password):
    new_secrets = st.secrets._secrets.copy()
    new_secrets[username] = hash_password(password)
    with open(".streamlit/secrets.toml", "w") as f:
        toml.dump(new_secrets, f)
    st.success("User registered successfully! Please log in.")

def main():
    st.title("Login Page")
    
    if "users" not in st.session_state:
        st.session_state.users = {user: st.secrets[user] for user in st.secrets}
    
    menu = ["Login", "Sign Up"]
    choice = st.selectbox("Select an option", menu)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if choice == "Login":
        if st.button("Login"):
            if check_login(username, password, st.session_state.users):
                st.success(f"Welcome {username}!")
            else:
                st.error("Invalid username or password.")
    
    elif choice == "Sign Up":
        if username in st.session_state.users:
            st.error("User already exists. Please log in.")
        elif st.button("Sign Up"):
            save_new_user(username, password)
            st.session_state.users[username] = hash_password(password)

if __name__ == "__main__":
    main()
