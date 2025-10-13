const cartSidebar = document.getElementById('cart-sidebar');
document.addEventListener('DOMContentLoaded', function () {
    updateNavbar();
    fetchProducts();
    updateBurgerMenu();
});

function updateNavbar() {
    const navbarButtons = document.getElementById('navbar-buttons');
    const accessToken = localStorage.getItem('accessToken');

    if (accessToken) {
        // Usuario logueado
        navbarButtons.innerHTML = `
            <div class="row align-items-center g-6">
                <div class="col-auto">
                    <a class="link-secondary fs-11 fw-medium" href="#">Mi Perfil</a>
                </div>
                <div class="col-auto"> 
                    <button class="btn btn-link link-secondary fs-11 fw-medium p-0" onclick="toggleCartSidebar(); fetchCartDetails();">Carrito</button>
                </div>
                <div class="col-auto">
                    <button class="btn btn-sm btn-danger shadow" onclick="logout()">Cerrar Sesión</button>
                </div>
            </div>
        `;
    } else {
        // Usuario no logueado
        navbarButtons.innerHTML = `
            <div class="row align-items-center g-6">
                <div class="col-auto">
                    <a class="link-secondary fs-11 fw-medium" href="login.html">Iniciar Sesión</a>
                </div>
                <div class="col-auto">
                    <a class="btn btn-sm btn-success shadow" href="register.html">Registrarse</a>
                </div>
            </div>
        `;
    }
}

function updateBurgerMenu() {
    const navbarBurgerButtons = document.getElementById('navbar-burger-buttons');
    const accessToken = localStorage.getItem('accessToken');
    
    if (accessToken) {
        // Usuario logueado
        navbarBurgerButtons.innerHTML = `
            <div class="col-12">
                <a class="link-secondary fs-11 fw-medium d-block w-100 text-center" href="#">Mi Perfil</a>
            </div>
            <div class="col-12"> 
                <button class="btn btn-link link-secondary fs-11 fw-medium p-0 d-block w-100 text-center" onclick="toggleCartSidebar(); fetchCartDetails();"><i class="fa-solid fa-cart-shopping"></i></button>
            </div>
            <div class="col-12">
                <button class="btn btn-sm btn-danger shadow d-block w-100" onclick="logout()">Cerrar Sesión</button>
            </div>
        `;
    } else {
        // Usuario no logueado
        navbarBurgerButtons.innerHTML = `
            <div class="col-12">
                <a class="link-secondary fs-11 fw-medium d-block w-100 text-center" href="login.html">Iniciar Sesión</a>
            </div>
            <div class="col-12">
                <a class="btn btn-sm btn-success shadow d-block w-100" href="register.html">Registrarse</a>
            </div>
        `;
    }
}

async function fetchProducts() {
    try {
        const response = await fetch('/productos/');
        if (response.ok) {
            const products = await response.json();
            renderProducts(products);
        } else {
            console.error('Error al obtener los productos:', await response.text());
            document.getElementById('product-grid').innerHTML = '<p class="text-center">No se pudieron cargar los productos.</p>';
        }
    } catch (error) {
        console.error('Error de red:', error);
        document.getElementById('product-grid').innerHTML = '<p class="text-center">Error de conexión. No se pudieron cargar los productos.</p>';
    }
}

function renderProducts(products) {
    const productGrid = document.getElementById('product-grid');
    productGrid.innerHTML = ''; // Limpiar el grid

    if (products.length === 0) {
        productGrid.innerHTML = '<p class="text-center">No hay productos disponibles en este momento.</p>';
        return;
    }

    products.forEach(product => {
        const productCard = `
            <div class="col-12 col-md-6 col-lg-4">
                <div class="card h-100 shadow-sm">
                    <img src="${product.image_url || `https://via.placeholder.com/300x200.png?text=Imagen+no+disponible`}" class="card-img-top" alt="${product.name}" style="width: 100%; height: 180px; object-fit: contain;">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text text-secondary-dark flex-grow-1">${product.description || 'Sin descripción.'}</p>
                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <p class="card-text fs-5 fw-bold text-success mb-0">$${product.price.toFixed(2)}</p>
                            <button class="btn btn-sm btn-success" onclick="addToCart(${product.id})" ${product.stock === 0 ? 'disabled' : ''}>
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
        const response = await fetch('/carrito/mi_carrito/detalles', {
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
            if (!cartSidebar.classList.contains('open')) {
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
    cartSidebar.classList.toggle('open');
}

// Cerrar el sidebar al hacer clic en el botón de cerrar
document.getElementById('cart-sidebar-close').addEventListener('click', toggleCartSidebar);

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
        const response = await fetch('/carrito/mi_carrito/detalles', {
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
        const response = await fetch(`/carrito/mi_carrito/detalles/${itemId}`, {
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
        const response = await fetch(`/carrito/mi_carrito/detalles/${itemId}`, {
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
        const response = await fetch(`/carrito/mi_carrito/vaciar`, {
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