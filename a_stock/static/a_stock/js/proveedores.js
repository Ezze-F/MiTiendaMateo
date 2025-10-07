// static/a_stock/js/proveedores.js

$(document).ready(function() {
    // Almacenamos las instancias de los modales
    const registrarProveedorModal = new bootstrap.Modal(document.getElementById('registrarProveedorModal'));
    const modificarProveedorModal = new bootstrap.Modal(document.getElementById('modificarProveedorModal'));
    const eliminarProveedorModal = new bootstrap.Modal(document.getElementById('eliminarProveedorModal'));
    const restaurarProveedorModal = new bootstrap.Modal(document.getElementById('restaurarProveedorModal'));

    // Configuración base para las tablas
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
        if ($.fn.DataTable.isDataTable('#dataTableProveedoresDisponibles')) {
            $('#dataTableProveedoresDisponibles').DataTable().destroy();
        }
        $('#dataTableProveedoresDisponibles').DataTable({
            ...dataTableConfig,
            "ajax": "/stock/proveedores/disponibles/",
            "columns": [{
                "data": "cuit_proveedor"
            }, {
                "data": "nombre_proveedor"
            }, {
                "data": "telefono_proveedor"
            }, {
                "data": "email_proveedor"
            }, {
                "data": "direccion_proveedor"
            }, {
                "data": null,
                "defaultContent": "<button class='btn btn-warning btn-sm editar'>Editar</button> <button class='btn btn-danger btn-sm eliminar'>Eliminar</button>",
                "className": "text-center"
            }]
        });

        if ($.fn.DataTable.isDataTable('#dataTableProveedoresEliminados')) {
            $('#dataTableProveedoresEliminados').DataTable().destroy();
        }
        $('#dataTableProveedoresEliminados').DataTable({
            ...dataTableConfig,
            "ajax": "/stock/proveedores/eliminados/",
            "columns": [{
                "data": "cuit_proveedor"
            }, {
                "data": "nombre_proveedor"
            }, {
                "data": "telefono_proveedor"
            }, {
                "data": null,
                "defaultContent": "<button class='btn btn-success btn-sm restaurar'>Restaurar</button>",
                "className": "text-center"
            }]
        });
    }
    initializeDataTables();

    // Función para recargar las tablas
    function reloadTables() {
        setTimeout(function() {
            initializeDataTables();
        }, 500);
    }

    // Manejar el envío del formulario de registro
    $('#registrarProveedorForm').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        $.ajax({
            url: form.attr('action'),
            type: form.attr('method'),
            data: form.serialize(),
            success: function(response) {
                registrarProveedorModal.hide();
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Éxito',
                        text: 'Proveedor registrado correctamente.',
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
            error: function(xhr) {
                registrarProveedorModal.hide();
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error en la solicitud.'
                });
            }
        });
    });

    // Manejar clic en botón "Editar"
    $('#dataTableProveedoresDisponibles tbody').on('click', '.editar', function() {
        var data = $('#dataTableProveedoresDisponibles').DataTable().row($(this).parents('tr')).data();
        if (data && data.cuit_proveedor) {
            $('#modificar_cuit_proveedor').val(data.cuit_proveedor);
            $('#modificar_nombre_proveedor').val(data.nombre_proveedor);
            $('#modificar_telefono_proveedor').val(data.telefono_proveedor);
            $('#modificar_email_proveedor').val(data.email_proveedor);
            $('#modificar_direccion_proveedor').val(data.direccion_proveedor);
            modificarProveedorModal.show();
        }
    });

    // Manejar el envío del formulario de modificación
    $('#modificarProveedorForm').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var cuit_proveedor = $('#modificar_cuit_proveedor').val();
        if (cuit_proveedor) {
            $.ajax({
                url: window.AppUrls.modificarProveedor + cuit_proveedor + '/',
                type: 'POST',
                data: form.serialize(),
                success: function(response) {
                    modificarProveedorModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Proveedor modificado correctamente.',
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
                error: function(xhr) {
                    modificarProveedorModal.hide();
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
    $('#dataTableProveedoresDisponibles tbody').on('click', '.eliminar', function() {
        var data = $('#dataTableProveedoresDisponibles').DataTable().row($(this).parents('tr')).data();
        if (data && data.cuit_proveedor) {
            $('#eliminar_cuit_proveedor').val(data.cuit_proveedor);
            eliminarProveedorModal.show();
        }
    });

    // Confirmar eliminación
    $('#confirmarEliminarBtn').on('click', function() {
        var cuit_proveedor = $('#eliminar_cuit_proveedor').val();
        if (cuit_proveedor) {
            $.ajax({
                url: window.AppUrls.borrarProveedor + cuit_proveedor + '/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    eliminarProveedorModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Proveedor eliminado correctamente.',
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
                    eliminarProveedorModal.hide();
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
    $('#dataTableProveedoresEliminados tbody').on('click', '.restaurar', function() {
        var data = $('#dataTableProveedoresEliminados').DataTable().row($(this).parents('tr')).data();
        if (data && data.cuit_proveedor) {
            $('#restaurar_cuit_proveedor').val(data.cuit_proveedor);
            restaurarProveedorModal.show();
        }
    });

    // Confirmar restauración
    $('#confirmarRestaurarBtn').on('click', function() {
        var cuit_proveedor = $('#restaurar_cuit_proveedor').val();
        if (cuit_proveedor) {
            $.ajax({
                url: window.AppUrls.recuperarProveedor + cuit_proveedor + '/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    restaurarProveedorModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Proveedor restaurado correctamente.',
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
                    restaurarProveedorModal.hide();
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