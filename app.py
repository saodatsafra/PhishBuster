from flask import Flask, render_template, request, jsonify
import re #module
import requests
import whois
import tldextract
from datetime import datetime
from functools import lru_cache


#scoring constants
max_score = +7      # best possible after we add new rules later
min_score = -27     # worst possible
bad_tlds   = {".click", ".top", ".live", ".xyz"}
good_tlds  = {".edu", ".gov"}
weights = {
    "https_bonus": +1,
    "http_penalty": -4,
    "ssl_valid": +2,
    "ssl_invalid": -3,
    "age_young_30d": -4,
    "age_young_6m": -2,
    "age_older_3y": +2,
    "keyword_hit": -1,    # per word
    "keyword_cap": 5,
    "ip_url": -4,
    "at_symbol": -3,
    "subdomain_penalty": -2,
    "bad_tld": -2,
    "good_tld": +2,
    "long_url": -1,
}
suspicious_keywords = [
    "login", "verify", "update", "free", "gift", "security",
    "confirm", "account", "bank", "appleid", "paypal"
]

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

@lru_cache(maxsize=512)
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
    keyword_hits = [word for word in suspicious_keywords if word in link]
    is_young = domain_age is not None and domain_age < 1
    is_ip = re.match(r'^https?://\d{1,3}(\.\d{1,3}){3}', link) is not None

#SCORING ALGORITHM
    score = 0
    reasons = []
    if is_https:
        score += weights["https_bonus"]
    else:
        score += weights["http_penalty"]
        reasons.append("Uses insecure HTTP")
    if ssl_status is True:
        score += weights["ssl_valid"]
    elif ssl_status is False:
        score += weights["ssl_invalid"]
        reasons.append("SSL verification failed")
    if domain_age is None:
        score += -1 #small penalty
        reasons.append("Domain age is unknown")
    else:
        if domain_age < 0.08: # <30 days (~0.08 years)
            score += weights["age_young_30d"]
            reasons.append("Domain age is younger than 1 month")
        elif domain_age < 0.5: # < 6 month
            score += weights["age_young_6m"]
            reasons.append("Domain age is younger than 6 month")
        elif domain_age > 3:
            score += weights["age_older_3y"]
    keyword_hits = [w for w  in suspicious_keywords if w in link]
    score += weights["keyword_hit"] * min(len(keyword_hits), weights["keyword_cap"])
    if keyword_hits:
        reasons.append(f"Suspicious words in URL: {', '.join(keyword_hits)}")
    if is_ip:
        score += weights["ip_url"]
        reasons.append(f"URL uses raw IP address")
    tld = "." + tldextract.extract(link).suffix
    if tld in bad_tlds:
        score += weights["bad_tld"]
        reasons.append(f"Uses suspicious top-level domain: {tld}")
    if tld in good_tlds:
        score += weights["good_tld"]
        reasons.append(f"Trusted top-level domain: {tld}")
    if "@" in link:
        score += weights["at_symbol"]
        reasons.append(f"URL contains '@' symbol")
    extracted = tldextract.extract(link)
    if extracted.subdomain and extracted.subdomain.count(".") >= 1:
        score += weights["subdomain_penalty"]
        reasons.append(f"URL has multiple subdomains")
    if len(link) > 70:
        score += weights["long_url"]
        reasons.append("URL is unusually long")

#Percentage
    score = max(min(score, max_score), min_score)
    risk_pct = round(((max_score - score) / (max_score - min_score)) * 100)
    if risk_pct < 25:
        status = "safe"
    elif risk_pct < 70:
        status = "caution"
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
        "status": status,
        "message": message,
        "risk_pct": risk_pct,
        "score": score,
        "reasons": reasons,
        "is_www_only": is_www_only,
        "is_www_protocol": is_www_protocol,
        "is_https": is_https,
        "is_http": is_http,
        "ssl_valid": ssl_status,
        "domain_age": domain_age,
        "keywords_found": keyword_hits,
        "young_domain": is_young,
        "is_ip_address": is_ip,
        "registrar": domain_info["registrar"],
        "country": domain_info["country"],
        "creation_date": domain_info["creation_date"],
        "expiration_date": domain_info["expiration_date"],
    }
    return jsonify(response)  #sends the results back to the browser in a js format



if __name__ == '__main__':
    app.run(debug=True)