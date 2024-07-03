Array.from(document.getElementsByClassName("alert-detail")).forEach((btn) => {
    
    btn.addEventListener("click", (event) => {
        let notifWrapper = event.target.closest("div.notification");

        let alertContainer = notifWrapper.querySelector(".alert-expand");
        let alertWrapper = notifWrapper.querySelector(".alert-expand-wrapper");

        if (alertContainer.classList.contains("expand")) {
            alertContainer.classList.remove("expand");
            alertContainer.style.height = "0px";

            event.target.innerText = "Afficher le détail des alertes";
        } else {
            alertContainer.classList.add("expand");
            alertContainer.style.height = alertWrapper.getBoundingClientRect().height + "px";

            event.target.innerText = "Masquer le détail des alertes";
        }

    });
});

Array.from(document.getElementsByClassName("delete-alerts")).forEach((btn) => {
    
    btn.addEventListener("click", async (event) => {
        let notifWrapper = event.target.closest("div.notification");

        const data = new FormData();
        data.append("plate", notifWrapper.id);

        const response = await fetch("/admin/notification/delete", {method: 'POST', body: data});

        if (response.ok) {
            location.href = "/admin/notifications";
        } else {
            let failedDialog = document.getElementById("delete-alerts-failed");

            failedDialog.querySelector("span#delete-plate").value = notifWrapper.id;

            failedDialog.showModal();
        }
    });

});