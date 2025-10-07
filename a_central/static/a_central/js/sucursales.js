// static/a_central/js/sucursales.js

$(document).ready(function() {
    // Almacenamos las instancias de los modales
    const registrarSucursalModal = new bootstrap.Modal(document.getElementById('registrarSucursalModal'));
    const modificarSucursalModal = new bootstrap.Modal(document.getElementById('modificarSucursalModal'));
    const eliminarSucursalModal = new bootstrap.Modal(document.getElementById('eliminarSucursalModal'));
    const restaurarSucursalModal = new bootstrap.Modal(document.getElementById('restaurarSucursalModal'));

    // Configuración base para las tablas, para evitar repetición de código
    const dataTableConfig = {
        "dataSrc": "data",
        "cache": false,
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json"
        },
        "error": function(xhr, error, thrown) {
            Swal.fire({
                icon: 'error',
                title: 'Error de carga',
                text: 'No se pudieron cargar los datos. Revisa la URL de la API y el servidor.'
            });
        }
    };

    // Inicializar DataTables
    function initializeDataTables() {
        if (!$.fn.DataTable.isDataTable('#dataTableSucursalesDisponibles')) {
            $('#dataTableSucursalesDisponibles').DataTable({
                ...dataTableConfig,
                "ajax": "/central/sucursales/disponibles/",
                "columns": [{
                    "data": "id_sucursal"
                }, {
                    "data": "nombre_sucursal"
                }, {
                    "data": "cod_postal_suc"
                }, {
                    "data": "telefono_suc"
                }, {
                    "data": "direccion_suc"
                }, {
                    "data": "provincia"
                }, {
                    "data": null,
                    "defaultContent": "<button class='btn btn-warning btn-sm editar'>Editar</button> <button class='btn btn-danger btn-sm eliminar'>Eliminar</button>",
                    "className": "text-center"
                }]
            });
        }
        if (!$.fn.DataTable.isDataTable('#dataTableSucursalesEliminadas')) {
            $('#dataTableSucursalesEliminadas').DataTable({
                ...dataTableConfig,
                "ajax": "/central/sucursales/eliminadas/",
                "columns": [{
                    "data": "id_sucursal"
                }, {
                    "data": "nombre_sucursal"
                }, {
                    "data": "cod_postal_suc"
                }, {
                    "data": "telefono_suc"
                }, {
                    "data": "direccion_suc"
                }, {
                    "data": "provincia"
                }, {
                    "data": null,
                    "defaultContent": "<button class='btn btn-success btn-sm restaurar'>Restaurar</button>",
                    "className": "text-center"
                }]
            });
        }
    }
    initializeDataTables();

    // Función para (destruir y) recargar ambas DataTables de forma segura
    function reloadTables() {
        setTimeout(function() {
            if ($.fn.DataTable.isDataTable('#dataTableSucursalesDisponibles')) {
                $('#dataTableSucursalesDisponibles').DataTable().destroy();
            }
            if ($.fn.DataTable.isDataTable('#dataTableSucursalesEliminadas')) {
                $('#dataTableSucursalesEliminadas').DataTable().destroy();
            }
            initializeDataTables();
        }, 500); // 500ms de retraso para que el modal se cierre completamente
    }

    // Manejar el envío del formulario de registro
    $('#registrarSucursalForm').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        $.ajax({
            url: form.attr('action'),
            type: form.attr('method'),
            data: form.serialize(),
            success: function(response) {
                registrarSucursalModal.hide();
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Éxito',
                        text: 'Sucursal registrada correctamente.',
                        showConfirmButton: false,
                        timer: 1500
                    });
                    reloadTables();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Error: ' + response.error
                    });
                }
            },
            error: function() {
                registrarSucursalModal.hide();
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error en la solicitud.'
                });
            }
        });
    });

    // Manejar clic en botón "Editar"
    $('#dataTableSucursalesDisponibles tbody').on('click', '.editar', function() {
        var data = $('#dataTableSucursalesDisponibles').DataTable().row($(this).parents('tr')).data();
        if (data && data.id_sucursal) {
            $('#modificar_id_sucursal').val(data.id_sucursal);
            $('#modificar_nombre_sucursal').val(data.nombre_sucursal);
            $('#modificar_cod_postal_suc').val(data.cod_postal_suc);
            $('#modificar_telefono_suc').val(data.telefono_suc);
            $('#modificar_direccion_suc').val(data.direccion_suc);
            // Selecciona la provincia correcta en el modal de modificación
            $('#id_provincia_mod option').filter(function() {
                return $(this).text().trim() === data.provincia;
            }).prop('selected', true);
            modificarSucursalModal.show();
        }
    });

    // Manejar el envío del formulario de modificación
    $('#modificarSucursalForm').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var sucursal_id = $('#modificar_id_sucursal').val();
        if (sucursal_id) {
            $.ajax({
                url: window.AppUrls.modificarSucursal + sucursal_id + '/',
                type: 'POST',
                data: form.serialize(),
                success: function(response) {
                    modificarSucursalModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Sucursal modificada correctamente.',
                            showConfirmButton: false,
                            timer: 1500
                        });
                        reloadTables();
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'Error: ' + response.error
                        });
                    }
                },
                error: function() {
                    modificarSucursalModal.hide();
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Error en la solicitud.'
                    });
                }
            });
        }
    });

    // Manejar clic en botón "Eliminar"
    $('#dataTableSucursalesDisponibles tbody').on('click', '.eliminar', function() {
        var data = $('#dataTableSucursalesDisponibles').DataTable().row($(this).parents('tr')).data();
        if (data && data.id_sucursal) {
            $('#eliminar_id_sucursal').val(data.id_sucursal);
            eliminarSucursalModal.show();
        }
    });

    // Confirmar eliminación de sucursal
    $('#confirmarEliminarBtn').on('click', function() {
        var sucursal_id = $('#eliminar_id_sucursal').val();
        if (sucursal_id) {
            $.ajax({
                url: window.AppUrls.borrarSucursal + sucursal_id + '/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    eliminarSucursalModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Sucursal eliminada correctamente.',
                            showConfirmButton: false,
                            timer: 1500
                        });
                        reloadTables();
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'Error: ' + response.error
                        });
                    }
                },
                error: function() {
                    eliminarSucursalModal.hide();
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Error en la solicitud.'
                    });
                }
            });
        }
    });

    // Manejar clic en botón "Restaurar"
    $('#dataTableSucursalesEliminadas tbody').on('click', '.restaurar', function() {
        var data = $('#dataTableSucursalesEliminadas').DataTable().row($(this).parents('tr')).data();
        if (data && data.id_sucursal) {
            $('#restaurar_id_sucursal').val(data.id_sucursal);
            restaurarSucursalModal.show();
        }
    });

    // Confirmar restauración de sucursal
    $('#confirmarRestaurarBtn').on('click', function() {
        var sucursal_id = $('#restaurar_id_sucursal').val();
        if (sucursal_id) {
            $.ajax({
                url: window.AppUrls.recuperarSucursal + sucursal_id + '/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    restaurarSucursalModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Sucursal restaurada correctamente.',
                            showConfirmButton: false,
                            timer: 1500
                        });
                        reloadTables();
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'Error: ' + response.error
                        });
                    }
                },
                error: function() {
                    restaurarSucursalModal.hide();
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Error en la solicitud.'
                    });
                }
            });
        }
    });
});