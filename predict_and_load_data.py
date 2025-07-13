import pandas as pd
from sqlalchemy import create_engine
import numpy as np
from datetime import datetime, timedelta
import joblib
import glob

# ========== FUNCIONES AUXILIARES ==========

def get_holiday_dates(start_date, end_date):
    try:
        import holidays
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "holidays"])
        import holidays

    start_year = pd.to_datetime(start_date).year
    end_year = pd.to_datetime(end_date).year
    years_range = range(start_year, end_year + 1)

    us_holidays = holidays.UnitedStates(years=years_range)
    ca_holidays = holidays.UnitedStates(state='CA', years=years_range)

    sf_local_holidays = {}
    for year in years_range:
        sf_local_holidays[f"{year}-02-14"] = "Valentine's Day"
        sf_local_holidays[f"{year}-03-17"] = "St. Patrick's Day"
        sf_local_holidays[f"{year}-05-22"] = "Harvey Milk Day"

    all_holiday_dates = set(us_holidays.keys()) | set(ca_holidays.keys())
    for date_str in sf_local_holidays:
        all_holiday_dates.add(pd.to_datetime(date_str).date())

    holiday_dates = [d for d in sorted(all_holiday_dates)
                     if pd.to_datetime(start_date).date() <= d <= pd.to_datetime(end_date).date()]
    return holiday_dates

def feature_engineering_from_range(start_date, end_date):
    from datetime import timedelta
    import numpy as np
    import pandas as pd

    # Crea el índice horario
    dt_index = pd.date_range(start=start_date, end=end_date, freq='h')
    df = pd.DataFrame(index=dt_index)

    # Calcula feriados automáticamente en el rango
    holiday_dates = get_holiday_dates(start_date, end_date)

    # Variables temporales básicas
    df['hour'] = df.index.hour
    df['day'] = df.index.day
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayofweek'] = df.index.dayofweek
    df['dayofyear'] = df.index.dayofyear
    df['week'] = df.index.isocalendar().week

    df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)
    df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)
    df['is_rush_hour'] = df['hour'].isin([7,8,9,17,18,19]).astype(int)
    def get_period(hour):
        if 0 <= hour <= 5: return 'madrugada'
        elif 6 <= hour <= 11: return 'mañana'
        elif 12 <= hour <= 17: return 'tarde'
        else: return 'noche'
    df['period'] = df['hour'].apply(get_period)

    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['dayofweek_sin'] = np.sin(2 * np.pi * df['dayofweek'] / 7)
    df['dayofweek_cos'] = np.cos(2 * np.pi * df['dayofweek'] / 7)
    df['month_sin'] = np.sin(2 * np.pi * (df['month'] - 1) / 12)
    df['month_cos'] = np.cos(2 * np.pi * (df['month'] - 1) / 12)
    df['dayofyear_sin'] = np.sin(2 * np.pi * (df['dayofyear'] - 1) / 365.25)
    df['dayofyear_cos'] = np.cos(2 * np.pi * (df['dayofyear'] - 1) / 365.25)
    df['week_sin'] = np.sin(2 * np.pi * (df['week'] - 1) / 52)
    df['week_cos'] = np.cos(2 * np.pi * (df['week'] - 1) / 52)

    # Feriados, pre y post
    for feat, offset in [
        ('is_holiday', 0),
        ('is_pre_holiday', -1),
        ('is_post_holiday', +1)
    ]:
        if holiday_dates:
            target_dates = [d + timedelta(days=offset) for d in holiday_dates]
        else:
            target_dates = []
        mask = pd.Series(df.index.date).isin(target_dates)
        df[feat] = mask.astype(int)
        df[feat] = df[feat].fillna(0).astype(int)

    # One-hot period
    dummies = pd.get_dummies(df['period'], prefix='period', drop_first=False)
    df = pd.concat([df, dummies], axis=1)
    for col in dummies.columns:
        df[col] = df[col].astype(int)

    variables_to_drop = ['hour', 'day', 'month', 'year', 'dayofweek', 'dayofyear', 'week', 'period']
    df = df.drop(columns=[var for var in variables_to_drop if var in df.columns])
    return df

def ensure_dim_date(engine, fechas):
    fechas = pd.Series(pd.to_datetime(fechas)).dt.date  # <- CORREGIDO
    fechas = fechas.unique()
    dim_dates = pd.read_sql("SELECT date_id FROM dim_date", engine)
    existentes = set(pd.to_datetime(dim_dates['date_id']).dt.date)
    nuevas = sorted(set(fechas) - existentes)
    if nuevas:
        print(f"🟡 Insertando {len(nuevas)} fechas nuevas en dim_date...")
        df_new = pd.DataFrame({'date_id': nuevas})
        df_new['year']        = pd.to_datetime(df_new['date_id']).dt.year
        df_new['month']       = pd.to_datetime(df_new['date_id']).dt.month
        df_new['day']         = pd.to_datetime(df_new['date_id']).dt.day
        df_new['day_of_week'] = pd.to_datetime(df_new['date_id']).dt.day_name()
        df_new['quarter']     = pd.to_datetime(df_new['date_id']).dt.quarter
        df_new = df_new[['date_id', 'year', 'month', 'day', 'day_of_week', 'quarter']]
        df_new.to_sql('dim_date', engine, if_exists='append', index=False)
    else:
        print("✅ Todas las fechas necesarias ya están en dim_date.")

def ensure_dim_time(engine):
    dim_times = pd.read_sql("SELECT time_id FROM dim_time", engine)
    existentes = set(dim_times['time_id'])
    faltantes = sorted(set(range(24)) - existentes)
    if faltantes:
        print(f"🟡 Insertando horas faltantes en dim_time: {faltantes}")
        df_time = pd.DataFrame({'time_id': faltantes})
        df_time['hour'] = df_time['time_id']
        df_time['am_pm'] = df_time['hour'].apply(lambda h: 'AM' if h < 12 else 'PM')
        def period_of_day(hour):
            if 0 <= hour <= 5:
                return 'Madrugada'
            elif 6 <= hour <= 11:
                return 'Mañana'
            elif 12 <= hour <= 17:
                return 'Tarde'
            else:
                return 'Noche'
        df_time['period_of_day'] = df_time['hour'].apply(period_of_day)
        df_time = df_time[['time_id', 'hour', 'am_pm', 'period_of_day']]
        df_time.to_sql('dim_time', engine, if_exists='append', index=False)
    else:
        print("✅ Todas las horas necesarias ya están en dim_time.")

def export_predictions_to_sql(df_to_insert, table_name, engine):
    ensure_dim_date(engine, df_to_insert['date_id'])
    ensure_dim_time(engine)
    df_to_insert.to_sql(table_name, engine, if_exists="append", index=False)
    print(f"✅ Exportado a {table_name}")

def predict_and_export_all_models_fullrange(
    test_range, 
    future_range, 
    full_range, 
    conn_str, 
    models_folder="models_to_use"
):
    from prophet import Prophet
    engine = create_engine(conn_str)

    for path_model in glob.glob(f"{models_folder}/*.joblib"):
        model_data = joblib.load(path_model)
        modelo = model_data["model"]
        metadata = model_data["metadata"]
        model_name = metadata.get("model_name", "UnknownModel")
        district_id = metadata.get("district_id", None)
        if district_id is None:
            print(f"❌ district_id faltante en {path_model}")
            continue

        print(f"Procesando modelo {model_name}, distrito {district_id}")

        # Features para TODO el rango (test + future)
        df_full_features = feature_engineering_from_range(full_range[0], full_range[-1])
        df_full_features = df_full_features.loc[full_range]

        # ==== DETECCIÓN AUTOMÁTICA DE MODELO Y PREDICCIÓN ====
        if "prophet" in type(modelo).__name__.lower():
            # Prophet puro
            prophet_future = df_full_features.copy().reset_index().rename(columns={'index': 'ds'})
            prophet_future['ds'] = pd.to_datetime(prophet_future['ds'])

            # Extrae de los metadatos los regresores usados (si existen), para filtrar
            regressors = metadata.get("best_params", {}).get("regressor_names", None)
            if regressors is None:
                # Intenta detectar de las columnas presentes en el modelo Prophet
                regressors = [k for k in getattr(modelo, 'extra_regressors', {}).keys()]
            if regressors:
                cols_needed = ['ds'] + list(regressors)
                # Deja solo las columnas necesarias
                prophet_future = prophet_future[cols_needed]

            # Chequeo por NaN en exógenas usadas
            regressor_cols = [col for col in prophet_future.columns if col != 'ds']
            if prophet_future[regressor_cols].isnull().any().any():
                print(f"❗ Hay NaNs en las variables exógenas para el modelo {model_name}.")
                print(prophet_future[regressor_cols].isnull().sum())
                raise ValueError("Variables exógenas contienen NaN.")

            # Predicción Prophet
            yhat_full = modelo.predict(prophet_future)
            df_pred_full = pd.DataFrame({
                "datetime": yhat_full['ds'],
                "date_id": yhat_full['ds'].dt.date,
                "time_id": yhat_full['ds'].dt.hour,
                "district_id": district_id,
                "crime_count_predicted": yhat_full['yhat'],
                "model_name": model_name,
            }).set_index("datetime")

        else:
            # Modelos skforecast/autoregresivos/clásicos
            # Si tiene .current_exog_names úsalo, sino infiere
            if hasattr(modelo, "current_exog_names"):
                exog_features = modelo.current_exog_names
            else:
                # Si en los metadatos guardaste exógenas, úsalo (más seguro)
                exog_features = metadata.get("best_params", {}).get("exog_vars", None)
                if not exog_features:
                    exog_features = [col for col in df_full_features.columns if col != 'crime_count']
            # Garantiza que todas las features estén presentes
            for col in exog_features:
                if col not in df_full_features.columns:
                    df_full_features[col] = 0
            df_full_features = df_full_features[exog_features]

            # Chequeo por NaN
            if df_full_features.isnull().any().any():
                print(f"❗ Hay NaNs en las variables exógenas para el modelo {model_name}. Revisa tu feature engineering.")
                print(df_full_features.isnull().sum())
                raise ValueError("Variables exógenas contienen NaN.")

            # Predicción modelo autoregresivo
            y_pred_full = modelo.predict(steps=len(df_full_features), exog=df_full_features)
            df_pred_full = pd.DataFrame({
                "datetime": df_full_features.index,
                "date_id": df_full_features.index.date,
                "time_id": df_full_features.index.hour,
                "district_id": district_id,
                "crime_count_predicted": y_pred_full,
                "model_name": model_name,
            }).set_index("datetime")

        # Dividir en test y future (esto funciona igual para ambos)
        df_test = df_pred_full.loc[test_range]
        df_future = df_pred_full.loc[future_range]

        # Exportar a SQL
        export_predictions_to_sql(df_test.reset_index(drop=True), "prediction_test", engine)
        export_predictions_to_sql(df_future.reset_index(drop=True), "prediction_future", engine)

    print("✅ Proceso terminado para todos los modelos en prediction_test y prediction_future.")

# ================= PIPELINE PRINCIPAL =================

if __name__ == "__main__":
    conn_str = "mssql+pyodbc://sa:StrongPassw0rd!@localhost:1433/CrimeData?driver=ODBC+Driver+17+for+SQL+Server"
    engine = create_engine(conn_str)

    # 1. OBTENER DATETIMES REALES
    query = """
    SELECT date_id, time_id
    FROM fact_crime_hourly
    ORDER BY date_id, time_id
    """
    df = pd.read_sql(query, engine)
    df['datetime'] = pd.to_datetime(df['date_id']) + pd.to_timedelta(df['time_id'], unit='h')

    # 2. Obtener last_train_datetime (de cualquier modelo, suponiendo todos iguales)
    model_path = glob.glob("models_to_use/*.joblib")[0]
    model_data = joblib.load(model_path)
    last_train_datetime = pd.to_datetime(model_data['metadata']['last_train_datetime'])
    last_fact_datetime = df['datetime'].max()

    # 3. Definir rangos
    # Rango de test (desde el primer punto después del entrenamiento, hasta el último dato real)
    test_range = pd.date_range(
        start=last_train_datetime + pd.Timedelta(hours=1),
        end=last_fact_datetime,
        freq='h'
    )
    n_steps_test = len(test_range)

    # Rango de future (inmediatamente después de test, tamaño igual a test)
    future_range = pd.date_range(
        start=last_fact_datetime + pd.Timedelta(hours=1),
        periods=n_steps_test,
        freq='h'
    )

    # Rango total para predicción (test + future, secuencial sin saltos)
    full_range = pd.date_range(
        start=test_range[0],
        end=future_range[-1],
        freq='h'
    )

    # 4. Asegurar fechas y horas en dimensiones (una sola vez)
    all_needed_dates = pd.Series(
        list(full_range.date)
    ).unique()
    ensure_dim_date(engine, all_needed_dates)
    ensure_dim_time(engine)

    # 5. Ejecutar predicción y exportación
    predict_and_export_all_models_fullrange(
        test_range=test_range,
        future_range=future_range,
        full_range=full_range,
        conn_str=conn_str,
        models_folder="models_to_use"
    )