import os
import subprocess
from flask import Blueprint, render_template, request, jsonify, make_response, current_app, send_from_directory

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@main.route('/static/data/flag.json')
def serve_flag_data():
    """Serve the flag.json data file"""
    try:
        # Check static/data directory
        static_data_path = os.path.join(current_app.static_folder, 'data', 'flag.json')
        if os.path.exists(static_data_path):
            return send_from_directory(os.path.join(current_app.static_folder, 'data'), 'flag.json')
        
        # If it doesn't exist, return an error
        return jsonify({"error": "Flag data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint that helps users to accept the certificate"""
    return jsonify({
        "status": "ok",
        "message": "API is running. Static site is served directly from this Flask application.",
        "info": "This page helps your browser accept the self-signed certificate."
    })

@main.route("/change-flag", methods=["OPTIONS", "POST"])
def change_flag():
    """Change the displayed flag"""
    # Respond to preflight immediately
    if request.method == "OPTIONS":
        resp = make_response(("", 204))
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    country = request.args.get("country")
    if not country:
        return "Missing ?country=…", 400

    # Get the base directory path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script = os.path.join(base_dir, "scripts", "main.py")
    
    # Run the script to change the flag
    cmd = ["sudo", "-u", "chris", "python3", script, country]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    
    if proc.returncode != 0:
        return f"Error: {proc.stderr.strip()}", 500
    
    # Prepare response
    resp = make_response(f"Flag changed to {country}", 200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    
    return resp