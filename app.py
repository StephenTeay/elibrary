import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import hashlib
import requests
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="FEDERAL SCHOOL OF STATISTICS, IBADAN E-Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for distinctive design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+3:wght@300;400;600&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        font-family: 'Source Sans 3', sans-serif;
    }
    
    /* Main Content Area */
    .main .block-container {
        padding-top: 2rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 1rem auto;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: #fff;
        font-weight: 900;
        letter-spacing: -0.5px;
    }
    
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem !important;
        margin-bottom: 0.5rem;
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Card Styling */
    .resource-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .resource-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px rgba(102, 126, 234, 0.4);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Source Sans 3', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        color: white;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #fff;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: rgba(34, 197, 94, 0.2);
        border: 1px solid rgba(34, 197, 94, 0.5);
        border-radius: 10px;
        color: #86efac;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.5);
        border-radius: 10px;
        color: #fca5a5;
    }
    
    /* Info boxes */
    .stInfo {
        background: rgba(59, 130, 246, 0.2);
        border: 1px solid rgba(59, 130, 246, 0.5);
        border-radius: 10px;
        color: #93c5fd;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 600;
        border-bottom: 3px solid transparent;
        padding: 1rem 0;
    }
    
    .stTabs [aria-selected="true"] {
        color: #667eea;
        border-bottom-color: #667eea;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #667eea;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Labels */
    label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500;
    }
    
    /* Dataframe styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Database initialization
def init_db():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect('elibrary.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  role TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Resources table
    c.execute('''CREATE TABLE IF NOT EXISTS resources
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  author TEXT,
                  resource_type TEXT NOT NULL,
                  isbn TEXT,
                  description TEXT,
                  quantity INTEGER DEFAULT 1,
                  available INTEGER DEFAULT 1,
                  cover_url TEXT,
                  file_path TEXT,
                  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Borrowing records table
    c.execute('''CREATE TABLE IF NOT EXISTS borrowings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  resource_id INTEGER,
                  borrowed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  due_date TIMESTAMP,
                  returned_at TIMESTAMP,
                  status TEXT DEFAULT 'active',
                  FOREIGN KEY (user_id) REFERENCES users(id),
                  FOREIGN KEY (resource_id) REFERENCES resources(id))''')
    
    # Create default admin if not exists
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ("admin", admin_password, "admin"))
    
    conn.commit()
    conn.close()

# Authentication functions
def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    """Authenticate user credentials"""
    conn = sqlite3.connect('elibrary.db')
    c = conn.cursor()
    hashed = hash_password(password)
    c.execute("SELECT id, username, role FROM users WHERE username=? AND password=?",
              (username, hashed))
    result = c.fetchone()
    conn.close()
    return result

def register_user(username, password, role="student"):
    """Register a new user"""
    try:
        conn = sqlite3.connect('elibrary.db')
        c = conn.cursor()
        hashed = hash_password(password)
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, hashed, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# External API integration - Open Library API
def fetch_book_from_api(isbn_or_title):
    """Fetch book information from Open Library API"""
    try:
        # Try ISBN search first
        if isbn_or_title.replace('-', '').isdigit():
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn_or_title}&format=json&jscmd=data"
        else:
            # Title search
            url = f"https://openlibrary.org/search.json?title={isbn_or_title}&limit=1"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Parse ISBN response
            if f"ISBN:{isbn_or_title}" in data:
                book_data = data[f"ISBN:{isbn_or_title}"]
                return {
                    "title": book_data.get("title", ""),
                    "author": ", ".join([a["name"] for a in book_data.get("authors", [])]),
                    "isbn": isbn_or_title,
                    "description": book_data.get("notes", ""),
                    "cover_url": book_data.get("cover", {}).get("medium", "")
                }
            # Parse title search response
            elif "docs" in data and len(data["docs"]) > 0:
                book = data["docs"][0]
                return {
                    "title": book.get("title", ""),
                    "author": ", ".join(book.get("author_name", [])),
                    "isbn": book.get("isbn", [""])[0] if book.get("isbn") else "",
                    "description": book.get("first_sentence", [""])[0] if book.get("first_sentence") else "",
                    "cover_url": f"https://covers.openlibrary.org/b/id/{book.get('cover_i', '')}-M.jpg" if book.get('cover_i') else ""
                }
        return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# Resource management functions
def add_resource(title, author, resource_type, isbn="", description="", quantity=1, cover_url="", file_path=""):
    """Add a new resource to the library"""
    conn = sqlite3.connect('elibrary.db')
    c = conn.cursor()
    c.execute("""INSERT INTO resources 
                 (title, author, resource_type, isbn, description, quantity, available, cover_url, file_path) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (title, author, resource_type, isbn, description, quantity, quantity, cover_url, file_path))
    conn.commit()
    conn.close()

def search_resources(query, resource_type="all"):
    """Search for resources by title or author"""
    conn = sqlite3.connect('elibrary.db')
    c = conn.cursor()
    
    if resource_type == "all":
        c.execute("""SELECT id, title, author, resource_type, isbn, available, quantity, cover_url, file_path 
                     FROM resources 
                     WHERE title LIKE ? OR author LIKE ?""",
                  (f"%{query}%", f"%{query}%"))
    else:
        c.execute("""SELECT id, title, author, resource_type, isbn, available, quantity, cover_url, file_path 
                     FROM resources 
                     WHERE (title LIKE ? OR author LIKE ?) AND resource_type=?""",
                  (f"%{query}%", f"%{query}%", resource_type))
    
    results = c.fetchall()
    conn.close()
    return results

def get_all_resources(resource_type="all"):
    """Get all resources, optionally filtered by type"""
    conn = sqlite3.connect('elibrary.db')
    c = conn.cursor()
    
    if resource_type == "all":
        c.execute("SELECT id, title, author, resource_type, isbn, available, quantity, cover_url, file_path FROM resources")
    else:
        c.execute("SELECT id, title, author, resource_type, isbn, available, quantity, cover_url, file_path FROM resources WHERE resource_type=?", 
                  (resource_type,))
    
    results = c.fetchall()
    conn.close()
    return results

def borrow_resource(user_id, resource_id):
    """Borrow a resource with validation"""
    conn = sqlite3.connect('elibrary.db')
    c = conn.cursor()
    
    # Check if user already borrowed this resource
    c.execute("""SELECT COUNT(*) FROM borrowings 
                 WHERE user_id=? AND resource_id=? AND status='active'""",
              (user_id, resource_id))
    already_borrowed = c.fetchone()[0] > 0
    
    if already_borrowed:
        conn.close()
        return False, "You have already borrowed this resource!"
    
    # Check if user has reached max borrowing limit (5 books)
    c.execute("SELECT COUNT(*) FROM borrowings WHERE user_id=? AND status='active'", (user_id,))
    active_count = c.fetchone()[0]
    
    if active_count >= 5:
        conn.close()
        return False, "You have reached the maximum borrowing limit of 5 resources!"
    
    # Check availability
    c.execute("SELECT available FROM resources WHERE id=?", (resource_id,))
    result = c.fetchone()
    
    if result and result[0] > 0:
        # Create borrowing record
        due_date = datetime.now() + timedelta(days=14)  # 2 weeks borrowing period
        c.execute("""INSERT INTO borrowings (user_id, resource_id, due_date) 
                     VALUES (?, ?, ?)""",
                  (user_id, resource_id, due_date))
        
        # Update available count
        c.execute("UPDATE resources SET available = available - 1 WHERE id=?", (resource_id,))
        conn.commit()
        conn.close()
        return True, "Resource borrowed successfully!"
    
    conn.close()
    return False, "Resource is not available!"

def return_resource(borrowing_id):
    """Return a borrowed resource"""
    conn = sqlite3.connect('elibrary.db')
    c = conn.cursor()
    
    # Get resource_id from borrowing
    c.execute("SELECT resource_id FROM borrowings WHERE id=?", (borrowing_id,))
    result = c.fetchone()
    
    if result:
        resource_id = result[0]
        
        # Update borrowing record
        c.execute("""UPDATE borrowings 
                     SET returned_at=?, status='returned' 
                     WHERE id=?""",
                  (datetime.now(), borrowing_id))
        
        # Update available count
        c.execute("UPDATE resources SET available = available + 1 WHERE id=?", (resource_id,))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def get_user_borrowings(user_id):
    """Get all borrowings for a user"""
    conn = sqlite3.connect('elibrary.db')
    c = conn.cursor()
    
    c.execute("""SELECT b.id, r.title, r.author, r.resource_type, b.borrowed_at, b.due_date, b.status, r.id
                 FROM borrowings b
                 JOIN resources r ON b.resource_id = r.id
                 WHERE b.user_id=? AND b.status='active'
                 ORDER BY b.borrowed_at DESC""",
              (user_id,))
    
    results = c.fetchall()
    conn.close()
    return results

def get_all_borrowings():
    """Get all borrowings (admin view)"""
    conn = sqlite3.connect('elibrary.db')
    c = conn.cursor()
    
    c.execute("""SELECT b.id, u.username, r.title, r.resource_type, b.borrowed_at, b.due_date, b.status
                 FROM borrowings b
                 JOIN users u ON b.user_id = u.id
                 JOIN resources r ON b.resource_id = r.id
                 ORDER BY b.borrowed_at DESC
                 LIMIT 50""")
    
    results = c.fetchall()
    conn.close()
    return results

def get_library_stats():
    """Get library statistics"""
    conn = sqlite3.connect('elibrary.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM resources")
    total_resources = c.fetchone()[0]
    
    c.execute("SELECT SUM(quantity) FROM resources")
    total_copies = c.fetchone()[0] or 0
    
    c.execute("SELECT COUNT(*) FROM borrowings WHERE status='active'")
    active_borrowings = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    total_students = c.fetchone()[0]
    
    conn.close()
    return {
        "total_resources": total_resources,
        "total_copies": total_copies,
        "active_borrowings": active_borrowings,
        "total_students": total_students
    }

# Main application
def main():
    init_db()
    
    # Session state initialization
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.role = None
    
    # Login/Register page
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h1 style='text-align: center;'>📚 FEDERAL SCHOOL OF STATISTICS, IBADAN E-LIBRARY</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.7); font-size: 1.2rem;'>Digital Library</p>", unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                st.markdown("### Welcome Back")
                username = st.text_input("Username", key="login_username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
                
                if st.button("Login", width=300):
                    user = authenticate(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.session_state.username = user[1]
                        st.session_state.role = user[2]
                        st.success(f"Welcome back, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")
                
                st.info("**If you are not registered, please create an account to access the library resources.**")
            
            with tab2:
                st.markdown("### Create Account")
                new_username = st.text_input("Choose Username", key="reg_username", placeholder="Enter a unique username")
                new_password = st.text_input("Choose Password", type="password", key="reg_password", placeholder="Create a strong password")
                confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", placeholder="Re-enter password")
                
                if st.button("Register", width=300):
                    if new_password != confirm_password:
                        st.error("Passwords don't match!")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters!")
                    else:
                        if register_user(new_username, new_password):
                            st.success("Registration successful! Please login.")
                        else:
                            st.error("Username already exists!")
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        st.markdown(f"**Role:** {st.session_state.role.title()}")
        st.markdown("---")
        
        if st.button("🚪 Logout", width=200):
            st.session_state.clear()
            st.rerun()
    
    # Main content based on role
    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        student_dashboard()

def student_dashboard():
    """Student dashboard interface"""
    st.title("📚 FSS E-Library")
    
    # Get current borrowing count
    borrowings = get_user_borrowings(st.session_state.user_id)
    borrow_count = len(borrowings)
    
    # Display borrowing limit info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📖 Books Borrowed", f"{borrow_count}/5")
    with col2:
        st.metric("📚 Available Slots", f"{5 - borrow_count}")
    with col3:
        overdue_count = sum(1 for b in borrowings if (datetime.strptime(b[5].split('.')[0], "%Y-%m-%d %H:%M:%S") - datetime.now()).days < 0)
        st.metric("⚠️ Overdue Items", overdue_count)
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Browse & Search", "📖 My Borrowings", "ℹ️ About"])
    
    with tab1:
        st.markdown("### Explore Our Collection")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("🔎 Search by title or author", placeholder="Search for books, journals, audio files...")
        with col2:
            resource_filter = st.selectbox("Filter by type", ["all", "book", "journal", "audio"])
        
        if st.button("Search", width=200) or search_query:
            if search_query:
                resources = search_resources(search_query, resource_filter)
            else:
                resources = get_all_resources(resource_filter)
        else:
            resources = get_all_resources(resource_filter)
        
        if resources:
            st.markdown(f"**Found {len(resources)} resources**")
            
            # Display resources in cards
            for resource in resources:
                resource_id, title, author, res_type, isbn, available, quantity, cover_url, file_path = resource
                
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="resource-card">
                            <h3 style="margin-top: 0; color: #667eea;">{title}</h3>
                            <p style="color: rgba(255,255,255,0.8);"><strong>Author:</strong> {author or 'Unknown'}</p>
                            <p style="color: rgba(255,255,255,0.7);"><strong>Type:</strong> {res_type.title()}</p>
                            <p style="color: rgba(255,255,255,0.7);"><strong>ISBN:</strong> {isbn or 'N/A'}</p>
                            <p style="color: {'#86efac' if available > 0 else '#fca5a5'};"><strong>Available:</strong> {available} of {quantity}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if cover_url:
                            st.image(cover_url, width=120)
                    
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
                    
                    with col1:
                        if available > 0:
                            if st.button(f"📚 Borrow", key=f"borrow_{resource_id}"):
                                st.session_state[f'show_borrow_modal_{resource_id}'] = True
                        else:
                            st.button("❌ Unavailable", disabled=True, key=f"unavail_{resource_id}")
                    
                    with col2:
                        if file_path:
                            if st.button("👁️ Preview", key=f"preview_{resource_id}"):
                                st.session_state[f'show_preview_{resource_id}'] = True
                                st.pdf(file_path)
                                
                    
                    # Borrowing Modal
                    if st.session_state.get(f'show_borrow_modal_{resource_id}', False):
                        st.markdown("---")
                        st.markdown(f"### 📚 Borrowing: {title}")
                        
                        st.info(f"""
                        **Borrowing Details:**
                        - **Title:** {title}
                        - **Author:** {author or 'Unknown'}
                        - **Type:** {res_type.title()}
                        - **Loan Period:** 14 days
                        - **Due Date:** {(datetime.now() + timedelta(days=14)).strftime('%B %d, %Y')}
                        - **Current Borrowed:** {borrow_count}/5 books
                        """)
                        
                        st.markdown("""
                        <div style="background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                        <h4 style="margin: 0; color: #667eea;">📋 Terms & Conditions</h4>
                        <ul style="color: rgba(255,255,255,0.8); margin-top: 0.5rem;">
                            <li>Return the resource on or before the due date</li>
                            <li>Handle the resource with care</li>
                            <li>Late returns may incur fines</li>
                            <li>Resources are non-transferable</li>
                        </ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button("✅ Confirm Borrow", key=f"confirm_{resource_id}", width=200):
                                success, message = borrow_resource(st.session_state.user_id, resource_id)
                                if success:
                                    st.success(f"✅ {message}")
                                    st.balloons()
                                    st.session_state[f'show_borrow_modal_{resource_id}'] = False
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                        
                        with col2:
                            if st.button("❌ Cancel", key=f"cancel_{resource_id}", width=200):
                                st.session_state[f'show_borrow_modal_{resource_id}'] = False
                                st.rerun()
                        
                        st.markdown("---")
                    
                    # Preview Modal
                    if st.session_state.get(f'show_preview_{resource_id}', False) and file_path:
                        st.markdown("---")
                        st.markdown(f"### 👁️ Preview: {title}")
                        
                        try:
                            if file_path.lower().endswith(('.pdf')):
                                with open(file_path, "rb") as f:
                                    st.download_button(
                                        label="📥 Download PDF",
                                        data=f,
                                        file_name=f"{title}.pdf",
                                        mime="application/pdf"
                                    )
                                st.info("PDF preview - Click download to view the full document")
                            elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                                st.image(file_path, caption=title)
                            elif file_path.lower().endswith(('.txt', '.md')):
                                with open(file_path, "r", encoding='utf-8') as f:
                                    content = f.read()
                                    st.text_area("Content Preview", content, height=300)
                            else:
                                st.warning("Preview not available for this file type")
                        except Exception as e:
                            st.error(f"Error loading preview: {str(e)}")
                        
                        if st.button("Close Preview", key=f"close_preview_{resource_id}"):
                            st.session_state[f'show_preview_{resource_id}'] = False
                            st.rerun()
                        
                        st.markdown("---")
        else:
            st.info("No resources found. Try a different search term.")
    
    with tab2:
        st.markdown("### Your Borrowed Items")
        
        if borrowings:
            for borrowing in borrowings:
                borrow_id, title, author, res_type, borrowed_at, due_date, status, resource_id = borrowing
                
                # Parse due date safely
                try:
                    due_date_str = due_date.split('.')[0]  # Remove microseconds
                    due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
                
                days_left = (due_date_obj - datetime.now()).days
                
                color = "#86efac" if days_left > 3 else "#fbbf24" if days_left > 0 else "#fca5a5"
                status_text = "✅ On Time" if days_left > 3 else "⚠️ Due Soon" if days_left > 0 else "🔴 Overdue"
                
                st.markdown(f"""
                <div class="resource-card">
                    <h3 style="margin-top: 0; color: #667eea;">{title}</h3>
                    <p style="color: rgba(255,255,255,0.8);"><strong>Author:</strong> {author}</p>
                    <p style="color: rgba(255,255,255,0.7);"><strong>Type:</strong> {res_type.title()}</p>
                    <p style="color: rgba(255,255,255,0.7);"><strong>Borrowed:</strong> {borrowed_at.split('.')[0]}</p>
                    <p style="color: {color};"><strong>Due Date:</strong> {due_date_obj.strftime('%B %d, %Y')} ({abs(days_left)} days {'left' if days_left >= 0 else 'overdue'})</p>
                    <p style="color: {color}; font-weight: bold;">{status_text}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button(f"📤 Return", key=f"return_{borrow_id}"):
                        if return_resource(borrow_id):
                            st.success("Resource returned successfully!")
                            st.rerun()
                        else:
                            st.error("Unable to return resource!")
        else:
            st.info("You haven't borrowed any resources yet. Browse the collection to get started!")
    
    with tab3:
        st.markdown("### About FSS E-Library")
        st.markdown("""
        Welcome to **FSS E-Library**, your comprehensive digital library platform!
        
        #### Features:
        - 📚 Browse extensive collection of books, journals, and audio files
        - 🔍 Smart search functionality
        - 📖 Easy borrowing and returns with confirmation system
        - 👁️ Preview resources before borrowing
        - ⏰ Track due dates and borrowing history
        - 📊 Real-time borrowing statistics
        - 📱 Accessible anytime, anywhere
        
        #### Borrowing Policy:
        - **Maximum limit:** 5 resources at a time
        - **Borrowing period:** 14 days
        - **Cannot borrow duplicates:** Each resource can only be borrowed once
        - **Late returns:** May incur fines (contact librarian)
        - Resources can be renewed if no one is waiting
        
        #### Color Coding:
        - 🟢 **Green:** More than 3 days remaining
        - 🟡 **Yellow:** Due soon (1-3 days)
        - 🔴 **Red:** Overdue
        
        #### Need Help?
        Contact the librarian for any assistance.
        """)
        
        st.markdown("---")
        st.markdown("**Your Library Statistics:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Borrowed", borrow_count)
        with col2:
            st.metric("Slots Available", 5 - borrow_count)
        with col3:
            on_time = sum(1 for b in borrowings if (datetime.strptime(b[5].split('.')[0], "%Y-%m-%d %H:%M:%S") - datetime.now()).days >= 0)
            st.metric("On-Time Returns", f"{on_time}/{borrow_count}" if borrow_count > 0 else "N/A")

def admin_dashboard():
    """Admin/Librarian dashboard interface"""
    st.title("🛠️ Library Management Dashboard")
    
    # Show statistics
    stats = get_library_stats()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Resources", stats['total_resources'])
    with col2:
        st.metric("📑 Total Copies", stats['total_copies'])
    with col3:
        st.metric("🔄 Active Loans", stats['active_borrowings'])
    with col4:
        st.metric("👥 Students", stats['total_students'])
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Resource", "📚 Manage Resources", "🔄 Borrowing Records", "🌐 Fetch from API"])
    
    with tab1:
        st.markdown("### Add New Resource")
        
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title *", placeholder="Enter resource title")
            author = st.text_input("Author", placeholder="Enter author name")
            resource_type = st.selectbox("Resource Type *", ["book", "journal", "audio"])
        with col2:
            isbn = st.text_input("ISBN", placeholder="Enter ISBN if available")
            quantity = st.number_input("Quantity *", min_value=1, value=1)
            cover_url = st.text_input("Cover Image URL", placeholder="Optional cover image URL")
        
        description = st.text_area("Description", placeholder="Brief description of the resource")
        
        # File upload section
        st.markdown("#### 📎 Upload Resource File (Optional)")
        uploaded_file = st.file_uploader(
            "Upload PDF, image, or text file", 
            type=['pdf', 'jpg', 'jpeg', 'png', 'txt', 'md'],
            help="Upload the actual resource file for preview and download"
        )
        
        file_path = ""
        if uploaded_file is not None:
            # Create uploads directory if it doesn't exist
            import os
            uploads_dir = "uploads"
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
            
            # Save the uploaded file
            file_path = os.path.join(uploads_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
        
        if st.button("Add Resource", width=200):
            if title and resource_type:
                add_resource(title, author, resource_type, isbn, description, quantity, cover_url, file_path)
                st.success(f"'{title}' added successfully!")
                st.balloons()
            else:
                st.error("Please fill in all required fields!")
    
    with tab2:
        st.markdown("### Resource Catalog")
        
        filter_type = st.selectbox("Filter by type", ["all", "book", "journal", "audio"], key="manage_filter")
        resources = get_all_resources(filter_type)
        
        if resources:
            import pandas as pd
            df = pd.DataFrame(resources, columns=["ID", "Title", "Author", "Type", "ISBN", "Available", "Total", "Cover URL", "File Path"])
            # Show only relevant columns
            display_df = df[["ID", "Title", "Author", "Type", "ISBN", "Available", "Total"]]
            st.dataframe(display_df, width=1200, hide_index=True)
            
            # Show resources with files
            resources_with_files = df[df["File Path"].notna() & (df["File Path"] != "")]
            if not resources_with_files.empty:
                st.markdown("#### 📎 Resources with Uploaded Files")
                st.dataframe(resources_with_files[["ID", "Title", "File Path"]], width=1200, hide_index=True)
        else:
            st.info("No resources in the library yet.")
    
    with tab3:
        st.markdown("### Borrowing Records")
        
        borrowings = get_all_borrowings()
        
        if borrowings:
            import pandas as pd
            df = pd.DataFrame(borrowings, columns=["ID", "Student", "Resource", "Type", "Borrowed", "Due Date", "Status"])
            st.dataframe(df, width=1200, hide_index=True)
        else:
            st.info("No borrowing records yet.")
    
    with tab4:
        st.markdown("### Fetch Resource from External API")
        st.info("Fetch book information from Open Library API using ISBN or title")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            api_query = st.text_input("Enter ISBN or Book Title", placeholder="e.g., 9780140328721 or 'The Great Gatsby'")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            search_api = st.button("Fetch from API", use_container_width=True)
        
        if search_api and api_query:
            with st.spinner("Fetching from Open Library..."):
                book_data = fetch_book_from_api(api_query)
                
                if book_data:
                    st.success("Book found!")
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if book_data.get('cover_url'):
                            st.image(book_data['cover_url'], width=200)
                    
                    with col2:
                        st.markdown(f"**Title:** {book_data['title']}")
                        st.markdown(f"**Author:** {book_data['author']}")
                        st.markdown(f"**ISBN:** {book_data['isbn']}")
                        if book_data['description']:
                            st.markdown(f"**Description:** {book_data['description']}")
                    
                    st.markdown("---")
                    quantity = st.number_input("Number of copies to add", min_value=1, value=1, key="api_quantity")
                    
                    if st.button("Add to Library", width=200):
                        add_resource(
                            book_data['title'],
                            book_data['author'],
                            'book',
                            book_data['isbn'],
                            book_data['description'],
                            quantity,
                            book_data['cover_url'],
                            ""  # No file path for API fetched books
                        )
                        st.success(f"'{book_data['title']}' added to library!")
                        st.balloons()
                else:
                    st.error("Book not found in Open Library. Try a different ISBN or title.")

if __name__ == "__main__":
    main()
