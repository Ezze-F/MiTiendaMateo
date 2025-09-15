// Lógica para desplegar el menú de submenús

document.addEventListener('DOMContentLoaded', () => {

    // Selecciona todos los enlaces (<a>) que están dentro de un elemento con la clase 'has-submenu'
    const hasSubmenuLinks = document.querySelectorAll('.has-submenu > a');

    // Itera sobre cada uno de los enlaces
    hasSubmenuLinks.forEach(link => {
        // Agrega un 'event listener' para el evento 'click'
        link.addEventListener('click', (event) => {
            // Evita la acción por defecto del enlace si no tiene una URL definida
            if (link.getAttribute('href') === '#') {
                event.preventDefault();
            }

            // Alterna la clase 'open' en el elemento padre (<li>) para desplegar el submenú
            const parentLi = link.closest('.has-submenu');
            parentLi.classList.toggle('open');
        });
    });

    // Lógica para el menú responsive de dispositivos móviles
    // Selecciona el botón del menú por su ID
    const menuToggle = document.getElementById('menu-toggle');
    // Selecciona el cuerpo del documento
    const body = document.body;

    // Escucha el evento 'click' en el botón de hamburguesa
    menuToggle.addEventListener('click', () => {
        // Alterna la clase 'menu-open' en el cuerpo del documento
        body.classList.toggle('menu-open');
    });

});