var table = document.querySelector(".table .body");

var expandBookingsDialog = document.getElementById("expand-booking-dialog");
var editBookingSubmitBtn = document.getElementById("submit-booking");
var editBookingDialog = document.getElementById("edit-booking-dialog");
var editBookingCustomDialog = document.getElementById("edit-booking-custom-dialog");
var editBookingForm = document.getElementById("add-booking");
var editBookingCustomForm = document.getElementById("add-booking-custom");
var editBookingClose = document.getElementById("close-edit-booking-dialog");
var editBookingCustomClose = document.getElementById("close-edit-booking-custom-dialog");

var editBookingPeriodSelector = document.getElementById("period-selector");
var editBookingDateStart = document.getElementById("start-date-picker");
var editBookingDateEnd = document.getElementById("end-date-picker");
var editBookingTimeStart = document.getElementById("time-start-picker");
var editBookingTimeEnd = document.getElementById("time-end-picker");

var editBookingRecurrenceEndWrapper = document.getElementById("end-recurrence");
var editBookingRecurrenceEnd = document.getElementById("recurrence-end-date-picker");

var editBookingCustomIntervalSelector = document.getElementById("custom-recurrence-interval-selector");
var editBookingCustomIntervalWeekWrapper = document.getElementById("custom-recurrence-week");

var editBookingForm = document.getElementById("edit-booking");

var currentEditingBooking = null;

var askDeleteDialog = document.getElementById("ask-delete");

var editBookingSuccessDialog = document.getElementById("edit-booking-success");
var editBookingFailedDialog = document.getElementById("edit-booking-failed");

var deleteBookingSuccessDialog = document.getElementById("delete-booking-success");
var deleteBookingFailedDialog = document.getElementById("delete-booking-failed");

var bookingDuration = document.getElementById("edit-duration");

var bookings = [];
var entries = [];

fetch("/adminPannel/getAllBookings").then((response) => {
    if (response.ok) {
        return response.json();
    } else {
        return null;
    }
}).then((data) => {
    if (data === null) {
        return;
    }

    for (var booking of data) {
        bookings.push(booking);
    }

    feedTable();
});

const weekdayEn = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const monthEn = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

const weekdayFr = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"];
const monthFr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Décembre"];

function getFormatDate(d, region) {
    // Format date given based on region (en or fr)
    switch (region) {
        case "fr":
            return weekdayFr[d.getUTCDay()] + " " + d.getUTCDate() + " " + monthFr[d.getUTCMonth()] + " " + d.getFullYear();

        default:
            return d.getFullYear() + " " + weekdayEn[d.getDay() - 1] + ", " + monthEn[d.getMonth()] + " " + d.getUTCDate();
    }
}

function getFormatTime(t, region) {
    let h;
    let m;
    switch (region) {
        case "fr":
            h = t.getUTCHours();
            m = t.getUTCMinutes();
            if (h < 10) {
                h = "0" + h;
            }
            if ((""+m).length == 1) {
                m = m + "0";
            }
            return h + ":" + m;

        case "en":
            h = t.getHours();
            m = t.getMinutes();
            let ap = t.getHours() >= 12 ? 'pm' : 'am';

            h = h % 12 ? h % 12 : 12;
            m = m < 10 ? '0' + m : m;

            return h + ":" + m + " " + ap;

        default:
            return getFormatTime("en");
    }
}

function dateAndTimeToDatetime(d, t, region) {
    switch (region) {
        case "fr":
            tokens = d.split(' ');
            return tokens[3] + "-" + (monthFr.indexOf(tokens[2]) + 1).toLocaleString('en-US', { minimumIntegerDigits: 2 }) + "-" + parseInt(tokens[1]).toLocaleString('en-US', { minimumIntegerDigits: 2 }) + " " + t + ":00.000000";
    }
}

function clearSelector(select) {
    for (var i = select.options.length - 1; i >= 0; i--) {
        select.remove(i);
    }
}

function feedSelector(select, data) {
    for (let i = 0; i < data.length; i++) {
        let option = new Option(data[i], data[i]);
        select.add(option);
    }
}

function checkEditValidBooking() {
    let inputs = editBookingForm.elements;

    let datetimeStart = dateAndTimeToDatetime(inputs["booking-date-start"].value, inputs["booking-time-start"].value, "fr");
    let dateTimeEnd = dateAndTimeToDatetime(inputs["booking-date-end"].value, inputs["booking-time-end"].value, "fr");

    let ddS = new Date(datetimeStart);
    let ddE = new Date(dateTimeEnd);

    let dEnd = new Date(dateAndTimeToDatetime(inputs["recurrence-booking-date-end"].value, "00:00", "fr"));

    if (ddS.getTime() >= ddE.getTime() || (editBookingPeriodSelector.value != "unique" && dEnd.getTime() <= ddE.getTime())) {
        editBookingSubmitBtn.setAttribute("disabled", "true");
    } else {
        editBookingSubmitBtn.removeAttribute("disabled");
    }
}

function getBookingById(id) {
    for (var booking of bookings) {
        if (booking['bookingID'] === id) {
            return booking;
        }
    }
    return null;
}

function openExpandBookingDialog(bookingId) {
    let booking = getBookingById(bookingId);

    if (booking == null) {
        console.log("Wrong booking id");
        return;
    }

    if (typeof expandBookingsDialog.showModal === "function") {
        expandBookingsDialog.querySelector("#user-name").textContent = booking['userFirstname'] + " " + booking['userLastname'].toUpperCase();

        expandBookingsDialog.querySelector("#lastname").textContent = booking['userLastname'];
        expandBookingsDialog.querySelector("#firstname").textContent = booking['userFirstname'];
        expandBookingsDialog.querySelector("#mail").textContent = booking['userMail'];
        expandBookingsDialog.querySelector("#tel").textContent = booking['userPhoneNumber'] == null ? "Non renseigné" : booking['userPhoneNumber'];

        expandBookingsDialog.querySelector("#plate").textContent = booking['bookingPlate'];
        let date = new Date(booking['bookingStart']);
        expandBookingsDialog.querySelector("#start").textContent = getFormatDate(date, 'fr') + " " + getFormatTime(date, 'fr');
        date = new Date(booking['bookingEnd']);
        expandBookingsDialog.querySelector("#end").textContent = getFormatDate(date, 'fr') + " " + getFormatTime(date, 'fr');
        expandBookingsDialog.querySelector("#duration").textContent = booking['bookingDuration'];

        date = new Date(booking['bookingRepeatEnding']);
        let endingText = getFormatDate(date, 'fr') + " " + getFormatTime(date, 'fr');
        switch (booking['bookingRepeat']) {
            case "daily":
                expandBookingsDialog.querySelector("#repeat-type").textContent = "Quotidienne";
                expandBookingsDialog.querySelector("#repeat-ending").textContent = endingText;
                expandBookingsDialog.querySelector("#repeat-ending-headline").style.display = "flex";
                break;

            case "weekly":
                expandBookingsDialog.querySelector("#repeat-type").textContent = "Hebdomadaire";
                expandBookingsDialog.querySelector("#repeat-ending").textContent = endingText;
                expandBookingsDialog.querySelector("#repeat-ending-headline").style.display = "flex";
                break;

            case "monthly":
                expandBookingsDialog.querySelector("#repeat-type").textContent = "Mensuelle";
                expandBookingsDialog.querySelector("#repeat-ending").textContent = endingText;
                expandBookingsDialog.querySelector("#repeat-ending-headline").style.display = "flex";
                break;

            case "custom":
                expandBookingsDialog.querySelector("#repeat-type").textContent = "Personnalisée";
                expandBookingsDialog.querySelector("#repeat-ending").textContent = endingText;
                expandBookingsDialog.querySelector("#repeat-ending-headline").style.display = "flex";

                switch (booking['bookingRepeatCustomInterval']) {
                    case "day":
                        expandBookingsDialog.querySelector("#repeat-type").textContent = "Se répète tous les " + booking['bookingRepeatCustomAmount'] + " jours";
                        break;

                    case "week":
                        let s = "Se répète toutes les " + booking['bookingRepeatCustomAmount'] + " semaines le ";

                        if (booking['bookingRepeatCustomMonday'] == 1) {
                            s += "Lundi, ";
                        }

                        if (booking['bookingRepeatCustomTuesday'] == 1) {
                            s += "Mardi, ";
                        }

                        if (booking['bookingRepeatCustomWednesday'] == 1) {
                            s += "Mercredi, ";
                        }

                        if (booking['bookingRepeatCustomThursday'] == 1) {
                            s += "Jeudi, ";
                        }

                        if (booking['bookingRepeatCustomFriday'] == 1) {
                            s += "Vendredi, ";
                        }

                        if (booking['bookingRepeatCustomSaturday'] == 1) {
                            s += "Samedi, ";
                        }

                        if (booking['bookingRepeatCustomSunday'] == 1) {
                            s += "Dimanche, ";
                        }

                        s = s.substring(0, s.length - 2);


                        expandBookingsDialog.querySelector("#repeat-type").textContent = s;
                        break;

                    case "month":
                        expandBookingsDialog.querySelector("#repeat-type").textContent = "Se répète tous les " + booking['bookingRepeatCustomAmount'] + " mois";
                        break;

                    default:
                        break;
                }
                break;


            default:
                expandBookingsDialog.querySelector("#repeat-type").textContent = "Pas de répétition";
                break;
        }

        expandBookingsDialog.showModal();
    }
}

async function deleteBooking(url, usrId, bookingId) {
    const data = new FormData();
    data.set("usrId", usrId);
    data.set("id", bookingId);

    const response = await fetch(url, {
        method: "DELETE",
        body: data
    });
    return response.ok;
}

async function postBooking(url, data) {
    const response = await fetch(url, {
        method: "POST",
        body: data
    });
    return response.ok;
}

async function getEditBookingDataAndPost(booking) {
    let inputs = editBookingForm.elements;
    console.log(inputs);
    console.log(booking);
    
    let plate = inputs['plate'].value;
    let datetimeStart = dateAndTimeToDatetime(inputs["booking-date-start"].value, inputs["booking-time-start"].value, "fr");
    let dateTimeEnd = dateAndTimeToDatetime(inputs["booking-date-end"].value, inputs["booking-time-end"].value, "fr");

    let ddS = new Date(datetimeStart);
    let ddE = new Date(dateTimeEnd);

    if (ddS.getTime() === ddE.getTime() || ddE < ddS) {
        // Invalid datetimes
        document.body.style.overflow = "visible";
        editBookingForm.close();
        openEditBookingDialog();
    } else {
        let data = new FormData();
        data.set('usrId', booking['userId'])
        data.set("plate", plate);
        data.set("booking-start", datetimeStart);
        data.set("booking-end", dateTimeEnd);

        let interval = inputs['interval'].value
        data.set("interval", interval);

        if (interval != 'unique') {
            data.set('ending', dateAndTimeToDatetime(editBookingRecurrenceEnd.value, "00:00", "fr"));
        } else {
            data.set('ending', dateTimeEnd);
        }

        if (interval == 'custom') {
            let customInputs = editBookingCustomForm.elements;

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
        return await postBooking(editBookingForm.action, data);
    }
}

function openEditBookingDialog(bookingId) {
    let booking = getBookingById(bookingId);
    currentEditingBooking = booking;

    if (booking == null) {
        console.log("Wrong booking id");
        return;
    }

    if (typeof editBookingDialog.showModal === "function") {
        fetch('/adminPannel/fetchUserPlates?' + new URLSearchParams({
            usrID: booking['userId'],
        })).then((response) => {
            if (response.ok) {
                return response.json();
            } else {
                return null;
            }
        }).then((plateData) => {

            let selector = document.getElementById('plate-selector');
            clearSelector(selector);

            if (plateData.length <= 0) {
                console.log("Data length <= 0");
                return;
            }

            feedSelector(selector, plateData);

            editBookingDialog.querySelector("#plate-selector").value = booking['bookingPlate'];
            editBookingDialog.querySelector("#period-selector").value = booking['bookingRepeat'];

            editBookingDialog.querySelector("#start-date-picker").value = getFormatDate(new Date(booking['bookingStart']), 'fr');
            editBookingDialog.querySelector("#time-start-picker").value = getFormatTime(new Date(booking['bookingStart']), 'fr');

            editBookingDialog.querySelector("#end-date-picker").value = getFormatDate(new Date(booking['bookingEnd']), 'fr');
            editBookingDialog.querySelector("#time-end-picker").value = getFormatTime(new Date(booking['bookingEnd']), 'fr');

            setEditDuration();

            editBookingDialog.querySelector("#recurrence-end-date-picker").value = getFormatDate(new Date(booking['bookingRepeatEnding']), 'fr');

            if (booking['bookingRepeat'] === "unique") {
                editBookingDialog.querySelector("#end-recurrence").style.visibility = "hidden";
            } else {
                editBookingDialog.querySelector("#end-recurrence").style.visibility = "visible";
                if (booking['bookingRepeatCustomAmount'] !== null) {
                    editBookingCustomDialog.querySelector("#custom-recurrence-picker").value = booking['bookingRepeatCustomAmount'];
                } else {
                    editBookingCustomDialog.querySelector("#custom-recurrence-picker").value = 1;
                }

                if (booking['bookingRepeatCustomInterval'] !== null) {
                    editBookingCustomDialog.querySelector("#custom-recurrence-interval-selector").value = booking['bookingRepeatCustomInterval'];
                } else {
                    editBookingCustomDialog.querySelector("#custom-recurrence-interval-selector").value = 'day';
                }

                if (booking['bookingRepeatCustomMonday'] == 1) {
                    editBookingCustomDialog.querySelector("#custom-monday").setAttribute("checked", "true");
                }

                if (booking['bookingRepeatCustomTuesday'] == 1) {
                    editBookingCustomDialog.querySelector("#custom-tuesday").setAttribute("checked", "true");
                }

                if (booking['bookingRepeatCustomWednesday'] == 1) {
                    editBookingCustomDialog.querySelector("#custom-wednesday").setAttribute("checked", "true");
                }

                if (booking['bookingRepeatCustomThursday'] == 1) {
                    editBookingCustomDialog.querySelector("#custom-thursday").setAttribute("checked", "true");
                }

                if (booking['bookingRepeatCustomFriday'] == 1) {
                    editBookingCustomDialog.querySelector("#custom-friday").setAttribute("checked", "true");
                }

                if (booking['bookingRepeatCustomSaturday'] == 1) {
                    editBookingCustomDialog.querySelector("#custom-saturday").setAttribute("checked", "true");
                }

                if (booking['bookingRepeatCustomSunday'] == 1) {
                    editBookingCustomDialog.querySelector("#custom-sunday").setAttribute("checked", "true");
                }
            }

            editBookingDialog.showModal();
        });
    } else {
        console.log("Navigateur non compatible");
    }
}

function openBookingCustomDialog() {
    if (typeof editBookingCustomDialog.showModal === "function") {
        let nowDate = new Date();

        //addBookingCustomDateEnd.min = nowDate.toLocaleDateString("en-ca");

        nowDate.setMonth(nowDate.getMonth()+3)
        //addBookingCustomDateEnd.value = getFormatDate(nowDate, "fr");

        //if (addBookingCustomNeverEndRadio.checked) {
        //    addBookingCustomDateEnd.style.color = "lightgrey";
        //}
        editBookingCustomDialog.showModal();


    } else {
        console.log("Navigateur non compatible");
    }
}

function setEditDuration() {
    let start = new Date(dateAndTimeToDatetime(editBookingDateStart.value, editBookingTimeStart.value, "fr"))
    let end = new Date(dateAndTimeToDatetime(editBookingDateEnd.value, editBookingTimeEnd.value, "fr"));
    let days = Math.floor((end-start)/(24*3600*1000));
    let hours = Math.floor(((end-start)-days*24*3600*1000)/(3600*1000));
    let mins = Math.floor(((end-start)-days*24*3600*1000-hours*3600*1000)/(60*1000));

    if (isNaN(days) || isNaN(hours) || isNaN(mins)) {
        bookingDuration.innerText = `0j 0h0mins`;
    } else {
        bookingDuration.innerText = `${days}j ${hours}h${mins}mins`;
    }
}

function feedTable() {
    for (var booking of bookings) {
        let entry = document.createElement("div");
        entry.classList.add("entry");
        entry.setAttribute("id", booking['bookingID']);

        let lastname = document.createElement("label");
        lastname.classList.add("cell");
        lastname.classList.add("lastname");
        lastname.textContent = booking['userLastname'];

        let firstname = document.createElement("label");
        firstname.classList.add("cell");
        firstname.classList.add("firstname");
        firstname.textContent = booking['userFirstname'];

        let plate = document.createElement("label");
        plate.classList.add("cell");
        plate.classList.add("plate");
        plate.textContent = booking['bookingPlate'];

        let start = document.createElement("label");
        start.classList.add("cell");
        start.classList.add("start");

        let dStart = new Date(booking['bookingStart']);
        let textStart = dStart.getUTCDate() + " " + monthFr[dStart.getUTCMonth()] + " " + dStart.getUTCFullYear() + " " + getFormatTime(dStart, 'fr');
        start.textContent = textStart;

        let end = document.createElement("label");
        end.classList.add("cell");
        end.classList.add("end");

        let dEnd = new Date(booking['bookingEnd']);
        let textEnd = dEnd.getUTCDate() + " " + monthFr[dEnd.getUTCMonth()] + " " + dEnd.getUTCFullYear() + " " + getFormatTime(dEnd, 'fr');
        end.textContent = textEnd;

        let duration = document.createElement("label");
        duration.classList.add("cell");
        duration.classList.add("duration");
        duration.textContent = booking['bookingDuration'];

        let ending = document.createElement("label");
        ending.classList.add("cell");
        ending.classList.add("ending");

        let dEnding = new Date(booking['bookingRepeatEnding']);
        let textEnding = dEnding.getUTCDate() + " " + monthFr[dEnding.getUTCMonth()] + " " + dEnding.getUTCFullYear() + " " + getFormatTime(dEnding, 'fr');
        ending.textContent = textEnding;

        let expandBtn = document.createElement("button");
        expandBtn.classList.add("expand-btn");
        expandBtn.setAttribute("type", "button");
        expandBtn.textContent = "Voir plus";

        expandBtn.addEventListener("click", (e) => {
            openExpandBookingDialog(e.target.closest("div").getAttribute("id"));
        });

        let editBtn = document.createElement("button");
        editBtn.classList.add("edit-btn");
        editBtn.setAttribute("type", "button");
        editBtn.textContent = "Modifier";

        editBtn.addEventListener("click", (e) => {
            openEditBookingDialog(e.target.parentNode.id);
        });

        entry.appendChild(lastname);
        entry.appendChild(firstname);
        entry.appendChild(plate);
        entry.appendChild(start);
        entry.appendChild(end);
        entry.appendChild(duration);
        entry.appendChild(ending);
        entry.appendChild(expandBtn);
        entry.appendChild(editBtn);

        table.appendChild(entry);

        entries.push(entry);
    }
}

expandBookingsDialog.addEventListener("close", (closeEvent) => {
    expandBookingsDialog.querySelectorAll(".optionnal").forEach(optionnalElmt => {
        optionnalElmt.style.display = "none";
    });
});

editBookingTimeStart.addEventListener('input', () => {
    setEditDuration();
    checkEditValidBooking();
});

editBookingTimeEnd.addEventListener('input', () => {
    setEditDuration();
    checkEditValidBooking();
});

editBookingClose.addEventListener('click', () => {
    document.body.style.overflow = "visible";
    editBookingDialog.close();
});

editBookingPeriodSelector.addEventListener("change", (e) => {
    if (e.target.value != "unique") {
        editBookingRecurrenceEndWrapper.style.visibility = "visible";
    } else {
        editBookingRecurrenceEndWrapper.style.visibility = "hidden";
    }
    
    if (e.target.value == "custom") {
        openBookingCustomDialog();
    }

    if (e.target.value == "weekly") {
        editBookingDateEnd.value = editBookingDateStart.value;
    }

    setEditDuration();
    checkEditValidBooking();
});

editBookingCustomIntervalSelector.addEventListener("change", (e) => {
    if (e.target.value === 'week') {
        editBookingCustomIntervalWeekWrapper.style.display = "flex";
        editBookingDateEnd.value = editBookingDateStart.value;
    } else {
        editBookingCustomIntervalWeekWrapper.style.display = "none";
    }

    setEditDuration();
    checkEditValidBooking();
});

editBookingCustomClose.addEventListener("click", () => {
    document.body.style.overflow = "visible";
    editBookingCustomDialog.close();
    editBookingPeriodSelector.value = "unique";  // Reset selector if close whithout submitting
    editBookingRecurrenceEndWrapper.style.visibility = "hidden";
});

editBookingCustomIntervalSelector.addEventListener("change", (e) => {
    if (e.target.value === 'week') {
        editBookingCustomIntervalWeekWrapper.style.display = "flex";
    } else {
        editBookingCustomIntervalWeekWrapper.style.display = "none";
    }
});

editBookingCustomForm.addEventListener("submit", (e) => {
    if (editBookingCustomIntervalSelector.value == "week") {
        let nd = new Date();
        let d = new Date();
        let candidates = [];
        if (editBookingCustomIntervalWeekWrapper.querySelector("#custom-monday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 1 - nd.getUTCDay()) % 7)));
        }
        if (editBookingCustomIntervalWeekWrapper.querySelector("#custom-tuesday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 2 - nd.getUTCDay()) % 7)));
        }
        if (editBookingCustomIntervalWeekWrapper.querySelector("#custom-wednesday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 3 - nd.getUTCDay()) % 7)));
        }
        if (editBookingCustomIntervalWeekWrapper.querySelector("#custom-thursday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 4 - nd.getUTCDay()) % 7)));
        }
        if (editBookingCustomIntervalWeekWrapper.querySelector("#custom-friday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 5 - nd.getUTCDay()) % 7)));
        }
        if (editBookingCustomIntervalWeekWrapper.querySelector("#custom-saturday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 6 - nd.getUTCDay()) % 7)));
        }
        if (editBookingCustomIntervalWeekWrapper.querySelector("#custom-sunday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 7 - nd.getUTCDay()) % 7)));
        }
        editBookingDateStart.value = getFormatDate(new Date(Math.min.apply(null,candidates)), 'fr');
        editBookingDateEnd.value = getFormatDate(new Date(Math.min.apply(null,candidates)), 'fr');
    }
})

editBookingForm.addEventListener('submit', (e) => {
    e.preventDefault();
    editBookingForm.querySelector("button#submit-booking").disabled = true;

    (async () => {
        const result = await getEditBookingDataAndPost(currentEditingBooking);
        editBookingForm.querySelector("button#submit-booking").disabled = false;
        if (result) {
            deleteResponse = await deleteBooking("/adminPannel/deleteUserBooking", currentEditingBooking['userId'], currentEditingBooking['bookingID']);

            if (typeof editBookingSuccessDialog.showModal === "function") {
                editBookingSuccessDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }
        } else {
            document.getElementById("add-booking-failed").showModal();
        }
    })();
});

document.getElementById("date-start-label").addEventListener("click", () => {
    if (editBookingPeriodSelector.value !== "custom" || editBookingCustomIntervalSelector.value !== "week") {
        editBookingDateStart.removeAttribute('readonly');
        editBookingDateStart.type = "date";
        editBookingDateStart.showPicker();
    } else {
        weeklyBookingRestrictWarn.style.visibility = "visible";
        weeklyBookingRestrictWarn.style.opacity = "1";
        setTimeout(() => {
            weeklyBookingRestrictWarn.style.opacity = "0";
            weeklyBookingRestrictWarn.style.visibility = "hidden";
        }, 5000);
    }
});

document.getElementById("date-end-label").addEventListener("click", () => {
    if (editBookingPeriodSelector.value !== "custom" || editBookingCustomIntervalSelector.value !== "week") {
        editBookingDateEnd.removeAttribute('readonly');
        editBookingDateEnd.type = "date";
        editBookingDateEnd.showPicker();
    } else {
        weeklyBookingRestrictWarn.style.visibility = "visible";
        weeklyBookingRestrictWarn.style.opacity = "1";
        setTimeout(() => {
            weeklyBookingRestrictWarn.style.opacity = "0";
            weeklyBookingRestrictWarn.style.visibility = "hidden";
        }, 5000);
    }
});

document.getElementById("recurrence-date-end-label").addEventListener("click", () => {
    editBookingRecurrenceEnd.removeAttribute('readonly');
    editBookingRecurrenceEnd.type = "date";
    editBookingRecurrenceEnd.showPicker();
});

editBookingDateStart.addEventListener("change", (e) => {
    let selectedDate = new Date(e.target.value);
    e.target.type = "text";
    e.target.value = getFormatDate(selectedDate, "fr");
    editBookingDateStart.setAttribute('readonly', true);

    if (editBookingPeriodSelector.value === "weekly") {
        editBookingDateEnd.value = editBookingDateStart.value;
    }

    setEditDuration();
    checkEditValidBooking();
});

editBookingDateEnd.addEventListener("change", (e) => {
    let selectedDate = new Date(e.target.value);
    e.target.type = "text";
    e.target.value = getFormatDate(selectedDate, "fr");
    editBookingDateEnd.setAttribute('readonly', true);

    if (editBookingPeriodSelector.value === "weekly") {
        editBookingDateStart.value = editBookingDateEnd.value;
    }
    
    setEditDuration();
    checkEditValidBooking();
});

editBookingRecurrenceEnd.addEventListener("change", (e) => {
    let selectedDate = new Date(e.target.value);
    e.target.type = "text";
    e.target.value = getFormatDate(selectedDate, "fr");
    editBookingRecurrenceEnd.setAttribute('readonly', true);

    checkEditValidBooking();
});

document.getElementById("delete-booking").addEventListener("click", (e) => {
    // Ask for confirmation
    if (typeof askDeleteDialog.showModal === "function") {
        askDeleteDialog.showModal();
    }
});

askDeleteDialog.querySelector("form").addEventListener("submit", (e) => {
    e.preventDefault();
    (async () => {
        const result = await deleteBooking(e.target.action, currentEditingBooking['userId'], currentEditingBooking['bookingID']);
        if (result) {
            if (typeof deleteBookingSuccessDialog.showModal === "function") {
                deleteBookingSuccessDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }    
        } else {
            if (typeof deleteBookingFailedDialog.showModal === "function") {
                deleteBookingFailedDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }    
            
        }
    })();
});

askDeleteDialog.querySelector("button[type='button']").addEventListener("click", (e) => {
    askDeleteDialog.close();
});