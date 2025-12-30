# 🚓 SF Crime Analytics: Pipeline de Predicción y Análisis de Seguridad

[![Power BI](https://img.shields.io/badge/Business_Intelligence-Power_BI-F2C811?logo=powerbi)](https://powerbi.microsoft.com/)
[![Python](https://img.shields.io/badge/Data_Engineering-Python_3.9-3776AB?logo=python)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/Database-SQL_Server-CC2927?logo=microsoft-sql-server)]()
[![Docker](https://img.shields.io/badge/Infrastructure-Docker-2496ED?logo=docker)]()
[![Machine Learning](https://img.shields.io/badge/Models-XGBoost_%7C_Prophet-orange)]()

> **Solución integral de Business Intelligence que combina un pipeline ETL en Python, infraestructura dockerizada y modelos de Machine Learning para predecir la incidencia delictiva.**

---

## 📋 Entendimiento del Proyecto

Este proyecto se basa en el dataset histórico de **San Francisco Crime Classification** de [Kaggle](https://www.kaggle.com/c/sf-crime).

Aunque el desafío original de Kaggle propone un problema de clasificación (identificar el tipo de crimen), este proyecto realiza un pivote estratégico hacia un enfoque de **Forecasting (Series de Tiempo)**.

**El objetivo:** Predecir la **cantidad** de crímenes por distrito, fecha y hora en los distritos policiales de San Francisco, utilizando modelos predictivos para optimizar la asignación de recursos.

### Flujo de Trabajo
1.  **Infraestructura de Datos:** Inicialización de una base de datos SQL Server mediante Docker, precargada con datos históricos.
2.  **Entrenamiento (Notebooks):** En `final.ipynb` se realiza el análisis exploratorio (EDA), creación de variables exógenas y entrenamiento de modelos.
3.  **Pipeline de Producción:** El script `predict_and_load_data.py` orquesta la generación de predicciones utilizando los modelos entrenados (carpeta `models_to_use`) y carga los resultados en la base de datos.
4.  **Visualización:** Power BI consume los datos procesados para generar insights operativos.

---

## 🏗️ Arquitectura de Datos

El sistema utiliza un esquema relacional optimizado para Analytics, alimentado por un proceso batch automatizado.

1.  **Ingesta & ETL (Python):** Extracción de datos crudos, normalización temporal y gestión de nulos.
2.  **Machine Learning Engine:**
    * Entrenamiento de modelos competitivos (**XGBoost, LightGBM, Prophet**).
    * *Nota:* Se exploraron modelos SARIMA y LSTM, pero se priorizaron los modelos basados en árboles y regresión aditiva por estabilidad.
3.  **Data Warehouse (SQL Server):** Almacenamiento estructurado de hechos históricos y predicciones.
4.  **Visualización (Power BI):** Tableros interactivos conectados a la DB.

---

## 📊 Dashboards y Módulos de Análisis

### 1. Análisis Histórico
Visión general de la criminalidad histórica. Incluye **Heatmaps** que cruzan *Día de la Semana vs. Hora*, identificando patrones críticos.
![Historical Analysis](assets/image.png)

### 2. Validación de Modelos (Backtesting)
Módulo técnico para evaluar la fiabilidad. Compara la curva de **Datos Reales vs. Predicción**.
![Model Validation](assets/image-1.png)

### 3. Benchmarking de Algoritmos
Comparativa de rendimiento entre arquitecturas (LightGBM, Prophet, XGBoost).
![Model Benchmark](assets/image-2.png)

### 4. Forecasting Operativo
Tableros que proyectan la demanda futura mensual y semanal.
| Proyección Mensual | Planificación Semanal |
|:---:|:---:|
| ![Monthly Forecast](assets/image-3.png) | ![Weekly Forecast](assets/image-4.png) |

---

## ⚙️ Guía de Instalación y Despliegue

Sigue estos pasos estrictos para levantar el entorno correctamente.

### 1. Despliegue de Infraestructura (Docker)

Es fundamental limpiar cualquier estado previo de los contenedores para evitar conflictos de volúmenes.

```bash
# Eliminar cualquier contenedor existente y sus volúmenes asociados
docker compose down -v

# Iniciar los contenedores en segundo plano
docker-compose up -d

```

**⚠️ Verificación Crítica:**
Debes revisar los logs del contenedor `init-db` y esperar a que finalice la carga masiva de datos. El proceso habrá terminado exitosamente cuando veas una salida similar a esta:

```text
2025-07-13 14:49:58 Waiting for SQL Server to be ready...
2025-07-13 14:50:08 Initializing database...
2025-07-13 14:50:08 Changed database context to 'CrimeData'.
2025-07-13 14:50:31 
2025-07-13 14:50:31 (1762311 rows affected)
...
2025-07-13 14:50:39 (695398 rows affected)

```

*(No ejecutes los scripts de Python hasta confirmar que la base de datos ha terminado de inicializarse).*

### 2. Configuración del Entorno Python

```bash
# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows: venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar las dependencias del proyecto
pip install -r requirements.txt

```

### 3. Ejecución del Pipeline ETL/ML

Este script toma los modelos entrenados, genera las predicciones futuras y puebla las tablas de hechos en SQL Server.

```bash
# Ejecutar script para predecir y cargar los datos a la DB
python predict_and_load_data.py

```

### 4. Visualización en Power BI

Abre el archivo `.pbix` en Power BI Desktop.

* **Nota sobre Relaciones:** Asegúrate de que todas las tablas de hechos estén correctamente relacionadas con `dim_date`.
* **Columnas Calculadas:** Atributos como `month_name`, `day_of_week` y `week_number` se calculan directamente en Power BI (DAX) para facilitar la gestión de fechas futuras generadas por el script de predicción.

---

## 🚀 Roadmap y Oportunidades de Mejora

Si decides retomar o escalar este proyecto, estas son las áreas técnicas prioritarias a atender:

* **Refactorización de Código (SOLID):** Modularizar la lógica de `final.ipynb` y `predict_and_load_data.py`. Actualmente, funcionalidades como la creación de variables exógenas se repiten; se recomienda centralizarlas en una librería común.
* **Gestión de Idempotencia:** El script de carga actualmente no valida si ya existen predicciones para un rango de fechas. Ejecutarlo múltiples veces podría duplicar registros en `prediction_test` y `prediction_future`.
* **Implementación Robusta de SARIMA/LSTM:** Las clases para estos modelos requieren revisión y ajuste de hiperparámetros para ser estables en el pipeline automatizado.
* **Interfaz de Entrenamiento (CLI/UI):** Desarrollar una interfaz sencilla que permita re-entrenar modelos por distrito seleccionando el algoritmo deseado, facilitando el uso para perfiles no técnicos.
* **Orquestación:** Mejorar el `docker-compose` para que el contenedor de la aplicación espere automáticamente (`wait-for-it`) a que la base de datos esté lista.

---

## ⚠️ Consideraciones Técnicas y Rendimiento

* **Evaluación de Modelos:** Se recomienda encarecidamente realizar pruebas piloto con el distrito **SOUTHERN** (el que posee más datos). Si el MAPE obtenido es superior al 30%, se sugiere revisar la estrategia de agrupación (ej. agrupar solo por `fecha-hora` ignorando distrito).
* **Tiempo de Cómputo:** El entrenamiento completo (9 distritos x 5 modelos + Backtesting) es intensivo. Planifica los tiempos de ejecución acorde al hardware disponible.
* **Optimización del Dataset:** El dataset de Kaggle es extenso. Descartar años muy antiguos puede mejorar significativamente los tiempos de entrenamiento sin sacrificar precisión reciente.

---

## 👤 Autor

**José Luis Vergara Pachas**

* *Data Analyst & Analytics Engineer*
* [LinkedIn](https://www.linkedin.com/in/jose-luis-vergara-pachas-194914259) | [GitHub](https://github.com/DivorcedLance) | [Email](mailto:divorcedlance@gmail.com)