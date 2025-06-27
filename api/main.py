from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.pedidos_pagos import endpoints as pedidos_endpoints
from api.auth import endpoints as auth_endpoints
from api.productos import endpoints as productos_endpoints

import api.abrir_carrito.endpoints
import api.productos.endpoints
import api.login.endpoints


app = FastAPI(title="E-commerce API")

prefix_base="/NoteMania"
app.include_router(api.productos.endpoints.router, prefix=f"{prefix_base}")
app.include_router(api.login.endpoints.router, prefix=f"{prefix_base}/login")
app.include_router(api.abrir_carrito.endpoints.router, prefix=f"{prefix_base}")
app.include_router(pedidos_endpoints.router)
app.include_router(productos_endpoints.router)
app.include_router(auth_endpoints.router)

app.mount("/", StaticFiles(directory="public", html=True), name="static")