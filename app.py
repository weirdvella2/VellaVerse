import streamlit as st
from pathlib import Path
import json
import base64

# Admin credentials (hidden)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "vellaverse123"  # Change this!

# App configuration
CONFIG_FILE = "data/vellaverse_config.json"

# Initialize data structure
def init_data():
    return {
        "subjects": {
            "Mathematics": {"resources": []},
            "Physics": {"resources": []},
            "Chemistry": {"resources": []},
            "Biology": {"resources": []},
            "Computer Science": {"resources": []},
            "English": {"resources": []},
        },
        "recent_activity": []
    }

# Load or create config
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        data = init_data()
        save_config(data)
        return data

def save_config(data):
    Path("data").mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# Main app
def main():
    st.set_page_config(page_title="VellaVerse", layout="wide")
    
    # Initialize session state
    if "data" not in st.session_state:
        st.session_state.data = load_config()
    if "admin_mode" not in st.session_state:
        st.session_state.admin_mode = False
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .subject-card {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f0f2f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Admin login (hidden in sidebar)
    with st.sidebar:
        if not st.session_state.admin_mode:
            with st.expander("Admin Login", expanded=False):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.button("Login"):
                    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                        st.session_state.admin_mode = True
                        st.success("Admin mode activated")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid credentials")
        else:
            st.success("Admin Mode")
            if st.button("Logout"):
                st.session_state.admin_mode = False
                st.experimental_rerun()
    
    # Main app header
    st.title("VellaVerse")
    st.markdown("Continue your learning journey. Pick up where you left off.")
    
    # Admin controls
    if st.session_state.admin_mode:
        with st.expander("Admin Controls", expanded=True):
            st.subheader("Manage Content")
            
            # Subject selection
            subject = st.selectbox("Select Subject", list(st.session_state.data["subjects"].keys()))
            
            # Resource management
            st.subheader(f"Resources for {subject}")
            for i, resource in enumerate(st.session_state.data["subjects"][subject]["resources"]):
                col1, col2 = st.columns([4,1])
                with col1:
                    st.write(f"📄 {resource['name']}")
                with col2:
                    if st.button(f"Delete {i}"):
                        st.session_state.data["subjects"][subject]["resources"].pop(i)
                        save_config(st.session_state.data)
                        st.experimental_rerun()
            
            # Add new resource
            st.subheader("Add New Resource")
            new_resource_name = st.text_input("Resource Name")
            new_resource_file = st.file_uploader("Upload File")
            if st.button("Add Resource") and new_resource_name:
                if new_resource_file:
                    file_data = new_resource_file.read()
                    file_b64 = base64.b64encode(file_data).decode()
                    st.session_state.data["subjects"][subject]["resources"].append({
                        "name": new_resource_name,
                        "file": file_b64,
                        "type": new_resource_file.type,
                        "date": str(st.datetime.now())
                    })
                    save_config(st.session_state.data)
                    st.success("Resource added!")
                    st.experimental_rerun()
    
    # Main content - Dashboard
    st.header("Your Subjects")
    
    # Display subjects in a grid
    cols = st.columns(3)
    for i, (subject, data) in enumerate(st.session_state.data["subjects"].items()):
        with cols[i % 3]:
            with st.container():
                st.markdown(f"<div class='subject-card'>", unsafe_allow_html=True)
                st.subheader(subject)
                
                # Display resources
                with st.expander("Resources"):
                    for resource in data["resources"]:
                        st.write(f"📄 {resource['name']}")
                        if st.button(f"Download {resource['name']}", key=f"dl_{subject}_{resource['name']}"):
                            file_data = base64.b64decode(resource["file"])
                            st.download_button(
                                label="Click to download",
                                data=file_data,
                                file_name=resource["name"],
                                mime=resource["type"]
                            )
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent activity
    st.header("Recent Activity")
    for activity in st.session_state.data["recent_activity"][-5:]:
        st.write(f"- {activity['action']} {activity['subject']} - {activity['date']}")

if __name__ == "__main__":
    main()
