var editEntitySpotsBtn = document.getElementsByClassName("edit-spots");
var editSpotsDialog = document.getElementById("edit-spots-dialog");
var closeEditSpotsDialog = document.getElementById("close-spots-edit-dialog");

var editSpotsSuccessDialog = document.getElementById("edit-spots-success");
var editSpotsFailedDialog = document.getElementById("edit-spots-failed");

var currentEntity = null;

var addEntityDialog = document.getElementById("addEntity");
var addEntityBtn = document.getElementById("add-entity");
var deleteEntityButtons = document.getElementsByClassName("delete-entity");
var deleteEntityDialog = document.getElementById("deleteEntity");

addEntityBtn.addEventListener("click", function() {
    if (typeof addEntityDialog.showModal === "function") {
        addEntityDialog.showModal();
    } else {
        console.log("Navigateur non compatible");
    }
});

addEntityDialog.addEventListener("submit", function(e) {
    e.preventDefault();
    let form = e.target;
    let data = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: data
    }).then(response => {
        if (response.ok) {
            window.location.reload(); // Recharger la page ou gérer l'affichage du succès
        } else {
            // Gérer l'affichage de l'échec
        }
    });
});

function openEditSpotsDialog(entityName, baseSpots) {
    if (typeof editSpotsDialog.showModal === "function") {
        editSpotsDialog.querySelector("#spots-entity-name").innerText = entityName;
        editSpotsDialog.querySelector("#new-spots-input").value = baseSpots;

        editSpotsDialog.showModal();
    } else {
        console.log("Navigateur non compatible");
    }
}

function putNewSpots(endpoint, id, spots) {
    let data = new FormData();
    data.append("id", id);
    data.append("spots", spots);
    fetch(endpoint, {
        body: data,
        method: "PUT"
    }).then((response) => {
        if (response.ok) {
            currentEntity = null;
            editSpotsDialog.close();
            
            if (typeof editSpotsSuccessDialog.showModal === "function") {
                editSpotsSuccessDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }
        } else {
            if (typeof editSpotsFailedDialog.showModal === "function") {
                editSpotsFailedDialog.showModal();
            } else {
                console.log("Navigateur non compatible");
            }
        }
    })
}

Array.from(deleteEntityButtons).forEach((btn) => btn.addEventListener("click", (e) => {
    let entry = btn.closest('.entry');
    let name = entry.querySelector(".entity-title").innerText;
    let entityId = entry.id;

    deleteEntityDialog.querySelector("#name").value = name;
    deleteEntityDialog.querySelector("#entity-id").value = entityId;

    if (typeof deleteEntityDialog.showModal === "function") {
        deleteEntityDialog.showModal();
    } else {
        console.log("Navigateur non compatible");
    }
}));


deleteEntityDialog.addEventListener("submit", (e) => {
    e.preventDefault();
    let form = e.target;
    let data = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: data
    }).then(response => {
        if (response.ok) {
            window.location.reload(); // Recharger la page ou gérer l'affichage du succès
        } else {
            // Gérer l'affichage de l'échec
        }
    });
});

document.getElementById("close-delete-entity-dialog").addEventListener("click", () => deleteEntityDialog.close());

document.getElementById("close-add-entity-dialog").addEventListener("click", () => addEntityDialog.close());

Array.from(editEntitySpotsBtn).forEach((btn) => btn.addEventListener("click", (e) => {
    let entry = btn.parentNode;
    let name = entry.querySelector(".entity-title").innerText;
    let spots = entry.querySelector(".entity-spots").innerText;

    currentEntity = entry.id;
    openEditSpotsDialog(name, spots);
}));

editSpotsDialog.addEventListener("submit", (e) => {
    e.preventDefault();
    putNewSpots(e.target.action, currentEntity, e.target.elements['spots'].value);
});

closeEditSpotsDialog.addEventListener("click", () => editSpotsDialog.close());