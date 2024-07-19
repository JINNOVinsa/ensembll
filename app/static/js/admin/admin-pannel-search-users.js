function searchForUser(targetString) {
    targetString = targetString.toUpperCase();
    for (i in users) {
        console.log(users);
        if (users[i]['lastName'].toUpperCase().includes(targetString)) {
            entries[i].style.display = 'grid';
            continue;
        }

        if (users[i]['firstName'].toUpperCase().includes(targetString)) {
            entries[i].style.display = 'grid';
            continue;
        }

        if (users[i]['mail'].toUpperCase().includes(targetString)) {
            entries[i].style.display = 'grid';
            continue;
        }

        if (users[i]['phoneNumber'] != null && users[i]['phoneNumber'].toUpperCase().includes(targetString)) {
            entries[i].style.display = 'grid';
            continue;
        }
        
        if (users[i]['profile'].toUpperCase().includes(targetString)) {
            entries[i].style.display = 'grid';
            continue;
        }

        for (plate of users[i]["plates"]) {
            console.log(plate);
            if (plate.toUpperCase().includes(targetString)) {
                entries[i].style.display = 'grid';
                break;
            }
        }
    }
}

var searchInput = document.getElementById("search-bar");
searchInput.value = ""

searchInput.addEventListener("input", (inputEvent) => {
    if (inputEvent.target.value != "") {
        Array.from(entries).forEach(entry => {
            entry.style.display = "none";
        });
        searchForUser(inputEvent.target.value);
    } else {
        Array.from(entries).forEach(entry => {
            entry.style.display = "grid";
        });
    }

    console.log(inputEvent.target.value);
});