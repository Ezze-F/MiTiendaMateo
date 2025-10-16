$(document).ready(function() {
    let dataTableDisponibles;
    let dataTableEliminados;
    let dataTableArqueos;
    // Obtener el token CSRF globalmente para las peticiones AJAX
    const CSRF_TOKEN = $('[name="csrfmiddlewaretoken"]').val(); 

    // ============================================================
    // 1. Inicialización y Configuración
    // ============================================================
    
    // Función para recargar ambas tablas
    const recargarTablas = () => {
        if (dataTableDisponibles) dataTableDisponibles.ajax.reload(null, false);
        if (dataTableEliminados) dataTableEliminados.ajax.reload(null, false);
        if (dataTableArqueos) dataTableArqueos.ajax.reload(null, false); // Recargar arqueos
    };

    // Función auxiliar para construir URLs con el ID.
    const buildActionUrl = (baseUrl, id) => {
        // Garantiza que la URL tenga el ID.
        if (!baseUrl) return '';
        if (baseUrl.endsWith('/0/')) {
            return baseUrl.replace('/0/', `/${id}/`);
        }
        // Si no tiene el marcador /0/, asumimos que necesita el ID al final.
        return baseUrl.endsWith('/') ? `${baseUrl}${id}/` : `${baseUrl}/${id}/`;
    }

    // Función auxiliar para formatear montos a moneda (Peso Argentino ARS)
    const formatCurrency = (amount) => {
        // Convertir a número si es string (viniendo de Django Decimal)
        const numberAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
        if (typeof numberAmount !== 'number' || isNaN(numberAmount) || numberAmount === null) return 'N/A';
        
        return numberAmount.toLocaleString('es-AR', {
            style: 'currency',
            currency: 'ARS',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }

    // Función unificada para manejar y mostrar errores de validación de formulario
    const handleFormError = (xhr, formSelector, errorAlertId, defaultMsg) => {
        const response = xhr.responseJSON;
        const form = $(formSelector);
        const errorAlert = $(errorAlertId);

        // Limpiar errores previos
        form.find('.form-control').removeClass('is-invalid');
        form.find('.invalid-feedback').empty();
        errorAlert.addClass('d-none').text('');

        if (response && response.errors) {
            // Manejo de errores de campo específicos (ej: número_caja duplicado)
            for (const [key, value] of Object.entries(response.errors)) {
                // Asumimos que los IDs de los campos son '#id_nombrecampo' y los errores son '#error-nombrecampo'
                const input = form.find(`#id_${key}`); 
                input.addClass('is-invalid');
                // Intentamos encontrar un feedback específico dentro del formulario.
                const feedbackId = `#error-${key}`; // Para el modal de registro
                const specificFeedback = form.find(feedbackId);
                
                if (specificFeedback.length) {
                    specificFeedback.text(value[0]);
                } else {
                    // Si no hay feedback específico, usamos el general
                    errorAlert.removeClass('d-none').text(`¡Error en el campo ${key}! ${value[0]}`);
                }
            }
            // Muestra el Swal genérico para validación fallida
            Swal.fire('Error de Validación', 'Verifique los campos marcados en rojo.', 'error');
        } else {
            // Manejo de errores generales (ej: permiso, error de servidor)
            const errorMessage = response?.error || defaultMsg;
            errorAlert.removeClass('d-none').text(`¡Error! ${errorMessage}`);
            Swal.fire('Error', errorMessage, 'error');
        }
    }

    // ============================================================
    // 2. DataTable: Cajas Disponibles (Activas)
    // ============================================================
    dataTableDisponibles = $('#dataTableCajasDisponibles').DataTable({
        "ajax": {
            "url": window.AppUrls.apiCajasDisponibles, 
            "dataSrc": "data" // <--- CAMBIO CLAVE: Asumimos { data: [...] } del nuevo views.py
        },
        "columns": [
            { "data": "id_caja", "visible": false },
            { "data": "id_loc_com__nombre_loc_com", "defaultContent": "N/A" }, 
            { "data": "numero_caja" },
            { 
                "data": "caja_abierta",
                "className": "text-center",
                "render": function(data, type, row) {
                    return data 
                        ? '<span class="badge bg-success">Abierta</span>' 
                        : '<span class="badge bg-danger">Cerrada</span>';
                }
            },
            { 
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_caja;
                    const numero = row.numero_caja;
                    const estaAbierta = row.caja_abierta;
                    
                    // USANDO LA FUNCIÓN AUXILIAR buildActionUrl
                    const urlAbrir = buildActionUrl(window.AppUrls.abrirCaja, id);
                    const urlCerrar = buildActionUrl(window.AppUrls.cerrarCaja, id);
                    // Las URLs de Modificar y Borrar ya vienen definidas aquí
                    const urlModificar = buildActionUrl(window.AppUrls.modificarCaja, id);
                    const urlBorrar = buildActionUrl(window.AppUrls.borrarCaja, id);


                    const btnAbrir = `
                        <form method="post" action="${urlAbrir}" class="d-inline-block form-caja-estado">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${CSRF_TOKEN}">
                            <button type="button" class="btn btn-sm btn-success me-1 btn-caja-estado" data-action-url="${urlAbrir}" ${estaAbierta ? 'disabled' : ''} title="Abrir Caja">
                                Abrir
                            </button>
                        </form>
                    `;
                    const btnCerrar = `
                        <form method="post" action="${urlCerrar}" class="d-inline-block form-caja-estado">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${CSRF_TOKEN}">
                            <button type="button" class="btn btn-sm btn-danger me-2 btn-caja-estado" data-action-url="${urlCerrar}" ${!estaAbierta ? 'disabled' : ''} title="Cerrar Caja">
                                Cerrar
                            </button>
                        </form>
                    `;

                    // Botones de Modificar y Borrar 
                    const btnModificar = `
                        <button class="btn btn-warning btn-sm me-2 btn-editar-caja" data-id="${id}" 
                                data-numero="${numero}" 
                                data-local-id="${row.id_loc_com}" 
                                data-local-nombre="${row.id_loc_com__nombre_loc_com}" 
                                title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                    `;
                    // El borrado solo debe ser posible si la caja está CERRADA (deshabilitado si está abierta)
                    const btnBorrar = `
                        <button class="btn btn-secondary btn-sm btn-borrar-caja" data-id="${id}" data-numero="${numero}" title="Dar de baja" ${estaAbierta ? 'disabled' : ''}>
                            <i class="fas fa-trash"></i>
                        </button>
                    `;

                    return `<div class="d-flex justify-content-center">${btnAbrir}${btnCerrar}${btnModificar}${btnBorrar}</div>`;
                },
                "orderable": false,
                "className": "text-center"
            }
        ],
        "language": { "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" },
        "responsive": true
    });

    // ============================================================
    // 3. DataTable: Cajas Eliminadas
    // ============================================================
    dataTableEliminados = $('#dataTableCajasEliminadas').DataTable({
        "ajax": {
            "url": window.AppUrls.apiCajasEliminadas, 
            "dataSrc": "data"
        },
        "columns": [
            { "data": "id_caja", "visible": false },
            { "data": "id_loc_com__nombre_loc_com", "defaultContent": "N/A" }, 
            { "data": "numero_caja" },
            {
                "data": "fh_borrado_caja",
                "className": "text-center",
                "render": function(data) { 
                    return data ? new Date(data).toLocaleString() : 'N/A'; 
                }
            },
            {
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_caja;
                    const numero = row.numero_caja;
                    const urlRecuperar = buildActionUrl(window.AppUrls.recuperarCaja, id);
                    return `
                        <div class="d-flex justify-content-center">
                            <button class="btn btn-success btn-sm btn-restaurar-caja" data-id="${id}" data-numero="${numero}" data-action-url="${urlRecuperar}" title="Restaurar">
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
    // 4. Registro de Caja (usando Modal con AJAX)
    // ============================================================
    $('#registrarCajaForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        
        // Limpiar errores previos
        form.find('.form-control').removeClass('is-invalid');
        form.find('.invalid-feedback').empty();
        $('#form-error-alerts').addClass('d-none').text('');

        $.ajax({
            url: window.AppUrls.registrarCaja,
            method: 'POST',
            data: form.serialize(),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Caja registrada correctamente.', 'success');
                $('#registrarCajaModal').modal('hide');
                form[0].reset();
                recargarTablas();
            },
            error: function(xhr) {
                // Usamos la función unificada de manejo de errores.
                handleFormError(xhr, '#registrarCajaForm', '#form-error-alerts', 'Error desconocido al registrar caja.');
            }
        });
    });
    
    // Al cerrar el modal de registro, limpiar errores visuales
    $('#registrarCajaModal').on('hidden.bs.modal', function () {
        const form = $('#registrarCajaForm');
        form[0].reset();
        form.find('.form-control').removeClass('is-invalid');
        form.find('.invalid-feedback').empty();
        $('#form-error-alerts').addClass('d-none').text('');
    });


    // ============================================================
    // 5. Modificación de Caja (Llenado y Submit de Modal)
    // ============================================================
    $('#dataTableCajasDisponibles tbody').on('click', '.btn-editar-caja', function() {
        const rowData = dataTableDisponibles.row($(this).parents('tr')).data();
        
        // Carga de datos al formulario de modificación
        $('#id_local_readonly').val(rowData.id_loc_com__nombre_loc_com); 
        $('#id_loc_com_mod').val(rowData.id_loc_com); // <--- CAMBIO: Asumo que el ID de local en el modal de mod es 'id_loc_com_mod'
        $('#id_numero_caja_mod').val(rowData.numero_caja); // <--- CAMBIO: Asumo que el ID de número de caja en el modal de mod es 'id_numero_caja_mod'
        $('#modificar_id_caja').val(rowData.id_caja); 
        
        // Establecer la URL de acción del formulario
        const id = rowData.id_caja;
        const actionUrl = buildActionUrl(window.AppUrls.modificarCaja, id);
        $('#modificarCajaForm').attr('action', actionUrl);

        // Limpiar alertas de error previas al abrir
        $('#modificarCajaForm').find('.form-control').removeClass('is-invalid');
        $('#modificarCajaForm').find('.invalid-feedback').empty();
        $('#modificar-error-alert').addClass('d-none').text('');


        $('#modificarCajaModal').modal('show');
    });

    // Limpieza de errores al cerrar el modal de Modificación (AÑADIDO)
    $('#modificarCajaModal').on('hidden.bs.modal', function () {
        const form = $('#modificarCajaForm');
        form.find('.form-control').removeClass('is-invalid');
        form.find('.invalid-feedback').empty();
        $('#modificar-error-alert').addClass('d-none').text('');
    });


    // Manejo del submit del formulario de Modificación
    $('#modificarCajaForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        
        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            // CRÍTICO: Forzar el envío de la cabecera AJAX para que Django devuelva JSON
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(response) {
                // Notificación simple de éxito (asumiendo que la vista devuelve un message)
                Swal.fire('¡Éxito!', response.message || 'Caja modificada correctamente.', 'success');
                $('#modificarCajaModal').modal('hide');
                recargarTablas();
            },
            error: function(xhr) {
                // USAMOS LA FUNCIÓN UNIFICADA para manejar errores de campo también (MEJORA)
                handleFormError(xhr, '#modificarCajaForm', '#modificar-error-alert', 'Error desconocido al modificar caja. Verifique si el número de caja ya existe.');
            }
        });
    });

    // ============================================================
    // 6. Baja/Borrado Lógico
    // ============================================================
    // Delegamos desde el documento para mejor compatibilidad con DataTables
    $(document).on('click', '#dataTableCajasDisponibles .btn-borrar-caja', function() {
        const id = $(this).data('id');
        const numero = $(this).data('numero');
        const actionUrl = buildActionUrl(window.AppUrls.borrarCaja, id);


        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se dará de baja (borrado lógico) a la Caja N°${numero}. Recuerda que debe estar CERRADA.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, dar de baja'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: actionUrl,
                    method: 'POST',
                    data: { csrfmiddlewaretoken: CSRF_TOKEN },
                    // CRÍTICO: Forzar el envío de la cabecera AJAX para que Django devuelva JSON
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                    success: function(response) {
                        Swal.fire('¡Baja realizada!', response.message || 'Caja borrada lógicamente.', 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al procesar la baja. (Verifica que la caja esté CERRADA)', 'error');
                    }
                });
            }
        });
    });
    
    // ============================================================
    // 7. Restauración de Caja (Recuperar)
    // ============================================================
    // Delegamos desde el documento para capturar elementos dinámicos.
    $(document).on('click', '.btn-restaurar-caja', function() {
        const button = $(this); // Referencia al botón
        const id = button.data('id');
        const numero = button.data('numero');
        const actionUrl = button.data('action-url'); 

        // Validación CRÍTICA: Si la URL es inválida, abortamos y notificamos inmediatamente.
        if (!actionUrl || actionUrl === 'undefined' || actionUrl.endsWith('/undefined/')) {
            console.error(`[Restaurar Caja] URL de Acción Inválida: ${actionUrl}`);
            Swal.fire('Error de Configuración', 'La URL para restaurar la caja no se pudo cargar correctamente. Revise la definición de URL.', 'error');
            return; 
        }

        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se restaurará la Caja N°${numero}.`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#28a745',
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Sí, restaurar'
        }).then(result => {
            if (result.isConfirmed) {
                // Deshabilitar el botón para evitar doble clic mientras se procesa la petición
                button.prop('disabled', true); 

                $.ajax({
                    url: actionUrl,
                    method: 'POST',
                    data: { csrfmiddlewaretoken: CSRF_TOKEN },
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }, 
                    success: function(response) {
                        Swal.fire('¡Restaurada!', response.message || 'Caja restaurada.', 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        console.error("Error al restaurar caja (Respuesta completa del servidor):", xhr);
                        
                        let errorMsg = xhr.responseJSON?.error;

                        if (!errorMsg) {
                            if (xhr.status === 0) {
                                errorMsg = 'Error de red o CORS. El servidor no responde o la URL es incorrecta.';
                            } else {
                                errorMsg = `Error al restaurar caja. (Status: ${xhr.status} - ${xhr.statusText || 'Error desconocido'})`;
                            }
                        }

                        Swal.fire('Error', errorMsg, 'error');
                    },
                    complete: function() {
                        // Re-habilitar el botón al finalizar, sea éxito o error
                        button.prop('disabled', false); 
                    }
                });
            }
        });
    });

    // ============================================================
    // 8. Manejo de Estado (Abrir/Cerrar) - Se intercepta el CLICK del botón
    // ============================================================
    $(document).on('click', '#dataTableCajasDisponibles .btn-caja-estado', function(e) {
        e.preventDefault();
        const button = $(this);

        if (button.prop('disabled')) {
            return;
        }

        // Obtener la URL de acción 
        const actionUrl = button.data('action-url'); 
        const form = button.closest('form');
        
        const buttonText = button.text().trim();
        const isAbrir = buttonText === 'Abrir'; 
        
        Swal.fire({
            title: `¿Confirmar ${isAbrir ? 'apertura' : 'Cierre'}?`,
            text: `Se procederá a ${isAbrir ? 'abrir' : 'cerrar'} la caja.`,
            icon: isAbrir ? 'info' : 'warning',
            showCancelButton: true,
            confirmButtonColor: isAbrir ? '#198754' : '#dc3545', 
            cancelButtonText: 'Cancelar',
            confirmButtonText: `Sí, ${isAbrir ? 'Abrir' : 'Cerrar'}`
        }).then(result => {
            if (result.isConfirmed) {
                // Deshabilitar el botón mientras se procesa la petición
                button.prop('disabled', true); 
                
                $.ajax({
                    url: actionUrl, 
                    method: 'POST',
                    data: form.serialize(),
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }, 
                    success: function(response) {
                        Swal.fire('¡Éxito!', response.message || `Caja ${isAbrir ? 'abierta' : 'cerrada'} correctamente.`, 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        // Extracción robusta del mensaje de error para mostrar al usuario
                        const errorMsg = xhr.responseJSON?.error || `Error al ${isAbrir ? 'abrir' : 'cerrar'} caja.`;
                        Swal.fire('Error', errorMsg, 'error');
                    },
                    complete: function() {
                         // Re-habilitar el botón al finalizar, sea éxito o error
                        button.prop('disabled', false); 
                    }
                });
            }
        });
    });
    
    // ============================================================
    // 9. DataTable: Arqueo de Cajas (Historial de cierres)
    // ============================================================
    dataTableArqueos = $('#dataTableArqueos').DataTable({
        "ajax": {
            "url": window.AppUrls.apiArqueos, 
            "dataSrc": "data" // <--- CAMBIO CLAVE: Asumimos { data: [...] } del nuevo views.py
        },
        "columns": [
            { "data": "id_arqueo", "visible": false },
            // Local y Caja
            { "data": "id_caja__id_loc_com__nombre_loc_com", "title": "Local", "defaultContent": "N/A" }, 
            { "data": "id_caja__numero_caja", "title": "N° Caja" },
            // Fechas
            { 
                "data": "fh_apertura",
                "title": "Apertura",
                "className": "text-center",
                "render": function(data) { 
                    return data ? new Date(data).toLocaleString() : 'N/A'; 
                }
            },
            {
                "data": "fh_cierre",
                "title": "Cierre",
                "className": "text-center",
                "render": function(data) { 
                    return data ? new Date(data).toLocaleString() : 'N/A'; 
                }
            },
            // Conteo Físico
            { 
                "data": "monto_inicial_efectivo", 
                "title": "Inicial (Físico)",
                "className": "text-end",
                "render": function(data) { return formatCurrency(data); }
            },
            { 
                "data": "monto_final_efectivo", 
                "title": "Final (Físico)",
                "className": "text-end",
                // Si el monto final es null, significa que el arqueo está pendiente
                "render": function(data) { return data === null ? 'Pendiente' : formatCurrency(data); }
            },
            // Ingresos/Egresos BV
            { 
                "data": "total_ingresos_bv", 
                "title": "Ingresos BV",
                "className": "text-end text-success",
                "render": function(data) { return formatCurrency(data); }
            },
            { 
                "data": "total_egresos_bv", 
                "title": "Egresos BV",
                "className": "text-end text-danger",
                "render": function(data) { return formatCurrency(data); }
            },
            // Resultado
            { 
                "data": "diferencia_arqueo",
                "title": "Diferencia",
                "className": "text-end font-weight-bold",
                "render": function(data) {
                    // Convertir la cadena Decimal de Django a número flotante
                    const diff = parseFloat(data);
                    
                    if (data === null || isNaN(diff)) return '<span class="badge bg-warning">Pendiente</span>';
                    
                    let badgeClass = 'bg-secondary'; // Cero
                    if (diff > 0.01) {
                        badgeClass = 'bg-success'; // Sobrante (verde)
                    } else if (diff < -0.01) {
                        badgeClass = 'bg-danger'; // Faltante (rojo)
                    } else {
                        badgeClass = 'bg-info'; // Arqueo perfecto
                    }
                    return `<span class="badge ${badgeClass}">${formatCurrency(diff)}</span>`;
                }
            },
            { 
                "data": null,
                "title": "Acciones",
                "render": function(data, type, row) {
                    // Botón para ver el detalle de movimientos
                    const urlDetalle = buildActionUrl(window.AppUrls.apiMovimientosArqueo, row.id_arqueo);
                    return `
                        <div class="d-flex justify-content-center">
                            <button class="btn btn-sm btn-info btn-detalle-arqueo" data-id="${row.id_arqueo}" data-url="${urlDetalle}" title="Ver Detalle de Movimientos">
                                <i class="fas fa-search"></i>
                            </button>
                        </div>
                    `;
                },
                "orderable": false,
                "className": "text-center"
            }
        ],
        "order": [[3, 'desc']], // Ordenar por fecha de apertura (columna 3)
        "language": { "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" },
        "responsive": true
    });


    // ============================================================
    // 10. Lógica de Detalle de Arqueo (Punto 10 del usuario)
    // ============================================================

    /**
     * Muestra el detalle de movimientos de un arqueo específico en un modal SweetAlert.
     * @param {string} arqueoId ID del arqueo.
     * @param {string} apiUrl URL para obtener los movimientos (ej: /api/arqueos/1/movimientos/)
     * @param {object} rowData Fila completa de DataTables para obtener contexto.
     */
    const showArqueoDetail = (arqueoId, apiUrl, rowData) => {
        if (!apiUrl || apiUrl.includes('undefined')) {
            Swal.fire('Error de Configuración', 'La URL para obtener el detalle de movimientos no está configurada (window.AppUrls.apiMovimientosArqueo) o el ID es inválido.', 'error');
            return;
        }

        // Mostrar un indicador de carga mientras se hace la petición AJAX
        Swal.fire({
            title: `Cargando Movimientos...`,
            html: `Obteniendo detalle de movimientos para el Arqueo N° ${arqueoId}.<br><br><i class="fas fa-spinner fa-spin fa-2x"></i>`,
            allowOutsideClick: false,
            showConfirmButton: false,
        });

        $.ajax({
            url: apiUrl,
            method: 'GET', // Se asume que la consulta es GET
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(response) {
                // response.data es el formato esperado para los movimientos del arqueo (mantiene consistencia)
                const movimientos = response.data || []; 
                let movementsHtml = '';

                if (movimientos.length === 0) {
                    movementsHtml = '<div class="alert alert-warning text-center">No se registraron movimientos para este período de caja.</div>';
                } else {
                    // Construir la tabla de movimientos
                    movementsHtml = `
                        <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                            <table class="table table-striped table-sm">
                                <thead>
                                    <tr>
                                        <th scope="col">Hora</th>
                                        <th scope="col">Tipo</th>
                                        <th scope="col" class="text-end">Monto</th>
                                        <th scope="col">Descripción</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    movimientos.forEach(mov => {
                        const isIngreso = mov.tipo === 'INGRESO'; // Asumiendo que el campo es 'tipo' con valor 'INGRESO' o 'EGRESO'
                        const amountClass = isIngreso ? 'text-success font-weight-bold' : 'text-danger font-weight-bold';
                        const time = new Date(mov.fh_registro).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

                        movementsHtml += `
                            <tr>
                                <td>${time}</td>
                                <td class="${isIngreso ? 'text-success' : 'text-danger'}">${mov.tipo}</td>
                                <td class="text-end ${amountClass}">${formatCurrency(mov.monto)}</td>
                                <td>${mov.descripcion || 'N/A'}</td>
                            </tr>
                        `;
                    });

                    movementsHtml += '</tbody></table></div>';
                }

                const arqueoTitle = `Detalle de Movimientos<br><small class="text-muted">Caja N° ${rowData.id_caja__numero_caja} | Apertura: ${new Date(rowData.fh_apertura).toLocaleDateString()}</small>`;

                // Mostrar el resultado en SweetAlert
                Swal.fire({
                    title: arqueoTitle,
                    html: movementsHtml,
                    icon: 'info',
                    width: '700px', // Ancho para la tabla
                    confirmButtonText: 'Cerrar',
                });

            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON?.error || 'No se pudo obtener el detalle de movimientos. Verifique el servidor.';
                Swal.fire('Error', errorMsg, 'error');
            }
        });
    }

    // Delegamos el evento de click al documento para manejar el botón dinámico
    $(document).on('click', '#dataTableArqueos .btn-detalle-arqueo', function() {
        const button = $(this);
        const id = button.data('id');
        const url = button.data('url');
        
        // Obtenemos la fila completa para el contexto del modal (número de caja, fechas, etc.)
        const rowData = dataTableArqueos.row(button.closest('tr')).data();

        if (rowData) {
            showArqueoDetail(id, url, rowData);
        } else {
            Swal.fire('Error', 'No se pudo obtener la información de la fila de DataTables.', 'error');
        }
    });


    // ============================================================
    // 11. Ajuste de columnas al cambiar pestañas (FIX para DataTables)
    // ============================================================
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
        const targetId = $(e.target).attr("data-bs-target");
        let dataTable;

        if (targetId === '#cajasEliminadasTab') { 
            dataTable = dataTableEliminados;
        } else if (targetId === '#cajasDisponiblesTab') {
            dataTable = dataTableDisponibles;
        } else if (targetId === '#arqueoCajasTab') { 
            dataTable = dataTableArqueos;
        }

        if (dataTable) {
            // 1. Ajustar columnas (siempre necesario para tablas ocultas)
            dataTable.columns.adjust();
            
            // 2. Intentar recalcular la responsabilidad si existe la extensión y el método.
            const responsiveAPI = dataTable.responsive;

            if (responsiveAPI && typeof responsiveAPI.recalc === 'function') {
                try {
                    responsiveAPI.recalc();
                } catch (err) {
                    // Si falla el recalc (ej. inicialización tardía), forzamos un re-dibujo.
                    console.error("Error al recalcular Responsive, forzando re-dibujo:", err);
                    dataTable.draw(false); 
                }
            } else {
                 // Si la extensión responsive no se detectó o el método no existe, forzamos re-dibujo.
                 // Esto es el fallback final para asegurar el ancho correcto.
                 dataTable.draw(false); 
            }
        }
    });
});
