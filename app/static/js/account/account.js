var new_plate_form = document.getElementById('new-plate-form');
var submit_plate_trigger = document.getElementById('plate-trigger');
var plate_input = document.getElementById('plate-input');
var plate_submit = document.getElementById('plate-submit');

var delete_plates_elements = document.querySelectorAll(".delete-plate")
var delete_plate_dialog = document.getElementById("delete-plate-dialog");
var delete_plate_booking_conflict_dialog = document.getElementById("delete-plate-booking-error-dialog");

function deletePlate(url, plate) {
    data = new FormData();
    data.set('plate', plate);
    fetch(url, {
        method: 'POST',
        body: data
    }).then((response) => {
        if (response.ok) {
            location.href = "/account"
        } else if (response.status === 409) {
            document.getElementById("error-delete-plate-label").innerHTML = plate;
            delete_plate_booking_conflict_dialog.showModal();
        }

        return response.text();
    })
}

function displayPlateInput() {
    submit_plate_trigger.classList.remove('contracted');
    submit_plate_trigger.classList.add('expanded');

    plate_input.classList.add('expanded');
    plate_input.classList.remove('contracted');

    plate_submit.classList.add('expanded');
    plate_submit.classList.remove('contracted');
}

function hidePlateInput() {
    submit_plate_trigger.classList.add('contracted');
    submit_plate_trigger.classList.remove('expanded');

    plate_input.classList.add('contracted');
    plate_input.classList.remove('expanded');

    plate_submit.classList.add('contracted');
    plate_submit.classList.remove('expanded');
}

function addPlateOnPage(plate) {
    let plates_wrapper = document.getElementById('plates');
    plateNode = document.createElement('p');
    plateNode.innerText = plate;
    plates_wrapper.insertBefore(plateNode, plates_wrapper.children[plates_wrapper.childElementCount - 1]);
}

delete_plates_elements.forEach((elmt) => {
    elmt.addEventListener("click", (e) => {
        if (typeof delete_plate_dialog.showModal === "function") {
            // Fetch user plates
            let plate = elmt.parentNode.innerText;
            document.getElementById("delete-plate-label").innerHTML = plate;
            delete_plate_dialog.showModal();

            delete_plate_dialog.addEventListener('submit', (e) => {
                deletePlate('/deleteplate', plate);
            })
        } else {
            console.error("Navigateur non compatible");
        }
    });
});

document.getElementById("close-delete-dialog").addEventListener("click", () => {
    delete_plate_dialog.close();
})

submit_plate_trigger.addEventListener('click', (event) => {
    event.preventDefault();
    submit_plate_trigger.classList.contains('contracted') ? displayPlateInput() : hidePlateInput();
});

new_plate_form.addEventListener('submit', (event) => {
    event.preventDefault();

    const formData = new FormData(event.target);

    fetch(event.target.action, {
        method: 'POST',
        body: formData
    }).then((response) => {
        if (response.ok) {
            addPlateOnPage(plate_input.value);
            plate_input.value = "";
            hidePlateInput();
            setTimeout(() => {
                document.location = "/account";
            }, 510);
            
        } else {

            let warn_invalid = document.getElementById('invalid-pattern');
            let warn_already_exists = document.getElementById('already-exists');
            let warn_max_reached = document.getElementById('max-reach');
            let warn_default_warn = document.getElementById('default-warn');
            warn_already_exists.classList.remove('show');
            warn_invalid.classList.remove('show');
            warn_max_reached.classList.remove('show');
            warn_default_warn.classList.remove('show');

            switch (response.status) {
                case 400:
                    // Bad Request - Plate pattern isn't good
                    warn_invalid.classList.add('show');
                    plate_input.style.borderColor = "red";
                    plate_submit.children[0].setAttribute("stroke", "red");
                    submit_plate_trigger.children[0].setAttribute("stroke", "red");
                    setTimeout(() => {
                        warn_invalid.classList.remove('show');
                        plate_input.style.borderColor = "green";
                        plate_submit.children[0].setAttribute("stroke", "green");
                        submit_plate_trigger.children[0].setAttribute("stroke", "green");
                    }, 5000);
                    break;
                case 409:
                    // Conflict - Plate already registered
                    warn_already_exists.classList.add('show');
                    plate_input.style.borderColor = "red";
                    plate_submit.children[0].setAttribute("stroke", "red");
                    submit_plate_trigger.children[0].setAttribute("stroke", "red");
                    setTimeout(() => {
                        warn_already_exists.classList.remove('show');
                        plate_input.style.borderColor = "green";
                        plate_submit.children[0].setAttribute("stroke", "green");
                        submit_plate_trigger.children[0].setAttribute("stroke", "green");
                    }, 5000);
                    break;

                case 403:
                    // FORBIDDEN - Already two plates
                    warn_max_reached.classList.add('show');
                    plate_input.style.borderColor = "red";
                    plate_submit.children[0].setAttribute("stroke", "red");
                    submit_plate_trigger.children[0].setAttribute("stroke", "red");
                    setTimeout(() => {
                        warn_max_reached.classList.remove('show');
                        plate_input.style.borderColor = "green";
                        plate_submit.children[0].setAttribute("stroke", "green");
                        submit_plate_trigger.children[0].setAttribute("stroke", "green");
                    }, 5000);
                    break;

                default:
                    // Other code
                    warn_default_warn.classList.add('show');
                    plate_input.style.borderColor = "red";
                    plate_submit.firstChild.stroke = "red";
                    submit_plate_trigger.children[0].style.stroke = "red";
                    setTimeout(() => {
                        warn_default_warn.classList.remove('show');
                        plate_input.style.borderColor = "green";
                        plate_submit.children[0].style.stroke = "green";
                        submit_plate_trigger.children[0].style.stroke = "green";
                    }, 5000);
                    break;
            }
        }

        r = response;
        return r.text();
    });
});