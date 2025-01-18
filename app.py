from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_link', methods=['POST'])
def check_link():
    data = request.get_json()
    link = data.get('link', '')

    # Check if the link is HTTPS or not
    if re.match(r'^https://', link):
        return jsonify({"status": "safe", "message": "The link is using HTTPS, which is generally secure."})
    elif re.match(r'^http://', link):
        return jsonify({"status": "warning", "message": "The link is using HTTP, which is not secure."})
    else:
        return jsonify({"status": "error", "message": "Invalid URL format. Please provide a valid link."})

if __name__ == '__main__':
    app.run(debug=True)
