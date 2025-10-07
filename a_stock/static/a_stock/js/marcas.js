$(document).ready(function() {
    // Almacenamos las instancias de los modales
    const registrarMarcaModal = new bootstrap.Modal(document.getElementById('registrarMarcaModal'));
    const modificarMarcaModal = new bootstrap.Modal(document.getElementById('modificarMarcaModal'));
    const eliminarMarcaModal = new bootstrap.Modal(document.getElementById('eliminarMarcaModal'));
    const restaurarMarcaModal = new bootstrap.Modal(document.getElementById('restaurarMarcaModal'));

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
        if ($.fn.DataTable.isDataTable('#dataTableMarcasDisponibles')) {
            $('#dataTableMarcasDisponibles').DataTable().destroy();
        }
        $('#dataTableMarcasDisponibles').DataTable({
            ...dataTableConfig,
            "ajax": "/stock/marcas/disponibles/",
            "columns": [{
                "data": "id_marca"
            }, {
                "data": "nombre_marca"
            }, {
                "data": null,
                "defaultContent": "<button class='btn btn-warning btn-sm editar'>Editar</button> <button class='btn btn-danger btn-sm eliminar'>Eliminar</button>",
                "className": "text-center"
            }]
        });

        if ($.fn.DataTable.isDataTable('#dataTableMarcasEliminadas')) {
            $('#dataTableMarcasEliminadas').DataTable().destroy();
        }
        $('#dataTableMarcasEliminadas').DataTable({
            ...dataTableConfig,
            "ajax": "/stock/marcas/eliminadas/",
            "columns": [{
                "data": "id_marca"
            }, {
                "data": "nombre_marca"
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
    $('#registrarMarcaForm').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        $.ajax({
            url: form.attr('action'),
            type: form.attr('method'),
            data: form.serialize(),
            success: function(response) {
                registrarMarcaModal.hide();
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Éxito',
                        text: 'Marca registrada correctamente.',
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
                registrarMarcaModal.hide();
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error en la solicitud.'
                });
            }
        });
    });

    // Manejar clic en botón "Editar"
    $('#dataTableMarcasDisponibles tbody').on('click', '.editar', function() {
        var data = $('#dataTableMarcasDisponibles').DataTable().row($(this).parents('tr')).data();
        if (data && data.id_marca) {
            $('#modificar_id_marca').val(data.id_marca);
            $('#modificar_nombre_marca').val(data.nombre_marca);
            modificarMarcaModal.show();
        }
    });

    // Manejar el envío del formulario de modificación
    $('#modificarMarcaForm').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var marca_id = $('#modificar_id_marca').val();
        if (marca_id) {
            $.ajax({
                url: window.AppUrls.modificarMarca + marca_id + '/',
                type: 'POST',
                data: form.serialize(),
                success: function(response) {
                    modificarMarcaModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Marca modificada correctamente.',
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
                    modificarMarcaModal.hide();
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
    $('#dataTableMarcasDisponibles tbody').on('click', '.eliminar', function() {
        var data = $('#dataTableMarcasDisponibles').DataTable().row($(this).parents('tr')).data();
        if (data && data.id_marca) {
            $('#eliminar_id_marca').val(data.id_marca);
            eliminarMarcaModal.show();
        }
    });

    // Confirmar eliminación
    $('#confirmarEliminarBtn').on('click', function() {
        var marca_id = $('#eliminar_id_marca').val();
        if (marca_id) {
            $.ajax({
                url: window.AppUrls.borrarMarca + marca_id + '/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    eliminarMarcaModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Marca eliminada correctamente.',
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
                    eliminarMarcaModal.hide();
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
    $('#dataTableMarcasEliminadas tbody').on('click', '.restaurar', function() {
        var data = $('#dataTableMarcasEliminadas').DataTable().row($(this).parents('tr')).data();
        if (data && data.id_marca) {
            $('#restaurar_id_marca').val(data.id_marca);
            restaurarMarcaModal.show();
        }
    });

    // Confirmar restauración
    $('#confirmarRestaurarBtn').on('click', function() {
        var marca_id = $('#restaurar_id_marca').val();
        if (marca_id) {
            $.ajax({
                url: window.AppUrls.recuperarMarca + marca_id + '/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    restaurarMarcaModal.hide();
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Marca restaurada correctamente.',
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
                    restaurarMarcaModal.hide();
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