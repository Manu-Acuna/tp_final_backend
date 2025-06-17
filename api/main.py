from fastapi import FastAPI

import api.usuarios.endpoints
import api.productos.endpoints
import api.login.endpoints

app = FastAPI()

prefix_base="/api/v1"
app.include_router(api.usuarios.endpoints.router, prefix=f"{prefix_base}/usuarios")
app.include_router(api.productos.endpoints.router, prefix=f"{prefix_base}/productos")
app.include_router(api.login.endpoints.router, prefix=f"{prefix_base}/login")