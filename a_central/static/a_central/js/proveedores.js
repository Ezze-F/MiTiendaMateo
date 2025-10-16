$(document).ready(function() {
    let dataTableDisponibles;
    let dataTableEliminados;

    const recargarTablas = () => {
        if (dataTableDisponibles) dataTableDisponibles.ajax.reload(null, false);
        if (dataTableEliminados) dataTableEliminados.ajax.reload(null, false);
    };

    // ============================================================
    // 1. DataTable: Proveedores Disponibles
    // ============================================================
    dataTableDisponibles = $('#dataTableProveedoresDisponibles').DataTable({
        "ajax": {
            "url": window.location.pathname.replace('proveedores/', 'proveedores/disponibles/'),
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_proveedor", "visible": false },
            { "data": "cuit_prov" },
            { "data": "nombre_prov" },
            { "data": "email_prov" },
            { "data": "telefono_prov", "defaultContent": "N/A" },
            { "data": "direccion_prov", "defaultContent": "N/A" },
            { "data": "fecha_alta_prov" },
            {
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_proveedor;
                    const nombre = row.nombre_prov;
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
    // 2. DataTable: Proveedores Eliminados
    // ============================================================
    dataTableEliminados = $('#dataTableProveedoresEliminados').DataTable({
        "ajax": {
            "url": window.location.pathname.replace('proveedores/', 'proveedores/eliminados/'),
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_proveedor", "visible": false },
            { "data": "cuit_prov" },
            { "data": "nombre_prov" },
            {
                "data": "fh_borrado_prov",
                "className": "text-center",
                "render": function(data) { return data ? data : 'N/A'; }
            },
            {
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_proveedor;
                    const nombre = row.nombre_prov;
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
    // 3. Registro de Proveedor
    // ============================================================
    $('#registrarProveedorForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);

        form.find('.form-control').removeClass('is-invalid');
        $('#form-error-alerts').addClass('d-none');

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Proveedor registrado correctamente.', 'success');
                $('#registrarProveedorModal').modal('hide');
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
                    Swal.fire('Error', r?.error || 'Error al registrar proveedor.', 'error');
                }
            }
        });
    });

    // ============================================================
    // 4. Modificación de Proveedor
    // ============================================================
    $('#dataTableProveedoresDisponibles tbody').on('click', '.btn-editar', function() {
        const rowData = dataTableDisponibles.row($(this).parents('tr')).data();

        $('#modificar_id_proveedor').val(rowData.id_proveedor);
        $('#modificar_cuit_prov').val(rowData.cuit_prov);
        $('#modificar_nombre_prov').val(rowData.nombre_prov);
        $('#modificar_email_prov').val(rowData.email_prov);
        $('#modificar_telefono_prov').val(rowData.telefono_prov);
        $('#modificar_direccion_prov').val(rowData.direccion_prov);
        $('#modificar_fecha_alta_prov').val(rowData.fecha_alta_prov);

        $('#modificarProveedorModal').modal('show');
    });

    $('#modificarProveedorForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const id = $('#modificar_id_proveedor').val();

        $('#modificar-error-alert').addClass('d-none').text('');

        $.ajax({
            url: window.AppUrls.modificarProveedor + id + '/',
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Proveedor modificado correctamente.', 'success');
                $('#modificarProveedorModal').modal('hide');
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                const errorMessage = r?.error || 'Error al modificar proveedor.';
                $('#modificar-error-alert').text(errorMessage).removeClass('d-none');
            }
        });
    });

    // ============================================================
    // 5. Baja/Borrado Lógico
    // ============================================================
    $('#dataTableProveedoresDisponibles tbody').on('click', '.btn-borrar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se dará de baja al proveedor: ${nombre}.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, dar de baja'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.borrarProveedor + id + '/',
                    method: 'POST',
                    data: { csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val() },
                    success: function(response) {
                        Swal.fire('¡Baja realizada!', response.message || 'Proveedor borrado.', 'success');
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
    $('#dataTableProveedoresEliminados tbody').on('click', '.btn-restaurar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se restaurará al proveedor: ${nombre}.`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#28a745',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, restaurar'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.recuperarProveedor + id + '/',
                    method: 'POST',
                    data: { csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val() },
                    success: function(response) {
                        Swal.fire('¡Restaurado!', response.message || 'Proveedor restaurado.', 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al restaurar proveedor.', 'error');
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

        if (targetId === '#proveedoresEliminadosTab' && dataTableEliminados) {
            dataTableEliminados.columns.adjust().responsive.recalc();
        }
        if (targetId === '#proveedoresDisponiblesTab' && dataTableDisponibles) {
            dataTableDisponibles.columns.adjust().responsive.recalc();
        }
    });
});
