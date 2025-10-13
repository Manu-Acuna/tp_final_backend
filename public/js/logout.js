function logout() {
			localStorage.removeItem('accessToken');
			updateNavbar();
			updateBurgerMenu();
			fetchCartDetails(); // Limpia la vista del carrito
		}