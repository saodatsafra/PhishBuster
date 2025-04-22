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


#--------------CHECK SSL/TLS VALIDATY---------------#
def check_ssl_certificate(url):
    try:
        response = requests.get(url, timeout=5)
        return True   #SSL is valid
    except requests.exceptions.SSLError as e: #as e --> If an error happens, save the error message in a variable called e.
        print(f"SSL error: {e}")
        return False   # SSL error
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None #connection Error


#------------------GET DOMAIN AGE----------------------#
def get_domain_age(url):
    try:
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}"
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
#Calculation
        if creation_date:
            age = (datetime.now() - creation_date).days // 365 #get full years by dividing by 365
            return age
        return None
    except Exception as e: #If anything at all fails above, just return None to avoid crashing
        print(f"Domain age error: {e}")
        return None




#------------------MAIN CHECK ROUTE (called by frontend)--------------------#
@app.route('/check_link', methods=['POST'])
def check_link():
    data = request.get_json()
    link = data.get('link', '')
    link = link.lower().strip()

    #Validate link format
    if not re.match(r'^(http|https)://', link):
        return jsonify({
            "status": "error",
            "message": "Invalid URL format. Please provide a valid link."
        })


###This is the part where your app checks the link the user typed in and builds a response to send back to the browser
    is_https = link.startswith('https://')                  # Check if the link uses HTTPS.
    ssl_status = check_ssl_certificate(link)                # Check ssl certificate
    domain_age = get_domain_age(link)                       # Get domain age, how old(years)

    response = {                                            # Creates a dictionary with all the results and prepare response :
        "status": "safe" if is_https else "warning",
        "message": "The link is using HTTPS, which is generally secure." if is_https else "The link is using HTTP, which is not secure.",
        "ssl_valid": ssl_status,
        "domain_age": domain_age
    }

    return jsonify(response)  #sends the results back to the browser in a js format




if __name__ == '__main__':
    app.run(debug=True)


