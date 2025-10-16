document.addEventListener('DOMContentLoaded', () => {
    // Busca el placeholder en el documento
    const headerPlaceholder = document.getElementById('header-placeholder');
    
    if (headerPlaceholder) {
        // Carga el contenido de header.html y lo inserta en el placeholder
        fetch('header.html')
            .then(response => response.text())
            .then(data => {
                headerPlaceholder.innerHTML = data;
                // Una vez cargado el header, inicializamos la app (navbar, burger menu, etc.)
                initApp();
            });
    }
});