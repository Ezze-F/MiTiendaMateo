// Configuración global de DataTables en español
function configurarDataTable(selector) {
    $(selector).DataTable({
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.10.25/i18n/Spanish.json"
        },
        responsive: true,
        dom: '<"top"lf>rt<"bottom"ip><"clear">',
        order: [[0, 'desc']], // Orden por primera columna (ID)
        columnDefs: [
            {
                targets: -1, // Última columna (ej: acciones, si existiera)
                orderable: false,
                searchable: false,
                className: "dt-center"
            }
        ]
    });
}

$(document).ready(function () {
    // Inicializa tabla de "Disponibles"
    configurarDataTable('#tablaDisponibles');

    // Inicializa otras tablas cuando se muestra su pestaña
    $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = $(e.target).attr("href");
        if (target === "#eliminados" && !$.fn.dataTable.isDataTable('#tablaEliminados')) {
            configurarDataTable('#tablaEliminados');
        }
        if (target === "#totales" && !$.fn.dataTable.isDataTable('#tablaTotales')) {
            configurarDataTable('#tablaTotales');
        }
    });
});