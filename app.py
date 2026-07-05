from flask import Flask, jsonify, send_file
import os
import sys
import threading

# Ensure terminal outputs support Bengali Unicode characters without crashing
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass


# Import existing functions
from main import run_cycle_with_retry
from social_poster import open_interactive_login, post_to_all
from download import create_repo_zip

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login_route():
    thread = threading.Thread(target=open_interactive_login)
    thread.start()
    return jsonify({"status": "login started"})

@app.route('/post_all', methods=['POST'])
def post_all_route():
    try:
        run_cycle_with_retry()
        return jsonify({"status": "cycle completed"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/download', methods=['GET'])
def download_route():
    zip_path = create_repo_zip()
    return send_file(zip_path, as_attachment=True, download_name='project.zip')

@app.route('/health', methods=['GET'])
def health_route():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
