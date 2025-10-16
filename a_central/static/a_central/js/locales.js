$(document).ready(function() {
    let dataTableDisponibles;
    let dataTableEliminados;

    // Función auxiliar para recargar ambas tablas
    const recargarTablas = () => {
        if (dataTableDisponibles) dataTableDisponibles.ajax.reload(null, false);
        if (dataTableEliminados) dataTableEliminados.ajax.reload(null, false);
    };

    // ============================================================
    // 1. DataTable: Locales Disponibles
    // ============================================================
    dataTableDisponibles = $('#dataTableLocalesDisponibles').DataTable({
        "ajax": {
            // Asume que la URL de la vista es /central/locales/ y la API es /central/locales/disponibles/
            "url": window.location.pathname.replace('locales/', 'locales/disponibles/'),
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_loc_com", "visible": false },
            { "data": "nombre_loc_com" },
            { "data": "provincia_nombre" }, // Nombre de la provincia serializado en views.py
            { "data": "telefono_loc_com", "defaultContent": "N/A" },
            { "data": "direccion_loc_com", "defaultContent": "N/A" },
            { "data": "cod_postal_loc_com", "defaultContent": "N/A" },
            { "data": "fecha_alta_loc_com" },
            {
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_loc_com;
                    const nombre = row.nombre_loc_com;
                    return `
                        <div class="d-flex justify-content-center">
                            <button class="btn btn-info btn-sm me-2 btn-editar" data-id="${id}" title="Editar">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-danger btn-sm btn-borrar" data-id="${id}" data-nombre="${nombre}" title="Dar de baja">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                },
                "orderable": false,
                "className": "text-center"
            }
        ],
        "language": { "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" },
        "responsive": true
    });

    // ============================================================
    // 2. DataTable: Locales Eliminados
    // ============================================================
    dataTableEliminados = $('#dataTableLocalesEliminados').DataTable({
        "ajax": {
            "url": window.location.pathname.replace('locales/', 'locales/eliminados/'),
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_loc_com", "visible": false },
            { "data": "nombre_loc_com" },
            { "data": "provincia_nombre" },
            {
                "data": "fh_borrado_lc", // Campo fh_borrado_lc del modelo
                "className": "text-center",
                "render": function(data) { return data ? data : 'N/A'; }
            },
            {
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_loc_com;
                    const nombre = row.nombre_loc_com;
                    return `
                        <div class="d-flex justify-content-center">
                            <button class="btn btn-success btn-sm btn-restaurar" data-id="${id}" data-nombre="${nombre}" title="Restaurar">
                                <i class="fas fa-undo"></i>
                            </button>
                        </div>
                    `;
                },
                "orderable": false,
                "className": "text-center"
            }
        ],
        "language": { "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" },
        "responsive": true
    });

    // ============================================================
    // 3. Registro de Local Comercial
    // ============================================================
    $('#registrarLocalForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);

        form.find('.form-control, .form-select').removeClass('is-invalid');
        $('#form-error-alerts').addClass('d-none');

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Local comercial registrado correctamente.', 'success');
                $('#registrarLocalModal').modal('hide');
                form[0].reset();
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                let errorListHtml = '';

                if (r && r.details) {
                    for (const field in r.details) {
                        const message = r.details[field];
                        const input = $(`#${field}`);
                        input.addClass('is-invalid');
                        $(`#error-${field}`).text(message);
                        errorListHtml += `<li>${message}</li>`;
                    }
                    $('#error-list').html(errorListHtml);
                    $('#form-error-alerts').removeClass('d-none');
                } else {
                    Swal.fire('Error', r?.error || 'Error al registrar local comercial.', 'error');
                }
            }
        });
    });

    // ============================================================
    // 4. Modificación de Local Comercial
    // ============================================================
    $('#dataTableLocalesDisponibles tbody').on('click', '.btn-editar', function() {
        const rowData = dataTableDisponibles.row($(this).parents('tr')).data();

        // Obtener el ID de la Provincia (esto requiere un ajuste en views.py para incluir id_provincia)
        // Ya que la vista solo serializa 'provincia_nombre', necesitamos el ID de la provincia
        // para establecer correctamente el <select> en el modal de modificación.
        
        // **Nota Importante:** Para que esta línea funcione, debes asegurarte que 
        // tu función _serialize_locales en views.py incluya el id_provincia.
        // Ejemplo de views.py: 'id_provincia': loc.id_provincia_id, 
        
        // Suponiendo que has añadido 'id_provincia' a la serialización:
        const id_provincia = rowData.id_provincia; 

        $('#modificar_id_loc_com').val(rowData.id_loc_com);
        $('#modificar_id_provincia').val(id_provincia); 
        $('#modificar_nombre_loc_com').val(rowData.nombre_loc_com);
        $('#modificar_cod_postal_loc_com').val(rowData.cod_postal_loc_com);
        $('#modificar_telefono_loc_com').val(rowData.telefono_loc_com);
        $('#modificar_direccion_loc_com').val(rowData.direccion_loc_com);
        $('#modificar_fecha_alta_loc_com').val(rowData.fecha_alta_loc_com);

        $('#modificarLocalModal').modal('show');
    });

    $('#modificarLocalForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const id = $('#modificar_id_loc_com').val();

        $('#modificar-error-alert').addClass('d-none').text('');

        $.ajax({
            url: window.AppUrls.modificarLocal + id + '/',
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Local comercial modificado correctamente.', 'success');
                $('#modificarLocalModal').modal('hide');
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                const errorMessage = r?.error || 'Error al modificar local comercial.';
                $('#modificar-error-alert').text(errorMessage).removeClass('d-none');
            }
        });
    });

    // ============================================================
    // 5. Baja/Borrado Lógico
    // ============================================================
    $('#dataTableLocalesDisponibles tbody').on('click', '.btn-borrar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se dará de baja al local comercial: ${nombre}.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, dar de baja'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.borrarLocal + id + '/',
                    method: 'POST',
                    data: { csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val() },
                    success: function(response) {
                        Swal.fire('¡Baja realizada!', response.message || 'Local comercial borrado.', 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al procesar la baja.', 'error');
                    }
                });
            }
        });
    });

    // ============================================================
    // 6. Restauración
    // ============================================================
    $('#dataTableLocalesEliminados tbody').on('click', '.btn-restaurar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se restaurará al local comercial: ${nombre}.`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#28a745',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, restaurar'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.recuperarLocal + id + '/',
                    method: 'POST',
                    data: { csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val() },
                    success: function(response) {
                        Swal.fire('¡Restaurado!', response.message || 'LocalcComercial restaurado.', 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al restaurar local comercial.', 'error');
                    }
                });
            }
        });
    });

    // ============================================================
    // 7. Ajuste de columnas al cambiar pestañas
    // ============================================================
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
        const targetId = $(e.target).attr("data-bs-target");

        if (targetId === '#localesEliminadosTab' && dataTableEliminados) {
            dataTableEliminados.columns.adjust().responsive.recalc();
        }
        if (targetId === '#localesDisponiblesTab' && dataTableDisponibles) {
            dataTableDisponibles.columns.adjust().responsive.recalc();
        }
    });
});