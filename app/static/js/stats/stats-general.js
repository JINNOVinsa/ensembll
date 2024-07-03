const currDate = new Date();
const currH = (currDate).getHours();
const currD = (currDate).getDay();
const currM = (currDate).getMonth();

async function fetchData(url, from_timestamp, to_timestamp) {
    let response = await fetch(url + "?" + new URLSearchParams({'from': from_timestamp, 'to': to_timestamp}));
    if (response.status != 200) {
        return null;
    }
    return await response.json();
}

function createChart(parent, labels, data, data_label) {
    return new Chart(parent, {
        type: 'bar',
        data: {
            labels: labels,   // Past 24 hours
            datasets: [{
                label: data_label,
                data: data,
                borderWidth: 1,
                onclick: null
            }]
        },
        options: {
            plugins: {
                legend: {
                  display: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}