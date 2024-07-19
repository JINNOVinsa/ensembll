var oldMail = document.getElementById("mail-content").innerText;
var editMailDialog = document.getElementById("edit-mail-dialog");
var newMailInput = document.getElementById("new-mail-input");

var changeMailOK = document.getElementById("edit-mail-success-dialog");
var changeMailErrorMailAlreadyBound = document.getElementById("edit-mail-failed-mail-already-bound-dialog");
var changeMailError = document.getElementById("edit-mail-failed-dialog");

function openEditMailDialog() {
    if (typeof editMailDialog.showModal !== "function") {
        console.log("Navigateur non compatible");
        return;
    }
    newMailInput.value = "";
    newMailInput.placeholder = oldMail;

    editMailDialog.showModal();
}

document.getElementById("edit-mail").addEventListener("click", (e) => {
    openEditMailDialog();
});

editMailDialog.addEventListener("submit", (e) => {
    e.preventDefault();
    data = new FormData(e.target);
    fetch(e.target.action, {
        body: data,
        method: "POST"
    }).then((response) => {
        if (response.ok) {
            changeMailOK.showModal();
        } else if (response.status == 403) {
            changeMailErrorMailAlreadyBound.showModal();
        } else {
            changeMailError.showModal();
        }
    });
});

editMailDialog.querySelector("button[type='button']").addEventListener("click", () => editMailDialog.close());