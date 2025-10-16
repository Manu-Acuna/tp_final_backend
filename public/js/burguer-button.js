/**
 * Inicializa los listeners para el menú hamburguesa.
 * Esta función debe ser llamada DESPUÉS de que el HTML del header haya sido inyectado en el DOM.
 */
function initBurgerMenuListeners() {
    // Botón para abrir el menú
    const burgers = document.querySelectorAll('.navbar-burger');
    const menus = document.querySelectorAll('.navbar-menu');

    if (burgers.length && menus.length) {
        burgers.forEach(burger => {
            burger.addEventListener('click', function() {
                menus.forEach(menu => {
                    menu.classList.toggle('d-none');
                });
            });
        });
    }

    // Botón para cerrar el menú (la 'X')
    const closes = document.querySelectorAll('.navbar-close');
    // Fondo oscuro que también cierra el menú
    const backdrops = document.querySelectorAll('.navbar-backdrop');

    const closeElements = [...closes, ...backdrops];

    if (closeElements.length) {
        closeElements.forEach(el => {
            el.addEventListener('click', function() {
                menus.forEach(menu => {
                    menu.classList.toggle('d-none');
                }
            )});
        });
    }
}
