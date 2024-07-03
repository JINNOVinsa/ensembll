var parkUsageChart = document.getElementById("park-usage-chart");
var parkUsageChart;

fetch("/stats/parkusage").then((response) => {
    if (response.ok) {
        return response.json();
    } else {
        return null;
    }
}).then((data) => {
    if (data === null) {
        console.log("no data");
    } else {
        parkUsageChart = createChart(parkUsageChart, data['labels'], data['data'], '#');
    }
});


