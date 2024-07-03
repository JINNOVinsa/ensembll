const fillRate = document.getElementById("fill-rate-chart");

var changePeriodFillRateForm = document.getElementById("fill-rate-change-period");
var startDateFillRate = document.getElementById("fill-rate-start-date");
var endDateFillRate = document.getElementById("fill-rate-end-date");

function getDateFromInputs(inputs) {
    let selectedStartDate = inputs["fill-rate-start-date"].value.split('/');
    let startDate = new Date(selectedStartDate[2], selectedStartDate[1] - 1, selectedStartDate[0]);
    if (startDate === null) {
        inputs["fill-rate-start-date"].style.borderBottomColor = "var(--invalid-red)";
        return null;
    }


    let startTime = inputs["fill-rate-start-time"].value.split(':');
    if (startTime.length != 2) {
        inputs["fill-rate-start-time"].style.borderBottomColor = "var(--invalid-red)";
        return null;
    }
    startDate = new Date(startDate.setHours(startTime[0]));
    startDate = new Date(startDate.setMinutes(startTime[1]));

    let selectedEndDate = inputs["fill-rate-end-date"].value.split('/');
    let endDate = new Date(selectedEndDate[2], selectedEndDate[1] - 1, selectedEndDate[0]);
    if (endDate === null) {
        inputs["fill-rate-end-date"].style.borderBottomColor = "var(--invalid-red)";
        return null;
    }


    let endTime = inputs["fill-rate-end-time"].value.split(':');
    if (endTime.length != 2) {
        inputs["fill-rate-end-time"].style.borderBottomColor = "var(--invalid-red)";
        return null;
    }
    endDate = new Date(endDate.setHours(endTime[0]));
    endDate = new Date(endDate.setMinutes(endTime[1]));
    return [startDate, endDate]
}

// Setup for fill rate chart
var fillRateChart;
var fillRateRadios = document.getElementsByClassName("fill-rate-radio");
var prevFillRateRadio;
var fillRateUnit = "hourly";
for (var i = 0; i < fillRateRadios.length; i++) {
    fillRateRadios[i].addEventListener("change", async (e) => {
        if (e.target === prevFillRateRadio) {
            return;
        }

        prevFillRateRadio = e.target;
        fillRateUnit = e.target.value;  // hourly, daily, ...
        // Get dates
        let dates = getDateFromInputs(changePeriodFillRateForm.elements);
        if (dates === null) {
            return;
        }
        changePeriodFillRateForm.elements["fill-rate-start-date"].style.borderBottomColor = "var(--main-blue)"
        changePeriodFillRateForm.elements["fill-rate-end-date"].style.borderBottomColor = "var(--main-blue)"
        changePeriodFillRateForm.elements["fill-rate-start-time"].style.borderBottomColor = "var(--main-blue)"
        changePeriodFillRateForm.elements["fill-rate-end-time"].style.borderBottomColor = "var(--main-blue)"
        let startDate = dates[0];
        let endDate = dates[1];
        if (fillRateChart !== undefined) {
            fillRateChart.destroy();
        }

        let data = await fetchData("/stats/fillrate/" + e.target.value, startDate.getTime() / 1000, endDate.getTime() / 1000);
        if (data === null) {
            console.log("no data");
        } else {
            fillRateChart = createChart(fillRate, data['labels'], data['data'], '%');
        }


    });
}

startDateFillRate.addEventListener("click", (e) => {
    e.target.type = "date";
    e.target.showPicker();
    e.target.showPicker();
});

startDateFillRate.addEventListener("change", (e) => {
    e.target.type = "text";

    let date = e.target.value.split('-');
    e.target.value = date[2] + "/" + date[1] + "/" + date[0];
});

endDateFillRate.addEventListener("click", (e) => {
    e.target.type = "date";
    e.target.showPicker();
    e.target.showPicker();
});

endDateFillRate.addEventListener("change", (e) => {
    e.target.type = "text";

    let date = e.target.value.split('-');
    e.target.value = date[2] + "/" + date[1] + "/" + date[0];
});

changePeriodFillRateForm.addEventListener("submit", (e) => {
    e.preventDefault();
    let inputs = e.target.elements;

    let dates = getDateFromInputs(inputs);
    if (dates === null) {
        return;
    }

    let startDate = dates[0];
    let endDate = dates[1];

    changePeriodFillRateForm.elements["fill-rate-start-date"].style.borderBottomColor = "var(--main-blue)"
    changePeriodFillRateForm.elements["fill-rate-end-date"].style.borderBottomColor = "var(--main-blue)"
    changePeriodFillRateForm.elements["fill-rate-start-time"].style.borderBottomColor = "var(--main-blue)"
    changePeriodFillRateForm.elements["fill-rate-end-time"].style.borderBottomColor = "var(--main-blue)"
    fetchData("/stats/fillrate/" + fillRateUnit, startDate.getTime() / 1000, endDate.getTime() / 1000).then((data) => {
        if (data === null) {
            console.log("No data");
        } else {
            if (fillRateChart !== undefined) {
                fillRateChart.destroy();
            }
            fillRateChart = createChart(fillRate, data['labels'], data['data'], '%');
        }
    });
});

document.getElementById("fill-rate-hourly").checked = true;
let dateMinusOneDay = new Date((new Date()).setDate(currDate.getDate() - 1));
startDateFillRate.value = dateMinusOneDay.toLocaleDateString('en-GB');
endDateFillRate.value = currDate.toLocaleDateString('en-GB');

let dates = getDateFromInputs(changePeriodFillRateForm.elements);
let startDate = dates[0];
let endDate = dates[1];
fetchData("/stats/fillrate/hourly", Math.floor(startDate.getTime() / 1000), Math.floor(endDate.getTime() / 1000)).then((data) => {
    if (data === null) {
        console.log("No data");
    } else {
        fillRateChart = createChart(fillRate, data['labels'], data['data'], '%');
    }
});
