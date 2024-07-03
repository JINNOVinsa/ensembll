var addUserDialog = document.getElementById("add-user-dialog");
var addUserFullSuccessDialog = document.getElementById("add-user-full-success-dialog");
var addUserFailedDialog = document.getElementById("add-user-failed-dialog");

function isFormFullFilled(form) {
    let inputs = form.elements;

    let good = true;

    if (inputs['firstname'].value === '') {
        inputs['firstname'].classList.add("invalid");
        good = false;
    }

    if (inputs['lastname'].value === '') {
        inputs['lastname'].classList.add("invalid");
        good = false;
    }

    if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$/.test(inputs['pswd'].value) && inputs['pswd'].value === '') {
        inputs['pswd'].classList.add("invalid");
        good = false;
    }

    if (!/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(inputs['mail'].value)) {
        inputs['mail'].classList.add("invalid");
        good = false;
    }

    if (inputs['phone'].value != '' && !/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/.test(inputs['phone'].value)) {
        inputs['phone'].classList.add("invalid");
        good = false;
    }

    if (inputs['plate'].value != '' && !/^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$/.test(inputs['plate'].value) && /^[0-9]{4}-[A-Z]{2}-[0-9]{2}$/.test(inputs['plate'].value) || /^[0-9]{1}-[A-Z]{3}-[0-9]{3}$/.test(inputs['plate'].value) || /^[0-9]{3}-[A-Z]{3}-[0-9]{2}$/.test(inputs['plate'].value)) {
        inputs['plate'].classList.add("invalid");
        good = false;
    }

    return good;
}

addUserDialog.querySelector("#lastname").addEventListener("input", (e) => {
    if (e.target.value != '') {
        e.target.classList.remove('invalid');
    } else {
        e.target.classList.add('invalid');
    }
});

addUserDialog.querySelector("#firstname").addEventListener("input", (e) => {
    if (e.target.value != '') {
        e.target.classList.remove('invalid');
    } else {
        e.target.classList.add('invalid');
    }
});

addUserDialog.querySelector("#pswd").addEventListener("input", (e) => {
    if (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$/.test(inputs['pswd'].value) && inputs['pswd'].value != '') {
        e.target.classList.remove('invalid');
    } else {
        e.target.classList.add('invalid');
    }
});

addUserDialog.querySelector("#mail").addEventListener("input", (e) => {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(e.target.value)) {
        e.target.classList.remove('invalid');
    } else {
        e.target.classList.add('invalid');
    }
});

addUserDialog.querySelector("#tel").addEventListener("input", (e) => {
    if (e.target.value != '' && /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/.test(e.target.value)) {
        e.target.classList.remove('invalid');
    } else if (e.target.value == '') {
        e.target.classList.remove('invalid');
    } else {
        e.target.classList.add('invalid');
    }
});

addUserDialog.querySelector("#plate").addEventListener("input", (e) => {
    if (e.target.value != '' && (/^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$/.test(e.target.value) || /^[0-9]{4}-[A-Z]{2}-[0-9]{2}$/.test(e.target.value) || /^[0-9]{1}-[A-Z]{3}-[0-9]{3}$/.test(e.target.value) || /^[0-9]{3}-[A-Z]{3}-[0-9]{2}$/.test(e.target.value))) {
        e.target.classList.remove('invalid');
    } else {
        e.target.classList.add('invalid');
    }
});

var confirmAddBtn = document.getElementById("submit-add-user");

document.getElementById("add-user-btn").addEventListener("click", (e) => {
    if (typeof addUserDialog.showModal === "function") {
        document.body.style.overflow = "hidden";
        addUserDialog.showModal();
    } else {
        console.log("Navigateur non compatible");
    }
});

addUserDialog.addEventListener("submit", (submitEvnt) => {
    let form = submitEvnt.target;
    const data = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: data
    }).then((response) => {
        if (response.ok) {
            if (typeof addUserFullSuccessDialog.showModal === "function") {
                document.body.style.overflow = "hidden";
                addUserFullSuccessDialog.showModal();
            }
            return response;
        } else if (response.status === 400) {
            if (typeof addUserFailedDialog.showModal === "function") {
                response.text().then((text) => {
                    addUserFailedDialog.querySelector("#failed-reason").innerText = text;
                    addUserFailedDialog.showModal();
                });
            }
        } else {
            if (typeof addUserFailedUnknownDialog.showModal === "function") {
                addUserFailedUnknownDialog.showModal();
            }
        }
    });
});

document.getElementById("add-input-valid-checkbox").addEventListener("change", (e) => {
    if (e.target.checked && isFormFullFilled(e.target.closest("form"))) {
        confirmAddBtn.removeAttribute("disabled");
    } else {
        confirmAddBtn.setAttribute("disabled", "true");
    }
});

document.getElementById("add-input-valid-checkbox").checked = false;
confirmAddBtn.setAttribute("disabled", "true");

document.getElementById("add-entity-selector").addEventListener("change", function() {
    var entityId = this.value;
    fetch('/get_profiles_by_entity?entityId=' + entityId)
        .then(response => response.json())
        .then(data => {
            var profileSelector = document.getElementById("add-profile-selector");
            profileSelector.innerHTML = ''; // Efface les options existantes
            data.forEach(function(profile) {
                var option = document.createElement("option");
                option.value = profile[0]; // l'identifiant du profil
                option.text = profile[1]; // le nom du profil
                profileSelector.appendChild(option);
            });
        });
});
