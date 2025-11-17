document.addEventListener('DOMContentLoaded', () => {
    const tablaBody = document.querySelector('#tablaStock tbody');

    async function cargarStock() {
        try {
            const response = await fetch('/stock/api/stock/');
            const data = await response.json();
            tablaBody.innerHTML = ''; // limpiar tabla
            const hoy = new Date();

            data.forEach(item => {
                const fila = document.createElement('tr');
                const fechaVenc = new Date(item.ID_Producto__Fecha_Venc_Prod);
                const stockActual = item.Stock_PxLC;
                const stockMinimo = item.Stock_Min_PxLC;

                // Determinar estilo según condiciones
                let clase = '';
                let mensaje = '';

                // Stock bajo
                if (stockActual <= stockMinimo) {
                    clase = 'table-danger';
                    mensaje = `⚠️ Stock bajo (${stockActual}/${stockMinimo})`;
                } else if (stockActual <= stockMinimo + 5) {
                    clase = 'table-warning';
                    mensaje = `🟡 Stock cerca del mínimo`;
                }

                // Vencimiento
                const diffDias = Math.ceil((fechaVenc - hoy) / (1000 * 60 * 60 * 24));
                if (diffDias <= 0) {
                    clase = 'table-danger';
                    mensaje = '❌ Producto vencido';
                } else if (diffDias <= 30) {
                    clase = 'table-warning';
                    mensaje = `⚠️ Por vencer (${diffDias} días)`;
                }

                fila.classList.add(clase);
                fila.title = mensaje;

                fila.innerHTML = `
                    <td>${item.ID_Producto__Nombre_Producto}</td>
                    <td>${stockActual}</td>
                    <td>${stockMinimo}</td>
                    <td>${fechaVenc.toLocaleDateString()}</td>
                `;
                tablaBody.appendChild(fila);
            });

        } catch (error) {
            console.error('Error cargando stock:', error);
        }
    }

    // Cargar al iniciar
    cargarStock();

    // Refrescar cada 30 segundos
    setInterval(cargarStock, 30000);
});
