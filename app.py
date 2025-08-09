import gradio as gr
from pathlib import Path
import json
import base64
import os
from datetime import datetime

# Admin credentials (hidden)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "vellaverse123"  # Change this!

# App configuration
CONFIG_FILE = "vellaverse_config.json"

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
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        data = init_data()
        save_config(data)
        return data

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# Track activity
def log_activity(action, subject):
    st.session_state.data["recent_activity"].append({
        "action": action,
        "subject": subject,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_config(st.session_state.data)

# Gradio UI Components
def create_subject_ui(subject, resources):
    with gr.Accordion(label=subject, open=False):
        if resources:
            for idx, resource in enumerate(resources):
                with gr.Row():
                    gr.Markdown(f"📄 {resource['name']}")
                    download_btn = gr.Button("Download", variant="secondary")
                    if st.session_state.get("admin_mode", False):
                        delete_btn = gr.Button("✕", variant="stop", size="sm")
                        delete_btn.click(
                            fn=lambda s, i: delete_resource(s, i),
                            inputs=[gr.State(subject), gr.State(idx)],
                            outputs=gr.Markdown()
                        )
        else:
            gr.Markdown("No resources yet")

def delete_resource(subject, resource_idx):
    st.session_state.data["subjects"][subject]["resources"].pop(resource_idx)
    save_config(st.session_state.data)
    return "Resource deleted!"

# Main UI
def build_ui():
    st.session_state.data = load_config()
    
    with gr.Blocks(title="VellaVerse", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 📚 VellaVerse")
        gr.Markdown("Continue your learning journey")
        
        # Admin login (hidden)
        with gr.Row(visible=not st.session_state.get("admin_mode", False)) as login_row:
            with gr.Column(scale=2):
                username = gr.Textbox(label="Username")
                password = gr.Textbox(label="Password", type="password")
            with gr.Column(scale=1):
                login_btn = gr.Button("Admin Login")
        
        # Admin controls
        if st.session_state.get("admin_mode", False):
            with gr.Row():
                gr.Markdown("## 🛠 Admin Controls")
                logout_btn = gr.Button("Logout")
            
            with gr.Row():
                subject_dropdown = gr.Dropdown(
                    label="Select Subject",
                    choices=list(st.session_state.data["subjects"].keys())
                )
                new_resource_name = gr.Textbox(label="Resource Name")
                file_upload = gr.File(label="Upload File")
                add_btn = gr.Button("Add Resource")
            
            # Admin functions
            def admin_login(u, p):
                if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
                    st.session_state.admin_mode = True
                    return gr.Row.update(visible=False), gr.Row.update(visible=True)
                else:
                    raise gr.Error("Invalid credentials")
            
            def admin_logout():
                st.session_state.admin_mode = False
                return gr.Row.update(visible=True), gr.Row.update(visible=False)
            
            def add_resource(subject, name, file):
                if not name:
                    raise gr.Error("Resource name required")
                if not file:
                    raise gr.Error("File required")
                
                file_data = base64.b64encode(file).decode()
                st.session_state.data["subjects"][subject]["resources"].append({
                    "name": name,
                    "file": file_data,
                    "type": "application/octet-stream",
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                save_config(st.session_state.data)
                return "Resource added!"
            
            login_btn.click(
                admin_login,
                inputs=[username, password],
                outputs=[login_row, admin_panel]
            )
            
            logout_btn.click(
                admin_logout,
                outputs=[login_row, admin_panel]
            )
            
            add_btn.click(
                add_resource,
                inputs=[subject_dropdown, new_resource_name, file_upload],
                outputs=gr.Markdown()
            )
        
        # Subjects grid
        with gr.Row():
            for subject, data in st.session_state.data["subjects"].items():
                with gr.Column():
                    create_subject_ui(subject, data["resources"])
        
        # Recent activity
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Recent Activity")
                if st.session_state.data["recent_activity"]:
                    for activity in st.session_state.data["recent_activity"][-5:]:
                        gr.Markdown(f"- {activity['action']} {activity['subject']} ({activity['date']})")
                else:
                    gr.Markdown("No recent activity")
    
    return app

if __name__ == "__main__":
    demo = build_ui()
    demo.launch()
