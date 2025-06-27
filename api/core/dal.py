from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.core import models

async def obtener_direccion_envio_por_id_y_usuario(db: AsyncSession, address_id: int, user_id: int):
    """Obtiene una dirección de envío por su ID y verifica que pertenezca al usuario."""
    result = await db.execute(
        select(models.DireccionesEnvio).where(
            models.DireccionesEnvio.id == address_id,
            models.DireccionesEnvio.user_id == user_id
        )
    )
    return result.scalars().first()

async def obtener_metodo_pago_tipo_por_id(db: AsyncSession, payment_method_id: int):
    """
    Obtiene un tipo de método de pago por su ID.
    NOTA: El modelo `models.MetodosPago` en el esquema actual no tiene `user_id`.
    Si se desea validar que un método de pago *específico* pertenece al usuario,
    se necesitaría una tabla `UserPaymentMethods` (o similar) con un `user_id`.
    """
    result = await db.execute(
        select(models.MetodosPago).where(models.MetodosPago.id == payment_method_id)
    )
    return result.scalars().first()