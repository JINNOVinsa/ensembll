var table = document.querySelector(".table .body");

var editUserDialog = document.getElementById("edit-user-dialog");
var editUserSuccessDialog = document.getElementById("edit-user-success-dialog");
var editUserFailedDialog = document.getElementById("edit-user-failed-dialog");

var deleteUserBtn = document.getElementById("delete-user");

var deleteUserSuccessDialog = document.getElementById("delete-user-success-dialog");
var deleteUserFailedDialog = document.getElementById("delete-user-failed-dialog");

function feedTable() {
    for (var usr of users) {
        let entry = document.createElement("div");
        entry.classList.add("entry");
        entry.setAttribute("id", usr['id']);

        let lastname = document.createElement("label");
        lastname.classList.add("cell");
        lastname.classList.add("lastname");
        lastname.textContent = usr["lastName"];

        let firstname = document.createElement("label");
        lastname.classList.add("cell");
        lastname.classList.add("firstname");
        firstname.textContent = usr["firstName"];

        let profile = document.createElement("label");
        profile.classList.add("cell");
        profile.classList.add("profile");
        profile.textContent = usr["profile"];

        let entityLabel = document.createElement("label");
        entityLabel.classList.add("cell");
        entityLabel.classList.add("entity");
        entityLabel.textContent = usr["entity"];

        let hierarchyLabel = document.createElement("label");
        hierarchyLabel.classList.add("cell");
        hierarchyLabel.classList.add("hierarchy");
        switch(usr["hierarchy"]) {
            case 0:
                hierarchyLabel.textContent = "Utilisateur";
                break;
            case 1:
                hierarchyLabel.textContent = "Direction";
                break;
            case 2:
                hierarchyLabel.textContent = "Administrateur";
                break;
            default:
                hierarchyLabel.textContent = "Inconnu";
        }

        let approbationContainer = document.createElement("div");
        approbationContainer.classList.add("cell");
        approbationContainer.classList.add("approbation");

        let approbationImg = document.createElement("img");
        switch (usr['approbation']) {
            case 1:
                approbationContainer.classList.add("approved");
                approbationImg.setAttribute("src", "/static/assets/usr/valid.png");
                break;
        
            case 0:
                approbationContainer.classList.add("pending");
                approbationImg.setAttribute("src", "/static/assets/usr/pending.png");
                break;

            default:
                approbationContainer.classList.add("invalid");
                approbationImg.setAttribute("src", "/static/assets/usr/refused.png");
                break;
        }

        approbationContainer.insertBefore(approbationImg, approbationContainer.firstChild);

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
                putNewUser(submitDialog.target, submitDialog.target.action, e.target.parentNode.id);
            });

            deleteUserBtn.addEventListener("click", () => {
                deleteUser(e.target.parentNode.id);
            });
        });

        entry.appendChild(lastname);
        entry.appendChild(firstname);
        entry.appendChild(profile);
        entry.appendChild(entityLabel);
        entry.appendChild(hierarchyLabel);
        entry.appendChild(approbationContainer);
        entry.appendChild(expandBtn);
        entry.appendChild(editBtn);

        table.appendChild(entry);

        entries.push(entry);
    }
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
        editUserDialog.querySelector("#profile").value = user.profile;
            
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

function putNewUser(form, endpoint, usrId) {
    let inputs = form.elements;
    let data = new FormData();
    data.append("id", usrId);
    data.append("lastname", inputs["lastname"].value);
    data.append("firstname", inputs["firstname"].value);
    data.append("mail", inputs["mail"].value);

    if (/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/.test(inputs["tel"].value)) {
        data.append("tel", inputs["tel"].value);
    } else {
        data.append("tel", "none");
    }
    data.append("profile", inputs["profile"].value);
    //data.append("immat", inputs["immat"]);
    fetch(endpoint, {
        method: 'PUT',
        body: data
    }).then((response) => {
        if (response.ok) {
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

var confirmEditBtn = document.getElementById("submit-edit-user");

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


/* Export users */
var exportUsersBtn = document.getElementById("export-users");

exportUsersBtn.addEventListener('click', () => {
    fetch('/adminPannel/exportUsers').then((response) => {
        return response.blob();
    }).then((blob) => {
        let file = window.URL.createObjectURL(blob);
        //window.location.assign(file);     // This set the filename with a random uuid

        // We go over that with a <a> tag with a download attribute
        let fileLink = document.createElement('a');
        fileLink.href = file;
        fileLink.download = 'users.csv';
        fileLink.click();
    });
});