-- DDL para la tabla de predicciones del modelo en el Data Warehouse
USE hotelera_caribe_dw;

CREATE TABLE IF NOT EXISTS predicciones_ocupacion_2025 (
    anio INT,
    mes INT,
    sede_hotel VARCHAR(50),
    tipo_habitacion VARCHAR(50),
    total_noches_ocupadas FLOAT,
    prediccion_noches_rf FLOAT,
    modelo_utilizado VARCHAR(50)
);