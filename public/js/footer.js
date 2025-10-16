document.addEventListener('DOMContentLoaded', () => {
    // Busca el placeholder del footer en el documento
    const footerPlaceholder = document.getElementById('footer-placeholder');
    
    if (footerPlaceholder) {
        // Carga el contenido de footer.html y lo inserta en el placeholder
        fetch('footer.html')
            .then(response => response.text())
            .then(data => {
                footerPlaceholder.innerHTML = data;
            });
    }
});