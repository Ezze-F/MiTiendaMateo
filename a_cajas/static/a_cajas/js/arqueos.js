$(document).ready(function () {

    // ========================
    // TABLA: Arqueos Abiertos
    // ========================
    const tablaArqueosAbiertos = $('#dataTableArqueosAbiertos').DataTable({
        ajax: {
            url: AppUrls.listarArqueosAbiertos,
            dataSrc: ''
        },
        columns: [
            { data: 'id_arqueo', visible: false },
            { data: 'numero_caja' },
            { data: 'nombre_local' },
            { data: 'usuario_apertura' },
            { data: 'fecha_apertura' },
            { data: 'monto_inicial', render: $.fn.dataTable.render.number(',', '.', 2, '$') },
            {
                data: null,
                render: function (data) {
                    return `
                        <button class="btn btn-success btn-sm cerrar-arqueo" data-id="${data.id_arqueo}">
                            <i class="fas fa-lock"></i> Cerrar
                        </button>
                        <button class="btn btn-info btn-sm detalle-arqueo" data-id="${data.id_arqueo}">
                            <i class="fas fa-eye"></i> Ver Detalle
                        </button>
                    `;
                }
            }
        ],
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
        }
    });

    // ========================
    // TABLA: Arqueos Cerrados
    // ========================
    const tablaArqueosCerrados = $('#dataTableArqueosCerrados').DataTable({
        ajax: {
            url: AppUrls.listarArqueosCerrados,
            dataSrc: ''
        },
        columns: [
            { data: 'id_arqueo', visible: false },
            { data: 'numero_caja' },
            { data: 'nombre_local' },
            { data: 'usuario_cierre' },
            { data: 'fecha_cierre' },
            { data: 'monto_final', render: $.fn.dataTable.render.number(',', '.', 2, '$') },
            {
                data: null,
                render: function (data) {
                    return `
                        <button class="btn btn-info btn-sm detalle-arqueo" data-id="${data.id_arqueo}">
                            <i class="fas fa-eye"></i> Ver Detalle
                        </button>
                    `;
                }
            }
        ],
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
        }
    });

    // ========================
    // EVENTOS
    // ========================

    // Cerrar Arqueo
    $('#dataTableArqueosAbiertos').on('click', '.cerrar-arqueo', function () {
        const id = $(this).data('id');

        Swal.fire({
            title: '¿Cerrar arqueo?',
            text: 'Una vez cerrado no se podrá modificar.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Sí, cerrar',
            cancelButtonText: 'Cancelar'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: AppUrls.cerrarArqueo + id + '/',
                    type: 'POST',
                    headers: { 'X-CSRFToken': getCSRFToken() },
                    success: function (response) {
                        Swal.fire('Cerrado', 'El arqueo ha sido cerrado correctamente.', 'success');
                        tablaArqueosAbiertos.ajax.reload();
                        tablaArqueosCerrados.ajax.reload();
                    },
                    error: function () {
                        Swal.fire('Error', 'No se pudo cerrar el arqueo.', 'error');
                    }
                });
            }
        });
    });

    // Ver Detalle de Arqueo
    $(document).on('click', '.detalle-arqueo', function () {
        const id = $(this).data('id');
        window.location.href = AppUrls.verDetalleArqueo + id + '/';
    });

    // ========================
    // FUNCIONES AUXILIARES
    // ========================
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

});
