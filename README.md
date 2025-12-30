# 🚍 TransportData: Pipeline de Predicción y Análisis de Transporte Urbano

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![ETL](https://img.shields.io/badge/Pipeline-ETL-green)]()
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-orange)]()
[![React](https://img.shields.io/badge/Frontend-React-61DAFB)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Deploy-Docker-2496ED)](https://www.docker.com/)

> **Sistema integral de Inteligencia de Negocios y Data Engineering para la gestión, validación y predicción de demanda en transporte universitario.**

---

## 📋 Descripción del Proyecto

**TransportData** es una solución _end-to-end_ diseñada para modernizar la gestión logística del transporte. El proyecto no solo administra la operación diaria (validación de usuarios vía QR), sino que implementa un **Pipeline ETL (Extract, Transform, Load)** robusto que alimenta modelos de Machine Learning para predecir la demanda futura y optimizar la asignación de flotas.

Este repositorio demuestra la integración de ingeniería de software con ciencia de datos, enfocándose en la **toma de decisiones basada en datos**.

### 📸 Vista General del Dashboard
![Dashboard Corporativo](assets/image.png)
*Panel administrativo centralizado con KPIs en tiempo real.*

---

## 🏗️ Arquitectura de Datos & Pipeline ETL

El núcleo del proyecto se basa en una arquitectura modular documentada en nuestra wiki interna:

1.  **Ingesta de Datos (Data Ingestion):** Captura de datos transaccionales en tiempo real (validaciones QR, registros de usuarios).
2.  **Infraestructura de Base de Datos:**
    * Modelado relacional optimizado para consultas analíticas.
    * *Ref: [Database Infrastructure](https://deepwiki.com/DivorcedLance/dm-work/2-database-infrastructure)*
3.  **ETL & Preprocesamiento:**
    * Limpieza de datos crudos y manejo de valores nulos.
    * Transformación de timestamps a variables categóricas para análisis temporal.
    * Ingeniería de características (Feature Engineering) para los modelos predictivos.
4.  **Modelado Predictivo:**
    * Entrenamiento de modelos de regresión para estimar afluencia por distrito y día.
    * Pipeline de re-entrenamiento automatizado.
    * *Ref: [Model Development](https://deepwiki.com/DivorcedLance/dm-work/3-model-development)*

---

## 📊 Módulos de Visualización y BI

El sistema cuenta con un frontend analítico que consume los datos procesados, actuando como una herramienta de Business Intelligence personalizada.

### 1. Métricas Clave (KPIs)
Visualización del estado actual de la organización, desglosando usuarios por roles y estado de actividad.
![Métricas](assets/image-2.png)

### 2. Predicción de Demanda (Machine Learning)
El sistema utiliza datos históricos para proyectar la carga de pasajeros.
* **Por Distrito:** Identificación de zonas críticas (ej. San Juan de Lurigancho) para optimizar rutas.
* **Por Día de la Semana:** Análisis de tendencias semanales para la gestión de horarios.

| Distribución Geográfica | Tendencia Semanal |
|:---:|:---:|
| ![Predicción Distritos](assets/image-3.png) | ![Predicción Semana](assets/image-4.png) |

### 3. Validación Operativa
Interfaz móvil para la captura de datos en campo mediante escaneo QR, punto de entrada para el pipeline de datos.
<img src="assets/image-1.png" width="300">

---

## 🛠️ Stack Tecnológico

### Data Engineering & Backend
* **Lenguaje:** Python (Pandas, NumPy).
* **Machine Learning:** Scikit-learn (Modelos de Regresión y Clasificación).
* **Persistencia de Modelos:** Joblib/Pickle para serialización.
* **API:** RESTful API para servir predicciones y datos al frontend.

### Visualización & Frontend
* **Framework:** React / Next.js (Dashboard interactivo).
* **Gráficos:** Recharts / Chart.js para visualización de datos.

### Infraestructura (DevOps)
* **Contenedores:** Docker & Docker Compose para orquestación de servicios.
* **Entorno:** Configuración aislada para reproducibilidad.
* *Ref: [Development Environment](https://deepwiki.com/DivorcedLance/dm-work/7-development-environment)*

---

## 🚀 Instalación y Despliegue

Este proyecto utiliza Docker para facilitar el despliegue del entorno completo (DB, API, Frontend).

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/DivorcedLance/transport-data-etl.git](https://github.com/DivorcedLance/transport-data-etl.git)
    cd transport-data-etl
    ```

2.  **Configurar variables de entorno:**
    Renombrar `.env.example` a `.env` y configurar las credenciales de base de datos.

3.  **Ejecutar con Docker Compose:**
    ```bash
    docker-compose up --build
    ```

4.  **Acceso:**
    * Dashboard: `http://localhost:3000`
    * API Documentation: `http://localhost:8000/docs`

---

## 📈 Impacto de Negocio

La implementación de este sistema permite:
* **Reducción de incertidumbre:** Predicción de picos de demanda con un margen de error reducido.
* **Optimización de recursos:** Asignación dinámica de buses basada en la densidad de usuarios por distrito.
* **Integridad de datos:** Validación digital que elimina el fraude en el acceso al servicio.

---

## 👤 Autor

**José Luis Vergara Pachas**
* *Ingeniero de Software & Data Engineer*
* [LinkedIn](https://www.linkedin.com/in/jose-luis-vergara-pachas-194914259) | [GitHub](https://github.com/DivorcedLance) | [Email](mailto:divorcedlance@gmail.com)