from fastapi import FastAPI
from api.pedidos_pagos import endpoints as pedidos_endpoints

import api.abrir_carrito.endpoints
import api.productos.endpoints
import api.login.endpoints

app = FastAPI()

prefix_base="/api/v1"
app.include_router(api.productos.endpoints.router, prefix=f"{prefix_base}/productos")
app.include_router(api.login.endpoints.router, prefix=f"{prefix_base}/login")
app.include_router(api.abrir_carrito.endpoints.router, prefix=f"{prefix_base}/carrito")
app.include_router(pedidos_endpoints.router)
