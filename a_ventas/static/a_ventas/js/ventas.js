$(document).ready(function() {
    let detalles = [];
    
    // Cargar cajas cuando se selecciona un local
    $('#id_loc_com').change(function() {
        const localId = $(this).val();
        if (localId) {
            $.get(`/ventas/api/cajas-disponibles/${localId}/`, function(data) {
                const selectCaja = $('#id_caja');
                selectCaja.empty().append('<option value="">Seleccionar caja...</option>');
                data.forEach(caja => {
                    selectCaja.append(`<option value="${caja.id}">Caja ${caja.numero}</option>`);
                });
            });
        }
    });
    
    // Buscar productos
    $('#btn-buscar').click(buscarProductos);
    $('#buscar_producto').keypress(function(e) {
        if (e.which === 13) {
            e.preventDefault();
            buscarProductos();
        }
    });
    
    function buscarProductos() {
        const query = $('#buscar_producto').val();
        if (query.length < 2) return;
        
        $.get('/ventas/api/productos/', { q: query }, function(data) {
            const resultados = $('#resultados-busqueda');
            resultados.empty().show();
            
            if (data.length === 0) {
                resultados.append('<div class="list-group-item text-muted">No se encontraron productos</div>');
                return;
            }
            
            data.forEach(producto => {
                const item = $(`
                    <div class="list-group-item list-group-item-action">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h6 class="mb-1">${producto.nombre}</h6>
                                <small class="text-muted">${producto.marca} - $${producto.precio}</small>
                            </div>
                            <button type="button" class="btn btn-sm btn-primary btn-agregar" 
                                    data-id="${producto.id}" data-nombre="${producto.nombre}" 
                                    data-precio="${producto.precio}">
                                Agregar
                            </button>
                        </div>
                    </div>
                `);
                resultados.append(item);
            });
            
            // Evento para agregar producto
            $('.btn-agregar').click(function() {
                const productoId = $(this).data('id');
                const productoNombre = $(this).data('nombre');
                const productoPrecio = $(this).data('precio');
                
                agregarProducto(productoId, productoNombre, productoPrecio);
                $('#resultados-busqueda').hide().empty();
                $('#buscar_producto').val('');
            });
        });
    }
    
    function agregarProducto(productoId, productoNombre, productoPrecio) {
        // Verificar si el producto ya está en los detalles
        const existe = detalles.find(d => d.productoId == productoId);
        if (existe) {
            alert('Este producto ya está en la venta');
            return;
        }
        
        // Verificar stock
        const localId = $('#id_loc_com').val();
        if (!localId) {
            alert('Primero seleccione un local comercial');
            return;
        }
        
        $.get(`/ventas/api/stock/${productoId}/${localId}/`, function(stockData) {
            if (stockData.disponible <= 0) {
                alert('Producto sin stock disponible');
                return;
            }
            
            const detalle = {
                productoId: productoId,
                nombre: productoNombre,
                precio: parseFloat(productoPrecio),
                cantidad: 1,
                subtotal: parseFloat(productoPrecio)
            };
            
            detalles.push(detalle);
            actualizarTablaDetalles();
            actualizarTotal();
        });
    }
    
    function actualizarTablaDetalles() {
        const tbody = $('#tbody-detalles');
        tbody.empty();
        
        detalles.forEach((detalle, index) => {
            const fila = $(`
                <tr>
                    <td>${detalle.nombre}</td>
                    <td>
                        <input type="number" class="form-control form-control-sm cantidad" 
                               value="${detalle.cantidad}" min="1" data-index="${index}" 
                               style="width: 80px;">
                    </td>
                    <td>$${detalle.precio.toFixed(2)}</td>
                    <td class="subtotal">$${detalle.subtotal.toFixed(2)}</td>
                    <td>
                        <button type="button" class="btn btn-sm btn-danger btn-eliminar" 
                                data-index="${index}">Eliminar</button>
                    </td>
                </tr>
            `);
            tbody.append(fila);
        });
        
        // Eventos para modificar cantidad
        $('.cantidad').change(function() {
            const index = $(this).data('index');
            const nuevaCantidad = parseInt($(this).val());
            
            if (nuevaCantidad > 0) {
                detalles[index].cantidad = nuevaCantidad;
                detalles[index].subtotal = nuevaCantidad * detalles[index].precio;
                actualizarTablaDetalles();
                actualizarTotal();
            }
        });
        
        // Eventos para eliminar
        $('.btn-eliminar').click(function() {
            const index = $(this).data('index');
            detalles.splice(index, 1);
            actualizarTablaDetalles();
            actualizarTotal();
        });
    }
    
    function actualizarTotal() {
        const total = detalles.reduce((sum, detalle) => sum + detalle.subtotal, 0);
        $('#total-venta').text('$' + total.toFixed(2));
        
        // Actualizar campo oculto con detalles
        const detallesHidden = $('#detalles-hidden');
        detallesHidden.empty();
        detalles.forEach(detalle => {
            detallesHidden.append(
                `<input type="hidden" name="detalles" value="${detalle.productoId}|${detalle.cantidad}|${detalle.precio}">`
            );
        });
    }
    
    // Validación del formulario antes de enviar
    $('#form-venta').submit(function(e) {
        if (detalles.length === 0) {
            e.preventDefault();
            alert('Debe agregar al menos un producto a la venta');
            return false;
        }
        
        const localId = $('#id_loc_com').val();
        const cajaId = $('#id_caja').val();
        const empleadoId = $('#id_empleado').val();
        
        if (!localId || !cajaId || !empleadoId) {
            e.preventDefault();
            alert('Complete todos los campos requeridos');
            return false;
        }
    });
});