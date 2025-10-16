$(document).ready(function() {
    if (!window.AppUrls) {
        console.error("window.AppUrls no está definido. Asegúrate de incluir la definición de URLs en el template antes de cargar este JS.");
        return; // No continuar si no hay URLs
    }

    let dataTableDisponibles = null;
    let dataTableEliminadas = null;

    // Configuración global de AJAX para Django (CSRF Token)
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

    // Inicialización tabla disponibles
    dataTableDisponibles = $('#dataTableProvinciasDisponibles').DataTable({
        "ajax": {
            "url": window.AppUrls.listarProvinciasActivas, 
            "dataSrc": "data",
            "error": function(xhr, error, thrown) {
                console.error("Error al cargar dataTableDisponibles:", thrown, xhr.responseText);
            }
        },
        "columns": [
            { "data": "id_provincia", "visible": false }, 
            { "data": "nombre_provincia" },
            {
                "data": null,
                "render": function (data, type, row) {
                    const id = row.id_provincia;
                    const nombre = row.nombre_provincia;
                    return `
                        <div class="d-flex justify-content-center">
                            <button class="btn btn-info btn-sm me-2 btn-editar"
                                data-id="${id}" title="Editar">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-danger btn-sm btn-borrar"
                                data-id="${id}" data-nombre="${nombre}"
                                title="Eliminar (Baja Lógica)">
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

    // Inicialización tabla eliminadas al mostrar la pestaña
    $('button[data-bs-target="#provinciasEliminadasTab"]').on('shown.bs.tab', function () {
        if (!dataTableEliminadas) {
            dataTableEliminadas = $('#dataTableProvinciasEliminadas').DataTable({
                "ajax": {
                    "url": window.AppUrls.listarProvinciasEliminadas,
                    "dataSrc": "data",
                    "error": function(xhr, error, thrown) {
                        console.error("Error al cargar dataTableEliminadas:", thrown, xhr.responseText);
                    }
                },
                "columns": [
                    { "data": "id_provincia", "visible": false }, 
                    { "data": "nombre_provincia" },
                    {
                        "data": "fh_borrado_p",
                        "className": "text-center",
                        "render": function (data) {
                            return data ? data : 'N/A';
                        }
                    },
                    {
                        "data": null,
                        "render": function (data, type, row) {
                            const id = row.id_provincia;
                            const nombre = row.nombre_provincia;
                            return `
                                <div class="d-flex justify-content-center">
                                    <button class="btn btn-success btn-sm btn-restaurar"
                                        data-id="${id}" data-nombre="${nombre}"
                                        title="Restaurar">
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
        if (dataTableEliminadas) {
            dataTableEliminadas.columns.adjust().responsive.recalc();
        }
    });

    $('button[data-bs-target="#provinciasDisponiblesTab"]').on('shown.bs.tab', function () {
        if (dataTableDisponibles) {
            dataTableDisponibles.columns.adjust().responsive.recalc();
        }
    });

    // Registro
    $('#registrarProvinciaForm').on('submit', function(e) {
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
                $('#registrarProvinciaModal').modal('hide');
                form[0].reset();
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                let generalErrorMessage = r?.error || 'Error desconocido al registrar provincia.';

                if (r && r.details) {
                    let errorListHtml = '';
                    for (const field in r.details) {
                        const message = r.details[field];
                        $(`#${field}`).addClass('is-invalid');
                        $(`#error-${field}`).text(message); 
                        errorListHtml += `<li>${message}</li>`;
                        
                        if (field === 'nombre_provincia') { 
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

    // Modificación
    $('#dataTableProvinciasDisponibles tbody').on('click', '.btn-editar', function() {
        const rowData = dataTableDisponibles.row($(this).parents('tr')).data();
        $('#modificar_id_provincia').val(rowData.id_provincia);
        $('#modificar_nombre_provincia').val(rowData.nombre_provincia); 
        $('#modificar-error-alert').addClass('d-none').text('');
        $('#modificarProvinciaModal').modal('show');
    });

    $('#modificarProvinciaForm').on('submit', function(e) {
        e.preventDefault();
        const id = $('#modificar_id_provincia').val();
        const form = $(this);
        $('#modificar-error-alert').addClass('d-none').text('');

        $.ajax({
            url: window.AppUrls.modificarProvincia + id + '/',
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message, 'success');
                $('#modificarProvinciaModal').modal('hide');
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                const errorMessage = r?.error || r?.details?.nombre_provincia || 'Error al modificar provincia.';
                Swal.fire('Error', errorMessage, 'error');
                $('#modificar-error-alert').text(errorMessage).removeClass('d-none');
            }
        });
    });

    // Baja lógica
    $('#dataTableProvinciasDisponibles tbody').on('click', '.btn-borrar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se dará de baja la provincia: ${nombre}.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, dar de baja'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.borrarProvincia + id + '/',
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
    $('#dataTableProvinciasEliminadas tbody').on('click', '.btn-restaurar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se restaurará la provincia: ${nombre}.`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#28a745',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, restaurar'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.recuperarProvincia + id + '/',
                    method: 'POST',
                    success: function(response) {
                        Swal.fire('¡Restaurada!', response.message, 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al restaurar provincia.', 'error');
                    }
                });
            }
        });
    });
});
