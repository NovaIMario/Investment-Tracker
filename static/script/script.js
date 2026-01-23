async function loadChart() {
    const response = await fetch("/data");
    const data = await response.json();

    const ctx = document.getElementById("moneyChart").getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: data.dates,
            datasets: [{
                label: "Money Over Time",
                data: data.amounts,
                tension: 0.2
            }]
        }
    });
}

loadChart();
