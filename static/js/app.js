document.getElementById("travel-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const origin = document.getElementById("origin").value;
    const dates = document.getElementById("dates").value;
    const preferences = document.getElementById("preferences").value;
    const budget = document.getElementById("budget").value;

    const response = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ origin, dates, preferences, budget })
    });

    const data = await response.json();
    document.getElementById("recommendations").innerHTML = `
        <h3>Flight Options:</h3>
        <pre>${JSON.stringify(data.flightOptions, null, 2)}</pre>
        <h3>Recommendations:</h3>
        <pre>${JSON.stringify(data.recommendations, null, 2)}</pre>
    `;
});