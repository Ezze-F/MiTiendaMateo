$(document).ready(function() {
    let dataTableDisponibles;
    let dataTableEliminados;
    let dataTableArqueos;
    // La tabla de movimientos se inicializaría si existiera un modal de detalle de arqueo
    let dataTableMovimientos = null; 
    
    // Obtener el token CSRF globalmente para las peticiones AJAX
    const CSRF_TOKEN = $('[name="csrfmiddlewaretoken"]').val(); 

    // ============================================================
    // 1. Inicialización y Configuración
    // ============================================================
    
    // Función para cargar datos automáticos del arqueo
    const cargarDatosArqueoAutomaticos = (cajaId) => {
        return new Promise((resolve, reject) => {
            const arqueoUrl = buildActionUrl(window.AppUrls.datosArqueoActual, cajaId);
            
            $.ajax({
                url: arqueoUrl,
                method: 'GET',
                success: function(response) {
                    resolve(response);
                },
                error: function(xhr) {
                    reject(xhr.responseJSON?.error || 'Error al cargar datos del arqueo');
                }
            });
        });
    };

    // Función para recargar ambas tablas
    const recargarTablas = () => {
        if (dataTableDisponibles) dataTableDisponibles.ajax.reload(null, false);
        if (dataTableEliminados) dataTableEliminados.ajax.reload(null, false);
        // CRÍTICO: Recargar tabla de arqueos
        if (dataTableArqueos) dataTableArqueos.ajax.reload(null, false); 
        // NOTA: dataTableMovimientos se recarga de forma manual en la sección 10
    };

    // Función auxiliar para construir URLs con el ID.
    const buildActionUrl = (baseUrl, id) => {
        // Garantiza que la URL tenga el ID.
        if (!baseUrl) return '';
        // Reemplazo el marcador /0/ por el ID.
        if (baseUrl.includes('/0/')) {
            return baseUrl.replace('/0/', `/${id}/`);
        }
        // Si no tiene el marcador, añado el ID al final (caso menos ideal)
        return baseUrl.endsWith('/') ? `${baseUrl}${id}/` : `${baseUrl}/${id}/`;
    }

    // Función auxiliar para formatear montos a moneda (Peso Argentino ARS)
    const formatCurrency = (amount) => {
        // Convertir a número si es string (viniendo de Django Decimal)
        const numberAmount = typeof amount === 'string' ? parseFloat(amount.replace(',', '.')) : amount;
        if (typeof numberAmount !== 'number' || isNaN(numberAmount) || numberAmount === null) return 'N/A';
        
        // Usar 'es-AR' para formato de Peso Argentino
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
            let specificErrorFound = false;
            for (const [key, value] of Object.entries(response.errors)) {
                // Asumimos que los IDs de los campos son '#id_nombrecampo' y los errores son '#error-nombrecampo'
                // Adaptamos para buscar IDs específicos en listar_cajas.html:
                let inputId = `#id_${key}`;
                if (key === 'numero_caja') {
                    // Si estamos en un modal de registro/modificación, la id del input es diferente
                    if (formSelector === '#registrarCajaForm') {
                        inputId = `#id_${key}`; // Django default
                    } else if (formSelector === '#modificarCajaForm') {
                        inputId = `#modificar_numero_caja_input`; 
                    }
                }
                
                const input = form.find(inputId); 
                input.addClass('is-invalid');
                
                // Buscamos el elemento .invalid-feedback específico
                const feedbackId = `#error-${key}`;
                const specificFeedback = form.find(feedbackId);
                
                if (specificFeedback.length) {
                    specificFeedback.text(value[0]);
                    specificErrorFound = true;
                } else {
                    // Si no hay feedback específico, usamos el general
                    errorAlert.removeClass('d-none').text(`¡Error en el campo ${key}! ${value[0]}`);
                    specificErrorFound = true;
                }
            }
            
            if (specificErrorFound) {
                 // Muestra el Swal genérico para validación fallida
                 Swal.fire('Error de Validación', 'Verifique los campos marcados en rojo.', 'error');
            } else if (response.error) {
                 // Manejo de errores generales si no son errores de campo
                 errorAlert.removeClass('d-none').text(`¡Error! ${response.error}`);
                 Swal.fire('Error', response.error, 'error');
            }
            
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
            "dataSrc": "data" 
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
                    // La URL de abrir/cerrar solo necesita el ID de la caja
                    const urlAbrir = buildActionUrl(window.AppUrls.abrirCaja, id);
                    const urlCerrar = buildActionUrl(window.AppUrls.cerrarCaja, id);

                    // Nota: Los botones Abrir/Cerrar se manejan con un modal o Swal, 
                    // no con submit directo de este form.
                    const btnAbrir = `
                        <button type="button" class="btn btn-sm btn-success me-1 btn-caja-estado" data-action-type="abrir" data-id="${id}" data-action-url="${urlAbrir}" ${estaAbierta ? 'disabled' : ''} title="Abrir Caja">
                            Abrir
                        </button>
                    `;
                    const btnCerrar = `
                        <button type="button" class="btn btn-sm btn-danger me-2 btn-caja-estado" data-action-type="cerrar" data-id="${id}" data-action-url="${urlCerrar}" ${!estaAbierta ? 'disabled' : ''} title="Cerrar Caja">
                            Cerrar
                        </button>
                    `;

                    // Botón Modificar: Cambiado a btn-info y DESHABILITADO si la caja está ABIERTA.
                    const btnModificar = `
                        <button class="btn btn-info btn-sm me-2 btn-editar-caja" data-id="${id}" 
                                data-numero="${numero}" 
                                data-local-id="${row.id_loc_com}" 
                                data-local-nombre="${row.id_loc_com__nombre_loc_com}" 
                                title="Editar"
                                ${estaAbierta ? 'disabled' : ''}> 
                            <i class="fas fa-edit"></i>
                        </button>
                    `;
                    // Botón Borrar: Cambiado a btn-danger y DESHABILITADO si la caja está ABIERTA.
                    const btnBorrar = `
                        <button class="btn btn-danger btn-sm btn-borrar-caja" data-id="${id}" data-numero="${numero}" title="Dar de baja" ${estaAbierta ? 'disabled' : ''}>
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
                    return data ? new Date(data).toLocaleString('es-AR') : 'N/A'; // Formato local de Argentina
                }
            },
            {
                "data": null,
                "render": function(data, type, row) {
                    const id = row.id_caja;
                    const numero = row.numero_caja;
                    const urlRecuperar = buildActionUrl(window.AppUrls.recuperarCaja, id);
                    // Botón Restaurar
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

        // Deshabilitar botón para evitar doble submit
        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.text(); // Guardar texto original
        submitButton.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Registrando...');


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
            },
            complete: function() {
                // Re-habilitar botón
                submitButton.prop('disabled', false).text(originalButtonText);
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
        // Obtener la fila de datos
        const rowData = dataTableDisponibles.row($(this).closest('tr')).data();

        // Verificar si el botón está deshabilitado ANTES de abrir el modal (seguridad visual)
        if ($(this).prop('disabled')) {
            Swal.fire('Atención', 'No se puede editar una caja que se encuentra abierta. Por favor, ciérrela primero.', 'warning');
            return; 
        }
        
        // Carga de datos al formulario de modificación
        $('#modificar_local_nombre').val(rowData.id_loc_com__nombre_loc_com); // Campo de solo lectura
        $('#modificar_numero_caja_input').val(rowData.numero_caja); // Input editable
        $('#modificar_id_caja').val(rowData.id_caja); // Input oculto con el ID
        
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

    // Limpieza de errores al cerrar el modal de Modificación
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
        
        // Deshabilitar botón para evitar doble submit
        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.text(); // Guardar texto original
        submitButton.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Guardando...');

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
            },
            complete: function() {
                // Re-habilitar botón
                submitButton.prop('disabled', false).text(originalButtonText);
            }
        });
    });

    // ============================================================
    // 6. Baja/Borrado Lógico
    // ============================================================
    // Delegamos desde el documento para mejor compatibilidad con DataTables
    $(document).on('click', '#dataTableCajasDisponibles .btn-borrar-caja', function() {
        const button = $(this);
        // Verificar si el botón está deshabilitado ANTES de la acción (doble chequeo)
        if (button.prop('disabled')) {
            Swal.fire('Atención', 'No se puede dar de baja (borrar) una caja que se encuentra abierta. Por favor, ciérrela primero.', 'warning');
            return; 
        }

        const id = button.data('id');
        const numero = button.data('numero');
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
                 // Deshabilitar el botón mientras se procesa la petición
                const originalButtonContent = button.html();
                button.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i>');

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
                    },
                    complete: function() {
                        // Re-habilitar el botón al finalizar, sea éxito o error
                        button.prop('disabled', false).html(originalButtonContent); 
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
                const originalButtonContent = button.html();
                button.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Restaurando...'); 

                $.ajax({
                    url: actionUrl,
                    method: 'POST',
                    data: { csrfmiddlewaretoken: CSRF_TOKEN },
                    headers: { 'X-requested-with': 'XMLHttpRequest' }, 
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
                        button.prop('disabled', false).html(originalButtonContent); 
                    }
                });
            }
        });
    });

    // ============================================================
    // 8. Manejo de Estado (Abrir/Cerrar) - Se usa modal de Apertura/Cierre
    // ============================================================
    $(document).on('click', '#dataTableCajasDisponibles .btn-caja-estado', function(e) {
        e.preventDefault();
        const button = $(this);
        const actionType = button.data('action-type');
        const idCaja = button.data('id');
        const actionUrl = button.data('action-url'); 
        
        const rowData = dataTableDisponibles.row(button.closest('tr')).data();

        if (button.prop('disabled')) return;
        
        if (actionType === 'abrir') {
            const now = new Date();
            // Llenar el modal de apertura
            $('#abrir_id_caja').val(idCaja);
            $('#abrir_local').val(rowData.id_loc_com__nombre_loc_com);
            $('#abrir_numero_caja').val(rowData.numero_caja);
            $('#abrir_fecha_hora').val(now.toLocaleString('es-AR'));
            $('#abrirCajaForm').attr('action', actionUrl);

            // Limpiar errores previos
            $('#abrirCajaForm').find('.form-control').removeClass('is-invalid');
            $('#abrirCajaForm').find('.invalid-feedback').empty();
            $('#abrir-error-alert').addClass('d-none').text('');

            $('#abrirCajaModal').modal('show');
        } 
        else if (actionType === 'cerrar') {
            const originalText = button.html();
            button.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i>'); 

            // CARGAR DATOS AUTOMÁTICOS DEL ARQUEO
            cargarDatosArqueoAutomaticos(idCaja)
                .then(datosArqueo => {
                console.log("Datos del arqueo cargados:", datosArqueo);
                
                // Llenar el modal de cierre con datos automáticos
                $('#cerrar_id_arqueo').val(datosArqueo.id_arqueo);
                $('#cerrar_id_caja').val(idCaja);
                $('#cerrar_local').val(rowData.id_loc_com__nombre_loc_com);
                $('#cerrar_numero_caja').val(rowData.numero_caja);
                
                // Datos automáticos calculados - EFECTIVO
                $('#cerrar_efectivo_inicial_readonly').val(formatCurrency(datosArqueo.monto_inicial_efectivo));
                $('#cerrar_efectivo_inicial').val(datosArqueo.monto_inicial_efectivo);
                
                // Mostrar resumen automático COMPLETO
                $('#resumen_ingresos').text(formatCurrency(datosArqueo.total_ingresos_efectivo));
                $('#resumen_egresos').text(formatCurrency(datosArqueo.total_egresos_efectivo));
                $('#resumen_saldo_esperado').text(formatCurrency(datosArqueo.saldo_esperado_efectivo));
                $('#resumen_ventas').text(datosArqueo.ventas_total_count || 0);
                
                // Mostrar información de billeteras virtuales
                $('#resumen_ingresos_bv').text(formatCurrency(datosArqueo.total_ingresos_bv));
                $('#resumen_egresos_bv').text(formatCurrency(datosArqueo.total_egresos_bv));
                
                // Establecer el saldo esperado como valor sugerido para el monto final
                $('#cerrar_efectivo_final').val(datosArqueo.saldo_esperado_efectivo.toFixed(2));
                
                // Los campos de BV se llenan automáticamente (no editables por el usuario)
                $('#cerrar_ingresos_bv').val(datosArqueo.total_ingresos_bv.toFixed(2));
                $('#cerrar_egresos_bv').val(datosArqueo.total_egresos_bv.toFixed(2));
                
                $('#cerrarCajaForm').attr('action', actionUrl);

                // Limpiar errores previos
                $('#cerrarCajaForm').find('.form-control').removeClass('is-invalid');
                $('#cerrarCajaForm').find('.invalid-feedback').empty();
                $('#cerrar-error-alert').addClass('d-none').text('');

                $('#cerrarCajaModal').modal('show');
                })
                .catch(error => {
                    console.error("Error al cargar datos del arqueo:", error);
                    Swal.fire('Error', error, 'error');
                })
                .finally(() => {
                    button.prop('disabled', false).html(originalText);
                });
        }
    });

    // ============================================================
    // 9. DataTable: Arqueo de Cajas (Historial de cierres)
    // ============================================================
    
    // Función de inicialización de la tabla de arqueos
    const initArqueosDataTable = () => {
        // Inicializar solo si no ha sido inicializada
        if ($.fn.DataTable.isDataTable('#dataTableArqueos')) {
            return;
        }

        dataTableArqueos = $('#dataTableArqueos').DataTable({
            "processing": true,
            "serverSide": false, 
            "ajax": {
                "url": window.AppUrls.apiArqueos, // CRÍTICO: URL de la API de Django
                "type": "GET",
                "dataSrc": "data",
                "error": function (xhr, error, code) {
                    console.error("Error al cargar datos de arqueos:", xhr.responseText);
                    Swal.fire('Error de Carga', 'No se pudo cargar el historial de arqueos. Revisa el endpoint de Django y la estructura de los datos.', 'error');
                }
            },
            "columns": [
                // 0: ID (oculto)
                { "data": "id_arqueo", "className": "d-none", "visible": false, "defaultContent": "N/A" }, 
                // 1: Local
                { "data": "local_nombre", "className": "text-center", "defaultContent": "N/A" }, 
                // 2: Caja
                { "data": "caja_numero", "className": "text-center", "defaultContent": "N/A" }, 
                // 3: Empleado de apertura
                { "data": "empleado_apertura_nombre", "className": "text-center", "defaultContent": "N/A" }, 
                // 4: Fecha y hora de apertura
                { 
                    "data": "fecha_hora_apertura", 
                    "className": "text-center", 
                    "defaultContent": "N/A",
                    "render": function(data) {
                        return data ? new Date(data).toLocaleString('es-AR') : 'N/A';
                    }
                }, 
                // 5: Efectivo inicial
                { 
                    "data": "efectivo_inicial", 
                    "className": "text-center", 
                    "defaultContent": formatCurrency(0),
                    "render": function(data, type, row) {
                        return formatCurrency(data);
                    }
                }, 
                // 6: Empleado de cierre
                { "data": "empleado_cierre_nombre", "className": "text-center", "defaultContent": "N/A" }, 
                // 7: Fecha y hora de cierre
                { 
                    "data": "fecha_hora_cierre", 
                    "className": "text-center", 
                    "defaultContent": "N/A",
                    "render": function(data) {
                        return data ? new Date(data).toLocaleString('es-AR') : '<span class="badge bg-warning text-dark">Pendiente</span>';
                    }
                }, 
                // 8: Efectivo final
                { 
                    "data": "efectivo_final", 
                    "className": "text-center", 
                    "defaultContent": "N/A",
                    "render": function(data, type, row) {
                        return data !== null ? formatCurrency(data) : 'N/A';
                    }
                },
                // 9: Ingresos BV
                { 
                    "data": "ingresos_bv", 
                    "className": "text-center", 
                    "defaultContent": formatCurrency(0),
                    "render": function(data, type, row) {
                        return formatCurrency(data);
                    }
                },
                // 10: Egresos BV
                { 
                    "data": "egresos_bv", 
                    "className": "text-center", 
                    "defaultContent": formatCurrency(0),
                    "render": function(data, type, row) {
                        return formatCurrency(data);
                    }
                },
                // 11: Acciones (Botones de Ver Detalle/Arqueo)
                { 
                    "data": null, // El valor es construido completamente por la función render
                    "className": "text-center", 
                    "orderable": false,
                    "render": function(data, type, row) {
                        // El ID que se usa aquí es el que se intenta obtener de "id_arqueo"
                        const id = row.id_arqueo; 
                        
                        // Solo mostramos el botón de detalle si está cerrado (fecha_hora_cierre no es nulo)
                        if (row.fecha_hora_cierre) {
                            return `
                                <button class="btn btn-sm btn-info ver-detalle-arqueo" data-id="${id}" title="Ver Detalle">
                                    <i class="fas fa-search"></i> Detalle
                                </button>
                            `;
                        }
                        // Si está pendiente de cierre
                        return '<span class="badge bg-warning text-dark">En curso</span>';
                    }
                },
            ],
            "language": { "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" },
            "order": [[4, "desc"]], // Ordenar por fecha de apertura descendente
            "responsive": true
        });
    }

    // Inicialización de la tabla de arqueos cuando se hace clic en la pestaña
    $('button[data-bs-target="#arqueoCajasTab"]').on('shown.bs.tab', function (e) {
        // Se inicializa la primera vez que se accede a la pestaña
        initArqueosDataTable();
        // Si ya estaba inicializada, solo recargamos (aunque DataTables lo hace automáticamente)
        if (dataTableArqueos) dataTableArqueos.ajax.reload(null, false);
    });


    // ============================================================
    // 10. Lógica de Detalle de Arqueo - (NUEVA SECCIÓN) - Pendiente de Modal HTML
    // ============================================================
    
    // Este código ASUME que tienes un Modal HTML (ej: #detalleArqueoModal) y una tabla (ej: #dataTableMovimientos)
    // para mostrar los detalles del arqueo y los movimientos asociados.
    
    $(document).on('click', '#dataTableArqueos .ver-detalle-arqueo', function() {
        const arqueoId = $(this).data('id');
        
        // 1. Llama a la API de Django para obtener los detalles del arqueo (incluidos movimientos)
        // ASUME QUE EXISTE: window.AppUrls.apiDetalleArqueo: "{% url 'a_cajas:detalle_arqueo_api' arqueo_id=0 %}".replace('/0/', '/'),
        const detalleUrl = buildActionUrl(window.AppUrls.apiDetalleArqueo, arqueoId); 
    
        // Mostrar spinner o mensaje de carga
        Swal.fire({
            title: 'Cargando detalle...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        $.ajax({
            url: detalleUrl,
            method: 'GET',
            timeout: 5000, // Timeout de seguridad
            success: function(response) {
                Swal.close(); // Cerrar spinner
                
                if (response.error) {
                    Swal.fire('Error', response.error, 'error');
                    return;
                }
    
                // 2. Rellenar campos del modal con datos generales del arqueo (response.arqueo)
                const arqueo = response.arqueo;
                $('#detalle_arqueo_id').text(arqueo.id_arqueo || 'N/A');
                $('#detalle_local').text(arqueo.local_nombre || 'N/A');
                $('#detalle_caja').text(arqueo.caja_numero || 'N/A');
                $('#detalle_empleado_apertura').text(arqueo.empleado_apertura_nombre || 'N/A');
                $('#detalle_fecha_apertura').text(arqueo.fecha_hora_apertura ? new Date(arqueo.fecha_hora_apertura).toLocaleString('es-AR') : 'N/A');
                $('#detalle_empleado_cierre').text(arqueo.empleado_cierre_nombre || 'N/A');
                $('#detalle_fecha_cierre').text(arqueo.fecha_hora_cierre ? new Date(arqueo.fecha_hora_cierre).toLocaleString('es-AR') : 'N/A');
                
                // Montos
                $('#detalle_efectivo_inicial').text(formatCurrency(arqueo.efectivo_inicial));
                $('#detalle_ingresos_bv').text(formatCurrency(arqueo.ingresos_bv));
                $('#detalle_egresos_bv').text(formatCurrency(arqueo.egresos_bv));
                $('#detalle_efectivo_final').text(formatCurrency(arqueo.efectivo_final));
                
                // Campos calculados si los devuelve la API, sino se deben calcular en front (ej: diferencia)
                // Asumo que Django calcula y envía estos campos.
                $('#detalle_total_sistema').text(formatCurrency(arqueo.total_sistema)); 
                $('#detalle_diferencia').text(formatCurrency(arqueo.diferencia)); 

    
                // 3. Inicializar/Cargar DataTables para movimientos (response.movimientos)
                if ($.fn.DataTable.isDataTable('#dataTableMovimientos')) {
                    dataTableMovimientos.destroy();
                    dataTableMovimientos = null;
                }
    
                dataTableMovimientos = $('#dataTableMovimientos').DataTable({
                    data: response.movimientos,
                    columns: [
                        { "data": "tipo_movimiento", "title": "Tipo", "defaultContent": "N/A" },
                        { "data": "monto", "title": "Monto", "render": (data) => formatCurrency(data), "className": "text-center" },
                        { "data": "descripcion", "title": "Descripción", "defaultContent": "-" },
                        { "data": "fecha_hora", "title": "Fecha/Hora", "render": (data) => data ? new Date(data).toLocaleString('es-AR') : 'N/A', "className": "text-center" },
                    ],
                    "paging": true,
                    "info": true,
                    "searching": true,
                    "responsive": true,
                    "language": { "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" },
                    "order": [[3, "desc"]],
                });
    
                // 4. Mostrar el modal
                $('#detalleArqueoModal').modal('show');
    
            },
            error: function(xhr) {
                Swal.close(); // Cerrar spinner
                
                let errorMsg = xhr.responseJSON?.error || 'No se pudo obtener el detalle del arqueo. Error de red o timeout.';
                
                if (xhr.status === 0 && xhr.statusText === 'timeout') {
                    errorMsg = 'La solicitud expiró (Timeout). El servidor no respondió a tiempo.';
                } else if (xhr.status >= 500) {
                    errorMsg = `Error interno del servidor (${xhr.status}). Revise los logs de Django.`;
                }
                
                Swal.fire('Error', errorMsg, 'error');
            }
        });
    });
    
    // ============================================================
    // 11. Ejecución Inicial al cargar el documento
    // ============================================================

    // CRÍTICO: Inicializar la tabla de arqueos si es la pestaña activa al cargar la página
    if ($('#arqueos-tab').hasClass('active')) {
        initArqueosDataTable();
    }

    $('#cerrarCajaForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        
        // Deshabilitar botón para evitar doble submit
        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.text();
        submitButton.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Cerrando...');

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(response) {
                Swal.fire('¡Éxito!', response.message || 'Caja cerrada correctamente.', 'success');
                $('#cerrarCajaModal').modal('hide');
                recargarTablas();
            },
            error: function(xhr) {
                handleFormError(xhr, '#cerrarCajaForm', '#cerrar-error-alert', 'Error al cerrar la caja.');
            },
            complete: function() {
                // Re-habilitar botón
                submitButton.prop('disabled', false).text(originalButtonText);
            }
        });
    });
    // ============================================================
    // 12. Limpieza de modales
    // ============================================================
    
    // Limpieza de errores al cerrar el modal de Cierre
    $('#cerrarCajaModal').on('hidden.bs.modal', function () {
        const form = $('#cerrarCajaForm');
        form[0].reset();
        form.find('.form-control').removeClass('is-invalid');
        form.find('.invalid-feedback').empty();
        $('#cerrar-error-alert').addClass('d-none').text('');
    });
});
