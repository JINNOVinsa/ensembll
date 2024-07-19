var inputPswd = document.getElementById("input-pswd");
var inputPswdMatch = document.getElementById("input-repeat-pswd");
var warnPswdCriteria = document.getElementById("pswd-criteria");
var warnPswdMatch = document.getElementById("pswd-match");
var profilesSelector = document.getElementById("profile-type-select");

var inputMail = document.getElementById("mail");
var inputTel = document.getElementById("phonenumber");
var warnMail = document.getElementById("warn-mail");
var warnTel = document.getElementById("warn-phonenumber");
var inputPlate = document.getElementById("plate");

function checkPassword(password) {
    // Password must have lower and upper case with at least one number and one special character
    return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$/.test(password);
}

function matchPassword() {
    return inputPswd.value === inputPswdMatch.value;
}

function checkPlate(plate) {
    return /^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$/.test(plate) || /^[0-9]{4}-[A-Z]{2}-[0-9]{2}$/.test(plate) || /^[0-9]{1}-[A-Z]{3}-[0-9]{3}$/.test(plate) || /^[0-9]{3}-[A-Z]{3}-[0-9]{2}$/.test(plate);
}

inputPswd.addEventListener('input', (event) => {
    if (warnPswdCriteria.classList.contains("hidden") && !checkPassword(event.target.value)) {
        // Password was good before but isn't now
        warnPswdCriteria.classList.remove("hidden");
        inputPswd.classList.add('error-input');
    } else if (!warnPswdCriteria.classList.contains("hidden") && checkPassword(event.target.value)) {
        // Password wasn't good but is now
        warnPswdCriteria.classList.add("hidden");
        inputPswd.classList.remove('error-input');
    }

    // Check if password match each time we change this input too
    if (warnPswdMatch.classList.contains('hidden') && !matchPassword()) {
        warnPswdMatch.classList.remove('hidden');
        inputPswdMatch.classList.add('error-input');
    } else if (!warnPswdMatch.classList.contains('hidden') && matchPassword()) {
        warnPswdMatch.classList.add('hidden');
        inputPswdMatch.classList.remove('error-input');
    }
});

inputPswdMatch.addEventListener('input', (event) => {
    if (warnPswdMatch.classList.contains('hidden') && !matchPassword()) {
        warnPswdMatch.classList.remove('hidden');
        inputPswdMatch.classList.add('error-input');
    } else if (!warnPswdMatch.classList.contains('hidden') && matchPassword()) {
        warnPswdMatch.classList.add('hidden');
        inputPswdMatch.classList.remove('error-input');
    }
});

inputPlate.addEventListener('input', (e) => {
    if (e.target.value != '' && checkPlate(e.target.value)) {
        e.target.classList.remove('error-input');
    } else {
        e.target.classList.add('error-input');
    }
});



document.getElementById('create-form').addEventListener("submit", (event) => {
    event.preventDefault(); // Empêche la soumission par défaut du formulaire

    // Réinitialisation des styles et des avertissements
    inputMail.style.borderColor = "#0071ba";
    inputTel.style.borderColor = "#0071ba";
    inputPlate.style.borderColor = "#0071ba";
    warnMail.classList.add("hidden");
    warnTel.classList.add("hidden");

    // Vérification du mot de passe
    if (!checkPassword(inputPswd.value)) {
        warnPswdCriteria.classList.remove("hidden");
        inputPswd.classList.add('error-input');
        return; // Arrête la soumission si le mot de passe n'est pas valide
    } else {
        warnPswdCriteria.classList.add("hidden");
        inputPswd.classList.remove('error-input');
    }

    // Vérification de la correspondance des mots de passe
    if (!matchPassword()) {
        warnPswdMatch.classList.remove('hidden');
        inputPswdMatch.classList.add('error-input');
        return; // Arrête la soumission si les mots de passe ne correspondent pas
    } else {
        warnPswdMatch.classList.add('hidden');
        inputPswdMatch.classList.remove('error-input');
    }

    // Vérification de la plaque d'immatriculation
    if (!checkPlate(inputPlate.value)) {
        inputPlate.classList.add('error-input');
        // Vous pouvez ajouter ici une notification ou un message d'erreur
        return; // Arrête la soumission si la plaque d'immatriculation n'est pas valide
    } else {
        inputPlate.classList.remove('error-input');
    }

    // Création de FormData et envoi de la requête
    const formData = new FormData(event.target);
    fetch(event.target.action, {
        method: "POST",
        body: formData
    }).then((response) => {
        return response.text();
    }).then((text) => {
        switch (text) {
            case "MAIL ALREADY BOUND":
                inputMail.style.borderColor = "red";
                warnMail.classList.remove("hidden");
                break;
        
            case "INCORRECT TEL":
                inputTel.style.borderColor = "red";
                warnTel.classList.remove("hidden");
                break;

            default:
                document.documentElement.innerHTML = text;
                break;
        }
    });
});


function clearSelector(select) {
    let l = select.options.length;
    for (let i = 0; i < l; i++) {
        select.remove(0);
    }
}

function fetchProfilesByEntity(entityId) {
    fetch('/profiles?' + new URLSearchParams({'entity': entityId})).then((response) => {
        return response.json();
    }).then((data) => {
        for (let p of data) {
            let o = document.createElement('option');
            o.text = p;
            profilesSelector.add(o);
        }
    });
}

document.getElementById('entity-select').addEventListener('change', (e) => {
    clearSelector(profilesSelector);
    fetchProfilesByEntity(e.target.value);
});

fetchProfilesByEntity(document.getElementById('entity-select').value);