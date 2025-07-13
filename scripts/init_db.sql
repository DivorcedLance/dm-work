-- 1. BASE DE DATOS Y TABLA ORIGEN (GUARDA TODO)
CREATE DATABASE CrimeData;
GO

USE CrimeData;
GO

-- TABLA RAW: Incluye TODO, aunque haya nulos en category, descript, resolution
CREATE TABLE crime_data (
    Date DATETIME,
    Category VARCHAR(255) NULL,
    Descript VARCHAR(255) NULL,
    DayOfWeek VARCHAR(50),
    PdDistrict VARCHAR(50),
    Resolution VARCHAR(50) NULL,
    Address VARCHAR(255),
    X FLOAT,
    Y FLOAT,
    Id FLOAT,
    DateOnly DATE
);

-- CARGA DE DATOS (ajusta la ruta)
-- Recuerda que debes tener permisos para BULK INSERT y la ruta ser accesible para SQL Server
SET DATEFORMAT ymd;
BULK INSERT crime_data
FROM '/data/crime_data.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FORMAT = 'CSV'
);
GO

-- LIMPIEZA FECHAS Y EXTRACCIÓN DE DateOnly
UPDATE crime_data
SET Date = TRY_CAST(Date AS DATETIME),
    DateOnly = CAST(Date AS DATE)
WHERE TRY_CAST(Date AS DATETIME) IS NOT NULL;
GO

-- 2. DIMENSIONES

-- FECHAS
CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    year INT,
    month INT,
    month_name VARCHAR(20),
    day INT,
    day_of_week VARCHAR(50),
    week_number INT,
    quarter INT
);

INSERT INTO dim_date (date_id, year, month, month_name, day, day_of_week, week_number, quarter)
SELECT DISTINCT
    DateOnly,
    YEAR(DateOnly),
    MONTH(DateOnly),
    DATENAME(MONTH, DateOnly),
    DAY(DateOnly),
    DATENAME(WEEKDAY, DateOnly),
    DATEPART(WEEK, DateOnly),
    DATEPART(QUARTER, DateOnly)
FROM crime_data
WHERE DateOnly IS NOT NULL;
GO

-- TIEMPO (SOLO HORA)
CREATE TABLE dim_time (
    time_id INT PRIMARY KEY,   -- 0-23
    hour INT,
    am_pm VARCHAR(2),
    period_of_day VARCHAR(20)
);

INSERT INTO dim_time (time_id, hour, am_pm, period_of_day)
SELECT n AS time_id,
       n AS hour,
       CASE WHEN n < 12 THEN 'AM' ELSE 'PM' END AS am_pm,
       CASE 
            WHEN n BETWEEN 0 AND 5 THEN 'Madrugada'
            WHEN n BETWEEN 6 AND 11 THEN 'Mañana'
            WHEN n BETWEEN 12 AND 17 THEN 'Tarde'
            ELSE 'Noche'
       END AS period_of_day
FROM (SELECT TOP 24 ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1 AS n FROM sys.objects) t;
GO

-- DISTRITOS
CREATE TABLE dim_district (
    district_id INT IDENTITY(1,1) PRIMARY KEY,
    PdDistrict VARCHAR(50) UNIQUE
);

INSERT INTO dim_district (PdDistrict)
SELECT DISTINCT PdDistrict
FROM crime_data
WHERE PdDistrict IS NOT NULL;
GO

-- 3. TABLA DE HECHOS: CONTEO POR FECHA Y HORA (SOLO CON DATOS COMPLETOS)

CREATE TABLE fact_crime_hourly (
    fact_id INT IDENTITY(1,1) PRIMARY KEY,
    date_id DATE NOT NULL,
    time_id INT NOT NULL,
    district_id INT NOT NULL,
    crime_count INT NOT NULL,

    -- Foreign keys
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
    FOREIGN KEY (district_id) REFERENCES dim_district(district_id)
);

-- RELLENAR CON DATOS LIMPIOS (EXCLUYE FILAS SIN PdDistrict, DateOnly)
INSERT INTO fact_crime_hourly (date_id, time_id, district_id, crime_count)
SELECT
    DateOnly AS date_id,
    DATEPART(HOUR, Date) AS time_id,
    d.district_id,
    COUNT(*) AS crime_count
FROM crime_data c
INNER JOIN dim_district d ON c.PdDistrict = d.PdDistrict
WHERE c.Date IS NOT NULL
  AND c.PdDistrict IS NOT NULL
  AND c.DateOnly IS NOT NULL
GROUP BY DateOnly, DATEPART(HOUR, Date), d.district_id;
GO

-- 4. TABLAS DE PREDICCIONES

-- PREDICCIONES EN EL RANGO DE TEST
CREATE TABLE prediction_test (
    prediction_id INT IDENTITY(1,1) PRIMARY KEY,
    date_id DATE NOT NULL,
    time_id INT NOT NULL,
    district_id INT NOT NULL,
    crime_count_real INT,    -- Valor real (NULL si no hay)
    crime_count_predicted FLOAT NOT NULL,
    model_name VARCHAR(50) NOT NULL,

    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
    FOREIGN KEY (district_id) REFERENCES dim_district(district_id)
);

-- PREDICCIONES PARA EL FUTURO (SÓLO PREDICCIÓN, NO HAY REAL)
CREATE TABLE prediction_future (
    prediction_id INT IDENTITY(1,1) PRIMARY KEY,
    date_id DATE NOT NULL,
    time_id INT NOT NULL,
    district_id INT NOT NULL,
    crime_count_predicted FLOAT NOT NULL,
    model_name VARCHAR(50) NOT NULL,

    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
    FOREIGN KEY (district_id) REFERENCES dim_district(district_id)
);

-- 5. ÍNDICES PARA OPTIMIZAR POWER BI

CREATE INDEX idx_fact_crime_hourly_date ON fact_crime_hourly(date_id);
CREATE INDEX idx_fact_crime_hourly_time ON fact_crime_hourly(time_id);
CREATE INDEX idx_fact_crime_hourly_district ON fact_crime_hourly(district_id);

CREATE INDEX idx_prediction_test_date ON prediction_test(date_id);
CREATE INDEX idx_prediction_test_time ON prediction_test(time_id);
CREATE INDEX idx_prediction_test_district ON prediction_test(district_id);

CREATE INDEX idx_prediction_future_date ON prediction_future(date_id);
CREATE INDEX idx_prediction_future_time ON prediction_future(time_id);
CREATE INDEX idx_prediction_future_district ON prediction_future(district_id);
GO
-- 6. OPCIONAL: VIEW PARA CONSULTAR DATOS "BASE" CON TODAS LAS COLUMNAS RAW

CREATE VIEW vw_crime_data_raw AS
SELECT *
FROM crime_data;
GO

-- VIEW CON EL FORMATO DE TU DATASET DE MODELADO (por fecha, hora, distrito y conteo)
CREATE VIEW vw_fact_crime_hourly AS
SELECT
    f.date_id,
    f.time_id,
    t.hour,
    d.PdDistrict,
    f.crime_count
FROM fact_crime_hourly f
JOIN dim_time t ON f.time_id = t.time_id
JOIN dim_district d ON f.district_id = d.district_id;
GO
