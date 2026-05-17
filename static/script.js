async function loadChart() {
    const response = await fetch("/data");
    const data = await response.json();

    const ctx = document.getElementById("moneyChart").getContext("2d");

    // colour line green if going up, red if going down
    const amounts = data.amounts;
    const trend = amounts.length > 1 && amounts[amounts.length-1] >= amounts[0];
    const lineColor = trend ? "#4caf7d" : "#e05555";
    const fillColor = trend ? "rgba(76,175,125,0.06)" : "rgba(224,85,85,0.06)";

    new Chart(ctx, {
        type: "line",
        data: {
            labels: data.dates,
            datasets: [{
                label: "Portfolio Value",
                data: data.amounts,
                borderColor: lineColor,
                backgroundColor: fillColor,
                borderWidth: 2,
                pointRadius: 4,
                pointBackgroundColor: lineColor,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    ticks: {
                        color: "#5a5a6a",
                        font: { family: "DM Mono", size: 11 },
                        maxTicksLimit: 8,
                        maxRotation: 0
                    },
                    grid: { color: "#1c1c22" }
                },
                y: {
                    beginAtZero: false,
                    ticks: {
                        color: "#5a5a6a",
                        font: { family: "DM Mono", size: 11 },
                        callback: val => "£" + val.toLocaleString()
                    },
                    grid: { color: "#1c1c22" }
                }
            }
        }
    });
}

loadChart();