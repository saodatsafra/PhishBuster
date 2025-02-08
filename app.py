from flask import Flask, render_template, request, jsonify
import re #module
import requests

app = Flask(__name__)

#Open homepage
@app.route('/')
def index():
    return render_template('index.html')

#Check SSL/TLS certificate validaty
def check_ssl_certificate(url):
    try:
        response = requests.get(url, timeout=5)
        return True
    except requests.exceptions.SSLError:
        return False
    except requests.exceptions.RequestException:
        return None #connection Error


#Check the link
@app.route('/check_link', methods=['POST'])
def check_link():
    data = request.get_json()
    link = data.get('link', '')

    # Logic of checking the link for HTTPS or not
    if re.match(r'^https://', link):
        return jsonify({"status": "safe", "message": "The link is using HTTPS, which is generally secure."})
    elif re.match(r'^http://', link):
        return jsonify({"status": "warning", "message": "The link is using HTTP, which is not secure."})
    else:
        return jsonify({"status": "error", "message": "Invalid URL format. Please provide a valid link."})

if __name__ == '__main__':
    app.run(debug=True)
