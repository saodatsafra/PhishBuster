document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('link-form');
    const resultDiv = document.getElementById('result');
    const statusHeader = document.getElementById('main-status');
    const detailsPara = document.getElementById('details');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const link = document.getElementById('link-input').value;

        const response = await fetch('/check_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ link }),
        });

        const result = await response.json();

        // Set main status message and color
        if (result.status === "safe") {
            statusHeader.textContent = "The link is safe!";
            statusHeader.style.color = "green";
        } else if (result.status === "might not be safe") {
            statusHeader.textContent = "The link might not be safe!";
            statusHeader.style.color = "orange";
        } else {
            statusHeader.textContent = "The link is dangerous!";
            statusHeader.style.color = "red";
        }

        // Build details message
        let details = "";
        details += result.message + "<br>";

        if (result.ssl_valid === true) {
            details += "✅ SSL Certificate is valid.<br>";
        } else if (result.ssl_valid === false) {
            details += "❌ SSL Certificate is NOT valid.<br>";
        } else {
            details += "⚠️ SSL status could not be determined.<br>";
        }

        if (result.domain_age !== null) {
            details += `🌍 Domain age: ${result.domain_age} years.<br>`;
        } else {
            details += "⚠️ Unable to retrieve domain age.<br>";
        }

        if (result.young_domain === true) {
            details += "🚨 Domain is very new — might be suspicious.<br>";
        }

        if (result.keywords_found && result.keywords_found.length > 0) {
            details += `🚩 Suspicious keywords in link: ${result.keywords_found.join(', ')}.<br>`;
        } else {
            details += "✅ No suspicious keywords found in the link.<br>";
        }

        if (result.is_ip_address) {
            details += "⚠️ Link uses an IP address instead of a domain — might be suspicious.<br>";
        } else {
            details += "✅ The link uses a normal domain name (not an IP).<br>";
        }

        details += `🧮 Final Score: ${result.score}/8`;

        // Display all messages
        detailsPara.innerHTML = details;
    });
});
