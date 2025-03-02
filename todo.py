import streamlit as st
import sqlite3

# Database connection with WAL mode and timeout
def get_connection():
    conn = sqlite3.connect("tasks.db", timeout=10, check_same_thread=False, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL;")  # Enable WAL mode
    return conn

# Initialize database tables
def initialize_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                assigned_to TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        conn.commit()

# Default list of names
NAMES = [   
    "Media Team", "Event Team", "Content Team", "PR Team", "Design Team", "Business Communication",
    "Creative Team", "IOT Team", "App Dev Team", "Algorithm Team", "AI Team", "Backend Team",
    "Kumaran", "Maria", "Kabilesh", "Krithika", "Pragatheesh", "Pugazhendhi", "Janani",
    "Roshini", "Sujitha", "Shivani", "Nandhini", "Prinkayatthra", "Padmapriya",
    "Hareesh", "Madhan", "Kaarunya", "Aadithya", "Lakshmi Bhargavi", "Jayakanth", "Ganesh Kumar",
    "Swetha", "Vishnupriya", "Dhivya Shree", "Joderick Sherwin", "Yudeeswaran", "Alfred Sam",
    "Avinash", "Shangamitra", "Bharathraj", "Fareed Ahamed", "Jagadeshwaran",
    "Daksh", "Shanmuga Priya", "Jeffrin", "Prasanth", "Saiviswaram", "Surweesh",
    "Shanthosh", "Sivaraman", "Rakhul", "Keerthana"
]

# Insert names into DB (avoid duplicates)
def insert_names():
    with get_connection() as conn:
        cursor = conn.cursor()
        for name in NAMES:
            cursor.execute("INSERT OR IGNORE INTO names (name) VALUES (?)", (name,))
        conn.commit()

# Get stored names from DB
def get_names():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM names ORDER BY name")
        return [row[0] for row in cursor.fetchall()]

# Add a new task (Concurrent Write Handling)
def add_task(task, assigned_to):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task, assigned_to, completed) VALUES (?, ?, ?)", (task, assigned_to, 0))
        conn.commit()

# Fetch tasks
def get_tasks():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, assigned_to, completed FROM tasks")
        return cursor.fetchall()

# Update task status
def update_task(task_id, completed):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id))
        conn.commit()

# Delete task
def delete_task(task_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

# Initialize Database
initialize_db()
insert_names()

# Streamlit UI
st.set_page_config(page_title="✅ Persistent To-Do List", page_icon="📌", layout="centered")
st.title("📌 Persistent To-Do List with SQLite")

# Fetch names from DB
stored_names = get_names()

# Add new task with assigned name
new_task = st.text_input("Add a new task:")
assigned_to = st.selectbox("Assign to:", stored_names)

if st.button("➕ Add Task"):
    if new_task.strip():
        add_task(new_task.strip(), assigned_to)
        st.rerun()

# Display tasks
st.markdown("### 📋 Your Tasks:")
tasks = get_tasks()

if not tasks:
    st.info("No tasks added yet!")

for task_id, task, assigned_to, completed in tasks:
    col1, col2, col3, col4 = st.columns([0.1, 0.6, 0.2, 0.1])

    with col1:
        checked = st.checkbox("", value=bool(completed), key=f"chk_{task_id}")
        if checked != bool(completed):  
            update_task(task_id, checked)
            st.rerun()

    with col2:
        task_text = f"~~{task}~~ (Assigned to: **{assigned_to}**)" if completed else f"{task} (Assigned to: **{assigned_to}**)"
        st.markdown(f"<p style='margin-top:8px;'>{task_text}</p>", unsafe_allow_html=True)

    with col3:
        if st.button("❌", key=f"del_{task_id}"):
            delete_task(task_id)
            st.rerun()

st.markdown("---")
st.caption("Your tasks and names are saved permanently in SQLite! 🎯")
