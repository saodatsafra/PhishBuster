
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('link-form');
    const spinner = document.getElementById('spinner');
    const resultDiv = document.getElementById('result');
    const statusHeader = document.getElementById('main-status');
    const mainIcon = document.getElementById('main-icon');
    const detailsPara = document.getElementById('details');
    let riskBar = document.getElementById('risk-bar');

    if (!riskBar) {
        riskBar = document.createElement('div');
        riskBar.id = 'risk-bar';
        riskBar.style.height = '18px';
        riskBar.style.width = '100%';
        riskBar.style.margin = '12px 0 16px 0';
        riskBar.style.borderRadius = '5px';
        riskBar.style.display = 'none';
        riskBar.style.position = 'relative';
        resultDiv.insertBefore(riskBar, detailsPara);
    }

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        spinner.style.display = "block";
        resultDiv.style.display = "none";
        statusHeader.textContent = "";
        mainIcon.textContent = "";
        detailsPara.innerHTML = "";
        riskBar.style.display = "none";
        riskBar.innerHTML = "";

        const link = document.getElementById('link-input').value;
        const response = await fetch('/check_link', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', },
            body: JSON.stringify({ link }),
        });

        const result = await response.json();
        spinner.style.display = "none";
        resultDiv.style.display = "block";

        // --- Error Case ---
        if (result.status === "error") {
            statusHeader.textContent = "Invalid link";
            statusHeader.style.color = "red";
            mainIcon.textContent = "⚠️";
            detailsPara.innerHTML = result.message + "<br>Please provide the full link, like https://example.com";
            riskBar.style.display = "none";
            riskBar.innerHTML = "";
            return;
        }

        // --- Top Bar/Status ---
        if (result.status === "safe") {
            statusHeader.textContent = "SAFE: No major phishing signs detected.";
            statusHeader.style.color = "#15803d";
            mainIcon.textContent = "🟢";
        } else if (result.status === "caution") {
            statusHeader.textContent = "CAUTION: Potential risk factors detected!";
            statusHeader.style.color = "#eab308";
            mainIcon.textContent = "🟠";
        } else {
            statusHeader.textContent = "DANGEROUS: Multiple high-risk features detected!";
            statusHeader.style.color = "#dc2626";
            mainIcon.textContent = "🔴";
        }

        // --- Risk Bar ---
        riskBar.style.display = "block";
        const pct = Math.min(Math.max(result.risk_pct, 0), 100); // clamp 0-100
        let barColor = "#19c37d"; // green
        if (pct >= 70) barColor = "#ff4545";
        else if (pct >= 25) barColor = "#ffc107";
        riskBar.style.background = `linear-gradient(to right, ${barColor} ${pct}%, #e2e6ea ${pct}%)`;
        riskBar.innerHTML = "";

        // --- Section 1: Technical Summary ---
        let details = `<div style="font-size:1.08em; margin-bottom:11px;"><b>Technical Analysis Summary:</b> `;
        if (result.status === "safe") {
            details += "No significant phishing indicators detected. Link appears to be low risk based on analyzed factors.";
        } else if (result.status === "caution") {
            details += "Some technical indicators suggest potential risk. Review technical details below.";
        } else {
            details += "Severe risk factors present! Treat this link as highly suspicious. Avoid entering credentials.";
        }
        details += "</div>";

        // --- Section 2: Ordered Risk Factors ---
        if (result.reasons && result.reasons.length > 0) {
            details += `<div style="margin-bottom:11px;">
            <b>Detected Risk Factors:</b>
            <ul style="color:#b22222; margin-top:5px;">`;
            for (const reason of result.reasons) {
                details += `<li>${reason}</li>`;
            }
            details += "</ul></div>";
        }

        // --- Section 3: Technical Scan Details ---
        details += `<div style="margin-bottom:11px;"><b>Technical Scan Details:</b><ul>`;
        details += `<li>Protocol: ${result.is_https ? "HTTPS (encrypted)" : result.is_http ? "HTTP (unencrypted)" : "Unknown"}</li>`;
        details += `<li>SSL Certificate: ${result.ssl_valid === true ? "Valid" : result.ssl_valid === false ? "Invalid/Failed" : "Not checked"}</li>`;
        if (result.domain_age !== null) {
            details += `<li>Domain Age: ${result.domain_age} year(s)</li>`;
            if (result.young_domain) details += `<li><b>Warning:</b> Domain is less than 1 year old</li>`;
        } else {
            details += `<li>Domain Age: Unknown</li>`;
        }
        if (result.keywords_found && result.keywords_found.length > 0) {
            details += `<li>Suspicious Keywords: <b>${result.keywords_found.join(', ')}</b></li>`;
        }
        if (result.is_ip_address) {
            details += `<li>Domain is a raw IP address (suspicious)</li>`;
        }
        if (result.is_www_only) {
            details += `<li>Missing protocol (http/https)</li>`;
        }
        details += `</ul></div>`;

        // --- Section 4: Risk Score (Technical Explanation) ---
        details += `<div style="margin-bottom:12px;">
            <b>Calculated Risk Percentage:</b> <span style="color:${barColor};font-weight:700;">${pct}%</span><br>
            <small style="color:#7d8591;">
                This score is calculated based on the presence of suspicious technical features (see above), including SSL, domain age, protocol, keywords, top-level domain, subdomains, and URL structure.
            </small>
        </div>`;

        // --- Section 5: WHOIS Registration Info ---
        details += `<hr><strong>Domain Registration Info:</strong><br>`;
        details += `<div style="margin-left:7px;line-height:1.9">`;
        details += `🌐 Registrar: <b>${result.registrar ? result.registrar : "Unknown"}</b><br>`;
        details += `🏳️ Country: <b>${result.country ? result.country : "Unknown"}</b><br>`;
        details += `📅 Created: <b>${result.creation_date ? result.creation_date : "Unknown"}</b><br>`;
        details += `⏳ Expires: <b>${result.expiration_date ? result.expiration_date : "Unknown"}</b><br>`;
        details += `</div>`;

        detailsPara.innerHTML = details;
    });
});
