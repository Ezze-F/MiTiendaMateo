$(document).ready(function() {
    let dataTableDisponibles;
    let dataTableEliminados;

    const recargarTablas = () => {
        if (dataTableDisponibles) dataTableDisponibles.ajax.reload(null, false);
        if (dataTableEliminados) dataTableEliminados.ajax.reload(null, false);
    };

    // ============================================================
    // 1. DataTable: Billeteras Disponibles
    // ============================================================
    dataTableDisponibles = $('#dataTableBilleterasDisponibles').DataTable({
        "ajax": {
            "url": window.location.pathname.replace('billeteras/', 'billeteras/disponibles/'),
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_bv", "visible": false },
            { "data": "nombre_bv" },
            { "data": "usuario_bv" },
            { "data": "cbu_bv", "defaultContent": "N/A" },
            { 
                "data": "saldo_bv",
                "className": "text-end",
                "render": $.fn.dataTable.render.number('.', ',', 2, '$') // Formato de moneda
            },
            { "data": "fh_alta_bv" },
            {
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_bv;
                    const nombre = row.nombre_bv;
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
    // 2. DataTable: Billeteras Eliminadas
    // ============================================================
    dataTableEliminados = $('#dataTableBilleterasEliminados').DataTable({
        "ajax": {
            "url": window.location.pathname.replace('billeteras/', 'billeteras/eliminados/'),
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_bv", "visible": false },
            { "data": "nombre_bv" },
            { "data": "usuario_bv" },
            {
                "data": "fh_borrado_bv",
                "className": "text-center",
                "render": function(data) { return data ? data : 'N/A'; }
            },
            {
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_bv;
                    const nombre = row.nombre_bv;
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
    // 3. Registro de Billetera Virtual
    // ============================================================
    $('#registrarBilleteraForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);

        form.find('.form-control, .form-select').removeClass('is-invalid');
        $('#form-error-alerts').addClass('d-none');

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Billetera virtual registrada correctamente.', 'success');
                $('#registrarBilleteraModal').modal('hide');
                form[0].reset();
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;

                if (r && r.details) {
                    // Manejo de errores de validación de campos
                    for (const field in r.details) {
                        const message = r.details[field];
                        const input = $(`#${field}`);
                        input.addClass('is-invalid');
                        $(`#error-${field}`).text(message);
                    }
                    $('#form-error-alerts').removeClass('d-none');
                } else {
                    Swal.fire('Error', r?.error || 'Error al registrar billetera virtual.', 'error');
                }
            }
        });
    });

    // ============================================================
    // 4. Modificación de Billetera Virtual
    // ============================================================
    $('#dataTableBilleterasDisponibles tbody').on('click', '.btn-editar', function() {
        const rowData = dataTableDisponibles.row($(this).parents('tr')).data();

        $('#modificar_id_bv').val(rowData.id_bv);
        $('#modificar_nombre_bv').val(rowData.nombre_bv);
        $('#modificar_usuario_bv').val(rowData.usuario_bv);
        $('#modificar_cbu_bv').val(rowData.cbu_bv === 'N/A' ? '' : rowData.cbu_bv);
        // Limpiar y usar formato float para el saldo
        $('#modificar_saldo_bv').val(rowData.saldo_bv.replace('$', '').replace('.', '').replace(',', '.')); 
        $('#modificar_fh_alta_bv').val(rowData.fh_alta_bv);
        // Limpiar campo de contraseña al abrir
        $('#modificar_nueva_contrasena_bv').val(''); 

        $('#modificarBilleteraModal').modal('show');
    });

    $('#modificarBilleteraForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const id = $('#modificar_id_bv').val();

        $('#modificar-error-alert').addClass('d-none').text('');

        $.ajax({
            url: window.AppUrls.modificarBilletera + id + '/',
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Billetera virtual modificada correctamente.', 'success');
                $('#modificarBilleteraModal').modal('hide');
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                const errorMessage = r?.error || 'Error al modificar billetera virtual.';
                $('#modificar-error-alert').text(errorMessage).removeClass('d-none');
            }
        });
    });

    // ============================================================
    // 5. Baja/Borrado Lógico
    // ============================================================
    $('#dataTableBilleterasDisponibles tbody').on('click', '.btn-borrar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se dará de baja a la billetera virtual: ${nombre}.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, dar de baja'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.borrarBilletera + id + '/',
                    method: 'POST',
                    data: { csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val() },
                    success: function(response) {
                        Swal.fire('¡Baja realizada!', response.message || 'Billetera virtual borrada.', 'success');
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
    $('#dataTableBilleterasEliminados tbody').on('click', '.btn-restaurar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se restaurará a la Billetera Virtual: ${nombre}.`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#28a745',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, restaurar'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.recuperarBilletera + id + '/',
                    method: 'POST',
                    data: { csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val() },
                    success: function(response) {
                        Swal.fire('¡Restaurada!', response.message || 'Billetera virtual restaurada.', 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al restaurar billetera virtual.', 'error');
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

        if (targetId === '#billeterasEliminadosTab' && dataTableEliminados) {
            dataTableEliminados.columns.adjust().responsive.recalc();
        }
        if (targetId === '#billeterasDisponiblesTab' && dataTableDisponibles) {
            dataTableDisponibles.columns.adjust().responsive.recalc();
        }
    });
    // ============================================================
    // 8. FUNCIONALIDAD DE MOSTRAR/OCULTAR CONTRASEÑA
    // ============================================================
    $('.toggle-password').on('click', function() {
        // Obtiene el ID del input target desde el atributo data-target
        const targetId = $(this).data('target');
        const passwordInput = $(`#${targetId}`);
        const icon = $(this).find('i');
        
        // Cambia el tipo de input entre 'password' y 'text'
        if (passwordInput.attr('type') === 'password') {
            passwordInput.attr('type', 'text');
            icon.removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            passwordInput.attr('type', 'password');
            icon.removeClass('fa-eye-slash').addClass('fa-eye');
        }
    });
});