var addAdminDialog = document.getElementById("add-admin-dialog")

var addAdminSuccessDialog = document.getElementById("add-admin-full-success-dialog");
var addAdminFailedKnownDialog = document.getElementById("add-admin-failed-dialog");
var addAdminFailedUnknownDialog = document.getElementById("add-admin-failed-unknown-dialog");

var addAdminEntitySelector = document.getElementById("add-admin-entity-selector");
var addAdminProfileSelector = document.getElementById("add-admin-profile-selector");

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

addAdminDialog.querySelector("#lastname").addEventListener("input", (e) => {
    if (e.target.value != '') {
        e.target.classList.remove('invalid');
    } else {
        e.target.classList.add('invalid');
    }
});

addAdminDialog.querySelector("#firstname").addEventListener("input", (e) => {
    if (e.target.value != '') {
        e.target.classList.remove('invalid');
    } else {
        e.target.classList.add('invalid');
    }
});

addAdminDialog.querySelector("#pswd").addEventListener("input", (e) => {
    if (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$/.test(inputs['pswd'].value) && inputs['pswd'].value != '') {
        e.target.classList.remove('invalid');
    } else {
        e.target.classList.add('invalid');
    }
});

addAdminDialog.querySelector("#mail").addEventListener("input", (e) => {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(e.target.value)) {
        e.target.classList.remove('invalid');
    } else {
        e.target.classList.add('invalid');
    }
});

addAdminDialog.querySelector("#tel").addEventListener("input", (e) => {
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

var confirmAddAdminBtn = document.getElementById("submit-add-admin");

addAdminDialog.addEventListener("submit", (submitEvnt) => {
    submitEvnt.preventDefault();
    let form = submitEvnt.target;
    const data = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: data
    }).then((response) => {
        if (response.ok) {
            if (typeof addAdminSuccessDialog.showModal === "function") {
                document.body.style.overflow = "hidden";
                addAdminSuccessDialog.showModal();
            }
            return response;
        } else if (response.status === 400) {
            if (typeof addAdminFailedKnownDialog.showModal === "function") {
                
                response.text().then((text) => {
                    addAdminFailedKnownDialog.querySelector("#failed-reason").innerText = text;
                    addAdminFailedKnownDialog.showModal();
                });
            }
        } else {
            if (typeof addAdminFailedUnknownDialog.showModal === "function") {
                addAdminFailedUnknownDialog.showModal();
            }
        }
    });
});

document.getElementById("add-admin-input-valid-checkbox").addEventListener("change", (e) => {
    if (e.target.checked && isFormFullFilled(e.target.closest("form"))) {
        confirmAddAdminBtn.removeAttribute("disabled");
    } else {
        confirmAddAdminBtn.setAttribute("disabled", "true");
    }
});

document.getElementById("add-admin-input-valid-checkbox").checked = false;
confirmAddAdminBtn.setAttribute("disabled", "true");

addAdminEntitySelector.addEventListener('change', (e) => {
    clearSelector(addAdminProfileSelector);
    fetchProfilesByEntity(addAdminProfileSelector, e.target.value, null);
});
fetchProfilesByEntity(addAdminProfileSelector, addAdminEntitySelector.value, null);

document.getElementById("add-admin-btn").addEventListener("click", () => {
    if (typeof addAdminDialog.showModal === "function") {
        addAdminDialog.showModal();
    } else {
        console.log("Navigateur non compatible");
    }
})