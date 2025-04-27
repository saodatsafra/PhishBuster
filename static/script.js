document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('link-form');
    const spinner = document.getElementById('spinner');
    const resultDiv = document.getElementById('result');
    const statusHeader = document.getElementById('main-status');
    const mainIcon = document.getElementById('main-icon');
    const detailsPara = document.getElementById('details');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        spinner.style.display = "block";
        resultDiv.style.display = "none";
        statusHeader.textContent = "";
        mainIcon.textContent = "";
        detailsPara.innerHTML = "";

        const link = document.getElementById('link-input').value;

        const response = await fetch('/check_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ link }),
        });

        const result = await response.json();
        spinner.style.display = "none";
        resultDiv.style.display = "block";

        // Set main status and icon
        if (result.status === "safe") {
            statusHeader.textContent = "The link is safe!";
            statusHeader.style.color = "green";
            mainIcon.textContent = "🟢";
        } else if (result.status === "might not be safe") {
            statusHeader.textContent = "The link might not be safe!";
            statusHeader.style.color = "orange";
            mainIcon.textContent = "🟠";
        } else {
            statusHeader.textContent = "The link is dangerous!";
            statusHeader.style.color = "red";
            mainIcon.textContent = "🔴";
        }

        // Friendly details for the user
        let details = "";

        if (result.status =="error") {
            statusHeader.textContent = "Invalid link",
                statusHeader.style.color = "red";
            mainIcon.textContent = "⚠️",
                detailsPara.innerHTML = result.message + "<br>Please provide the full link, like https://example.com";
            return;
        }


        // Main message
        if (result.status === "safe") {
            details += "🎉 This link looks safe.<br>";
        } else if (result.status === "might not be safe") {
            details += "⚠️ Please be careful. Some things look suspicious.<br>";
        } else {
            details += "🚨 This link is dangerous. Do NOT enter personal information.<br>";
        }

        // HTTPS/HTTP info
        if (result.is_https) {
            details += "✅ Secure connection (HTTPS).<br>";
        } else if (result.is_http) {
            details += "❌ Not secure (HTTP).<br>";
        }

        // SSL certificate
        if (result.ssl_valid === true) {
            details += "✅ SSL certificate is valid.<br>";
        } else if (result.ssl_valid === false) {
            details += "❌ SSL certificate is NOT valid.<br>";
        } else {
            details += "⚠️ Couldn't check the site's security certificate.<br>";
        }

        // Domain age
        if (result.domain_age !== null) {
            if (result.young_domain) {
                details += "🚨 This website is very new. Be extra careful.<br>";
            } else {
                details += `🌍 Website age: ${result.domain_age} years. Older sites are usually safer.<br>`;
            }
        } else {
            details += "⚠️ Can't find out how old this site is.<br>";
        }

        // Suspicious keywords
        if (result.keywords_found && result.keywords_found.length > 0) {
            details += `🚩 Suspicious words found: ${result.keywords_found.join(', ')}.<br>`;
        } else {
            details += "✅ No suspicious words found in the link.<br>";
        }

        // IP address check
        if (result.is_ip_address) {
            details += "⚠️ This link uses numbers instead of a name. Be extra careful.<br>";
        } else {
            details += "✅ This link uses a normal website name.<br>";
        }

        // 'www.' with or without protocol
        if (result.is_www_only) {
            details += "⚠️ Link is missing 'http' or 'https'.<br>";
        } else if (result.is_www_protocol) {
            details += "ℹ️ This link uses 'www.' which is normal for many sites.<br>";
        }

        detailsPara.innerHTML = details;
    });
});