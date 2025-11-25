document.addEventListener("DOMContentLoaded", () => {
    const botones = document.querySelectorAll(".btn-procesar");

    botones.forEach(boton => {
        boton.addEventListener("click", async () => {

            const url = boton.dataset.url;
            const form = boton.closest("form");

            const formData = new FormData(form);

            try {
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    alert(data.success);
                    form.remove(); // sacar compra del listado
                } else {
                    alert("Error: " + data.error);
                }
            } catch (error) {
                alert("Error inesperado: " + error);
            }
        });
    });
});
