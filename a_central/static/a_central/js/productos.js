$(document).ready(function() {
    let dataTableDisponibles;
    let dataTableEliminados;

    const recargarTablas = () => {
        if (dataTableDisponibles) dataTableDisponibles.ajax.reload(null, false);
        if (dataTableEliminados) dataTableEliminados.ajax.reload(null, false);
    };

    // ============================================================
    // 1. DataTable: Productos Disponibles
    // ============================================================
    dataTableDisponibles = $('#dataTableProductosDisponibles').DataTable({
        "ajax": {
            "url": window.location.pathname.replace('productos/', 'productos/disponibles/'),
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_producto", "visible": false },
            { "data": "nombre_producto" },
            { "data": "nombre_marca", "defaultContent": "Sin Marca" },
            { 
                "data": "precio_unit_prod",
                "className": "text-end",
                "render": $.fn.dataTable.render.number('.', ',', 2, '$') // Formato de moneda
            },
            { "data": "fecha_alta_prod" },
            { "data": "id_loc_com", "visible": false },
            {
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_producto;
                    const nombre = row.nombre_producto;
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
    // 2. DataTable: Productos Eliminados
    // ============================================================
    dataTableEliminados = $('#dataTableProductosEliminados').DataTable({
        "ajax": {
            "url": window.location.pathname.replace('productos/', 'productos/eliminados/'),
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_producto", "visible": false },
            { "data": "nombre_producto" },
            { "data": "nombre_marca", "defaultContent": "Sin Marca" },
            {
                "data": "fh_borrado_prod",
                "className": "text-center",
                "render": function(data) { return data ? data : 'N/A'; }
            },
            {
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_producto;
                    const nombre = row.nombre_producto;
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
// 3. Registro de Producto (ACTUALIZADO)
// ============================================================
$('#registrarProductoForm').on('submit', function(e) {
    e.preventDefault();
    const form = $(this);

    form.find('.form-control, .form-select').removeClass('is-invalid');
    $('#form-error-alerts').addClass('d-none');

    // Crear el objeto FormData manualmente para incluir todo
    const formData = new FormData(form[0]);

    // Agregamos explícitamente los campos nuevos
    formData.append('id_loc_com', $('#id_loc_com').val());
    formData.append('stock_min_pxlc', $('#stock_min_pxlc').val());

    $.ajax({
        url: form.attr('action'),
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            Swal.fire('¡Éxito!', response.message || 'Producto y stock registrados correctamente.', 'success');
            $('#registrarProductoModal').modal('hide');
            form[0].reset();
            recargarTablas();
        },
        error: function(xhr) {
            const r = xhr.responseJSON;

            if (r && r.details) {
                for (const field in r.details) {
                    const message = r.details[field];
                    const input = $(`#${field}`);
                    input.addClass('is-invalid');
                    $(`#error-${field}`).text(message);
                }
                $('#form-error-alerts').removeClass('d-none');
            } else {
                Swal.fire('Error', r?.error || 'Error al registrar producto.', 'error');
            }
        }
    });
});


    // ============================================================
    // 4. Modificación de Producto
    // ============================================================
    $('#dataTableProductosDisponibles tbody').on('click', '.btn-editar', function() {
        const rowData = dataTableDisponibles.row($(this).parents('tr')).data();
        console.log(rowData);


        $('#modificar_id_producto').val(rowData.id_producto);
        $('#modificar_nombre_producto').val(rowData.nombre_producto);
        $('#modificar_id_marca').val(rowData.id_marca || ''); // Usamos el ID de la marca
        $('#modificar_precio_unit_prod').val(rowData.precio_unit_prod.replace('$', '').replace('.', '').replace(',', '.')); // Limpiar y usar formato float
        $('#modificar_fecha_alta_prod').val(rowData.fecha_alta_prod);

        $.get(`/central/stock/minimo/${rowData.id_producto}/${rowData.id_loc_com}/`, function(data) {
            $('#modificar_stock_min_pxlc').val(data.stock_minimo);
        });
        $('#modificarProductoModal').modal('show');
    });

    $('#modificarProductoForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const id = $('#modificar_id_producto').val();

        $('#modificar-error-alert').addClass('d-none').text('');

        $.ajax({
            url: window.AppUrls.modificarProducto + id + '/',
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Producto modificado correctamente.', 'success');
                $('#modificarProductoModal').modal('hide');
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                const errorMessage = r?.error || 'Error al modificar producto.';
                $('#modificar-error-alert').text(errorMessage).removeClass('d-none');
            }
        });
    });

    // ============================================================
    // 5. Baja/Borrado Lógico
    // ============================================================
    $('#dataTableProductosDisponibles tbody').on('click', '.btn-borrar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se dará de baja al producto: ${nombre}.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, dar de baja'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.borrarProducto + id + '/',
                    method: 'POST',
                    data: { csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val() },
                    success: function(response) {
                        Swal.fire('¡Baja realizada!', response.message || 'Producto borrado.', 'success');
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
    $('#dataTableProductosEliminados tbody').on('click', '.btn-restaurar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se restaurará al producto: ${nombre}.`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#28a745',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, restaurar'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: window.AppUrls.recuperarProducto + id + '/',
                    method: 'POST',
                    data: { csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val() },
                    success: function(response) {
                        Swal.fire('¡Restaurado!', response.message || 'Producto restaurado.', 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al restaurar producto.', 'error');
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

        if (targetId === '#productosEliminadosTab' && dataTableEliminados) {
            dataTableEliminados.columns.adjust().responsive.recalc();
        }
        if (targetId === '#productosDisponiblesTab' && dataTableDisponibles) {
            dataTableDisponibles.columns.adjust().responsive.recalc();
        }
    });
});