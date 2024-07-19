var editDialog = document.getElementById("edit-profile-dialog");
var confirmationEditDialog = document.getElementById("confirm-edit-profile-dialog");
var editProfileSuccessDialog = document.getElementById("edit-profile-success-dialog");
var editProfileFailedDialog = document.getElementById("edit-profile-failed-dialog");

var deleteDialog = document.getElementById("delete-profile-dialog");
var deleteProfileSuccessDialog = document.getElementById("delete-profile-success-dialog");
var deleteProfileFailedDialog = document.getElementById("delete-profile-failed-dialog")

var cancelEditBtn = editDialog.querySelector("#cancel-edit");
var submitEditBtn = editDialog.querySelector("#submit-edit");

var cancelDeleteBtn = deleteDialog.querySelector("#cancel-delete");
var submitDeleteBtn = deleteDialog.querySelector("#submit-delete");

function openEditDialogForForm(form) {
    if (typeof editDialog.showModal === "function") {
        editDialog.querySelector("#profile-headline").textContent = form.querySelector(".profile-title").textContent;
        editDialog.querySelector("#input-name").value = form.querySelector(".profile-title").textContent;
        editDialog.querySelector("#input-criticity").value = form.querySelector(".profile-criticity").textContent;

        editDialog.showModal();
    } else {
        console.log("Navigateur non compatible");
    }
}

function openConfirmationDialogForForm(newTitle, newCriticity) {
    if (typeof confirmationEditDialog.showModal === "function") {
        confirmationEditDialog.querySelector("#new-name-profile").textContent = newTitle;
        confirmationEditDialog.querySelector("#new-criticity-profile").textContent = newCriticity;
        confirmationEditDialog.showModal();
    } else {
        console.log("Navigateur non compatible");
    }
}

function postEditProfile(url, id, newTitle, newCriticity) {
    var data = new FormData();
    data.append("id", id);
    data.append("name", newTitle);
    data.append("criticity", newCriticity);

    fetch(url, {
        method: 'PUT',
        body: data
    }).then((response) => {
        if (response.ok) {
            if (typeof editProfileSuccessDialog.showModal === "function") {
                editProfileSuccessDialog.showModal();
            } else {
                console.log("Navigateur non compatbile");
            }
        } else {
            if (typeof editProfileFailedDialog.showModal === "function") {
                editProfileFailedDialog.showModal();
            } else {
                console.log("Navigateur non compatbile");
            }
        }
        return response;
    });
}

function openDeleteDialog(title) {
    if (typeof deleteDialog.showModal === "function") {
        deleteDialog.querySelector("#profile-headline").textContent = title;
        deleteDialog.showModal();
    } else {
        console.log("Navigateur non compatible");
    }
}

var editBtns = document.getElementsByClassName("edit-profile");
var deleteBtns = document.getElementsByClassName("delete-profile");

Array.from(editBtns).forEach(btn => {
    btn.addEventListener('click', (e) => {
        let formEntry = e.target.parentNode
        openEditDialogForForm(formEntry);

        editDialog.addEventListener("submit", (evnt) => {
            let inputs = evnt.target.elements;
            openConfirmationDialogForForm(inputs["name"].value, inputs["criticity"].value);

            confirmationEditDialog.addEventListener("submit", (confirmEvent) => {
                postEditProfile(confirmEvent.target.action, formEntry.id, inputs["name"].value, inputs["criticity"].value);
            });
        });
    });
});

Array.from(deleteBtns).forEach(btn => {
    btn.addEventListener("click", (e) => {
        let pId = e.target.parentNode.id;
        let pTitle = e.target.parentNode.querySelector(".profile-title").textContent;
        
        openDeleteDialog(pTitle);

        deleteDialog.addEventListener("submit", (submitE) => {
            let data = new FormData();
            data.append("profileId", pId);
            fetch(submitE.target.action, {
                method: 'DELETE',
                body: data
            }).then((response) => {
                if (response.ok) {
                    if (typeof deleteProfileSuccessDialog.showModal === "function") {
                        deleteProfileSuccessDialog.showModal();
                    } else {
                        console.log("Navigateur non compatbile");
                    }
                } else {
                    if (typeof deleteProfileFailedDialog.showModal === "function") {
                        deleteProfileFailedDialog.showModal();
                    } else {
                        console.log("Navigateur non compatbile");
                    }
                }

                return response;
            });
        });
    });
});

Array.from(document.querySelectorAll(".dialog.cancel")).forEach(btn => {
    btn.addEventListener("click", (e) => {
        e.target.closest("dialog").close();
    });
});

editDialog.querySelector("#input-valid-checkbox").addEventListener("change", (e) => {
    if (e.target.checked) {
        submitEditBtn.removeAttribute("disabled");
    } else {
        submitEditBtn.setAttribute("disabled", "true");
    }
});

deleteDialog.querySelector("#delete-input-valid-checkbox").addEventListener("change", (e) => {
    if (e.target.checked) {
        submitDeleteBtn.removeAttribute("disabled");
    } else {
        submitDeleteBtn.setAttribute("disabled", "true");
    }
});

editDialog.querySelector("#input-valid-checkbox").checked = false;
deleteDialog.querySelector("#delete-input-valid-checkbox").checked = false;