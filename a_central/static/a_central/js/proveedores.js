$(document).ready(function() {
    let dataTableDisponibles;
    let dataTableEliminados;

    const recargarTablas = () => {
        if (dataTableDisponibles) dataTableDisponibles.ajax.reload(null, false);
        if (dataTableEliminados) dataTableEliminados.ajax.reload(null, false);
    };

    // =============================
    // Inicializar DataTables
    // =============================
    function initDataTables() {
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

        dataTableEliminados = $('#dataTableProveedoresEliminados').DataTable({
            "ajax": {
                "url": window.location.pathname.replace('proveedores/', 'proveedores/eliminados/'),
                "dataSrc": "data"
            },
            "columns": [
                { "data": "id_proveedor", "visible": false },
                { "data": "cuit_prov" },
                { "data": "nombre_prov" },
                { "data": "fh_borrado_prov", "className": "text-center", "render": d => d || 'N/A' },
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
    }
    initDataTables();

    // =============================
    // Mostrar errores de formulario
    // =============================
    function mostrarErroresFormulario(errors) {
        $('#registrarProveedorForm .form-control').removeClass('is-invalid');
        $('.invalid-feedback').addClass('d-none').text('');
        $('#error-list').empty();
        $('#form-error-alerts').addClass('d-none');

        for (const field in errors) {
            const mensaje = errors[field];
            const input = $(`#${field}`);
            const errorDiv = $(`#error-${field}`);

            if (input.length) input.addClass('is-invalid');
            if (errorDiv.length) errorDiv.text(mensaje).removeClass('d-none');

            $('#error-list').append(`<li>${mensaje}</li>`);
        }

        $('#form-error-alerts').removeClass('d-none');
    }

    // =============================
    // Validaciones Frontend
    // =============================
    function validarFormulario() {
        let valido = true;

        // CUIT
        const cuit = $('#cuit_prov').val().replace(/\D/g,'');
        if (cuit.length !== 11) {
            $('#cuit_prov').addClass('is-invalid');
            $('#error-cuit_prov').text('El CUIT debe contener 11 dígitos.').removeClass('d-none');
            valido = false;
        }

        // Nombre
        const nombre = $('#nombre_prov').val().trim();
        if (nombre.length < 3 || !/[a-zA-Z]/.test(nombre)) {
            $('#nombre_prov').addClass('is-invalid');
            $('#error-nombre_prov').text('El nombre debe tener al menos 3 caracteres y contener letras.').removeClass('d-none');
            valido = false;
        }

        // Email
        const email = $('#email_prov').val().trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            $('#email_prov').addClass('is-invalid');
            $('#error-email_prov').text('Email no válido.').removeClass('d-none');
            valido = false;
        }

        // Teléfono
        const tel = $('#telefono_prov').val().replace(/\D/g,'');
        if (tel.length < 6 || tel.length > 15) {
            $('#telefono_prov').addClass('is-invalid');
            $('#error-telefono_prov').text('El teléfono debe tener entre 6 y 15 dígitos.').removeClass('d-none');
            valido = false;
        }

        // Dirección
        const dir = $('#direccion_prov').val().trim();
        if (dir.length < 5 || !/[a-zA-Z0-9]/.test(dir)) {
            $('#direccion_prov').addClass('is-invalid');
            $('#error-direccion_prov').text('La dirección debe tener al menos 5 caracteres y contener letras y números.').removeClass('d-none');
            valido = false;
        }

        // Locales Comerciales
        if ($('input[name="locales_comerciales"]:checked').length === 0) {
            alert('Debe seleccionar al menos un local comercial.');
            valido = false;
        }

        // Productos y precios
        let productosValidos = true;
        $('#productos-container .producto-item').each(function() {
            const prod = $(this).find('select').val();
            const costo = $(this).find('input').val();
            if (prod && (!costo || parseFloat(costo) <= 0)) productosValidos = false;
        });
        if (!productosValidos) {
            alert('Cada producto seleccionado debe tener un precio mayor a 0.');
            valido = false;
        }

        return valido;
    }

    // =============================
    // Enviar formulario
    // =============================
    $('#registrarProveedorForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);

        form.find('.form-control').removeClass('is-invalid');
        $('#form-error-alerts').addClass('d-none');

        if (!validarFormulario()) return;

        // Recolectar productos y precios
        const productos_proveedor = [];
        $('#productos-container .producto-item').each(function() {
            const prodId = $(this).find('select').val();
            const costo = $(this).find('input').val();
            if (prodId && costo) {
                productos_proveedor.push({id: prodId, costo: costo});
            }
        });

        // Preparar datos a enviar
        const formData = form.serializeArray();
        productos_proveedor.forEach(p => {
            formData.push({name: 'productos_proveedor[]', value: JSON.stringify(p)});
        });

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: formData,
            success: function(response) {
                if (!response.success) {
                    mostrarErroresFormulario(response.details);
                    return;
                }
                Swal.fire('¡Éxito!', response.message || 'Proveedor registrado correctamente.', 'success');
                $('#registrarProveedorModal').modal('hide');
                form[0].reset();
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                if (r?.details) mostrarErroresFormulario(r.details);
                else Swal.fire('Error', r?.error || 'Error al registrar proveedor.', 'error');
            }
        });
    });

    // ============================================================
    // 4. Modificación de Proveedor - VERSIÓN CORREGIDA
    // ============================================================
    $('#dataTableProveedoresDisponibles tbody').on('click', '.btn-editar', function() {
        const rowData = dataTableDisponibles.row($(this).parents('tr')).data();
        console.log('Editando proveedor ID:', rowData.id_proveedor);
        cargarDatosProveedorParaEdicion(rowData.id_proveedor);
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

// ============================================================
// Funcionalidad para editar proveedor con productos
// ============================================================

// Función para cargar datos del proveedor en el modal de modificación
function cargarDatosProveedorParaEdicion(proveedorId) {
    $.ajax({
        url: window.AppUrls.cargarDatosProveedor + proveedorId + '/',  // ← USAR LA URL CONFIGURADA
        method: 'GET',
        success: function(response) {
            // Llenar datos básicos
            $('#modificar_id_proveedor').val(response.proveedor.id_proveedor);
            $('#modificar_cuit_prov').val(response.proveedor.cuit_prov);
            $('#modificar_nombre_prov').val(response.proveedor.nombre_prov);
            $('#modificar_email_prov').val(response.proveedor.email_prov);
            $('#modificar_telefono_prov').val(response.proveedor.telefono_prov);
            $('#modificar_direccion_prov').val(response.proveedor.direccion_prov);
            
            // Llenar locales comerciales
            llenarLocalesComercialesModificar(response.locales_actuales, response.locales_comerciales);
            
            // Llenar productos
            llenarProductosModificar(response.productos_actuales, response.productos_disponibles);
            
            $('#modificarProveedorModal').modal('show');
        },
        error: function(xhr) {
            Swal.fire('Error', 'No se pudieron cargar los datos del proveedor.', 'error');
        }
    });
}

// Función para llenar los locales comerciales en el modal de modificación
function llenarLocalesComercialesModificar(localesActuales, localesComerciales) {
    const container = $('#modificar_locales_comerciales_checkboxes');
    container.empty();
    
    localesComerciales.forEach(local => {
        const isChecked = localesActuales.includes(local.id_loc_com) ? 'checked' : '';
        container.append(`
            <div class="form-check">
                <input class="form-check-input" type="checkbox" 
                       name="locales_comerciales" 
                       value="${local.id_loc_com}" 
                       id="modificar_local_comercial_${local.id_loc_com}"
                       ${isChecked}>
                <label class="form-check-label" for="modificar_local_comercial_${local.id_loc_com}">
                    ${local.nombre_loc_com}
                </label>
            </div>
        `);
    });
}

// Función para llenar los productos en el modal de modificación
function llenarProductosModificar(productosActuales, productosDisponibles) {
    const container = $('#modificar_productos_container');
    container.empty();
    
    // Agregar productos existentes
    productosActuales.forEach((producto, index) => {
        const options = productosDisponibles.map(p => 
            `<option value="${p.id_producto}" ${p.id_producto === producto.id_producto ? 'selected' : ''}>
                ${p.nombre_producto}
            </option>`
        ).join('');
        
        container.append(`
            <div class="producto-item-modificar d-flex gap-2 mb-2 align-items-end" data-id="${producto.id || ''}">
                <div style="flex:1;">
                    <label class="form-label small">Producto</label>
                    <select name="productos_vendidos" class="form-select" required>
                        <option value="">Seleccionar producto</option>
                        ${options}
                    </select>
                </div>
                <div style="flex:1;">
                    <label class="form-label small">Precio Compra</label>
                    <input type="number" step="0.01" min="0" name="costo_compra" 
                           class="form-control" placeholder="Precio" 
                           value="${producto.costo_compra}" required>
                </div>
                <div>
                    <label class="form-label small">&nbsp;</label>
                    <button type="button" class="btn btn-danger btn-sm btn-eliminar-producto-modificar">
                        <i class="fas fa-trash"></i>
                    </button>
                    ${producto.id_prov_prod ? `<input type="hidden" name="producto_id" value="${producto.id_prov_prod}">` : ''}
                </div>
            </div>
        `);
    });
    
    // Si no hay productos, agregar uno vacío
    if (productosActuales.length === 0) {
        agregarProductoModificar(productosDisponibles);
    }
}

// Función para agregar un nuevo producto en modificación
function agregarProductoModificar(productosDisponibles) {
    const container = $('#modificar_productos_container');
    const options = productosDisponibles.map(p => 
        `<option value="${p.id_producto}">${p.nombre_producto}</option>`
    ).join('');
    
    container.append(`
        <div class="producto-item-modificar d-flex gap-2 mb-2 align-items-end">
            <div style="flex:1;">
                <label class="form-label small">Producto</label>
                <select name="productos_vendidos" class="form-select" required>
                    <option value="">Seleccionar producto</option>
                    ${options}
                </select>
            </div>
            <div style="flex:1;">
                <label class="form-label small">Precio Compra</label>
                <input type="number" step="0.01" min="0" name="costo_compra" 
                       class="form-control" placeholder="Precio" required>
            </div>
            <div>
                <label class="form-label small">&nbsp;</label>
                <button type="button" class="btn btn-danger btn-sm btn-eliminar-producto-modificar">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `);
}

// Event listener para agregar producto en modificación
$(document).on('click', '#btn-agregar-producto-modificar', function() {
    // Obtener productos disponibles del primer select
    const productosDisponibles = [];
    $('#modificar_productos_container .producto-item-modificar:first select option').each(function() {
        if ($(this).val()) {
            productosDisponibles.push({
                id_producto: $(this).val(),
                nombre_producto: $(this).text()
            });
        }
    });
    
    agregarProductoModificar(productosDisponibles);
});

// Event listener para eliminar producto en modificación
$(document).on('click', '.btn-eliminar-producto-modificar', function() {
    $(this).closest('.producto-item-modificar').remove();
});

// SOLO UN MANEJADOR PARA EL FORMULARIO DE MODIFICACIÓN - ELIMINA EL DUPLICADO
$('#modificarProveedorForm').on('submit', function(e) {
    e.preventDefault();
    const form = $(this);
    const proveedorId = $('#modificar_id_proveedor').val();
    
    // Recolectar datos de productos
    const productosData = [];
    $('#modificar_productos_container .producto-item-modificar').each(function() {
        const productoId = $(this).find('select').val();
        const costoCompra = $(this).find('input[name="costo_compra"]').val();
        const productoExistenteId = $(this).find('input[name="producto_id"]').val();
        
        if (productoId && costoCompra) {
            productosData.push({
                producto_id: productoId,
                costo_compra: costoCompra,
                id_prov_prod: productoExistenteId || ''  // Asegurar que siempre se envíe, aunque sea vacío
            });
        }
    });
    
    // Validar que haya al menos un producto
    if (productosData.length === 0) {
        $('#modificar-error-alert').text('Debe agregar al menos un producto.').removeClass('d-none');
        return;
    }
    
    // Preparar datos del formulario
    const formData = new FormData(form[0]);
    
    // Agregar datos de productos
    productosData.forEach((producto, index) => {
        formData.append(`productos[${index}][producto_id]`, producto.producto_id);
        formData.append(`productos[${index}][costo_compra]`, producto.costo_compra);
        formData.append(`productos[${index}][id_prov_prod]`, producto.id_prov_prod);
    });
    
    $.ajax({
        url: window.AppUrls.modificarProveedor + proveedorId + '/',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                Swal.fire('¡Éxito!', response.message, 'success');
                $('#modificarProveedorModal').modal('hide');
                recargarTablas();
            } else {
                $('#modificar-error-alert').text(response.error).removeClass('d-none');
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON;
            if (response && response.error) {
                $('#modificar-error-alert').text(response.error).removeClass('d-none');
            } else {
                $('#modificar-error-alert').text('Error al modificar el proveedor.').removeClass('d-none');
            }
        }
    });
});