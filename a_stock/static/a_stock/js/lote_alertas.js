document.addEventListener("DOMContentLoaded", function () {
    const hoy = new Date();
    const filas = document.querySelectorAll("#tabla-lotes tr");

    // === COLORES DE FILAS SEGÚN VENCIMIENTO ===
    filas.forEach(fila => {
        const fechaAttr = fila.dataset.fechaVencimiento;
        if (!fechaAttr) return;

        const fechaVto = new Date(fechaAttr);
        const diffDias = (fechaVto - hoy) / (1000 * 60 * 60 * 24);

        if (diffDias <= 0) {
            fila.classList.add("table-danger"); // vencido
        } else if (diffDias <= 30) {
            fila.classList.add("table-warning"); // por vencer
        } else {
            fila.classList.add("table-light"); // vigente
        }
    });

    // === ALERTA DE LOTES (OCULTAR / MOSTRAR CON LOCALSTORAGE) ===
    const alerta = document.getElementById("alerta-lotes");
    const btnCerrar = document.getElementById("btn-cerrar-alerta");
    const btnMostrar = document.getElementById("btn-mostrar-alerta");

    if (btnCerrar && alerta) {
        btnCerrar.addEventListener("click", function () {
            alerta.style.display = "none";
            btnMostrar.classList.remove("d-none");
            localStorage.setItem("alertaLotesOculta", "true");
        });
    }

    if (btnMostrar) {
        btnMostrar.addEventListener("click", function () {
            alerta.style.display = "block";
            btnMostrar.classList.add("d-none");
            localStorage.removeItem("alertaLotesOculta");
        });
    }

    if (localStorage.getItem("alertaLotesOculta") === "true") {
        if (alerta) alerta.style.display = "none";
        if (btnMostrar) btnMostrar.classList.remove("d-none");
    }
});

// 🔔 Control de alerta del lote más próximo
document.addEventListener("DOMContentLoaded", function () {
    const alertaProximo = document.getElementById("alerta-lote-proximo");
    const btnCerrarProximo = document.getElementById("cerrar-alerta-lote-proximo");

    if (alertaProximo && btnCerrarProximo) {
        btnCerrarProximo.addEventListener("click", () => {
            alertaProximo.style.display = "none";
        });
    }
});
