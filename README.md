# Eliminar cualquier contenedor existente
docker compose down -v

# Iniciar los contenedores en segundo plano
docker-compose up -d

# Esperar a que los contenedores estén listos
En docker revisa que el contenedor init-db y haya terminado, deberá salir algo así:

```
2025-07-13 14:49:58 Waiting for SQL Server to be ready...
2025-07-13 14:50:08 Initializing database...
2025-07-13 14:50:08 Changed database context to 'CrimeData'.
2025-07-13 14:50:31 
2025-07-13 14:50:31 (1762311 rows affected)
2025-07-13 14:50:33 
2025-07-13 14:50:33 (1762311 rows affected)
2025-07-13 14:50:34 
2025-07-13 14:50:34 (4515 rows affected)
2025-07-13 14:50:34 
2025-07-13 14:50:34 (24 rows affected)
2025-07-13 14:50:34 
2025-07-13 14:50:34 (10 rows affected)
2025-07-13 14:50:39 
2025-07-13 14:50:39 (695398 rows affected)
```

# Instalar python venv
python -m venv venv

# Activar el entorno virtual
source venv/bin/activate

# Instalar las dependencias del proyecto
pip install -r requirements.txt

# Ejecutar script para predecir y cargar a la base de datos el flujo vehicular
python predict_and_load_data.py

# Abrir el dashboard en Power BI Desktop

# Relaciones

![Relacions 01](image.png)
![Relacions 02](image-1.png)