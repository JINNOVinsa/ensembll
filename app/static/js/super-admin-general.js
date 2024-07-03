var profileDialog = document.getElementById("expand-user-dialog");

const users = [];
var entries = [];

fetch("/superAdminPannel/getAllUsersAndAdmin")
.then((response) => {
    if (response.ok) {
        return response.json();
    } else {
        return null;
    }
}).then((data) => {
    if (data != null) {
        for (var usr of data) {
            users.push(usr);
        }
        users.sort((u1, u2) => {
            return u1.approbation - u2.approbation
        });
    } else {
        console.log("No data");
    }
    feedTable();
});

function getUserByID(id) {
    for (var u of users) {
        if (u['id'] === id) {
            return u;
        }
    }
    return null;
}

function openProfileByID(id) {
    if (typeof profileDialog.showModal === "function") {
        var user = getUserByID(id)

        profileDialog.querySelector("#user-name").innerHTML = user['firstName'] + " " + user['lastName'].toUpperCase();

        profileDialog.querySelector("#lastname").innerHTML = user['lastName'];
        profileDialog.querySelector("#firstname").innerHTML = user['firstName'];
        profileDialog.querySelector("#mail").innerHTML = user['mail'];
        if (user['phoneNumber'] === null) {
            profileDialog.querySelector("#tel").innerHTML = "Aucun numéro renseigné";
            profileDialog.querySelector("#tel").style.color = "red";
        } else {
            profileDialog.querySelector("#tel").innerHTML = user['phoneNumber'];
            profileDialog.querySelector("#tel").style.color = "black";
        }
        profileDialog.querySelector("#entity").innerText = user['entity'];
        profileDialog.querySelector("#profile").innerHTML = user['profile'];

        let platesContainer = profileDialog.querySelector("#immat");
        platesContainer.innerHTML = '';
        if (user['plates'].length > 0) {
            for (const plate of user['plates']) {
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
        profileDialog.showModal();

    } else {
        console.log("Navigateur non compatible");
    }
}

function deleteUser(usrId) {
    let data = new FormData();
    data.append('usrId', usrId);
    
    fetch("/superAdminPannel/deleteUser", {
        method: 'POST',
        body: data
    }).then((response) => {
        if (response.ok) {
            if (typeof deleteUserSuccessDialog.showModal === "function") {
                deleteUserSuccessDialog.showModal();
            } else {
                console.log("Navigateur non compataible");
            }
        } else {
            if (typeof deleteUserFailedDialog.showModal === "function") {
                deleteUserFailedDialog.showModal();
            } else {
                console.log("Navigatuer non compatible");
            }
        }
    })
}

Array.from(document.getElementsByClassName("close-user-dialog")).forEach(btn => {
    btn.addEventListener("click", (e) => {
        e.target.closest("dialog").close();
        document.body.style.overflow = "visible";
    });
});