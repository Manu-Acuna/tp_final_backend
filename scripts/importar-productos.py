import asyncio
import json
import os
import sys

# --- Configuración para poder importar desde la carpeta 'api' ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# ----------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

# Importamos lo necesario para la base de datos y la creación de productos
from api.core.database import AsyncSessionLocal
from api.productos import dal as productos_dal
from api.productos import schemas as productos_schemas



# Nombre del archivo de entrada
INPUT_FILE = "productos_exportados.txt"

async def import_products_from_txt():
    """
    Lee productos desde un archivo .txt (en formato JSON Lines) y los
    inserta en la base de datos.
    """
    print(f"Iniciando la importación de productos desde '{INPUT_FILE}'...")

    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: El archivo '{INPUT_FILE}' no fue encontrado. Asegúrate de que esté en la raíz del proyecto.")
        return

    imported_count = 0
    skipped_count = 0

    async with AsyncSessionLocal() as db:
        try:
            with open(INPUT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    # Convertimos la línea de texto JSON a un diccionario
                    product_data = json.loads(line.strip())

                    # Verificamos si un producto con el mismo nombre ya existe
                    existing_product = await productos_dal.obtener_producto_por_nombre(db, product_data["name"])
                    if existing_product:
                        print(f"🟡 Omitiendo producto existente: '{product_data['name']}'")
                        skipped_count += 1
                        continue

                    # Creamos un objeto Pydantic a partir de los datos
                    producto_a_crear = productos_schemas.ProductoCreate(**product_data)

                    # Usamos la función del DAL para crear el producto
                    await productos_dal.crear_producto(db, producto=producto_a_crear)
                    imported_count += 1

            print("\n--- Resumen de la importación ---")
            print(f"✅ Productos importados exitosamente: {imported_count}")
            print(f"🟡 Productos omitidos (ya existían): {skipped_count}")
            print("---------------------------------")

        except Exception as e:
            print(f"❌ Ocurrió un error durante la importación: {e}")

if __name__ == "__main__":
    asyncio.run(import_products_from_txt())


#COMANDO PARA EJECUTAR EN CONSOLA:

#python scripts/importar-productos.py
