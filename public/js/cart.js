document.addEventListener('DOMContentLoaded', () => {
    const cartPlaceholder = document.getElementById('cart-placeholder');
    
    if (cartPlaceholder) {
        fetch('cart.html')
            .then(response => response.text())
            .then(data => {
                cartPlaceholder.innerHTML = data;
                // Una vez que el HTML del carrito está cargado, podemos añadir el listener al botón de cierre.
                const closeButton = document.getElementById('cart-sidebar-close');
                if (closeButton) {
                    closeButton.addEventListener('click', toggleCartSidebar);
                }
            });
    }
});