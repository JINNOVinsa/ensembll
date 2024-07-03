function checkPswd(p) {
    return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$/.test(p);
}

var successDialog = document.getElementById("success-dialog");
var failedDialog = document.getElementById("failed-dialog");

document.getElementById("reset-form").addEventListener("submit", (e) => {
    e.preventDefault();

    data = new FormData(e.target);

    if (data.get("pswd") === data.get("pswd-confirm") && checkPswd(data.get("pswd"))) {
        fetch(e.target.action, {
            body: data,
            method: "POST"
        }).then((response) => {
            if (response.ok) {
                if (typeof successDialog.showModal === "function") {
                    successDialog.showModal();
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
        });
    }
});

var pswdInput1 = document.getElementById("pswd");
var pswdInput2 = document.getElementById("pswd-confirm");

var pswdInvalidWarn = document.getElementById("pswd-criteria");
var pswdDifferentWarn = document.getElementById("pswd-warn");

pswdInput1.addEventListener("input", (e) => {
    if (!checkPswd(e.target.value)) {
        pswdInvalidWarn.classList.remove("hidden");
        pswdInput1.classList.add("invalid");
    } else if (!pswdInvalidWarn.classList.contains("hidden") && checkPswd(e.target.value)) {
        pswdInvalidWarn.classList.add("hidden");
        pswdInput1.classList.remove("invalid");
    }

    if (pswdDifferentWarn.classList.contains("hidden") && pswdInput1.value !== pswdInput2.value) {
        pswdDifferentWarn.classList.remove("hidden");
        pswdInput2.classList.add("invalid");
    } else if (!pswdDifferentWarn.classList.contains("hidden") && pswdInput1.value === pswdInput2.value) {
        pswdDifferentWarn.classList.add("hidden");
        pswdInput2.classList.remove("invalid");
    }
});