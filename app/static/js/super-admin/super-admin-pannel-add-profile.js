var addProfileDialog = document.getElementById("add-profile-dialog");
var addProfileSuccessDialog = document.getElementById("add-profile-success-dialog");
var addProfileFailedDialog = document.getElementById("add-profile-failed-dialog");

function openAddProfileDialog() {
    if (typeof addProfileDialog.showModal === "function") {
        addProfileDialog.showModal();
    }
}

document.getElementById("add-profile-btn").addEventListener("click", (e) => {
    openAddProfileDialog();
});

addProfileDialog.addEventListener("submit", (submitEvent) => {
    submitEvent.preventDefault();
    const data = new FormData(submitEvent.target);
    
    if (isNaN(parseInt(data.get("criticity")))) {
        // Enter a valid integer
        // No need to specify user because HTML input type number specify it for us
        return;
    }

    addProfileDialog.close();
    fetch(submitEvent.target.action, {
        method: "POST",
        body: data
    }).then((response) => {
        if (response.ok) {
            if (typeof addProfileSuccessDialog.showModal === "function") {
                addProfileSuccessDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }
        } else {
            if (typeof addProfileFailedDialog.showModal === "function") {
                addProfileFailedDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }
        }

        return response;
    });
});