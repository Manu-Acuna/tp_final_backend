import asyncio
import sys
import os

# --- Configuración para poder importar desde la carpeta 'api' ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from sqlalchemy.future import select

# Asegurar que las rutas de importación sean correctas desde la raíz
from api.core.database import AsyncSessionLocal
from api.core import models

async def change_user_email(user_id: int, new_email: str):
    """
    Busca un usuario por su ID y cambia su dirección de email.
    """
    print(f"Intentando cambiar el email del usuario con ID={user_id} a '{new_email}'")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Opcional pero recomendado: Verificar si el nuevo email ya está en uso
            result_existing = await db.execute(select(models.Usuarios).where(models.Usuarios.email == new_email))
            if result_existing.scalars().first():
                print(f"Error: El email '{new_email}' ya está en uso por otro usuario.")
                return

            # 2. Buscar al usuario por ID
            user = await db.get(models.Usuarios, user_id)

            if not user:
                print(f"Error: No se encontró ningún usuario con el ID '{user_id}'.")
                return

            # 3. Actualizar el email y guardar los cambios
            user.email = new_email
            await db.commit()
            
            print(f"¡Éxito! El email del usuario con ID={user_id} ha sido cambiado a '{new_email}'.")

        except Exception as e:
            await db.rollback()
            print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python scripts/change_email.py <ID_del_usuario> <nuevo_email>")
        sys.exit(1)
        
    target_user_id = int(sys.argv[1])
    target_new_email = sys.argv[2]
    asyncio.run(change_user_email(target_user_id, target_new_email))