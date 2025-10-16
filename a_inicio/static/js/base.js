console.log('Base.js cargado y ejecutado correctamente.');

document.addEventListener('DOMContentLoaded', () => {
    
    // Seleccionamos los enlaces con la clase 'submenu-toggle'
    const submenuToggles = document.querySelectorAll('.submenu-toggle');
    // Seleccionamos TODOS los elementos LI padres del submenú
    const allSubmenuParents = document.querySelectorAll('.has-submenu');

    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function (e) {
            e.preventDefault(); // Evita comportamiento predeterminado (href="#")

            const parentLi = this.closest('.has-submenu');
            const isOpen = parentLi.classList.contains('open');

            // 1. Cerrar todos los submenús (elimina la clase 'open' de todos)
            allSubmenuParents.forEach(li => li.classList.remove('open'));

            // 2. Si el submenú NO estaba abierto, abrir el actual
            if (!isOpen) {
                parentLi.classList.add('open');
            }
        });
    });

    // Menú móvil (hamburguesa)
    const menuToggle = document.getElementById('menu-toggle');
    const body = document.body;

    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            body.classList.toggle('menu-open');

            // Cerrar submenús al colapsar el menú móvil
            if (!body.classList.contains('menu-open')) {
                allSubmenuParents.forEach(li => li.classList.remove('open'));
            }
        });
    }
});