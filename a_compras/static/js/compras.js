$(document).ready(function() {

    // ==========================================================
    // 1. Inicializar DataTables
    // ==========================================================
    if ($('#dataTableCompras').length) {
        $('#dataTableCompras').DataTable({
            "order": [[0, "desc"]],
            "language": { "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" }
        });
    }

    if ($('#dataTableComprasEliminadas').length) {
        $('#dataTableComprasEliminadas').DataTable({
            "order": [[0, "desc"]],
            "language": { "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" }
        });
    }

    // ==========================================================
    // 2. Cambiar Estado de Compra + Swal
    // ==========================================================
    $('.btn-abrir-estado').click(function() {
        let compraId = $(this).data('id');
        let estado = $(this).data('estado');
        $('#compra-id-input').val(compraId);
        $('#estado-select').val(estado);
        new bootstrap.Modal($('#estadoCompraModal')).show();
    });

    $('#estado-compra-form').submit(function(e) {
        e.preventDefault();

        $.ajax({
            url: '/compras/',
            type: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                Swal.fire(
                    '¡Estado Actualizado!',
                    response.message || 'La compra fue actualizada correctamente.',
                    'success'
                ).then(() => location.reload());
            },
            error: function(xhr) {
                Swal.fire(
                    'Error',
                    xhr.responseJSON?.error || 'No se pudo actualizar el estado.',
                    'error'
                );
            }
        });
    });

    // ==========================================================
    // 3. Crear Compra con Swal
    // ==========================================================
    $('#crearCompraModal form').submit(function(e) {
        e.preventDefault();

        $.ajax({
            url: '/compras/',
            type: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                Swal.fire('¡Compra guardada!',
                    response.message || 'La compra fue registrada con éxito.',
                    'success'
                ).then(() => location.reload());
            },
            error: function(xhr) {
                Swal.fire(
                    'Error',
                    'No se pudo crear la compra.',
                    'error'
                );
            }
        });
    });

    // Mostrar modal si hay errores validados desde backend (Django)
    const crearCompraModal = $('#crearCompraModal');
    if (crearCompraModal.data('show') === 'true') {
        new bootstrap.Modal(crearCompraModal).show();
    }

    // ==========================================================
    // 4. Eliminar Compra con Confirmación y Swal
    // ==========================================================
    $('.btn-eliminar-compra').click(function() {
        let compraId = $(this).data('id');

        Swal.fire({
            title: '¿Estás seguro?',
            text: 'Esta compra será eliminada.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `/compras/eliminar/${compraId}/`,
                    type: 'POST',
                    data: {
                        csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val()
                    },
                    success: function(response) {
                        Swal.fire(
                            'Eliminada!',
                            response.message || 'Compra eliminada con éxito.',
                            'success'
                        ).then(() => location.reload());
                    },
                    error: function(xhr) {
                        Swal.fire(
                            'Error',
                            xhr.responseJSON?.error || 'Ocurrió un error.',
                            'error'
                        );
                    }
                });
            }
        });
    });


    // ==========================================================
    // 6. Filtrado dinámico de Locales y Productos por Proveedor
    // ==========================================================
    function actualizarProductosLocales(proveedorId, fila=null) {
    if (proveedorId) {
        const url = ajaxLocalesProductosUrl.replace('0', proveedorId);

        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function(data) {

                // --- Actualizar Local ---
                let localSelect = $('#id_local');
                let selectedLocal = localSelect.val();
                localSelect.empty().append('<option value="">Seleccione un local</option>');

                data.locales.forEach(function(loc) {
                    localSelect.append(`<option value="${loc.id_loc_com}">${loc.nombre_loc_com}</option>`);
                });

                if (selectedLocal && data.locales.some(l => l.id_loc_com == selectedLocal)) {
                    localSelect.val(selectedLocal);
                } else {
                    localSelect.val('');
                }

                // --- Actualizar Productos ---
                if (fila) {
                    let sel = fila.find('select[name$="-id_producto"]');
                    let valorActual = sel.val();

                    sel.empty().append('<option value="">Seleccione un producto</option>');
                    data.productos.forEach(function(prod) {

                        let texto = `${prod.nombre_producto} — ${prod.id_marca__nombre_marca || "Sin marca"} — ${prod.texto_unidad}`;

                        sel.append(`<option value="${prod.id_producto}">${texto}</option>`);
                    });

                    sel.val(valorActual);

                } else {

                    $('.detalle-compra select[name$="-id_producto"]').each(function() {
                        let sel = $(this);
                        let valorActual = sel.val();

                        sel.empty().append('<option value="">Seleccione un producto</option>');
                        data.productos.forEach(function(prod) {

                            let texto = `${prod.nombre_producto} — ${prod.id_marca__nombre_marca || "Sin marca"} — ${prod.texto_unidad}`;

                            sel.append(`<option value="${prod.id_producto}">${texto}</option>`);
                        });

                        sel.val(valorActual);
                    });
                }
            },
            error: function(xhr, status, error) {
                console.error('Error AJAX locales-productos:', error);
            }
        });

    } else {
        $('#id_local').empty().append('<option value="">Seleccione un local</option>');
        $('.detalle-compra select[name$="-id_producto"]').empty().append('<option value="">Seleccione un producto</option>');
    }
}


    // Cuando cambia el proveedor
    $('#id_proveedor').change(function() {
        let proveedorId = $(this).val();
        actualizarProductosLocales(proveedorId);
    });

    // Cuando se agrega una nueva fila en el formset
    $('#formset-container').on('focus', 'select[name$="-id_producto"]', function() {
        let proveedorId = $('#id_proveedor').val();
        if (proveedorId) {
            actualizarProductosLocales(proveedorId, $(this).closest('.detalle-compra'));
        }
    });

    function resetCompraForm() {
        // Vacia el select de proveedor y productos
        $('#id_proveedor').val(''); // pone vacío
        $('#id_producto').empty().append('<option value="">---------</option>');

        // Si tenés otros campos del form, también los podés resetear
        $('#id_local').val('');
        $('#id_cantidad').val('');
    }

    // Llamar a esta función cuando se abra el modal de nueva compra
    $('#boton-nueva-compra').on('click', function() {
        resetCompraForm();
    });

    //CODIGO NUEVO
    $(document).on("click", ".btn-registrar-pago", function () {
        let compraId = $(this).data("id");

        Swal.fire({
            title: "Registrar Pago",
            text: "¿Cómo se pagó esta compra?",
            icon: "question",
            showCancelButton: true,
            confirmButtonText: "Billetera Virtual",
            cancelButtonText: "Efectivo",
        }).then((result) => {
            if (result.isConfirmed) {
                // ---- PEDIR LISTA DE BILLETERAS ----
                $.get("/compras/ajax/billeteras/", function (data) {
                    let opciones = {};
                    data.billeteras.forEach(b => {
                        opciones[b.id_bv] = b.nombre_bv;
                    });

                    Swal.fire({
                        title: "Selecciona una billetera",
                        input: "select",
                        inputOptions: opciones,
                        inputPlaceholder: "Seleccionar...",
                        showCancelButton: true,
                        confirmButtonText: "Pagar"
                    }).then(sel => {
                        if (sel.isConfirmed) {
                            registrarPago(compraId, "Billetera", sel.value);
                        }
                    });

                });

            } else if (result.dismiss === Swal.DismissReason.cancel) {
                registrarPago(compraId, "Efectivo", null);
            }
        });
    });


    function registrarPago(compraId, metodo, billeteraId = null) {
        $.ajax({
            url: "/compras/registrar-pago/" + compraId + "/",
            method: "POST",
            headers: { "X-CSRFToken": csrf_token },
            data: {
                metodo_pago: metodo,
                id_bv: billeteraId,
            },
            success: function (response) {
                Swal.fire("Pago Registrado", response.message, "success");
                setTimeout(() => location.reload(), 1200);
            },
            error: function (xhr) {
                Swal.fire("Error", xhr.responseJSON.error, "error");
            }
        });
    }

    // ======================================================
    // AGREGAR PRODUCTO AL FORMSET
    // ======================================================
    $(document).on("click", "#add-form", function () {

        const formsetContainer = $("#formset-container");

        // Obtener el TOTAL_FORMS real que usa Django
        const totalFormsInput = $("#id_detallescompras_set-TOTAL_FORMS");
        let formCount = parseInt(totalFormsInput.val());

        // Tomamos la primera tarjeta como plantilla
        let newForm = $(".detalle-compra").first().clone(true);

        // Limpiar inputs del formulario
        newForm.find("input, select").val("");

        // Reemplazar índices del formset
        newForm.html(
            newForm.html().replace(
                new RegExp(`detallescompras_set-(\\d+)`, "g"),
                `detallescompras_set-${formCount}`
            )
        );

        // Agregar el nuevo formulario debajo del último
        formsetContainer.append(newForm);

        // Actualizar TOTAL_FORMS
        totalFormsInput.val(formCount + 1);
    });


    // ======================================================
    // ELIMINAR PRODUCTO DEL FORMSET
    // ======================================================
    $(document).on("click", ".remove-form", function () {
        $(this).closest(".detalle-compra").remove();
    });


});