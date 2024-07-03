/* Park duration by plate */

document.getElementById("park-duration-by-plate").addEventListener("submit", (e) => {
    e.preventDefault();

    const result_html = document.getElementById("park-duration-result");
    result_html.classList.add("hidden");

    const inputs = e.target.elements;

    const params = new URLSearchParams({"plate": inputs["plate-duration"].value});
    fetch(e.target.action+"?"+params).then((response) => {
        if (response.ok) {
            return response.json();
        }

        result_html.innerHTML = `Echec de la demande des données. Vérifiez que la plaque entrée correspond au format <span class="italic">AA-123-AA</span> ou <span class="italic">1234-AA-56</span>`;
        result_html.classList.remove("hidden");

        return null;
    }).then((data) => {
        if (data === null) {
            return;
        }

        result_html.innerHTML = `Le véhicule portant la plaque <span>${inputs["plate-duration"].value}</span> a stationné dans le parking pendant <span>${data["duration"]["days"]}j ${data["duration"]["hours"]}h ${data["duration"]["minutes"]}m</span>`;

        if (data["present"]) {
            result_html.innerHTML += `<br>Le véhicule est présent dans le parking depuis <span>${data["ongoing"]["days"]}j ${data["ongoing"]["hours"]}h ${data["ongoing"]["minutes"]}m</span>`;
        }
        
        result_html.classList.remove("hidden");
    })
});


/* Park duration by entity */

document.getElementById("park-duration-by-entity").addEventListener("submit", (e) => {
    e.preventDefault();

    const result_html = document.getElementById("park-duration-result");
    const inputs = e.target.elements;
    const params = new URLSearchParams({"entity": inputs["entity-duration"].value});
    fetch(e.target.action+"?"+params).then((response) => {
        if (response.ok) {
            return response.json();
        }

        result_html.innerText = `Echec de la demande des données. Veuillez choisir une structure dans la liste`;
        result_html.classList.remove("hidden");
        return null;
    }).then((data) => {
        if (data === null) {
            return;
        }
        
        result_html.innerHTML = `Les véhicules de la structure <span>${inputs["entity-duration"].selectedOptions[0].text}</span> ont stationné un total de <span>${data["duration"]["days"]}j ${data["duration"]["hours"]}h ${data["duration"]["minutes"]}m</span>`;
        result_html.classList.remove("hidden");
    });
});