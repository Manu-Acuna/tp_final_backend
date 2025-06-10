from fastapi import FastAPI

import api.usuarios.endpoints
import api.ejemplo2.endpoints

app = FastAPI()

prefix_base="/api/v1"
app.include_router(api.usuarios.endpoints.router, prefix=f"{prefix_base}/usuarios")
app.include_router(api.ejemplo2.endpoints.router, prefix=f"{prefix_base}/ejemplo2")