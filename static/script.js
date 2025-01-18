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

        if (result.status === 'safe') {
            resultDiv.style.color = 'green';
        } else if (result.status === 'warning') {
            resultDiv.style.color = 'orange';
        } else {
            resultDiv.style.color = 'red';
        }

        resultDiv.textContent = result.message;
    });
});
