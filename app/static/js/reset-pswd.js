var sucessDialog = document.getElementById("success-dialog")
var failedDialog = document.getElementById("failed-dialog");

let submitBtn = document.querySelector("button[type='submit']");

document.getElementById("reset-form").addEventListener("submit", (e) => {
    e.preventDefault();
    data = new FormData(e.target);
    submitBtn.disabled = true;
    fetch(e.target.action, {
        body: data,
        method: "POST"
    }).then((response) => {
        if (response.ok) {
            if (typeof sucessDialog.showModal === "function") {
                sucessDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }
        } else {
            if (typeof failedDialog.showModal === "function") {
                failedDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }
        }
        submitBtn.disabled = false;
    });
});