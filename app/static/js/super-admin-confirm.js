var table = document.querySelector(".table .body");

var editUserDialog = document.getElementById("edit-user-dialog");
var confirmEditBtn = document.getElementById("submit-edit-user");
var editUserSuccessDialog = document.getElementById("edit-user-success-dialog");
var editUserFailedDialog = document.getElementById("edit-user-failed-dialog");

var editEntitySelector = document.getElementById("edit-entity-selector");
var editProfileSelector = document.getElementById("edit-profile-selector")

var confirmUserAskDialog = document.getElementById("confirm-user-ask-dialog");
var confirmSuccessDialog = document.getElementById("confirm-success-dialog");
var confirmFailedDialog = document.getElementById("confirm-failed-dialog");

var deleteUserBtn = document.getElementById("delete-user");

var deleteUserSuccessDialog = document.getElementById("delete-user-success-dialog");
var deleteUserFailedDialog = document.getElementById("delete-user-failed-dialog");

function feedTable() {
    for (var usr of users) {
        if (usr['approbation'] == 0) {
            let entry = document.createElement("form");
            entry.classList.add("entry");
            entry.setAttribute("action", "/superAdminPannel/confirmUser");
            entry.setAttribute("method", "post");
            entry.setAttribute("id", usr["id"]);

            let lastname = document.createElement("label");
            lastname.classList.add("cell");
            lastname.classList.add("lastname");
            lastname.textContent = usr["lastName"];
    
            let firstname = document.createElement("label");
            firstname.classList.add("cell");
            firstname.classList.add("firstname");
            firstname.textContent = usr["firstName"];
    
            let criticity = document.createElement("label");
            criticity.classList.add("cell");
            criticity.classList.add("criticity");
            criticity.textContent = usr["criticity"];
    
            let profile = document.createElement("label");
            profile.classList.add("cell");
            profile.classList.add("profile");
            profile.textContent = usr["profile"];

            let rgpd = document.createElement("label");
            rgpd.classList.add("cell");
            rgpd.classList.add("rgpd");
            rgpd.textContent = usr["rgpd"];
    
            let expandBtn = document.createElement("button");
            expandBtn.classList.add("expand-btn");
            expandBtn.setAttribute("type", "button");
            expandBtn.textContent = "Voir plus";
    
            expandBtn.addEventListener("click", (e) => {
                openProfileByID(e.target.parentNode.id)
            });

            let editBtn = document.createElement("button");
            editBtn.classList.add("edit-btn");
            editBtn.setAttribute("type", "button");
            editBtn.textContent = "Modifier";

            editBtn.addEventListener("click", (e) => {
                openEditUserDialog(e.target.parentNode.id);

                editUserDialog.addEventListener("submit", (submitDialog) => {
                    putNewUser(submitDialog.target, submitDialog.target.action, e.target.parentNode);
                });

                deleteUserBtn.addEventListener("click", () => {
                    deleteUser(e.target.parentNode.id);
                });
            });

            let submitBtn = document.createElement("button");
            submitBtn.classList.add("submit-profile-btn");
            submitBtn.setAttribute("type", "submit");
            submitBtn.textContent = "Approuver";
    
            submitBtn.addEventListener("click", (e) => {
                e.preventDefault();
                openAskDialog(e.target.parentNode);
                confirmUserAskDialog.addEventListener("submit", (dialog) => {
                    console.log("Submit dialog");
                    confirmUser(e.target.parentNode);
                });
            });

            if (usr["rgpd"] === "Non") {
                submitBtn.disabled = true;
            }

            entry.appendChild(lastname);
            entry.appendChild(firstname);
            entry.appendChild(criticity);
            entry.appendChild(profile);
            entry.appendChild(rgpd);
            entry.appendChild(expandBtn);
            entry.appendChild(editBtn);
            entry.appendChild(submitBtn);
    
            table.appendChild(entry);

            entries.push(entry);
        }
    }
}

function clearSelector(select) {
    let l = select.options.length;
    for (let i = 0; i < l; i++) {
        select.remove(0);
    }
}

function fetchProfilesByEntity(selector, entityId, defaultVal) {
    fetch('/profiles?' + new URLSearchParams({'entity': entityId})).then((response) => {
        return response.json();
    }).then((data) => {
        for (let p of data) {
            let o = document.createElement('option');
            o.text = p;
            selector.add(o);
        }

        if (defaultVal != null) {
            selector.value = defaultVal;
        }
    });
}

function openAskDialog(formTrigger) {
    if (typeof confirmUserAskDialog.showModal === "function") {
        let firstname = formTrigger.getElementsByClassName("firstname")[0].textContent;
        let lastname = formTrigger.getElementsByClassName("lastname")[0].textContent.toUpperCase();

        document.getElementById("confirm-user-text").innerHTML = firstname + " " + lastname;
        document.body.style.overflow = "hidden";
        confirmUserAskDialog.showModal();
    }
}

function confirmUser(form) {
    const dataF = new FormData();
    dataF.append("USR_ID", form.id);
    fetch(form.action, {
        method: 'POST',
        body: dataF,
    }).then((response) => {
        let firstname = form.getElementsByClassName("firstname")[0].textContent;
        let lastname = form.getElementsByClassName("lastname")[0].textContent.toUpperCase();

        if (response.ok) {
            if (typeof confirmSuccessDialog.showModal === "function") {
                confirmSuccessDialog.getElementsByTagName("span")[0].innerHTML = firstname + " " + lastname;
                confirmSuccessDialog.showModal();
            }
        } else if (typeof confirmFailedDialog.showModal === "function") {
            confirmFailedDialog.getElementsByTagName("span")[0].innerHTML = firstname + " " + lastname;
            confirmFailedDialog.showModal();
        } else {
            console.log("Navigateur non compatible");
        }
    });
}

function openEditUserDialog(id) {
    if (typeof editUserDialog.showModal === "function") {
        var user = getUserByID(id)

        editUserDialog.querySelector("#user-name").innerHTML = user.firstName + " " + user.lastName.toUpperCase();

        editUserDialog.querySelector("#lastname").value = user.lastName;
        editUserDialog.querySelector("#firstname").value = user.firstName;
        editUserDialog.querySelector("#mail").value = user.mail;
        
        if (user.phoneNumber === null || user.phoneNumber === undefined) {
            editUserDialog.querySelector("#tel").value = "Aucun numéro renseigné";
            editUserDialog.querySelector("#tel").style.color = "red";
        } else {
            editUserDialog.querySelector("#tel").value = user.phoneNumber;
            editUserDialog.querySelector("#tel").style.color = "black";
        }

        editEntitySelector.value = user.entityId;

        clearSelector(editProfileSelector);
        fetchProfilesByEntity(editProfileSelector, user.entityId, user.profile);

            
        let platesContainer = editUserDialog.querySelector("#immat");
        platesContainer.innerHTML = '';
        if (user.plates.length > 0) {
            for (const plate of user.plates) {
                let l = document.createElement("label");
                l.innerHTML = plate;
                platesContainer.appendChild(l);
            }
        } else {
            let l = document.createElement("label");
            l.innerHTML = "Aucune plaque renseignée";
            l.style.color = "red";
            platesContainer.appendChild(l);
        }

        document.body.style.overflow = "hidden";
        editUserDialog.showModal();
    } else {
        console.log("Navigateur non compatible");
    }
}

function putNewUser(form, endpoint, usr) {
    let inputs = form.elements;
    let data = new FormData();
    data.append("id", usr.id);
    data.append("lastname", inputs["lastname"].value);
    data.append("firstname", inputs["firstname"].value);
    data.append("mail", inputs["mail"].value);

    if (/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/.test(inputs["tel"])) {
        data.append("tel", inputs["tel"].value);
    } else {
        data.append("tel", "none");
    }

    data.append("entityId", inputs["entity"].value);
    data.append("profile", inputs["profile"].value);
    //data.append("immat", inputs["immat"]);
    fetch(endpoint, {
        method: 'PUT',
        body: data
    }).then((response) => {
        if (response.ok) {
            confirmUser(usr);
            if (typeof editUserSuccessDialog.showModal === "function") {
                editUserSuccessDialog.showModal();
            } else {
                console.log("Navigateur non compataible");
            }
        } else {
            if (typeof editUserFailedDialog.showModal === "function") {
                editUserFailedDialog.showModal();
            } else {
                console.log("Navigatuer non compatible");
            }
        }
    })
}


var confirmBtns = document.getElementsByClassName("submit-profile-btn");

confirmUserAskDialog.addEventListener("reset", (e) => {
    confirmUserAskDialog.close();
    document.body.style.overflow = "visible";
});

document.getElementById("edit-input-valid-checkbox").addEventListener("change", (e) => {
    if (e.target.checked) {
        confirmEditBtn.removeAttribute("disabled");
        deleteUserBtn.removeAttribute("disabled");
    } else {
        confirmEditBtn.setAttribute("disabled", "true");
        deleteUserBtn.setAttribute("disabled", "true");
    }
});

document.getElementById("edit-input-valid-checkbox").checked = false;
confirmEditBtn.setAttribute("disabled", "true");
deleteUserBtn.setAttribute("disabled", "true");

editEntitySelector.addEventListener('change', (e) => {
    clearSelector(editProfileSelector);
    fetchProfilesByEntity(editProfileSelector, e.target.value, null);
});