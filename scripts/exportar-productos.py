import asyncio
import json
import os
import sys

# --- Configuración para poder importar desde la carpeta 'api' ---
# Añade el directorio raíz del proyecto al path de Python.
# Esto permite que el script encuentre los módulos de tu aplicación (como 'api.core.database').
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# ----------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

# Importamos la sesión de la base de datos y el DAL de productos que ya existen
from api.core.database import AsyncSessionLocal
from api.productos import dal as productos_dal

# Nombre del archivo de salida
OUTPUT_FILE = "productos_exportados.txt"

async def export_products_to_txt():
    """
    Se conecta a la base deatos, obtiene todos los productos y los guarda
    en un archivo de texto en formato JSON Lines (un JSON por línea).
    """
    print("Iniciando la exportación de productos...")
    
    # Creamos una sesión de base de datos para este script
    async with AsyncSessionLocal() as db:
        try:
            # Usamos la función que ya existe para obtener todos los productos
            productos = await productos_dal.obtener_productos(db)
            
            if not productos:
                print("No se encontraron productos en la base de datos.")
                return

            # Abrimos el archivo de salida en modo escritura
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                count = 0
                for producto in productos:
                    # Convertimos el objeto producto a un diccionario
                    product_data = {
                        "name": producto.name,
                        "description": producto.description,
                        "price": float(producto.price), # Convertimos a float para que sea compatible con JSON
                        "stock": producto.stock,
                        "marca": producto.marca,
                        "image_url": producto.image_url,
                        "category_id": producto.category_id,
                    }
                    # Escribimos el diccionario como una línea de texto JSON en el archivo
                    f.write(json.dumps(product_data, ensure_ascii=False) + "\n")
                    count += 1
            
            print(f"✅ Exportación completa. Se guardaron {count} productos en el archivo '{OUTPUT_FILE}'.")

        except Exception as e:
            print(f"❌ Ocurrió un error durante la exportación: {e}")

if __name__ == "__main__":
    # Ejecutamos la función asíncrona
    asyncio.run(export_products_to_txt())


#COMANDO PARA EJECUTAR EN CONSOLA:

#python scripts/exportar-productos.py