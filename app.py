from flask import Flask, render_template, request, jsonify
import re #module
import requests
import whois
import tldextract
from datetime import datetime


app = Flask(__name__)

#Open homepage
@app.route('/')
def index():
    return render_template('index.html')

#-----------Check SSL/TLS certificate validity-----------#
def check_ssl_certificate(url):
    try:
        response = requests.get(url, timeout=5)
        return True   #SSL is valid
    except requests.exceptions.SSLError:
        return False   # SSL error
    except requests.exceptions.RequestException:
        return None #connection Error




#------------Get domain age-------------#
def get_domain_age(url):
    try:
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}"
        domain_info = whois.whois(domain)

        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        # Calculate domain age
        if creation_date:
            age = (datetime.now() - creation_date).days // 365
            return age
        return None  # Couldn't retrieve domain age
    except Exception:
        return None  # Whois query failed




#------------Check the link------------------#
@app.route('/check_link', methods=['POST'])
def check_link():
    data = request.get_json()
    link = data.get('link', '')

    #Validate URL format
    if not re.match(r'^(http|https)://', link):
        return jsonify({"status": "error", "message": "Invalid URL format. Please provide a valid link."})


    #Check HTTPS
    is_https = link.startswith('https://')
    ssl_status = check_ssl_certificate(link)

    # Check domain age
    domain_age = get_domain_age(link)

    # Prepare response
    response = {
        "status": "safe" if is_https else "warning",
        "message": "The link is using HTTPS, which is generally secure." if is_https else "The link is using HTTP, which is not secure.",
        "ssl_valid": ssl_status,
        "domain_age": domain_age
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)


