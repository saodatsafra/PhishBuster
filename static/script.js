document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('link-form');
    const resultDiv = document.getElementById('result');

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

        let message = result.message;


        // Display SSL status
        if (result.ssl_valid === true) {
            message += " ✅ SSL Certificate is valid.";
        } else if (result.ssl_valid === false) {
            message += " ❌ SSL Certificate is NOT valid.";
        } else {
            message += " ⚠️ SSL status could not be determined.";
        }

        // Display domain age
        if (result.domain_age !== null) {
            message += ` 🌍 Domain age: ${result.domain_age} years.`;
        } else {
            message += " ⚠️ Unable to retrieve domain age.";
        }

        resultDiv.style.color = result.status === "safe" ? "green" : "orange";
        resultDiv.textContent = message;
    });
});