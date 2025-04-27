from flask import Flask, render_template, request, jsonify
import re #module
import requests
import whois
import tldextract
from datetime import datetime


app = Flask(__name__)
@app.route('/')
def index(): #homepage
    return render_template("index.html")


def check_ssl_certificate(url):
    try:
        response = requests.get(url, timeout=3)
        return True   #SSL is valid
    except requests.exceptions.SSLError as e: #as e --> If an error happens, save the error message in a variable called e.
        print(f"SSL error: {e}")
        return False   # SSL error
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None #connection Error

def get_domain_info(url):
    try:
        extracted = tldextract.extract(url) # Extract domain name from URL
        domain = f"{extracted.domain}.{extracted.suffix}"

        domain_info = whois.whois(domain) #look up whois info

#registrar extract
        registrar = getattr(domain_info, "registrar", None)
        if isinstance(registrar, list): # Sometimes it's a list
            registrar = registrar[0] if registrar else None

#country extract
        country = getattr(domain_info, "country", None)
        if isinstance(country, list):
            country = country[0] if country else None

#creation and expiration dates extract
        creation_date = getattr(domain_info, 'creation_date', None)
        expiration_date = getattr(domain_info, 'expiration_date', None)

        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
#Calculation
        if creation_date:
            age = (datetime.now() - creation_date).days // 365 #get full years by dividing by 365
        else:
            age = None

# Return all collected info as a dictionary
        return {
            "registrar": registrar,
            "country": country,
            "creation_date": str(creation_date) if creation_date else None,
            "expiration_date": str(expiration_date) if expiration_date else None,
            "age": age
        }
    except Exception as e:
        print(f"Domain info error: {e}")
    # If there is any error, return all fields as None
    return {
        "registrar": None,
        "country": None,
        "creation_date": None,
        "expiration_date": None,
        "age": None
    }








#------------------main check route--------------------#
@app.route('/check_link', methods=['POST'])
def check_link():
    data = request.get_json()
    link = data.get('link', '')
    link = link.lower().strip()

    if not (re.match(r'^(http|https)://', link) or re.match(r'^www\.', link)):
        return jsonify({
            "status": "error",
            "message": "⚠️ Invalid URL format. Please provide a valid link."
        })

    is_https = link.startswith('https://')
    is_http = link.startswith('http://')
    is_www_only = link.startswith('www.')
    is_www_protocol = '://www.' in link
    ssl_status = check_ssl_certificate(link)                # Check ssl certificate
    domain_info = get_domain_info(link)
    domain_age = domain_info["age"]                       # Get domain age, how old(years)
    suspicious_keywords = ['login', 'verify', 'update', 'free', 'gift', 'security']
    keyword_hits = [word for word in suspicious_keywords if word in link]
    is_young = domain_age is not None and domain_age < 1
    is_ip = re.match(r'^https?://\d{1,3}(\.\d{1,3}){3}', link) is not None



    #SCORING ALGORITHM
    score = 0
    if is_https:
        score += 1
    else:
        score -= 2

    if ssl_status:
        score += 2
    elif ssl_status is False:
        score -= 2

    if domain_age is not None:
        if domain_age < 1:
            score -= 2
        elif domain_age >= 1:
            score += 2
    else:
        score -= 1 #cannt determine

    score -= 2* min(len(keyword_hits), 2) #up to -4
    if not keyword_hits:
        score += 2

    if is_ip:
        score -= 3

    if is_www_only:
        score -= 2

    if is_www_protocol:
        score += 1

    if score >= 4:
        status = "safe"
    elif 0 <= score < 4:
        status = "might not be safe"
    else:
        status = "dangerous"


    if is_https:
        message = "✅ The link is using HTTPS, which is generally secure."
    elif is_http:
        message = "⚠️ The link is using HTTP, which is not secure."
    elif is_www_only:
        message = "⚠️ The link is missing http or https. It starts with 'www.' — this is less trustworthy."
    else:
        message = "⚠️ The link is missing a protocol. Please use a full URL."

    #response dictionary:
    response = {
        "status": "safe" if score >= 4 else "might not be safe" if  0 <= score < 4 else "dangerous",
        "message": message,
        "is_www_only": is_www_only,
        "is_www_protocol": is_www_protocol,
        "is_https": is_https,
        "is_http": is_http,
        "ssl_valid": ssl_status,
        "domain_age": domain_age,
        "keywords_found": keyword_hits,
        "young_domain": is_young,
        "is_ip_address": is_ip,
        "score": score,
        "registrar": domain_info["registrar"],
        "country": domain_info["country"],
        "creation_date": domain_info["creation_date"],
        "expiration_date": domain_info["expiration_date"],
    }
    return jsonify(response)  #sends the results back to the browser in a js format



if __name__ == '__main__':
    app.run(debug=True)