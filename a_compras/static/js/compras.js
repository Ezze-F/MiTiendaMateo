$(document).ready(function() {

    // 1. Inicializar DataTable
    $('#dataTableCompras').DataTable({
        "order": [[0, "desc"]],
        "language": { "url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json" }
    });

    // 2. Formset dinámico
    let form_idx = parseInt($('#formset-container').data('total-forms'));

    $('#add-form').click(function() {
        agregarProducto();
    });

    $('#formset-container').on('click', '.remove-form', function() {
        eliminarProducto($(this));
    });

    function agregarProducto() {
        let form_html = $('.detalle-compra:first').clone(false);
        form_html.find('input, select').each(function() {
            let name = $(this).attr('name').replace(/\-\d+\-/, '-' + form_idx + '-');
            let id = 'id_' + name;
            $(this).attr({'name': name, 'id': id}).val('').removeClass('is-invalid');
        });
        form_html.find('.errorlist, .invalid-feedback').remove();
        $('#formset-container').append(form_html);
        form_idx++;
        $('#id_detallescompras_set-TOTAL_FORMS').val(form_idx);
    }

    function eliminarProducto(button) {
        if($('.detalle-compra').length > 1){
            button.closest('.detalle-compra').remove();
            let current_total = parseInt($('#id_detallescompras_set-TOTAL_FORMS').val());
            $('#id_detallescompras_set-TOTAL_FORMS').val(current_total - 1);
        }
    }

    // 3. Modal de cambiar estado
    $('.btn-abrir-estado').click(function() {
        let compraId = $(this).data('id');
        let estado = $(this).data('estado');
        $('#compra-id-input').val(compraId);
        $('#estado-select').val(estado);
        new bootstrap.Modal(document.getElementById('estadoCompraModal')).show();
    });

    // 4. Confirmación de eliminación
    $('.btn-eliminar-compra').click(function() {
        return confirm('¿Seguro que deseas eliminar esta compra?');
    });

    // 5. Mostrar modal de nueva compra si viene del backend
    const crearCompraModal = document.getElementById('crearCompraModal');
    if (crearCompraModal.dataset.show === 'true') {
        new bootstrap.Modal(crearCompraModal).show();
    }

});
