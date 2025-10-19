from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.auth import endpoints as auth_endpoints
from api.productos import endpoints as productos_endpoints
from api.checkout import endpoints as checkout_endpoints
from api.metodos_pago import endpoints as metodos_pago_endpoints
from api.usuarios import endpoints as usuarios_endpoints
from api.pagos import endpoints as pagos_endpoints
import api.abrir_carrito.endpoints


app = FastAPI(title="E-commerce API")


app.include_router(api.abrir_carrito.endpoints.router)
app.include_router(productos_endpoints.router)
app.include_router(auth_endpoints.router)
app.include_router(checkout_endpoints.router)
app.include_router(metodos_pago_endpoints.router)
app.include_router(usuarios_endpoints.router)
app.include_router(pagos_endpoints.router)

app.mount("/", StaticFiles(directory="public", html=True), name="static")