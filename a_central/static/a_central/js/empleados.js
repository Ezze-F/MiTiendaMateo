$(document).ready(function() {
    let dataTableDisponibles;
    let dataTableEliminados;

    const recargarTablas = () => {
        if (dataTableDisponibles) dataTableDisponibles.ajax.reload(null, false);
        if (dataTableEliminados) dataTableEliminados.ajax.reload(null, false);
    };

    // ============================================================
    // 1. DataTable: Empleados Disponibles
    // **ASUMIMOS que la vista proporciona el campo 'usuario_emp' para la edición.**
    // ============================================================
    dataTableDisponibles = $('#dataTableEmpleadosDisponibles').DataTable({
        "ajax": {
            // URL de la API: /central/empleados/disponibles/
            "url": window.location.pathname.replace('empleados/', 'empleados/disponibles/'), 
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_empleado", "visible": false },
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
                                data-rol-actual="${row.rol_emp}">
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
            // URL de la API: /central/empleados/eliminados/
            "url": window.location.pathname.replace('empleados/', 'empleados/eliminados/'),
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_empleado", "visible": false },
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
    // 3. Registro de Empleado (Corregido el manejo de errores)
    // ============================================================
    $('#registrarEmpleadoForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        // Limpiar errores previos
        form.find('.form-control').removeClass('is-invalid');
        $('#form-error-alerts').addClass('d-none');

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
                let errorListHtml = '';

                if (r && r.details) {
                    // Errores de campo
                    for (const field in r.details) {
                        const message = r.details[field];
                        const input = $(`#${field}`);
                        input.addClass('is-invalid');
                        $(`#error-${field}`).text(message);
                        errorListHtml += `<li>${message}</li>`;
                    }
                    // Mostrar lista de errores general
                    $('#error-list').html(errorListHtml);
                    $('#form-error-alerts').removeClass('d-none');
                } else {
                    // Error general (IntegrityError, Exception)
                    Swal.fire('Error', r?.error || 'Error al registrar empleado.', 'error');
                }
            }
        });
    });

    // ============================================================
    // 4. Modificación de Empleado (Ajustado para 'usuario_emp' y Rol)
    // ============================================================
    $('#dataTableEmpleadosDisponibles tbody').on('click', '.btn-editar', function() {
        const rowData = dataTableDisponibles.row($(this).parents('tr')).data();
        
        // 1. Llenar campos
        $('#modificar_id_empleado').val(rowData.id_empleado);
        $('#modificar_dni_emp').val(rowData.dni_emp);
        $('#modificar_apellido_emp').val(rowData.apellido_emp);
        $('#modificar_nombre_emp').val(rowData.nombre_emp);
        $('#modificar_email_emp').val(rowData.email_emp);
        $('#modificar_telefono_emp').val(rowData.telefono_emp);
        $('#modificar_domicilio_emp').val(rowData.domicilio_emp);
        $('#modificar_fecha_alta_emp').val(rowData.fecha_alta_emp);
        $('#modificar_usuario_emp').val(rowData.usuario_emp || '');
        
        // ASUMIMOS que la vista serializa 'usuario_emp' para que esto funcione
        $('#modificar_usuario_emp').val(rowData.usuario_emp || ''); 

        // 2. Seleccionar el rol actual
        // Dado que la vista solo serializa el nombre del rol ('rol_emp'), se debe buscar el ID del rol
        // en el select del modal. Esto asume que el nombre del rol es único.
        const rolActualNombre = rowData.rol_emp;
        const selectRol = $('#modificar_id_rol');
        let rolId = '';

        selectRol.find('option').each(function() {
            // Se asume que el texto de la opción es el nombre del rol.
            if ($(this).text().trim() === rolActualNombre) {
                rolId = $(this).val();
                return false; // Salir del each
            }
        });
        
        // Si no se encuentra (por defecto 'Sin Rol Asignado'), se deja el select vacío o en el primer valor
        selectRol.val(rolId);
        
        // 3. Mostrar Modal
        $('#modificarEmpleadoModal').modal('show');
    });

    $('#modificarEmpleadoForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const id = $('#modificar_id_empleado').val();
        
        // Limpiar alerta de errores
        $('#modificar-error-alert').addClass('d-none').text('');

        $.ajax({
            url: window.AppUrls.modificarEmpleado + id + '/',
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Empleado modificado correctamente.', 'success');
                $('#modificarEmpleadoModal').modal('hide');
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                const errorMessage = r?.error || 'Error al modificar empleado.';
                
                $('#modificar-error-alert').text(errorMessage).removeClass('d-none');
                // Adicionalmente, se puede mostrar una alerta SWAL para errores fatales/generales
                // Swal.fire('Error', errorMessage, 'error');
            }
        });
    });

    // ============================================================
    // 5. Baja/Borrado Lógico (Uso de Swal.fire y mensaje de éxito de la vista)
    // ============================================================
    $('#dataTableEmpleadosDisponibles tbody').on('click', '.btn-borrar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');
        
        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se dará de baja (borrado lógico) al empleado: ${nombre}.`,
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
                        Swal.fire('¡Baja realizada!', response.message || 'Empleado borrado lógicamente.', 'success');
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
    // 6. Restauración (Uso de Swal.fire y mensaje de éxito de la vista)
    // ============================================================
    $('#dataTableEmpleadosEliminados tbody').on('click', '.btn-restaurar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');
        
        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se restaurará (reactivará) al empleado: ${nombre}.`,
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
                        Swal.fire('¡Restaurado!', response.message || 'Empleado restaurado exitosamente.', 'success');
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
    // 7. CONTROL DE PESTAÑAS (AJUSTE DE DATATABLES - Usando Bootstrap 5)
    // ======================================================================
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        const targetId = $(e.target).attr("data-bs-target");
        
        if (targetId === '#empleadosEliminadosTab' && dataTableEliminados) {
            dataTableEliminados.columns.adjust().responsive.recalc();
        }
        if (targetId === '#empleadosDisponiblesTab' && dataTableDisponibles) {
            dataTableDisponibles.columns.adjust().responsive.recalc();
        }
    });

});