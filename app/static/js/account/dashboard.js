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

async function deleteBooking(url, bookingId) {
    const data = new FormData();
    data.set("id", bookingId);

    const response = await fetch(url, {
        method: "DELETE",
        body: data
    });
    return response.ok;
}


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
            return d.getFullYear() + " " + weekdayEn[d.getDay() -1] + ", " + monthEn[d.getMonth()] + " " + d.getUTCDate();
    }
}

function getFormatTime(t, region) {
    switch (region) {
        case "fr":
            return t.getUTCHours().toString().padStart(2, "0") + ":" + t.getUTCMinutes().toString().padStart(2, "0");

        case "en":
            let h = t.getHours();
            let m = t.getMinutes();

            let ap = t.getHours() >= 12 ? 'pm' : 'am';

            h = h%12 ? h%12 : 12;
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
            return tokens[3] + "-" + (monthFr.indexOf(tokens[2])+1).toLocaleString('en-US', {minimumIntegerDigits:2}) + "-" + parseInt(tokens[1]).toLocaleString('en-US', {minimumIntegerDigits:2}) + " " + t + ":00.000000";
    }
}

var addBookingBtn = document.getElementById("add-booking-btn");
var addBookingDialog = document.getElementById("add-booking-dialog");
var addBookingClose = document.getElementById("close-add-booking-dialog");
var addBookingForm = document.getElementById("add-booking");
var addBookingSubmitBtn = document.getElementById("submit-booking");

var addBookingRecurrenceEndWrapper = document.getElementById("end-recurrence");
var addBookingRecurrenceEnd = document.getElementById("recurrence-end-date-picker");

var addBookingCustomDialog = document.getElementById("add-booking-custom-dialog");
var addBookingCustomForm = document.getElementById("add-booking-custom");
var addBookingCustomClose = document.getElementById("close-add-booking-custom-dialog");

var addBookingPeriodSelector = document.getElementById("period-selector");
var addBookingDateStart = document.getElementById("start-date-picker");
var addBookingDateEnd = document.getElementById("end-date-picker");
var addBookingTimeStart = document.getElementById("time-start-picker");
var addBookingTimeEnd = document.getElementById("time-end-picker");

var addBookingCustomIntervalSelector = document.getElementById("custom-recurrence-interval-selector");
addBookingCustomIntervalSelector.value = "day";

var addBookingCustomIntervalWeekWrapper = document.getElementById("custom-recurrence-week");

//var addBookingCustomNeverEndRadio = document.getElementById("custom-end-never");
//var addBookingCustomDateEndRadio = document.getElementById("custom-end-date");

//var addBookingCustomDateEnd = document.getElementById("custom-end-date-picker");

var editBookingElements = document.querySelectorAll(".entry .edit");
var deleteBookingElements = document.querySelectorAll(".entry .delete");

var deleteBookingDialog = document.getElementById("delete-booking-dialog");

var noPlatesWarn = document.getElementById("no-plates");
var profileNotConfirm = document.getElementById("not-confirmed");

var bookingDuration = document.getElementById("duration");

var weeklyBookingRestrictWarn = document.getElementById("weekly-booking-restrict");

var bookindIdToDelete = null;

function openBookingDialog() {
    if (typeof addBookingDialog.showModal === "function") {
        // Fetch user plates
        getServer('/fetchplates').then((response) => {
            if (response.ok) {
                return response.json();
            } else {
                profileNotConfirm.classList.add('show');
                setTimeout(() => {
                    profileNotConfirm.classList.remove('show');
                }, 5000);
            }
        }).then((data) => {

            let selector = document.getElementById('plate-selector');
            clearSelector(selector);
            
            if (data.length <= 0) {
                // No plates registered
                noPlatesWarn.classList.add('show');
                setTimeout(() => {
                    noPlatesWarn.classList.remove('show');
                }, 5000);
                return;
            }

            feedSelector(selector, data);

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
            addBookingDialog.showModal();
        });
    } else {
        console.error("Navigateur non compatible");
    }
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
        bookingDuration.innerText = `0j 0h0mins`;
    } else {
        bookingDuration.innerText = `${days}j ${hours}h${mins}mins`;
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
    let plate = inputs['plate'].value;
    let datetimeStart = dateAndTimeToDatetime(inputs["booking-date-start"].value, inputs["booking-time-start"].value, "fr");
    let dateTimeEnd = dateAndTimeToDatetime(inputs["booking-date-end"].value, inputs["booking-time-end"].value, "fr");

    let ddS = new Date(datetimeStart);
    let ddE = new Date(dateTimeEnd);

    if (ddS.getTime() === ddE.getTime() || ddE < ddS) {
        // Invalid datetimes
        document.body.style.overflow = "visible";
        addBookingDialog.close();
        openBookingDialog();
    } else {
        let data = new FormData();
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

addBookingBtn.addEventListener('click',() => {
    openBookingDialog();
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
    addBookingForm.querySelector("button#submit-booking").disabled = true;
    (async () => {
    result = await getBookingDataAndPost();
        addBookingForm.querySelector("button#submit-booking").disabled = false;
        if (!result) {
            document.getElementById("add-booking-failed").showModal();
        } else {
            if (bookindIdToDelete !== null) {
                await deleteBooking("/deletebooking", bookindIdToDelete);
                bookindIdToDelete = null;
            }
            location.href = "/";
        }
    })();
});

addBookingClose.addEventListener('click', () => {
    bookindIdToDelete = null;
    document.body.style.overflow = "visible";
    window.scrollTo(0, 0);

    addBookingDialog.close();
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

//document.getElementById("date-start-label").addEventListener("click", () => {
addBookingDateStart.addEventListener("click", () => {
    if (addBookingPeriodSelector.value !== "custom" || addBookingCustomIntervalSelector.value !== "week") {
        addBookingDateStart.removeAttribute('readonly');
        addBookingDateStart.type = "date";
        addBookingDateStart.showPicker();
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

//document.getElementById("date-end-label").addEventListener("click", () => {
addBookingDateEnd.addEventListener("click", () => {
    if (addBookingPeriodSelector.value !== "custom" || addBookingCustomIntervalSelector.value !== "week") {
        addBookingDateEnd.removeAttribute('readonly');
        addBookingDateEnd.type = "date";
        addBookingDateEnd.showPicker();
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

//document.getElementById("recurrence-date-end-label").addEventListener("click", () => {
addBookingRecurrenceEnd.addEventListener("click", () => {
    addBookingRecurrenceEnd.removeAttribute('readonly');
    addBookingRecurrenceEnd.type = "date";
    addBookingRecurrenceEnd.showPicker();
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
        if (addBookingCustomIntervalWeekWrapper.querySelector("#custom-monday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 1 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#custom-tuesday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 2 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#custom-wednesday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 3 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#custom-thursday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 4 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#custom-friday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 5 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#custom-saturday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 6 - nd.getUTCDay()) % 7)));
        }
        if (addBookingCustomIntervalWeekWrapper.querySelector("#custom-sunday").checked) {
            candidates.push(d.setUTCDate(nd.getUTCDate() + ((7 + 7 - nd.getUTCDay()) % 7)));
        }
        addBookingDateStart.value = getFormatDate(new Date(Math.min.apply(null,candidates)), 'fr');
        addBookingDateEnd.value = getFormatDate(new Date(Math.min.apply(null,candidates)), 'fr');
    }
})

editBookingElements.forEach((elmt) => {
    elmt.addEventListener("click", (e) => {
        let bookingId = elmt.closest("div").getAttribute("id");

        // Fetch booking info
        fetch('/getbooking?'+ new URLSearchParams({
            bookingID: bookingId,
        })).then((response) => {
            if (response.ok) {
                return response.json();
            } else {
                return null;
            }
        }).then((data) => {
            if (data == null) {
                return;
            }
            
            if (typeof addBookingDialog.showModal === "function") {
                getServer('/fetchplates').then((response) => {
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
                
                    addBookingDialog.querySelector("#plate-selector").value = data['bookingPlate'];
                    addBookingDialog.querySelector("#period-selector").value = data['bookingRepeat'];

                    addBookingDialog.querySelector("#start-date-picker").value = getFormatDate(new Date(data['bookingStart']), 'fr');
                    addBookingDialog.querySelector("#time-start-picker").value = getFormatTime(new Date(data['bookingStart']), 'fr');

                    addBookingDialog.querySelector("#end-date-picker").value = getFormatDate(new Date(data['bookingEnd']), 'fr');
                    addBookingDialog.querySelector("#time-end-picker").value = getFormatTime(new Date(data['bookingEnd']), 'fr');

                    setDuration();

                    addBookingDialog.querySelector("#recurrence-end-date-picker").value = getFormatDate(new Date(data['bookingRepeatEnding']), 'fr');

                    if (data['bookingRepeat'] === "unique") {
                        addBookingDialog.querySelector("#end-recurrence").style.visibility = "hidden";
                    } else {
                        addBookingCustomDialog.querySelector("#custom-recurrence-picker").value = data['bookingRepeatCustomAmount'];
                        addBookingCustomDialog.querySelector("#custom-recurrence-interval-selector").value = data['bookingRepeatCustomInterval'];

                        if (data['bookingRepeatCustomMonday'] == 1) {
                            addBookingCustomDialog.querySelector("#custom-monday").setAttribute("checked", "true");
                        }

                        if (data['bookingRepeatCustomTuesday'] == 1) {
                            addBookingCustomDialog.querySelector("#custom-tuesday").setAttribute("checked", "true");
                        }

                        if (data['bookingRepeatCustomWednesday'] == 1) {
                            addBookingCustomDialog.querySelector("#custom-wednesday").setAttribute("checked", "true");
                        }

                        if (data['bookingRepeatCustomThursday'] == 1) {
                            addBookingCustomDialog.querySelector("#custom-thursday").setAttribute("checked", "true");
                        }

                        if (data['bookingRepeatCustomFriday'] == 1) {
                            addBookingCustomDialog.querySelector("#custom-friday").setAttribute("checked", "true");
                        }

                        if (data['bookingRepeatCustomSaturday'] == 1) {
                            addBookingCustomDialog.querySelector("#custom-saturday").setAttribute("checked", "true");
                        }

                        if (data['bookingRepeatCustomSunday'] == 1) {
                            addBookingCustomDialog.querySelector("#custom-sunday").setAttribute("checked", "true");
                        }
                    }
                    
                    bookindIdToDelete = bookingId;
                    addBookingDialog.showModal();
                });
            }
        });
    });
});

deleteBookingElements.forEach((elmt) => {
    elmt.addEventListener("click", (e) => {
        let entry = e.target.parentNode.parentNode;
        let booking_id = entry.id;
        if (typeof addBookingDialog.showModal === "function") {
            // Fetch user plates
            document.getElementById("delete-booking-date-start").innerHTML = entry.querySelector(".start").textContent;
            document.getElementById("delete-booking-date-end").innerHTML = entry.querySelector(".end").textContent;

            deleteBookingDialog.addEventListener('submit', (e) => {
                (async () => {
                    const result = await deleteBooking('/deletebooking', booking_id);
                    if (result) {
                        location.href = "/"
                    }
                })();
            })
            document.body.style.overflow = "hidden";
            deleteBookingDialog.showModal();
        } else {
            console.error("Navigateur non compatible");
        }
    });
});

document.getElementById('close-delete-dialog').addEventListener('click', (e) => {
    document.body.style.overflow = "visible";
    deleteBookingDialog.close();
});

document.addEventListener('DOMContentLoaded', function() {
    fetch('../static/assets/text/rgpd.txt')
        .then(response => response.text())
        .then(text => {
            document.getElementById('rgpdPre').textContent = text;
        })
        .catch(err => {
            console.error('Erreur de chargement du fichier :', err);
            document.getElementById('rgpdPre').textContent = 'Erreur de chargement du texte.';
        });
});

document.addEventListener('DOMContentLoaded', function() {

    var rgpdDialog = document.getElementById('rgpdDialog');
    var acceptButton = document.getElementById('acceptButton');
    var acceptRGPD = document.getElementById('acceptRGPD');
    var checkRGPD = rgpdDialog.getAttribute('data-checkrgpd');

    checkRGPD = Number(checkRGPD);

    rgpdDialog.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            event.preventDefault();
        }
    });

    // Afficher le dialogue si l'utilisateur n'a pas accepté les CGU/RGPD
    if (checkRGPD === 0) {
        rgpdDialog.showModal();
    }

    // Gérer l'acceptation des CGU/RGPD
    acceptButton.addEventListener('click', function() {
        // Vérifier si les deux cases sont cochées
        if (acceptRGPD.checked) {
            // Envoyer une requête au backend pour mettre à jour la base de données
            fetch('/update-rgpd-consent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ rgpdAccepted: true })
            })
            .then(response => response.json())
            .then(data => {
                // Gérer la réponse ici
                rgpdDialog.close();
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    });
});