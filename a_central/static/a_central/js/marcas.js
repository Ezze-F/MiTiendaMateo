$(document).ready(function() {
    if (!window.AppUrls) {
        console.error("window.AppUrls no está definido. Asegúrate de incluir la definición de URLs en el template antes de cargar este JS.");
        return;
    }

    let dataTableDisponibles = null;
    let dataTableEliminadas = null;

    const csrfToken = $('[name="csrfmiddlewaretoken"]').val();
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    });

    const recargarTablas = () => {
        if (dataTableDisponibles) dataTableDisponibles.ajax.reload(null, false);
        if (dataTableEliminadas) dataTableEliminadas.ajax.reload(null, false); 
    };

    // Tabla disponibles
    dataTableDisponibles = $('#dataTableMarcasDisponibles').DataTable({
        "ajax": {
            "url": window.AppUrls.listarMarcasActivas,
            "dataSrc": "data",
            "error": function(xhr, error, thrown) {
                console.error("Error al cargar dataTableMarcasDisponibles:", thrown, xhr.responseText);
            }
        },
        "columns": [
            { "data": "id_marca", "visible": false },
            { "data": "nombre_marca" },
            {
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_marca;
                    const nombre = row.nombre_marca;
                    return `
                        <div class="d-flex justify-content-center">
                            <button class="btn btn-info btn-sm me-2 btn-editar" data-id="${id}" title="Editar">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-danger btn-sm btn-borrar" data-id="${id}" data-nombre="${nombre}" title="Eliminar (Baja Lógica)">
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

    // Tabla eliminadas
    $('button[data-bs-target="#marcasEliminadasTab"]').on('shown.bs.tab', function() {
        if (!dataTableEliminadas) {
            dataTableEliminadas = $('#dataTableMarcasEliminadas').DataTable({
                "ajax": {
                    "url": window.AppUrls.listarMarcasEliminadas,
                    "dataSrc": "data",
                    "error": function(xhr, error, thrown) {
                        console.error("Error al cargar dataTableMarcasEliminadas:", thrown, xhr.responseText);
                    }
                },
                "columns": [
                    { "data": "id_marca", "visible": false },
                    { "data": "nombre_marca" },
                    {
                        "data": "fh_borrado_m",
                        "className": "text-center",
                        "render": function(data) {
                            return data ? data : 'N/A';
                        }
                    },
                    {
                        "data": null,
                        "render": function(data, type, row) {
                            const id = row.id_marca;
                            const nombre = row.nombre_marca;
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
        }
        if (dataTableEliminadas) dataTableEliminadas.columns.adjust().responsive.recalc();
    });

    $('button[data-bs-target="#marcasDisponiblesTab"]').on('shown.bs.tab', function() {
        if (dataTableDisponibles) dataTableDisponibles.columns.adjust().responsive.recalc();
    });

    // Registro
    $('#registrarMarcaForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        form.find('.form-control').removeClass('is-invalid');
        $('#form-error-alerts').addClass('d-none');
        $('#error-list').empty();

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message, 'success');
                $('#registrarMarcaModal').modal('hide');
                form[0].reset();
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                let generalErrorMessage = r?.error || 'Error desconocido al registrar marca.';
                if (r && r.details) {
                    let errorListHtml = '';
                    for (const field in r.details) {
                        const message = r.details[field];
                        $(`#${field}`).addClass('is-invalid');
                        $(`#error-${field}`).text(message);
                        errorListHtml += `<li>${message}</li>`;
                        if (field === 'nombre_marca') {
                            generalErrorMessage = message;
                        }
                    }
                    $('#error-list').html(errorListHtml);
                    $('#form-error-alerts').removeClass('d-none');
                }
                Swal.fire('Error al registrar', generalErrorMessage, 'error');
            }
        });
    });

    // Modificar
    $('#dataTableMarcasDisponibles tbody').on('click', '.btn-editar', function() {
        const rowData = dataTableDisponibles.row($(this).parents('tr')).data();
        $('#modificar_id_marca').val(rowData.id_marca);
        $('#modificar_nombre_marca').val(rowData.nombre_marca);
        $('#modificar-error-alert').addClass('d-none').text('');
        $('#modificarMarcaModal').modal('show');
    });

    $('#modificarMarcaForm').on('submit', function(e) {
        e.preventDefault();
        const id = $('#modificar_id_marca').val();
        const form = $(this);
        $('#modificar-error-alert').addClass('d-none').text('');

        $.ajax({
            url: window.AppUrls.modificarMarca + id + '/',
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message, 'success');
                $('#modificarMarcaModal').modal('hide');
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                const errorMessage = r?.error || r?.details?.nombre_marca || 'Error al modificar marca.';
                Swal.fire('Error', errorMessage, 'error');
                $('#modificar-error-alert').text(errorMessage).removeClass('d-none');
            }
        });
    });

    // Borrado lógico
    $('#dataTableMarcasDisponibles tbody').on('click', '.btn-borrar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se dará de baja (borrado lógico) la marca: ${nombre}.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, dar de baja'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.borrarMarca + id + '/',
                    method: 'POST',
                    success: function(response) {
                        Swal.fire('¡Baja realizada!', response.message, 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al procesar la baja.', 'error');
                    }
                });
            }
        });
    });

    // Restaurar
    $('#dataTableMarcasEliminadas tbody').on('click', '.btn-restaurar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se restaurará la marca: ${nombre}.`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#28a745',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, restaurar'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.recuperarMarca + id + '/',
                    method: 'POST',
                    success: function(response) {
                        Swal.fire('¡Restaurada!', response.message, 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al restaurar marca.', 'error');
                    }
                });
            }
        });
    });
});
