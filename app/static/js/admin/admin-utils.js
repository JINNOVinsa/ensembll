var criticalOpenInProgressDialog = document.getElementById("critical-open-in-progress-dialog");
var criticalOpenSuccessDialog = document.getElementById("critical-open-success-dialog");
var criticalOpenFailedDialog = document.getElementById("critical-open-failed-dialog");

function openBarrier() {
    if (typeof criticalOpenInProgressDialog.showModal === "function") {
        criticalOpenInProgressDialog.showModal();
    } else {
        console.log("Navigateur non compatible");
    }

    fetch('/critical/open', {
        method: 'GET'
    }).then((response) => {
        try {
            criticalOpenInProgressDialog.close();            
        } catch (error) {
            
        }
        if (response.ok) {
            if (typeof criticalOpenSuccessDialog.showModal === "function") {
                criticalOpenSuccessDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }
        } else {
            if (typeof criticalOpenFailedDialog.showModal === "function") {
                criticalOpenFailedDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }
        }
    })
}

Array.from(document.getElementsByClassName('critical-open-btn')).forEach((elmt) => elmt.addEventListener('click', (e) => openBarrier()));

document.getElementById("problem-btn").addEventListener("click", () => {
    openReportProblemDialog();
});

document.getElementById("under-problem-btn").addEventListener("click", () => {
    openReportProblemDialog();
});

function openReportProblemDialog() {
    let dialog = document.getElementById("report-problem-dialog");
    if (typeof dialog.showModal === "function") {
        fetchUserInformation();
        dialog.showModal();
    } else {
        console.log("Navigateur non compatible");
    }

    document.getElementById("problemType").addEventListener("change", function() {
        let value = this.value;
        let barrierIssueFields = document.getElementById("barrierIssueFields");
        let planningFullFields = document.getElementById("planningFullFields");
        let otherIssueField = document.getElementById("otherIssueField");
        let barrierIssueConfirmation = document.getElementById("barrierIssueConfirmation");
        
        // Reset display states
        barrierIssueFields.style.display = "none";
        planningFullFields.style.display = "none";
        otherIssueField.style.display = "none";
        barrierIssueConfirmation.style.display = "none";
    
        certifyInfo.required = false;
    
        if (value === "barrierIssue") {
            barrierIssueFields.style.display = "block";
            barrierIssueConfirmation.style.display = "block";
            certifyInfo.required = true;
        } else if (value === "planningFull") {
            planningFullFields.style.display = "block";
        } else if (value === "other") {
            otherIssueField.style.display = "block";
        }
    });        
}

function fetchUserInformation() {
    fetch('/getUserInformation', {
        method: 'GET'
    }).then(response => response.json())
    .then(data => {
        document.getElementById("firstName").value = data.firstName;
        document.getElementById("lastName").value = data.lastName;
        document.getElementById("email").value = data.email;

        let plateSelect = document.getElementById("plateNumber");
        plateSelect.innerHTML = '';

        data.plates.forEach(plate => {
            let option = new Option(plate, plate);
            plateSelect.appendChild(option);
        });
    });
}

document.getElementById("report-problem-form").addEventListener("submit", function(event) {
    event.preventDefault();
    submitProblemReport();
});

function submitProblemReport() {
    let problemType = document.getElementById("problemType").value;
    let formData = new FormData();

    formData.append("firstName", document.getElementById("firstName").value);
    formData.append("lastName", document.getElementById("lastName").value);
    formData.append("email", document.getElementById("email").value);

    let url = '';

    if (problemType === "planningFull") {
        formData.append("bookingStartDate", document.getElementById("bookingStartDate").value);
        formData.append("bookingStartTime", document.getElementById("bookingStartTime").value);
        formData.append("bookingEndDate", document.getElementById("bookingEndDate").value);
        formData.append("bookingEndTime", document.getElementById("bookingEndTime").value);
        formData.append("repetition", document.getElementById("repetition").value);
        url = '/report/planningFull';
    } else if (problemType === "other") {
        formData.append("comment", document.getElementById("comment").value);
        url = '/report/other';
    } else if (problemType === "barrierIssue") {
        formData.append("plateNumber", document.getElementById("plateNumber").value);
        formData.append("passageDate", document.getElementById("passageDate").value);
        formData.append("passageTime", document.getElementById("passageTime").value);
        url = '/report/bearer';
    }

    fetch(url, {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            document.getElementById("report-problem-dialog").close();
            showSuccessDialog();
        } else {
            throw new Error('La requête a échoué');
        }
    }).catch(error => {
        showErrorDialog();
    });
}

function showSuccessDialog() {
    let successDialog = document.getElementById("problem-report-success-dialog");
    if (typeof successDialog.showModal === "function") {
        successDialog.showModal();
    } else {
        console.log("Navigateur non compatible avec HTML dialog.");
    }
}

function showErrorDialog() {
    let errorDialog = document.getElementById("problem-report-failure-dialog");
    if (typeof errorDialog.showModal === "function") {
        errorDialog.showModal();
    } else {
        console.log("Navigateur non compatible avec HTML dialog.");
    }
}

function updateErrorCounts() {
    fetch('/get_error_counts')
        .then(response => response.json())
        .then(data => {
            document.getElementById("bearerTrue-value").textContent = data.bearerTrue;
            document.getElementById("bearerFalse-value").textContent = data.bearerFalse;
        })
        .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    updateErrorCounts();
});