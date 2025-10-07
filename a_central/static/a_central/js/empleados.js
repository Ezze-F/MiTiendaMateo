$(document).ready(function() {
    let dataTableDisponibles;
    let dataTableEliminados;

    const recargarTablas = () => {
        if (dataTableDisponibles) dataTableDisponibles.ajax.reload(null, false);
        if (dataTableEliminados) dataTableEliminados.ajax.reload(null, false);
    };

    // ============================================================
    // 1. DataTable: Empleados Disponibles
    // ============================================================
    dataTableDisponibles = $('#dataTableEmpleadosDisponibles').DataTable({
        "ajax": {
            "url": "/central/empleados/disponibles/",
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_empleado", "visible": false },  // 🔴 ID oculto
            { "data": "dni_emp" },
            { "data": "apellido_emp" },
            { "data": "nombre_emp" },
            { "data": "email_emp" },
            { "data": "telefono_emp", "defaultContent": "N/A" },
            { "data": "rol_emp", "defaultContent": "Sin Rol" },
            { "data": "fecha_alta_emp" },
            {
                "data": null,
                "render": function (data, type, row) {
                    const id = row.id_empleado;
                    const nombre = `${row.nombre_emp} ${row.apellido_emp}`;
                    return `
                        <div class="d-flex justify-content-center">
                            <button class="btn btn-info btn-sm me-2 btn-editar"
                                data-id="${id}" title="Editar"
                                data-nombre="${nombre}">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-danger btn-sm btn-borrar"
                                data-id="${id}" data-nombre="${nombre}"
                                title="Dar de Baja">
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
    // 2. DataTable: Empleados Eliminados
    // ============================================================
    dataTableEliminados = $('#dataTableEmpleadosEliminados').DataTable({
        "ajax": {
            "url": "/central/empleados/eliminados/",
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_empleado", "visible": false },  // 🔴 ID oculto
            { "data": "dni_emp" },
            { "data": "apellido_emp" },
            { "data": "nombre_emp" },
            {
                "data": "fh_borrado_e",
                "className": "text-center",
                "render": function (data) {
                    return data ? data : 'N/A';
                }
            },
            {
                "data": null,
                "render": function (data, type, row) {
                    const id = row.id_empleado;
                    const nombre = `${row.nombre_emp} ${row.apellido_emp}`;
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

    // ============================================================
    // 3. Registro, Modificación, Baja y Restauración (igual que antes)
    // ============================================================
    $('#registrarEmpleadoForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Empleado registrado correctamente.', 'success');
                $('#registrarEmpleadoModal').modal('hide');
                form[0].reset();
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                let msg = r?.error || 'Error al registrar empleado.';
                if (r?.details) {
                    const fields = Object.keys(r.details);
                    if (fields.length > 0) msg = r.details[fields[0]][0];
                }
                Swal.fire('Error', msg, 'error');
            }
        });
    });

    $('#dataTableEmpleadosDisponibles tbody').on('click', '.btn-editar', function() {
        const rowData = dataTableDisponibles.row($(this).parents('tr')).data();
        $('#modificar_id_empleado').val(rowData.id_empleado);
        $('#modificar_dni_emp').val(rowData.dni_emp);
        $('#modificar_apellido_emp').val(rowData.apellido_emp);
        $('#modificar_nombre_emp').val(rowData.nombre_emp);
        $('#modificar_email_emp').val(rowData.email_emp);
        $('#modificar_telefono_emp').val(rowData.telefono_emp);
        $('#modificar_domicilio_emp').val(rowData.domicilio_emp);
        $('#modificar_fecha_alta_emp').val(rowData.fecha_alta_emp);
        $('#modificarEmpleadoModal').modal('show');
    });

    $('#modificarEmpleadoForm').on('submit', function(e) {
        e.preventDefault();
        const id = $('#modificar_id_empleado').val();
        $.ajax({
            url: window.AppUrls.modificarEmpleado + id + '/',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Empleado modificado correctamente.', 'success');
                $('#modificarEmpleadoModal').modal('hide');
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                Swal.fire('Error', r?.error || 'Error al modificar empleado.', 'error');
            }
        });
    });

    $('#dataTableEmpleadosDisponibles tbody').on('click', '.btn-borrar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');
        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se dará de baja al empleado: ${nombre}.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, dar de baja'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.borrarEmpleado + id + '/',
                    method: 'POST',
                    data: { csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val() },
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

    $('#dataTableEmpleadosEliminados tbody').on('click', '.btn-restaurar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');
        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se restaurará al empleado: ${nombre}.`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#28a745',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, restaurar'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.recuperarEmpleado + id + '/',
                    method: 'POST',
                    data: { csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val() },
                    success: function(response) {
                        Swal.fire('¡Restaurado!', response.message, 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al restaurar empleado.', 'error');
                    }
                });
            }
        });
    });


    // ======================================================================
    // 6. CONTROL DE PESTAÑAS (AJUSTE DE DATATABLES)
    // ======================================================================
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        const target = $(e.target).attr("href");
        if (target === '#empleadosEliminadosTab' && dataTableEliminados) {
            dataTableEliminados.columns.adjust().responsive.recalc();
        }
        if (target === '#empleadosDisponiblesTab' && dataTableDisponibles) {
            dataTableDisponibles.columns.adjust().responsive.recalc();
        }
    });

});