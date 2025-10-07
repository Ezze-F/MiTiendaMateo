$(document).ready(function() {

    // ------------------ MINI-CSS AJUSTE ------------------
    $('<style>')
        .prop('type', 'text/css')
        .html(`
            /* Ajuste márgenes botones dentro de las tablas */
            #dataTableProvinciasActivas .btn,
            #dataTableProvinciasEliminadas .btn {
                margin-right: 0.25rem;
            }

            /* Alineación central de botones */
            #dataTableProvinciasActivas td.text-center,
            #dataTableProvinciasEliminadas td.text-center {
                vertical-align: middle !important;
            }

            /* Margen entre título y botón Registrar */
            #btnRegistrarProvincia {
                margin-left: 0.5rem;
            }

            /* Iconos dentro de botones */
            .btn i.fas {
                margin-right: 0.25rem;
            }
        `)
        .appendTo('head');

    let dataTableActivas;
    let dataTableEliminadas;

    const recargarTablas = () => {
        if (dataTableActivas) dataTableActivas.ajax.reload(null, false);
        if (dataTableEliminadas) dataTableEliminadas.ajax.reload(null, false);
    };

    // ------------------ DATATABLES ------------------
    dataTableActivas = $('#dataTableProvinciasActivas').DataTable({
        ajax: { url: listarProvinciasActivasUrl, dataSrc: "data" },
        columns: [
            { data: "id_provincia" },
            { data: "nombre_provincia" },
            {
                data: null,
                render: function(data,type,row) {
                    const id = row.id_provincia;
                    const nombre = row.nombre_provincia;
                    return `
                        <div class="d-flex justify-content-center">
                            <button class="btn btn-info btn-sm me-2 btn-modificar" data-id="${id}" data-nombre="${nombre}" title="Modificar">
                                <i class="fas fa-edit"></i>Modificar
                            </button>
                            <button class="btn btn-danger btn-sm btn-borrar" data-id="${id}" data-nombre="${nombre}" title="Borrar">
                                <i class="fas fa-trash-alt"></i>Borrar
                            </button>
                        </div>
                    `;
                },
                orderable: false,
                searchable: false,
                className: "text-center"
            }
        ],
        language: { url: "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" },
        responsive: true
    });

    dataTableEliminadas = $('#dataTableProvinciasEliminadas').DataTable({
        ajax: { url: listarProvinciasEliminadasUrl, dataSrc: "data" },
        columns: [
            { data: "id_provincia" },
            { data: "nombre_provincia" },
            { 
                data: "fh_borrado_p",
                className: "text-center",
                render: data => data ? data : 'N/A'
            },
            {
                data: null,
                render: function(data,type,row) {
                    const id = row.id_provincia;
                    const nombre = row.nombre_provincia;
                    return `
                        <div class="d-flex justify-content-center">
                            <button class="btn btn-success btn-sm btn-recuperar" data-id="${id}" data-nombre="${nombre}" title="Recuperar">
                                <i class="fas fa-undo"></i>Recuperar
                            </button>
                        </div>
                    `;
                },
                orderable: false,
                searchable: false,
                className: "text-center"
            }
        ],
        language: { url: "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" },
        responsive: true
    });

    // ------------------ REGISTRO ------------------
    $('#formRegistroProvincia').on('submit', function(e) {
        e.preventDefault();
        $('#btnRegistrar').prop('disabled', true);
        $('#reg_error_message').text('');
        $.ajax({
            url: registrarProvinciaUrl,
            method: 'POST',
            data: $(this).serialize(),
            success: function(res) {
                Swal.fire('¡Éxito!', res.message, 'success');
                $('#modalRegistroProvincia').modal('hide');
                $('#formRegistroProvincia')[0].reset();
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                let msg = r.error || 'Error desconocido';
                if (r.errors) msg = r.errors.nombre_provincia || msg;
                $('#reg_error_message').text(msg);
                Swal.fire('Error', msg, 'error');
            },
            complete: function() { $('#btnRegistrar').prop('disabled', false); }
        });
    });

    $('#btnRegistrarProvincia').on('click', function() {
        $('#formRegistroProvincia')[0].reset();
        $('#reg_error_message').text('');
        $('#modalRegistroProvincia').modal('show');
    });

    // ------------------ MODIFICACIÓN ------------------
    $('#dataTableProvinciasActivas tbody').on('click', '.btn-modificar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');
        $('#mod_id_provincia').val(id);
        $('#mod_nombre_provincia').val(nombre);
        $('#mod_error_message').text('');
        $('#modalModificarProvincia').modal('show');
    });

    $('#formModificarProvincia').on('submit', function(e) {
        e.preventDefault();
        const id = $('#mod_id_provincia').val();
        const url = modificarProvinciaUrl.replace('0', id);
        $('#btnModificar').prop('disabled', true);
        $('#mod_error_message').text('');
        $.ajax({
            url: url,
            method: 'POST',
            data: $(this).serialize(),
            success: function(res) {
                Swal.fire('¡Éxito!', res.message, 'success');
                $('#modalModificarProvincia').modal('hide');
                recargarTablas();
            },
            error: function(xhr) {
                const r = xhr.responseJSON;
                let msg = r.error || 'Error desconocido';
                if (r.errors) msg = r.errors.nombre_provincia || msg;
                $('#mod_error_message').text(msg);
                Swal.fire('Error', msg, 'error');
            },
            complete: function() { $('#btnModificar').prop('disabled', false); }
        });
    });

    // ------------------ BAJA ------------------
    $('#dataTableProvinciasActivas tbody').on('click', '.btn-borrar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');
        const url = borrarProvinciaUrl.replace('0', id);
        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se dará de baja la provincia: ${nombre}. Podrás recuperarla luego.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, borrar',
            cancelButtonText: 'Cancelar'
        }).then(result => {
            if(result.isConfirmed) {
                $.ajax({
                    url: url,
                    method: 'POST',
                    headers: { 'X-CSRFToken': $('[name="csrfmiddlewaretoken"]').val() },
                    success: function(res) {
                        Swal.fire('¡Borrada!', res.message, 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al borrar', 'error');
                    }
                });
            }
        });
    });

    // ------------------ RECUPERAR ------------------
    $('#dataTableProvinciasEliminadas tbody').on('click', '.btn-recuperar', function() {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');
        const url = recuperarProvinciaUrl.replace('0', id);
        Swal.fire({
            title: '¿Estás seguro?',
            text: `Se recuperará la provincia: ${nombre}.`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#28a745',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, Recuperar',
            cancelButtonText: 'Cancelar'
        }).then(result => {
            if(result.isConfirmed) {
                $.ajax({
                    url: url,
                    method: 'POST',
                    headers: { 'X-CSRFToken': $('[name="csrfmiddlewaretoken"]').val() },
                    success: function(res) {
                        Swal.fire('¡Recuperada!', res.message, 'success');
                        recargarTablas();
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al recuperar', 'error');
                    }
                });
            }
        });
    });

    // ------------------ AJUSTE DE COLUMNAS PESTAÑAS ------------------
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        const target = $(e.target).data('bs-target');
        if(target === '#provinciasActivasTab' && dataTableActivas) dataTableActivas.columns.adjust().responsive.recalc();
        if(target === '#provinciasEliminadasTab' && dataTableEliminadas) dataTableEliminadas.columns.adjust().responsive.recalc();
    });

});
