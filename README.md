# 🚍 TransportAnalytics: Pipeline ETL y Predicción de Demanda en Power BI

[![Power BI](https://img.shields.io/badge/Business_Intelligence-Power_BI-F2C811?logo=powerbi)](https://powerbi.microsoft.com/)
[![Python](https://img.shields.io/badge/Data_Engineering-Python_3.9-3776AB?logo=python)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/Database-SQL-4479A1)]()
[![Machine Learning](https://img.shields.io/badge/Analytics-Scikit--Learn-orange)]()

> **Solución de Inteligencia de Negocios (BI) que integra scripts de Python para ETL y Machine Learning, alimentando un sistema de reportes centralizado en Power BI.**

---

## 📋 Resumen del Proyecto

Este proyecto implementa una arquitectura de datos moderna para optimizar la gestión de transporte universitario. A diferencia de los reportes estáticos tradicionales, **TransportAnalytics** utiliza un script de Python automatizado que actúa como motor de cálculo: extrae datos operativos, ejecuta modelos predictivos de demanda y escribe los resultados en una base de datos. Finalmente, **Power BI** se conecta a esta fuente para visualizar métricas históricas y predicciones futuras.

El objetivo es demostrar cómo transformar datos crudos de validación (QR) en decisiones estratégicas sobre rutas y flotas.

---

## 🏗️ Arquitectura del Flujo de Datos (Pipeline)

El sistema sigue un flujo ELT/ETL estricto documentado en nuestra wiki:

1.  **Fuente de Datos (Data Entry):** Registro de validaciones de usuarios mediante escaneo QR (Interfaz Operativa).
2.  **Motor de Procesamiento (Python):**
    * **Extracción:** Script que consulta los nuevos registros de la base de datos transaccional.
    * **Transformación (ETL):** Limpieza de datos, manejo de nulos y estructuración temporal.
    * **Predicción (ML):** Aplicación de modelos de regresión (`scikit-learn`) para estimar la demanda futura por distrito y día.
    * **Carga:** Inserción de los datos procesados y predicciones en tablas analíticas (Data Mart).
3.  **Capa de Visualización (Power BI):**
    * Conexión directa a la base de datos analítica.
    * Modelado de datos (relaciones y medidas DAX).
    * Visualización interactiva para stakeholders.

---

## 📊 Dashboards en Power BI

### 1. Tablero de Control Gerencial (Overview)
Vista principal diseñada para la toma de decisiones rápida. Muestra KPIs consolidados y tendencias de crecimiento mensual procesadas por el script de Python.
![Dashboard Corporativo](assets/image.png)

### 2. Análisis de Métricas y Segmentación
Desglose detallado de la base de usuarios. Permite filtrar por roles (Pasajeros, Conductores) y estado de actividad, facilitando la auditoría del sistema.
![Métricas](assets/image-2.png)

### 3. Modelado Predictivo (Machine Learning Integration)
Aquí se visualiza el valor agregado del script de Python. Power BI grafica los resultados del modelo predictivo almacenados en la DB.

* **Predicción Geoespacial:** Estimación de demanda por distritos (ej. San Juan de Lurigancho) para planificación de nuevas rutas.
* **Predicción Temporal:** Proyección de afluencia por día de la semana para optimizar la frecuencia de buses.

| Distribución por Distrito (Predicción) | Tendencia Semanal (Predicción) |
|:---:|:---:|
| ![Predicción Distritos](assets/image-3.png) | ![Predicción Semana](assets/image-4.png) |

---

## 📱 Origen de los Datos (Validación)
Interfaz de operación utilizada para el registro y validación de usuarios. Estos datos crudos son el insumo principal (`input`) que el script de Python procesa posteriormente.
<img src="assets/image-1.png" width="300">

---

## 🛠️ Stack Tecnológico

### Data Engineering & Scripting
* **Python:** Lenguaje núcleo para la orquestación del pipeline.
* **Pandas/NumPy:** Manipulación y limpieza de dataframes.
* **Scikit-learn:** Entrenamiento y ejecución de modelos predictivos (Regresión).
* **SQL Connector:** Inyección de datos procesados a la base de datos.

### Business Intelligence
* **Microsoft Power BI:** Herramienta de visualización y modelado semántico.
* **DAX:** Creación de medidas calculadas para KPIs dinámicos.
* **Data Modeling:** Diseño de esquema estrella/copo de nieve para optimizar el rendimiento de los reportes.

---

## ⚙️ Cómo ejecutar el Pipeline

1.  **Configuración de Base de Datos:**
    Asegúrese de tener la instancia de base de datos activa y las credenciales en el archivo `.env`.

2.  **Ejecución del Script ETL/ML:**
    El script procesa los datos históricos y genera las predicciones:
    ```bash
    pip install -r requirements.txt
    python etl_prediction_engine.py
    ```
    *Este proceso limpia los datos nuevos y actualiza las tablas de hechos en la DB.*

3.  **Actualización de Power BI:**
    Abrir el archivo `.pbix` y hacer clic en **"Actualizar"**. El dashboard extraerá las nuevas predicciones generadas por Python directamente de la base de datos.

---

## 👤 Autor

**José Luis Vergara Pachas**
* *Data Analyst & BI Developer*
* [LinkedIn](https://www.linkedin.com/in/jose-luis-vergara-pachas-194914259) | [GitHub](https://github.com/DivorcedLance) | [Email](mailto:divorcedlance@gmail.com)