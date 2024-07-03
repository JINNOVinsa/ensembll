const realFillRate = document.getElementById("real-fill-rate-chart");

var startDateRealFillRate = document.getElementById("real-fill-rate-start-date");
var endDateRealFillRate = document.getElementById("real-fill-rate-end-date");
var changePeriodRealFillRateForm = document.getElementById("real-fill-rate-change-period");

function getDateFromRealInputs(inputs) {
    let selectedStartDate = inputs["real-fill-rate-start-date"].value.split('/');
    let startDate = new Date(selectedStartDate[2], selectedStartDate[1] - 1, selectedStartDate[0]);
    if (startDate === null) {
        inputs["real-fill-rate-start-date"].style.borderBottomColor = "var(--invalid-red)";
        return null;
    }


    let startTime = inputs["real-fill-rate-start-time"].value.split(':');
    if (startTime.length != 2) {
        inputs["real-fill-rate-start-time"].style.borderBottomColor = "var(--invalid-red)";
        return null;
    }
    startDate = new Date(startDate.setHours(startTime[0]));
    startDate = new Date(startDate.setMinutes(startTime[1]));

    let selectedEndDate = inputs["real-fill-rate-end-date"].value.split('/');
    let endDate = new Date(selectedEndDate[2], selectedEndDate[1] - 1, selectedEndDate[0]);
    if (endDate === null) {
        inputs["real-fill-rate-end-date"].style.borderBottomColor = "var(--invalid-red)";
        return null;
    }


    let endTime = inputs["real-fill-rate-end-time"].value.split(':');
    if (endTime.length != 2) {
        inputs["real-fill-rate-end-time"].style.borderBottomColor = "var(--invalid-red)";
        return null;
    }
    endDate = new Date(endDate.setHours(endTime[0]));
    endDate = new Date(endDate.setMinutes(endTime[1]));
    return [startDate, endDate]
}

var realFillRateChart;
var realFillRateRadios = document.getElementsByClassName("real-fill-rate-radio");
var prevRealFillRateRadio;
var realFillRateUnit = "hourly";
for (var i = 0; i < realFillRateRadios.length; i++) {
    realFillRateRadios[i].addEventListener("change", async (e) => {
        if (e.target === prevRealFillRateRadio) {
            return;
        }

        prevRealFillRateRadio = e.target;
        realFillRateUnit = e.target.value;

        // Get dates
        let dates = getDateFromRealInputs(changePeriodRealFillRateForm.elements);

        if (dates === null) {
            return;
        }

        changePeriodRealFillRateForm.elements["real-fill-rate-start-date"].style.borderBottomColor = "var(--main-blue)"
        changePeriodRealFillRateForm.elements["real-fill-rate-end-date"].style.borderBottomColor = "var(--main-blue)"
        changePeriodRealFillRateForm.elements["real-fill-rate-start-time"].style.borderBottomColor = "var(--main-blue)"
        changePeriodRealFillRateForm.elements["real-fill-rate-end-time"].style.borderBottomColor = "var(--main-blue)"

        let startDate = dates[0];
        let endDate = dates[1];
        
        if (realFillRateChart !== undefined) {
            realFillRateChart.destroy();
        }

        let data = await fetchData("/stats/realfillrate/"+realFillRateUnit, startDate.getTime() / 1000, endDate.getTime() / 1000);
        if (data === null) {
            console.log("no data");
        } else {
            realFillRateChart = createChart(realFillRate, data['labels'], data['data'], 'Previsionnel/Réel');
        }
    });
}

startDateRealFillRate.addEventListener("click", (e) => {
    e.target.type = "date";
    e.target.showPicker();
    e.target.showPicker();
});

startDateRealFillRate.addEventListener("change", (e) => {
    e.target.type = "text";

    let date = e.target.value.split('-');
    e.target.value = date[2] + "/" + date[1] + "/" + date[0];
});

endDateRealFillRate.addEventListener("click", (e) => {
    e.target.type = "date";
    e.target.showPicker();
    e.target.showPicker();
});

endDateRealFillRate.addEventListener("change", (e) => {
    e.target.type = "text";

    let date = e.target.value.split('-');
    e.target.value = date[2] + "/" + date[1] + "/" + date[0];
});

changePeriodRealFillRateForm.addEventListener("submit", (e) => {
    e.preventDefault();
    let inputs = e.target.elements;

    let dates = getDateFromRealInputs(inputs);

    if (dates === null) {
        return;
    }

    let startDate = dates[0];
    let endDate = dates[1];

    changePeriodRealFillRateForm.elements["real-fill-rate-start-date"].style.borderBottomColor = "var(--main-blue)"
    changePeriodRealFillRateForm.elements["real-fill-rate-end-date"].style.borderBottomColor = "var(--main-blue)"
    changePeriodRealFillRateForm.elements["real-fill-rate-start-time"].style.borderBottomColor = "var(--main-blue)"
    changePeriodRealFillRateForm.elements["real-fill-rate-end-time"].style.borderBottomColor = "var(--main-blue)"

    fetchData("/stats/realfillrate/" + realFillRateUnit, startDate.getTime() / 1000, endDate.getTime() / 1000).then((data) => {
        if (data === null) {
            console.log("No data");
        } else {
            if (realFillRateChart !== undefined) {
                realFillRateChart.destroy();
            }
            realFillRateChart = createChart(realFillRate, data['labels'], data['data'], 'Previsionnel/Réel');
        }
    });
});

function firstDisplayRealFillRate() {
    document.getElementById("real-fill-rate-hourly").checked = true;
    let dateMinusOneDay = new Date((new Date()).setDate(currDate.getDate() - 1));
    startDateRealFillRate.value = dateMinusOneDay.toLocaleDateString('en-GB');
    endDateRealFillRate.value = currDate.toLocaleDateString('en-GB');

    let dates = getDateFromRealInputs(changePeriodRealFillRateForm.elements);

    if (dates === null) {
        return;
    }

    let startDate = dates[0];
    let endDate = dates[1];

    changePeriodRealFillRateForm.elements["real-fill-rate-start-date"].style.borderBottomColor = "var(--main-blue)"
    changePeriodRealFillRateForm.elements["real-fill-rate-end-date"].style.borderBottomColor = "var(--main-blue)"
    changePeriodRealFillRateForm.elements["real-fill-rate-start-time"].style.borderBottomColor = "var(--main-blue)"
    changePeriodRealFillRateForm.elements["real-fill-rate-end-time"].style.borderBottomColor = "var(--main-blue)"

    fetchData("/stats/realfillrate/hourly", Math.floor(startDate.getTime() / 1000), Math.floor(endDate.getTime() / 1000)).then((data) => {
        if (data === null) {
            console.log("No data");
        } else {
            if (realFillRateChart !== undefined) {
                realFillRateChart.destroy();
            }
            realFillRateChart = createChart(realFillRate, data['labels'], data['data'], 'Previsionnel/Réel');
        }
    });
}

firstDisplayRealFillRate();