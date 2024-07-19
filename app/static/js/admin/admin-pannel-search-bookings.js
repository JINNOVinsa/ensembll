function searchForBooking(targetString) {
    targetString = targetString.toUpperCase();

    for (i in bookings) {
        if (bookings[i]['userLastname'].toUpperCase().includes(targetString)) {
            entries[i].style.display = 'grid';
            continue;
        }

        if (bookings[i]['userFirstname'].toUpperCase().includes(targetString)) {
            entries[i].style.display = 'grid';
            continue;
        }

        if (bookings[i]['userMail'].toUpperCase().includes(targetString)) {
            entries[i].style.display = 'grid';
            continue;
        }

        if (bookings[i]['userPhoneNumber'] != null && bookings[i]['phoneNumber'].toUpperCase().includes(targetString)) {
            entries[i].style.display = 'grid';
            continue;
        }

        if (bookings[i]['userProfile'].toUpperCase().includes(targetString)) {
            entries[i].style.display = 'grid';
            continue;
        }

        if (bookings[i]['bookingPlate'].toUpperCase().includes(targetString)) {
            entries[i].style.display = "grid";
            continue;
        }

        if (bookings[i]['bookingStart'].toUpperCase().includes(targetString)) {
            entries[i].style.display = "grid";
            continue;
        }

        if (bookings[i]['bookingEnd'].toUpperCase().includes(targetString)) {
            entries[i].style.display = "grid";
            continue;
        }

        if (bookings[i]['bookingDuration'].toUpperCase().includes(targetString)) {
            entries[i].style.display = "grid";
            continue;
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
        searchForBooking(inputEvent.target.value);
    } else {
        Array.from(entries).forEach(entry => {
            entry.style.display = "grid";
        });
    }
})