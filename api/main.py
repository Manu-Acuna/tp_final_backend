from fastapi import FastAPI

import api.abrir_carrito.endpoints
import api.productos.endpoints
import api.login.endpoints

app = FastAPI()

prefix_base="/api/v1"
app.include_router(api.productos.endpoints.router, prefix=f"{prefix_base}/productos")
app.include_router(api.login.endpoints.router, prefix=f"{prefix_base}/login")
app.include_router(api.abrir_carrito.endpoints.router, prefix=f"{prefix_base}/carrito")