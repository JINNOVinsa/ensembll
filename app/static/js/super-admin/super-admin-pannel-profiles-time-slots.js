var timeSlotsDialog = document.getElementById("time-slots-dialog");
var newTimeSlotDialog = document.getElementById("add-time-slot-dialog");
var newTimeSlotFailedDialog = document.getElementById("add-time-slot-failed");

var deleteTimeSlotDialog = document.getElementById("confirm-delete-time-slot-dialog");
var deleteTimeSlotFailedDialog = document.getElementById("confirm-delete-time-slot-failed")
var current_profile;
var time_slot_delete_id;

function openTimeSlotsDialog(profileNode) {
    if (typeof timeSlotsDialog.showModal !== "function") {
        console.log("Navigateur non compatible");
        return;
    }

    current_profile = profileNode;
    fetch('/superAdminPannel/timeslots?' + new URLSearchParams({ 'profile': profileNode.id })).then((response) => {
        if (response.ok) {
            return response.json();
        } else {
            return {};
        }
    }).then((data) => {
        timeSlotsDialog.querySelector("#profile-headline").innerText = profileNode.querySelector(".profile-title").innerText;
        let container = timeSlotsDialog.querySelector(".content");
        while (container.hasChildNodes()) {
            container.removeChild(container.firstChild);
        }

        if (Object.keys(data).length <= 0) {
            container.innerHTML = "<p>Aucune plage horaire pour ce profil</p>"
            timeSlotsDialog.showModal();
            return;
        }

        let header = document.createElement("div");
        header.classList.add("entry");

        let h1 = document.createElement("h4");
        h1.innerText = "Début";

        let h2 = document.createElement("h4");
        h2.innerText = "Fin";

        let h3 = document.createElement("h4");
        h3.innerText = "Criticité supplémentaire";

        header.appendChild(h1);
        header.appendChild(h2);
        header.appendChild(h3);

        container.appendChild(header);

        for (let t of data) {
            let entry = document.createElement("div");
            entry.id = t['id'];
            entry.classList.add("entry");

            let start = document.createElement("p");
            start.innerText = t["start"].substring(0, t["start"].length-3);

            let end = document.createElement("p");
            end.innerText = t["end"].substring(0, t["end"].length-3);

            let level = document.createElement("p");
            level.innerText = t["level"];

            let deleteEntry = document.createElement("button");
            deleteEntry.classList.add("danger");
            deleteEntry.innerText = "Supprimer";
            
            deleteEntry.addEventListener("click", (e) => {
                askTimeSpotDelete(e.target.parentNode.id);
            })

            entry.appendChild(start);
            entry.appendChild(end);
            entry.appendChild(level);
            entry.appendChild(deleteEntry);

            container.appendChild(entry);
        }

        timeSlotsDialog.showModal();
    })
}

function openNewTimeSlotDialog() {
    if (typeof newTimeSlotDialog.showModal !== "function") {
        console.log("Navigateur non compatible");
        return;
    }

    newTimeSlotDialog.showModal();
}

function postNewTime(form) {
    let inputs = form.elements;

    const data = new FormData();
    data.append('profile', current_profile.id);
    data.append('start', inputs["start"].value + ':00');
    data.append('end', inputs["end"].value + ':00');
    data.append('level', inputs["level"].value);

    fetch(form.action, {
        body: data,
        method: "POST"
    }).then((response) => {
        if (response.ok) {
            newTimeSlotDialog.close();
            timeSlotsDialog.close();
            openTimeSlotsDialog(current_profile);
        } else {
            if (typeof newTimeSlotFailedDialog.showModal === "function") {
                newTimeSlotFailedDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }
        }
    })
}

function askTimeSpotDelete(timeSlotId) {
    if (typeof deleteTimeSlotDialog.showModal !== "function") {
        console.log("Navigateur non compatible");
        return;
    }

    time_slot_delete_id = timeSlotId;

    deleteTimeSlotDialog.showModal();
}

function deleteTimeSlot(timeSlotId, form) {
    const data = new FormData();
    data.append("timeslot", timeSlotId)
    fetch(form.action, {
        body: data,
        method: "POST"
    }).then((response) => {
        if (response.ok) {
            deleteTimeSlotDialog.close();
            timeSlotsDialog.close();
            openTimeSlotsDialog(current_profile);
        } else {
            if (typeof deleteTimeSlotFailedDialog.showModal === "function") {
                deleteTimeSlotFailedDialog.showModal();
                deleteTimeSlotDialog.close();
            }
        }
    })
}

Array.from(document.getElementsByClassName("time-slots")).forEach((btn) => {
    btn.addEventListener("click", (event) => openTimeSlotsDialog(event.target.parentNode));
});

document.getElementById("add-time-slot").addEventListener("click", (event) => {
    openNewTimeSlotDialog();
});

document.getElementById("add-time-slot-form").addEventListener("submit", (event) => {
    event.preventDefault();

    postNewTime(event.target);
});

document.getElementById("delete-time-slot-form").addEventListener("submit", (event) => {
    event.preventDefault();

    deleteTimeSlot(time_slot_delete_id, event.target);
})