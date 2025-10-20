import asyncio
import sys
import json
import os
import sys

# --- Configuración para poder importar desde la carpeta 'api' ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from sqlalchemy.future import select

# Asegúrar de que las rutas de importación sean correctas desde la raíz
from api.core.database import AsyncSessionLocal

from api.core import models

async def set_admin_status(email: str, is_admin: bool = True):
    """
    Busca un usuario por su email y establece su estado de administrador.
    """
    print(f"Intentando establecer is_admin={is_admin} para el usuario: {email}")
    
    async with AsyncSessionLocal() as db:
        try:
            # Buscar al usuario
            result = await db.execute(select(models.Usuarios).where(models.Usuarios.email == email))
            user = result.scalars().first()

            if not user:
                print(f"Error: No se encontró ningún usuario con el email '{email}'.")
                return

            # Actualizar el estado de administrador
            user.is_admin = is_admin
            await db.commit()
            
            print(f"¡Éxito! El usuario '{email}' ahora tiene is_admin={is_admin}.")

        except Exception as e:
            await db.rollback()
            print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python make_admin.py <email_del_usuario>")
        sys.exit(1)
        
    user_email = sys.argv[1]
    asyncio.run(set_admin_status(user_email))


#COMANDO PARA EJECUTARLO POR CONSOLA

# python scripts/make_admin.py "ejemplo@mail.com" (sin comillas, el mail tiene que existir en la db)
