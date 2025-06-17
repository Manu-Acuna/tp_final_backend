from fastapi import APIRouter


router = APIRouter()


@router.get("/") #localhost:8000/productos/
async def productos():
    return {"productos": "productos"}