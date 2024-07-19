function getFormatDate(d, region) {
    // Format date given based on region (en or fr)
    switch (region) {
        case "fr":
            return weekdayFr[d.getUTCDay()] + " " + d.getUTCDate() + " " + monthFr[d.getUTCMonth()] + " " + d.getFullYear();

        default:
            return d.getFullYear() + " " + weekdayEn[d.getDay() -1] + ", " + monthEn[d.getMonth()] + " " + d.getUTCDate();
    }
}

function dateAndTimeToDatetime(d, t, region) {
    switch (region) {
        case "fr":
            tokens = d.split(' ');
            return tokens[3] + "-" + (monthFr.indexOf(tokens[2])+1).toLocaleString('en-US', {minimumIntegerDigits:2}) + "-" + parseInt(tokens[1]).toLocaleString('en-US', {minimumIntegerDigits:2}) + " " + t + ":00.000000";
    }
}

var addUserBookingDialog = document.getElementById("add-user-booking-dialog");
var addBookingClose = document.getElementById("close-add-booking-dialog");
var addBookingForm = document.getElementById("add-booking");
var addBookingSubmitBtn = document.getElementById("add-submit-booking");

var addBookingCustomDialog = document.getElementById("add-user-booking-custom-dialog");
var addBookingCustomForm = document.getElementById("add-user-booking-custom");
var addBookingCustomClose = document.getElementById("close-add-booking-custom-dialog");

var addBookingCustomIntervalSelector = document.getElementById("add-custom-recurrence-interval-selector");
addBookingCustomIntervalSelector.value = "day";

var addBookingCustomIntervalWeekWrapper = document.getElementById("add-custom-recurrence-week");

var addBookingDuration = document.getElementById("add-booking-duration");

var weeklyBookingRestrictWarn = document.getElementById("add-weekly-booking-restrict");


var addUserCustomBookingDialog = document.getElementById("add-user-booking-custom-dialog");
var addBookingUserSelector = document.getElementById("add-user-selector");
var addBookingPlateSelector = document.getElementById("add-plate-selector");

var addBookingPeriodSelector = document.getElementById("add-period-selector");
var addBookingDateStart = document.getElementById("add-start-date-picker");
var addBookingDateEnd = document.getElementById("add-end-date-picker");
var addBookingTimeStart = document.getElementById("add-time-start-picker");
var addBookingTimeEnd = document.getElementById("add-time-end-picker");

var addBookingRecurrenceEndWrapper = document.getElementById("add-end-recurrence");
var addBookingRecurrenceEnd = document.getElementById("add-recurrence-end-date-picker");

var bookindIdToDelete = null;

function feedSelector(select, data) {
    for (let i = 0; i < data.length; i++) {
        let option = new Option(data[i], data[i]);
        select.add(option);
    }
}

function fetchUserPlates(usrId) {
    fetch('/adminPannel/fetchUserPlates?' + new URLSearchParams({ 'usrID': usrId }), {
        method: "GET"
    }).then((response) => {
        if (response.ok) {
            return response.json();
        } else {
            return null;
        }
    }).then((data) => {
        if (data == null) {
            return null;
        }
        let selector = addBookingPlateSelector;
        clearSelector(selector);

        if (data.length <= 0) {
            // No plates registered
            selector.add(new Option("Aucune plaque", "None"))
            return;
        }
        feedSelector(selector, data);
    });
}

function feedUserAndPlatesSelector() {
    fetch("/adminPannel/getAllUsers", {
        method: "GET"
    }).then((response) => {
        if (response.ok) {
            return response.json();
        } else {
            return null
        }
    }).then((data) => {
        for (let u of data) {
            let o = document.createElement("option");
            o.value = u["id"];
            o.innerText = u["lastName"] + " " + u["firstName"];
            addBookingUserSelector.appendChild(o);
        }

        fetchUserPlates(addBookingUserSelector.value);
    });
}

function openAddUserBookingDialog() {
    if (typeof addUserBookingDialog.showModal === "function") {
        // Fetch user plates
        feedUserAndPlatesSelector();
        let nowDate = new Date();

        // Set minimum date
        addBookingDateStart.value = getFormatDate(nowDate, "fr");
        addBookingDateStart.min = nowDate.toLocaleDateString("en-ca");

        addBookingDateEnd.value = getFormatDate(nowDate, "fr");
        addBookingDateEnd.min = nowDate.toLocaleDateString("en-ca");
        
        addBookingPeriodSelector.value = "unique";

        // Set time start and end placeholder
        //addBookingTimeStart.value = getFormatTime(nowDate, "en");
        addBookingTimeStart.value = nowDate.toLocaleTimeString("fr-fr", {hour: '2-digit', minute: '2-digit', hour12: false});

        nowDate.setHours(nowDate.getHours() + 1);
        addBookingTimeEnd.value = nowDate.toLocaleTimeString("fr-fr", {hour: '2-digit', minute: '2-digit', hour12: false});

        setDuration();

        nowDate.setMonth(nowDate.getMonth() + 1);
        addBookingRecurrenceEnd.value = getFormatDate(nowDate, "fr");
        addBookingRecurrenceEndWrapper.style.visibility = "hidden";

        // Display the dialog window
        document.body.style.overflow = "hidden";
        addUserBookingDialog.showModal();
    } else {
        console.error("Navigateur non compatible");
    }

}


addBookingUserSelector.addEventListener("change", (e) => {
    fetchUserPlates(e.target.value);
});






function getServer(url) {
    return fetch(url, {
        method: "GET"
    });
}

function clearSelector(select) {
    for (var i = select.options.length-1; i >= 0; i--) {
        select.remove(i);
    }
}

function feedSelector(select, data) {
    for (let i = 0; i < data.length; i++) {
        let option = new Option(data[i], data[i]);
        select.add(option, undefined);
    }
}

async function postBooking(url, data) {
    const response = await fetch(url, {
        method: "POST",
        body: data
    });

    return response.ok;
}

function openBookingCustomDialog() {
    if (typeof addBookingCustomDialog.showModal === "function") {
        let nowDate = new Date();

        //addBookingCustomDateEnd.min = nowDate.toLocaleDateString("en-ca");

        nowDate.setMonth(nowDate.getMonth()+3)
        //addBookingCustomDateEnd.value = getFormatDate(nowDate, "fr");

        //if (addBookingCustomNeverEndRadio.checked) {
        //    addBookingCustomDateEnd.style.color = "lightgrey";
        //}
        document.body.style.overflow = "hidden";
        addBookingCustomDialog.showModal();


    } else {
        console.log("Navigateur non compatible");
    }
}

function setDuration() {
    let start = new Date(dateAndTimeToDatetime(addBookingDateStart.value, addBookingTimeStart.value, "fr"))
    let end = new Date(dateAndTimeToDatetime(addBookingDateEnd.value, addBookingTimeEnd.value, "fr"));
    let days = Math.floor((end-start)/(24*3600*1000));
    let hours = Math.floor(((end-start)-days*24*3600*1000)/(3600*1000));
    let mins = Math.floor(((end-start)-days*24*3600*1000-hours*3600*1000)/(60*1000));

    if (isNaN(days) || isNaN(hours) || isNaN(mins)) {
        addBookingDuration.innerText = `0j 0h0mins`;
    } else {
        addBookingDuration.innerText = `${days}j ${hours}h${mins}mins`;
    }
}

function checkValidBooking() {
    let inputs = addBookingForm.elements;

    let datetimeStart = dateAndTimeToDatetime(inputs["booking-date-start"].value, inputs["booking-time-start"].value, "fr");
    let dateTimeEnd = dateAndTimeToDatetime(inputs["booking-date-end"].value, inputs["booking-time-end"].value, "fr");

    let ddS = new Date(datetimeStart);
    let ddE = new Date(dateTimeEnd);

    let dEnd = new Date(dateAndTimeToDatetime(inputs["recurrence-booking-date-end"].value, "00:00", "fr"));

    if (ddS.getTime() >= ddE.getTime() || (addBookingPeriodSelector.value != "unique" && dEnd.getTime() <= ddE.getTime())) {
        addBookingSubmitBtn.setAttribute("disabled", "true");
    } else {
        addBookingSubmitBtn.removeAttribute("disabled");
    }
}

async function getBookingDataAndPost() {
    let inputs = addBookingForm.elements;
    let usr = inputs['user'].value;
    let plate = inputs['plate'].value;
    let datetimeStart = dateAndTimeToDatetime(inputs["booking-date-start"].value, inputs["booking-time-start"].value, "fr");
    let dateTimeEnd = dateAndTimeToDatetime(inputs["booking-date-end"].value, inputs["booking-time-end"].value, "fr");

    let ddS = new Date(datetimeStart);
    let ddE = new Date(dateTimeEnd);

    if (ddS.getTime() === ddE.getTime() || ddE < ddS) {
        // Invalid datetimes
        document.body.style.overflow = "visible";
        addUserBookingDialog.close();
        openBookingDialog();
    } else {
        let data = new FormData();
        data.set("usrId", usr);
        data.set("plate", plate);
        data.set("booking-start", datetimeStart);
        data.set("booking-end", dateTimeEnd);

        let interval = inputs['interval'].value
        data.set("interval", interval);

        if (interval != 'unique') {
            data.set('ending', dateAndTimeToDatetime(addBookingRecurrenceEnd.value, "00:00", "fr"));
        } else {
            data.set('ending', dateTimeEnd);
        }

        if (interval == 'custom') {
            let customInputs = addBookingCustomForm.elements;

            data.set('customInterval', customInputs['custom-interval'].value);
            data.set('customAmount', customInputs['custom-recurrence-amount'].value);

            data.set('monday', customInputs['monday'].checked);
            data.set('tuesday', customInputs['tuesday'].checked);
            data.set('wednesday', customInputs['wednesday'].checked);
            data.set('thursday', customInputs['thursday'].checked);
            data.set('friday', customInputs['friday'].checked);
            data.set('saturday', customInputs['saturday'].checked);
            data.set('sunday', customInputs['sunday'].checked);
        }

        return await postBooking(addBookingForm.action, data);
    }
}

document.getElementById("add-user-booking").addEventListener("click", (e) => {
    openAddUserBookingDialog();
});

addBookingTimeStart.addEventListener('input', () => {
    setDuration();
    checkValidBooking();
});

addBookingTimeEnd.addEventListener('input', () => {
    setDuration();
    checkValidBooking();
})

addBookingForm.addEventListener('submit', (e) => {
    e.preventDefault();
    addBookingForm.querySelector("button#add-submit-booking").disabled = true;
    (async () => {
    result = await getBookingDataAndPost();
        addBookingForm.querySelector("button#add-submit-booking").disabled = false;
        if (!result) {
            document.getElementById("add-booking-failed").showModal();
        } else {
            location.href = "/adminPannel/bookings";
        }
    })();
});

addBookingClose.addEventListener('click', () => {
    document.body.style.overflow = "visible";
    addUserBookingDialog.close();
});

addBookingPeriodSelector.addEventListener("change", (e) => {
    if (e.target.value != "unique") {
        addBookingRecurrenceEndWrapper.style.visibility = "visible";
    } else {
        addBookingRecurrenceEndWrapper.style.visibility = "hidden";
    }
    
    if (e.target.value == "custom") {
        openBookingCustomDialog();
    }

    if (e.target.value == "weekly") {
        addBookingDateEnd.value = addBookingDateStart.value;
    }

    setDuration();
    checkValidBooking();
});

addBookingCustomIntervalSelector.addEventListener("change", (e) => {
    if (e.target.value === 'week') {
        addBookingCustomIntervalWeekWrapper.style.display = "flex";
        addBookingDateEnd.value = addBookingDateStart.value;
    } else {
        addBookingCustomIntervalWeekWrapper.style.display = "none";
    }

    setDuration();
    checkValidBooking();
});

addBookingCustomClose.addEventListener("click", () => {
    document.body.style.overflow = "visible";
    addBookingCustomDialog.close();
    addBookingPeriodSelector.value = "unique";  // Reset selector if close whithout submitting
    addBookingRecurrenceEndWrapper.style.visibility = "hidden";
});

document.getElementById("add-date-start-label").addEventListener("click", () => {

    if (addBookingPeriodSelector.value !== "custom" || addBookingCustomIntervalSelector.value !== "week") {
        addBookingDateStart.removeAttribute('readonly');
        addBookingDateStart.type = "date";
        addBookingDateStart.showPicker();
    } else {
        weeklyBookingRestrictWarn.style.visibility = "visible";
        weeklyBookingRestrictWarn.style.opacity = "1";
        setTimeout(() => {
            weeklyBookingRestrictWarn.style.opacity = "0";
            weeklyBookingRestrictWarn.style.visibility = "hidden";
        }, 5000);
    }
});

document.getElementById("add-date-end-label").addEventListener("click", () => {
    if (addBookingPeriodSelector.value !== "custom" || addBookingCustomIntervalSelector.value !== "week") {
        addBookingDateEnd.removeAttribute('readonly');
        addBookingDateEnd.type = "date";
        addBookingDateEnd.showPicker();
    } else {
        weeklyBookingRestrictWarn.style.visibility = "visible";
        weeklyBookingRestrictWarn.style.opacity = "1";
        setTimeout(() => {
            weeklyBookingRestrictWarn.style.opacity = "0";
            weeklyBookingRestrictWarn.style.visibility = "hidden";
        }, 5000);
    }
});

document.getElementById("add-recurrence-date-end-label").addEventListener("click", () => {
    addBookingRecurrenceEnd.removeAttribute('readonly');
    addBookingRecurrenceEnd.type = "date";
    addBookingRecurrenceEnd.showPicker();
});

addBookingDateStart.addEventListener("change", (e) => {
    let selectedDate = new Date(e.target.value);
    e.target.type = "text";
    e.target.value = getFormatDate(selectedDate, "fr");
    addBookingDateStart.setAttribute('readonly', true);

    if (addBookingPeriodSelector.value === "weekly") {
        addBookingDateEnd.value = addBookingDateStart.value;
    }

    setDuration();
    checkValidBooking();
});

addBookingDateEnd.addEventListener("change", (e) => {
    let selectedDate = new Date(e.target.value);
    e.target.type = "text";
    e.target.value = getFormatDate(selectedDate, "fr");
    addBookingDateEnd.setAttribute('readonly', true);

    if (addBookingPeriodSelector.value === "weekly") {
        addBookingDateStart.value = addBookingDateEnd.value;
    }
    
    setDuration();
    checkValidBooking();
});

addBookingCustomIntervalSelector.addEventListener("change", (e) => {
    if (e.target.value === 'week') {
        addBookingCustomIntervalWeekWrapper.style.display = "flex";
        addBookingDateEnd.value = addBookingDateStart.value;
    } else {
        addBookingCustomIntervalWeekWrapper.style.display = "none";
    }

    setDuration();
    checkValidBooking();
});

addBookingRecurrenceEnd.addEventListener("change", (e) => {
    let selectedDate = new Date(e.target.value);
    e.target.type = "text";
    e.target.value = getFormatDate(selectedDate, "fr");
    addBookingRecurrenceEnd.setAttribute('readonly', true);

    checkValidBooking();
});

addBookingCustomForm.addEventListener("submit", (e) => {
    if (addBookingCustomIntervalSelector.value == "week") {
        let nd = new Date();
        let d = new Date();
        let candidates = [];
        if (addBookingCustomIntervalWeekWrapper.querySelector("#add-custom-monday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 1 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#add-custom-tuesday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 2 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#add-custom-wednesday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 3 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#add-custom-thursday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 4 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#add-custom-friday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 5 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#add-custom-saturday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 6 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#add-custom-sunday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 7 - nd.getUTCDay()) % 7)));
        }
        addBookingDateStart.value = getFormatDate(new Date(Math.min.apply(null,candidates)), 'fr');
        addBookingDateEnd.value = getFormatDate(new Date(Math.min.apply(null,candidates)), 'fr');
    }
})

