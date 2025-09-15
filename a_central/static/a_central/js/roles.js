$(document).ready(function() {
    // Almacenamos las instancias de los modales para una gestión más eficiente
    const registrarRolModal = new bootstrap.Modal(document.getElementById('registrarRolModal'));
    const modificarRolModal = new bootstrap.Modal(document.getElementById('modificarRolModal'));
    const eliminarRolModal = new bootstrap.Modal(document.getElementById('eliminarRolModal'));
    const restaurarRolModal = new bootstrap.Modal(document.getElementById('restaurarRolModal'));

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
    
    // Inicializar DataTables la primera vez que carga la página
    console.log("Inicializando DataTables...");
    try {
        if (!$.fn.DataTable.isDataTable('#dataTableRolesDisponibles')) {
            $('#dataTableRolesDisponibles').DataTable({
                ...dataTableConfig,
                "ajax": "/central/roles/disponibles/",
                "columns": [{
                    "data": "id"
                }, {
                    "data": "nombre"
                }, {
                    "data": "descripcion"
                }, {
                    "data": null,
                    "defaultContent": "<button class='btn btn-warning btn-sm editar'>Editar</button> <button class='btn btn-danger btn-sm eliminar'>Eliminar</button>",
                    "className": "text-center"
                }]
            });
        }
        if (!$.fn.DataTable.isDataTable('#dataTableRolesEliminados')) {
            $('#dataTableRolesEliminados').DataTable({
                ...dataTableConfig,
                "ajax": "/central/roles/eliminados/",
                "columns": [{
                    "data": "id"
                }, {
                    "data": "nombre"
                }, {
                    "data": "descripcion"
                }, {
                    "data": "fecha_borrado"
                }, {
                    "data": null,
                    "defaultContent": "<button class='btn btn-success btn-sm restaurar'>Restaurar</button>",
                    "className": "text-center"
                }]
            });
        }
        console.log("DataTables inicializadas correctamente.");
    } catch (e) {
        console.error("Error al inicializar DataTables:", e);
    }
    
    // Función para (destruir y) recargar ambas DataTables de forma segura
    function reloadTables() {
        console.log('Forzando recarga de DataTables...');
        // Esperamos un momento para que el modal se cierre completamente
        setTimeout(function() {
            // Destruir la instancia de las tablas existentes si existen
            if ($.fn.DataTable.isDataTable('#dataTableRolesDisponibles')) {
                $('#dataTableRolesDisponibles').DataTable().destroy();
            }
            if ($.fn.DataTable.isDataTable('#dataTableRolesEliminados')) {
                $('#dataTableRolesEliminados').DataTable().destroy();
            }

            // Volver a inicializar la tabla de roles disponibles
            $('#dataTableRolesDisponibles').DataTable({
                ...dataTableConfig,
                // **CORRECCIÓN:** Se añade el prefijo /central/
                "ajax": "/central/roles/disponibles/",
                "columns": [{
                    "data": "id"
                }, {
                    "data": "nombre"
                }, {
                    "data": "descripcion"
                }, {
                    "data": null,
                    "defaultContent": "<button class='btn btn-warning btn-sm editar'>Editar</button> <button class='btn btn-danger btn-sm eliminar'>Eliminar</button>",
                    "className": "text-center"
                }]
            });

            // Volver a inicializar la tabla de roles eliminados
            $('#dataTableRolesEliminados').DataTable({
                ...dataTableConfig,
                // **CORRECCIÓN:** Se añade el prefijo /central/
                "ajax": "/central/roles/eliminados/",
                "columns": [{
                    "data": "id"
                }, {
                    "data": "nombre"
                }, {
                    "data": "descripcion"
                }, {
                    "data": "fecha_borrado"
                }, {
                    "data": null,
                    "defaultContent": "<button class='btn btn-success btn-sm restaurar'>Restaurar</button>",
                    "className": "text-center"
                }]
            });
        }, 500); // 500ms de retraso
    }
    
    // Manejar el envío del formulario de registro de rol
    $('#registrarRolForm').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        $.ajax({
            url: form.attr('action'),
            type: form.attr('method'),
            data: form.serialize(),
            success: function(response) {
                registrarRolModal.hide();
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Éxito',
                        text: 'Rol registrado correctamente.',
                        showConfirmButton: false,
                        timer: 1500
                    });
                    // Recarga las tablas después de un registro exitoso.
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
                registrarRolModal.hide();
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error en la solicitud.'
                });
            }
        });
    });

    // Manejar clic en botón "Editar"
    $('#dataTableRolesDisponibles tbody').on('click', '.editar', function() {
        var data = $('#dataTableRolesDisponibles').DataTable().row($(this).parents('tr')).data();
        if (data && data.id) {
            $('#modificar_id_rol').val(data.id);
            $('#modificar_nombre_rol').val(data.nombre);
            $('#modificar_descripcion_rol').val(data.descripcion);
            modificarRolModal.show();
        }
    });

    // Manejar el envío del formulario de modificación de rol
    $('#modificarRolForm').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var rol_id = $('#modificar_id_rol').val();
        if (rol_id) {
            $.ajax({
                url: window.AppUrls.modificarRol + rol_id + '/',
                type: 'POST',
                data: form.serialize(),
                success: function(response) {
                    modificarRolModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Rol modificado correctamente.',
                            showConfirmButton: false,
                            timer: 1500
                        });
                        // Recarga las tablas después de una modificación exitosa.
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
                    modificarRolModal.hide();
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
    $('#dataTableRolesDisponibles tbody').on('click', '.eliminar', function() {
        var data = $('#dataTableRolesDisponibles').DataTable().row($(this).parents('tr')).data();
        if (data && data.id) {
            $('#eliminar_id_rol').val(data.id);
            eliminarRolModal.show();
        }
    });

    // Confirmar eliminación de rol
    $('#confirmarEliminarBtn').on('click', function() {
        var rol_id = $('#eliminar_id_rol').val();
        if (rol_id) {
            $.ajax({
                url: window.AppUrls.borrarRol + rol_id + '/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    eliminarRolModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Rol eliminado correctamente.',
                            showConfirmButton: false,
                            timer: 1500
                        });
                        // Recarga las tablas después de una eliminación exitosa.
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
                    eliminarRolModal.hide();
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
    $('#dataTableRolesEliminados tbody').on('click', '.restaurar', function() {
        var data = $('#dataTableRolesEliminados').DataTable().row($(this).parents('tr')).data();
        if (data && data.id) {
            $('#restaurar_id_rol').val(data.id);
            restaurarRolModal.show();
        }
    });

    // Confirmar restauración de rol
    $('#confirmarRestaurarBtn').on('click', function() {
        var rol_id = $('#restaurar_id_rol').val();
        if (rol_id) {
            $.ajax({
                url: window.AppUrls.recuperarRol + rol_id + '/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    restaurarRolModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Rol restaurado correctamente.',
                            showConfirmButton: false,
                            timer: 1500
                        });
                        // Recarga las tablas después de una restauración exitosa.
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
                    restaurarRolModal.hide();
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