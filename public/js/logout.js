function logout() {
			localStorage.removeItem('accessToken');
			// Recargamos la página para que el header se actualice correctamente.
			window.location.reload();
		}