const API_BASE_URL = 'http://127.0.0.1:8000';

function initApp() {
    // Esta función se llama DESPUÉS de que el header se ha cargado dinámicamente.
    updateNavbar();
    updateBurgerMenu();
    // También inicializa los listeners del menú hamburguesa que ahora están en el header cargado.
    if (typeof initBurgerMenuListeners === 'function') {
        initBurgerMenuListeners();
    }
    // Inicializa la funcionalidad de la barra de búsqueda.
    initSearch();
}

function initSearch() {
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', (event) => {
            event.preventDefault(); // Evita que la página se recargue
            const searchInput = document.querySelector('.search-input');
            const searchTerm = searchInput.value.trim();

            // Solo buscamos si el usuario está en una página con grilla de productos
            if (document.getElementById('product-grid')) {
                fetchProducts(searchTerm);
            } else {
                // Si no, lo redirigimos a la página principal con el término de búsqueda
                window.location.href = `index.html?search=${encodeURIComponent(searchTerm)}`;
            }
        });
    }
}

function updateNavbar() {
    // Actualiza los elementos de login/perfil tanto en el header de escritorio como en el menú móvil.
    const userLoginElements = document.querySelectorAll('.user-login');
    const accessToken = localStorage.getItem('accessToken');

    if (userLoginElements.length === 0) return;

    userLoginElements.forEach(element => {
        const icon = element.querySelector('svg');
        const span = element.querySelector('span');

        if (accessToken) {
            element.href = 'perfil.html'; // O la página de perfil que corresponda
            if(span) span.textContent = 'Mi Perfil';
            
            // Mostramos el botón de logout si existe
            const logoutButton = document.querySelector('.logout-button');
            if (logoutButton) logoutButton.style.display = 'block';

        } else {
            element.href = 'login.html';
            if(span) span.textContent = 'Iniciar sesión';

            // Ocultamos el botón de logout si existe
            const logoutButton = document.querySelector('.logout-button');
            if (logoutButton) logoutButton.style.display = 'none';
        }
    });
}

function updateBurgerMenu() {
    // La lógica principal para actualizar los elementos de usuario en el menú móvil
    // ya está cubierta por `updateNavbar` que selecciona todos los elementos con la clase `.user-login`
    // y `.logout-button`. Esta función puede quedar vacía o usarse para lógica específica del menú burger si es necesario.
}

async function fetchProducts(searchTerm = '') {
    const productGrid = document.getElementById('product-grid');
    // Si no hay una grilla de productos en la página, no hacemos nada.
    if (!productGrid) {
        return;
    }

    let url = `${API_BASE_URL}/productos/`;
    if (searchTerm) {
        // Asumimos que tienes un endpoint de búsqueda en tu backend.
        // ¡Deberás crearlo si aún no existe!
        url = `${API_BASE_URL}/productos/buscar/?query=${encodeURIComponent(searchTerm)}`;
    }

    try {
        const response = await fetch(url); // No necesita token para ver productos
        if (response.ok) {
            const products = await response.json();
            renderProducts(products, searchTerm);
        } else {
            console.error('Error al obtener los productos:', await response.text());
            productGrid.innerHTML = '<p class="text-center">No se pudieron cargar los productos.</p>';
        }
    } catch (error) {
        console.error('Error de red:', error);
        productGrid.innerHTML = '<p class="text-center">Error de conexión. No se pudieron cargar los productos.</p>';
    }
}

// funcion para filtrar productos por categoria y precio
async function filtrarProductos(categoryID, minPrice, maxPrice) {
    console.log('Filtrando productos con:', { categoryID, minPrice, maxPrice });
    try {
        const response = categoryID ? await fetch(`${API_BASE_URL}/productos/categoria/${categoryID}`) : await fetch(`${API_BASE_URL}/productos/`);
        console.log('Response from filterProducts:', response);
        if (response.ok) {
            const productos = await response.json();
            // filtrar producto por precio
            let productosFiltrados = productos;
            if (minPrice !== null) {
                productosFiltrados = productosFiltrados.filter(producto => producto.price >= minPrice);
            }
            if (maxPrice !== null) {
                productosFiltrados = productosFiltrados.filter(producto => producto.price <= maxPrice);
            }
            renderProducts(productosFiltrados);
        } else {
            console.error('Error al obtener el productos:', await response.text());
            document.getElementById('producto-grid').innerHTML = '<p class="text-center">No se pudo cargar el producto.</p>';
        }
    } catch (error) {
        console.error('Error de red:', error);
        document.getElementById('producto-grid').innerHTML = '<p class="text-center">Error de conexión. No se pudo cargar el producto.</p>';
    }
}

// Obtener los datos de los input de filtro
function obtenerFiltros() {
    // Como puedo obtener solo el valor del input radio seleccionado
    const categoryInputs = document.querySelector('input[name="category"]:checked');
    console.log(categoryInputs);
    const categoryID = categoryInputs ? parseInt(categoryInputs.value) : null;
    console.log('Categoria seleccionada:', categoryID);

    const minPriceInput = document.getElementById('minprice-input');
    const minPrice = minPriceInput && minPriceInput.value ? parseFloat(minPriceInput.value) : null;

    const maxPriceInput = document.getElementById('maxprice-input');
    const maxPrice = maxPriceInput && maxPriceInput.value ? parseFloat(maxPriceInput.value) : null;

    filtrarProductos(categoryID, minPrice, maxPrice);
}

function renderProducts(products, searchTerm = '') {
    const productGrid = document.getElementById('product-grid');
    productGrid.innerHTML = ''; // Limpiar el grid

    if (products.length === 0 && searchTerm) {
        productGrid.innerHTML = `<p class="text-center">No se encontraron productos para "<strong>${searchTerm}</strong>".</p>`;
        return;
    }

    if (products.length === 0 && !searchTerm) {
        productGrid.innerHTML = '<p class="text-center">No hay productos disponibles en este momento.</p>';
        return;
    }

    products.forEach(product => {
        const productCard = `
            <div class="col-12 col-sm-6 col-md-4 col-lg-3 mb-4">
                <div class="card h-100 shadow-sm">
                    <a href="producto.html?id=${product.id}">
                        <img src="${product.image_url || imagen_no_disponible}" class="card-img-top" alt="${product.name}" style="width: 100%; height: 180px; object-fit: contain;">
                    </a>
                    <div class="card-body d-flex flex-column p-3">
                        <a href="producto.html?id=${product.id}" class="text-decoration-none text-dark flex-grow-1 mb-1">
                            <h5 class="card-title fw-bold m-0">${product.name}</h5>
                        </a>
                        <p class="card-text text-muted mb-2 flex-grow-1">${product.description || 'Sin descripción.'}</p>
                        <div class="d-flex flex-column align-items-start">
                            <span class="card-price">$${product.price.toFixed(2)}</span>
                            <button class="btn btn-primary w-100 mt-2 p-2 text-white rounded-pill" onclick="addToCart(${product.id})" ${product.stock === 0 ? 'disabled' : ''}>
                                ${product.stock > 0 ? 'Añadir al carrito' : 'Sin stock'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        productGrid.innerHTML += productCard;
    });
}

async function addToCart(productId) {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        alert('Debes iniciar sesión para añadir productos al carrito.');
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/carrito/mi_carrito/detalles`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + accessToken
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: 1 // Añadimos de a uno
            })
        });

        if (response.status === 201) {
            // El producto se añadió correctamente.
            // Actualizamos la vista del carrito para que el usuario vea el cambio.
            fetchCartDetails();
            // Y abrimos el sidebar si no estaba ya abierto para mostrar el producto añadido.
            const cartSidebar = document.getElementById('cart-sidebar');
            if (cartSidebar && !cartSidebar.classList.contains('open')) {
                toggleCartSidebar();
            }
        } else {
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                const errorData = await response.json();
                alert('Error al añadir al carrito: ' + (errorData.detail || 'Error desconocido.'));
            } else {
                const errorText = await response.text();
                console.error("Respuesta no JSON del servidor:", errorText);
                alert('Error al añadir al carrito: El servidor devolvió un error inesperado.');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ocurrió un error al intentar añadir el producto al carrito.');
    }
}

// Función para alternar la visibilidad del sidebar del carrito
function toggleCartSidebar() {
    // Obtenemos el elemento del carrito justo cuando lo necesitamos.
    // Esto soluciona el problema de que el script se ejecute antes de que el carrito exista.
    const cartSidebar = document.getElementById('cart-sidebar');
    if (cartSidebar) {
        cartSidebar.classList.toggle('open');
    } else {
        console.error("El elemento #cart-sidebar no se encontró en la página.");
    }
}

// Función para cargar los detalles del carrito
async function fetchCartDetails() {
    const accessToken = localStorage.getItem('accessToken');
    const cartItemsContainer = document.getElementById('cart-items-container');
    const cartTotalContainer = document.getElementById('cart-total');

    if (!accessToken) {
        cartItemsContainer.innerHTML = '<p class="text-muted">Inicia sesión para ver tu carrito.</p>';
        cartTotalContainer.innerHTML = '';
        return;
    }

    cartItemsContainer.innerHTML = '<p class="text-muted">Cargando carrito...</p>';
    cartTotalContainer.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE_URL}/carrito/mi_carrito/detalles`, {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + accessToken
            }
        });

        if (response.ok) {
            const cartDetails = await response.json();
            renderCartDetails(cartDetails);
        } else {
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                const errorData = await response.json();
                cartItemsContainer.innerHTML = `<p class="text-danger">Error al cargar el carrito: ${errorData.detail || response.statusText}</p>`;
            } else {
                const errorText = await response.text();
                console.error("Respuesta no JSON del servidor:", errorText);
                cartItemsContainer.innerHTML = `<p class="text-danger">Error al cargar el carrito: El servidor devolvió un error inesperado.</p>`;
            }
            cartTotalContainer.innerHTML = '';
        }
    } catch (error) {
        console.error('Error de red al cargar el carrito:', error);
        cartItemsContainer.innerHTML = '<p class="text-danger">Error de conexión al cargar el carrito.</p>';
        cartTotalContainer.innerHTML = '';
    }
}

// Función para renderizar los detalles del carrito
function renderCartDetails(cartDetails) {
    const cartItemsContainer = document.getElementById('cart-items-container');
    const cartTotalContainer = document.getElementById('cart-total');
    cartItemsContainer.innerHTML = '';
    let total = 0;

    if (!cartDetails || cartDetails.length === 0) {
        cartItemsContainer.innerHTML = '<p class="text-muted">Tu carrito está vacío.</p>';
        cartTotalContainer.innerHTML = '';
        return;
    }

    cartDetails.forEach(item => {
        cartItemsContainer.innerHTML += `
            <div class="d-flex justify-content-between align-items-center mb-3 border-bottom pb-3">
                <div class="d-flex align-items-center">
                    <img src="${item.image_url || 'https://via.placeholder.com/50'}" alt="${item.product_name}" class="img-fluid me-3" style="width: 50px; height: 50px; object-fit: cover;">
                    <div>
                        <p class="mb-0 fw-bold" style="font-size: 0.9rem;">${item.product_name}</p>
                        <small class="text-muted">$${item.price.toFixed(2)} c/u</small>
                    </div>
                </div>
                <div class="d-flex flex-column align-items-end">
                    <div class="d-flex align-items-center mb-1">
                        <button class="btn btn-sm btn-outline-secondary py-0 px-2" onclick="updateCartItemQuantity(${item.id}, ${item.quantity - 1})">-</button>
                        <span class="mx-2">${item.quantity}</span>
                        <button class="btn btn-sm btn-outline-secondary py-0 px-2" onclick="updateCartItemQuantity(${item.id}, ${item.quantity + 1})">+</button>
                    </div>
                    <button class="btn btn-sm btn-link text-danger p-0" onclick="removeCartItem(${item.id})">
                        <small>Eliminar</small>
                    </button>
                </div>
            </div>
        `;
        total += item.price * item.quantity;
    });

    cartTotalContainer.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Total: $${total.toFixed(2)}</h5>
            <div>
                <button class="btn btn-sm btn-outline-danger me-2" onclick="emptyCart()">Vaciar Carrito</button>
                <button class="btn btn-sm btn-primary" onclick="checkout()">Finalizar Compra</button>
            </div>
        </div>
    `;
}

async function updateCartItemQuantity(itemId, newQuantity) {
    if (newQuantity <= 0) {
        // Si la cantidad es 0 o menos, eliminamos el item sin volver a preguntar.
        await removeCartItem(itemId, false);
        return;
    }

    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) { return; }

    try {
        const response = await fetch(`${API_BASE_URL}/carrito/mi_carrito/detalles/${itemId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken },
            body: JSON.stringify({ quantity: newQuantity })
        });

        if (response.ok) {
            await fetchCartDetails(); // Refrescar el carrito para mostrar el cambio
        } else {
            const errorData = await response.json();
            alert(`Error al actualizar el carrito: ${errorData.detail}`);
            await fetchCartDetails(); // Refrescar para mostrar el estado real del servidor
        }
    } catch (error) {
        console.error('Error de red al actualizar el carrito:', error);
    }
}

async function removeCartItem(itemId, confirmFirst = true) {
    if (confirmFirst && !confirm('¿Estás seguro de que quieres eliminar este producto del carrito?')) {
        return;
    }

    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) { return; }

    try {
        const response = await fetch(`${API_BASE_URL}/carrito/mi_carrito/detalles/${itemId}`, {
            method: 'DELETE',
            headers: { 'Authorization': 'Bearer ' + accessToken }
        });

        if (response.status === 204) {
            await fetchCartDetails(); // Refrescar el carrito para mostrar que se eliminó
        } else {
            const errorData = await response.json();
            alert(`Error al eliminar del carrito: ${errorData.detail}`);
        }
    } catch (error) {
        console.error('Error de red al eliminar del carrito:', error);
    }
}

async function emptyCart() {
    if (!confirm('¿Estás seguro de que quieres vaciar todo el carrito?')) {
        return;
    }

    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) { return; }

    try {
        const response = await fetch(`${API_BASE_URL}/carrito/mi_carrito/vaciar`, {
            method: 'DELETE',
            headers: { 'Authorization': 'Bearer ' + accessToken }
        });

        if (response.status === 204) {
            await fetchCartDetails(); // Refrescar el carrito para mostrar que está vacío
        } else {
            const errorData = await response.json();
            alert(`Error al vaciar el carrito: ${errorData.detail}`);
        }
    } catch (error) {
        console.error('Error de red al vaciar el carrito:', error);
        alert('Error de conexión al vaciar el carrito.');
    }
}

function checkout() {
    window.location.href = 'pedidos.html';
}